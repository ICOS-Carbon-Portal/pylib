import io
import numpy as np
from numpy.typing import NDArray
import os
import re
import sys
from typing import Any, TypeAlias, TypedDict, Tuple
from dataclasses import dataclass
from .metaclient import MetadataClient
from .metacore import DataObject, StationTimeSeriesMeta, URI
from .queries.dataobjlist import DataObjectLite
from .queries.cpbmeta import CpbMetaData, DatasetCol, get_cpb_meta, get_dataset_cols, get_good_flags_per_spec

@dataclass(frozen=True)
class ColumnInfo:
	label: str
	value_format_uri: URI
	flag_col: str | None = None

@dataclass(frozen=True)
class TableRequest:
	desired_columns: list[str] | None
	offset: int | None
	length: int | None

@dataclass(frozen=True)
class CodecInfo(TableRequest):
	dobj_hash_id: str
	obj_format_uri: URI
	columns: list[ColumnInfo]
	n_rows: int
	good_flags: list[str] | None

def codec_from_dobj_meta(dobj: DataObject, request: TableRequest) -> "Codec":
	spec_info = dobj.specificInfo
	if not isinstance(spec_info, StationTimeSeriesMeta):
			raise Exception(f"Object {dobj.hash} is not a station-specific time series data object.")
	cols_meta = spec_info.columns
	if cols_meta is None:
		raise Exception(f"Metadata of object '{dobj.hash}' does not include any column information")
	col_flags: dict[URI, str] = {
		flagged_col: col.label
		for col in cols_meta if col.isFlagFor is not None
		for flagged_col in col.isFlagFor
	}
	cols_meta_parsed = [
		ColumnInfo(
			label=col.label,
			value_format_uri=col.valueFormat,
			flag_col=col_flags.get(col.model.uri)
		)
		for col in cols_meta
		if col.valueFormat is not None
	]
	if len(cols_meta_parsed) == 0:
		raise Exception(f"Metadata of object '{dobj.hash}' does not include any column for which value format is provided")
	n_rows = spec_info.nRows
	if n_rows is None:
		raise Exception(f"Metadata of object '{dobj.hash}' does not include the number of table rows")
	ci = CodecInfo(
		dobj_hash_id=dobj.hash[:24],
		obj_format_uri=dobj.specification.format.self.uri,
		columns=cols_meta_parsed,
		n_rows=n_rows,
		good_flags=dobj.specification.format.goodFlagValues,
		desired_columns=request.desired_columns,
		offset=request.offset,
		length=request.length
	)
	return Codec(ci)

Dobj: TypeAlias = URI | DataObjectLite

def to_dobj_uri(dobj: Dobj) -> URI:
	if isinstance(dobj, DataObjectLite): return dobj.uri
	elif isinstance(dobj, URI): return dobj
	else: raise ValueError('dobj must be a string or a DataObjectLite instance')

def _resolve_flag_col(flag_col: str | None, actual_cols: list[str]) -> str | None:
	if flag_col is None or flag_col in actual_cols:
		return flag_col
	pattern = re.compile(flag_col)
	for col in actual_cols:
		if pattern.match(col):
			return col
	return None

def codecs_from_dobjs(dobjs: list[Dobj], request: TableRequest, meta: MetadataClient) -> list[Tuple[Dobj, "Codec"]]:

	if len(dobjs) == 0: raise Exception("Got an empty list of data objects")

	dobj_uris = [to_dobj_uri(dobj) for dobj in dobjs]

	cpb_metas: dict[URI, CpbMetaData] = {
		cpb.dobj: cpb for cpb in get_cpb_meta(dobj_uris, meta)
	}

	missing_dobjs = [str(dobj) for dobj in dobjs if to_dobj_uri(dobj) not in cpb_metas]

	if len(missing_dobjs) > 0: raise Exception(
		"Some of the requested objects don't have required metadata to fetch them as tabular data: " +
		",\n".join(missing_dobjs)
	)

	dataset_specs = {cpb.dataset_spec for cpb in cpb_metas.values()}

	if len(dataset_specs) > 1: raise Exception(
		"When requesting data from several data objects, all data objects "
		"must have a common dataset specification"
	)
	dataset_spec = dataset_specs.pop()

	dataset_cols = get_dataset_cols(dataset_spec, meta)
	col_lookup = ColumnLookupByLabel(dataset_cols, dataset_spec)

	dobj_specs = [cpb.obj_spec for cpb in cpb_metas.values()]
	good_flags_lookup: dict[URI, list[str]] = get_good_flags_per_spec(dobj_specs, meta)

	res: list[Tuple[Dobj, "Codec"]] = []
	for dobj in dobjs:
		cpb = cpb_metas[to_dobj_uri(dobj)]
		cols_names = cpb.col_names or col_lookup.default_actual_cols

		cols_info = [
			ColumnInfo(lbl, col.val_format, _resolve_flag_col(col.flag_col, cols_names))
			for lbl, col in
				[(lbl, col_lookup.lookup_column(lbl)) for lbl in cols_names]
			if col is not None
		]
		ci = CodecInfo(
			dobj_hash_id=cpb.dobj.split("/")[-1],
			obj_format_uri=cpb.obj_format,
			columns=cols_info,
			good_flags=good_flags_lookup.get(cpb.obj_spec),
			n_rows=cpb.n_rows,
			desired_columns=request.desired_columns,
			offset=request.offset,
			length=request.length
		)
		res.append((dobj, Codec(ci)))
	return res

ArraysDict: TypeAlias = dict[str, NDArray[Any]]

class Codec:
	def __init__(self, ci: CodecInfo) -> None:
		desired_indices: list[int]
		ci.columns.sort(key=lambda col: col.label)
		if ci.desired_columns is None:
			desired_indices = [i for i in range(len(ci.columns))]
		else:
			labels = [col_info.label for col_info in ci.columns]
			def get_col_idx(col_lbl: str) -> int:
				try:
					return labels.index(col_lbl)
				except ValueError:
					raise ValueError(f'Column "{col_lbl}" is not actually present in data object {ci.dobj_hash_id}')
			expl_desired_indices = {get_col_idx(desired_col) for desired_col in ci.desired_columns}
			flag_indices = {
				get_col_idx(flag_col)
				for flag_col in [ci.columns[i].flag_col for i in expl_desired_indices]
				if flag_col is not None
			}
			desired_indices = [i for i in expl_desired_indices | flag_indices]
			desired_indices.sort()

		# The following checks are needed because the backend does not return user-friendly error messages or results.
		for param, val in [("offset", ci.offset), ("length", ci.length)]:
			if val is not None and val > ci.n_rows:
				raise ValueError(f"The value provided for the '{param}' parameter ({val}) is larger than the number of available rows ({ci.n_rows})")
		if ci.offset is not None and ci.length is not None and ci.n_rows - ci.offset < ci.length:
			raise ValueError(
				f"The value provided for the 'length' parameter ({ci.length}) is larger than the number of available rows ({ci.n_rows}) "
				f"minus the value provided for the 'offset' parameter ({ci.offset})"
			)

		json: dict[str, Any] = {
			"tableId": ci.dobj_hash_id,
			"subFolder": _subfolder_path(ci),
			"schema": {
				"columns": [_get_fmt(col_info.value_format_uri) for col_info in ci.columns],
				"size": ci.n_rows
			},
			"columnNumbers": desired_indices
		}
		if ci.offset is not None or ci.length is not None:
			offset = ci.offset or 0
			length = ci.length or (ci.n_rows - offset)
			json["slice"] = {
				"offset": offset,
				"length": length
			}
		self._ci = ci
		self._json_payload = json
		self._desired_indices = desired_indices

	@property
	def json_payload(self):
		return self._json_payload

	def parse_cpb_response(self, resp: io.BufferedReader, keep_bad_data: bool) -> ArraysDict:
		return self._parse_from_buff(resp, None, keep_bad_data)

	def parse_cpb_file(self, data_folder_path: str, keep_bad_data: bool) -> ArraysDict:

		file_path = os.path.join(
			data_folder_path,
			_subfolder_path(self._ci),
			self._ci.dobj_hash_id + ".cpb"
		)

		col_offsets = _column_offsets(self._ci)

		with open(file_path, "rb") as file:
			return self._parse_from_buff(file, col_offsets, keep_bad_data)


	def _parse_from_buff(self, buff: io.BufferedReader, col_offsets: list[int] | None, keep_bad_data: bool) -> ArraysDict:
		res: ArraysDict = {}
		cols = self._ci.columns
		n_fetch = _n_rows_to_fetch(self._ci)
		for n in self._desired_indices:
			col = cols[n]
			fmt = _get_fmt(col.value_format_uri)
			must_read = _get_byte_size(fmt) * n_fetch
			if col_offsets is not None:
				buff.seek(col_offsets[n])
			col_bytes = buff.read(must_read)
			if must_read > len(col_bytes):
				raise IOError(f'Error while reading cpb response for column {col.label} ({n_fetch} values), reached end of data, but got only {len(col_bytes)} bytes instead of {must_read}')
			arr = np.frombuffer(col_bytes, dtype = _get_format_dtype(fmt))
			arr = _type_post_process(arr, col.value_format_uri)

			if sys.byteorder == 'little':
				# cpb files are all big-endian, fixing for Pandas compatibility on little endian systems:
				arr = arr.view(arr.dtype.newbyteorder()).byteswap()
			res[col.label] = arr

		if not keep_bad_data and self._ci.good_flags:
			flag_masks: dict[str, NDArray[Any]] = {}
			desired_cols = [cols[n] for n in self._desired_indices]
			flag_cols = [
				flag for flag in { # to make the list unique
					col.flag_col
					for col in desired_cols
					if col.flag_col
				}
			]
			good_flags = self._ci.good_flags
			for flag in flag_cols:
				flag_arr = res[flag]
				submasks = [flag_arr == good_flag for good_flag in good_flags]
				flag_masks[flag] = ~np.logical_or.reduce(submasks)
			for col in desired_cols:
				if col.flag_col:
					arr = res[col.label]
					arr[flag_masks[col.flag_col]] = np.nan
		return res


def _column_offsets(ci: CodecInfo) -> list[int]:
	col_cell_sizes: list[int] = [
		_get_byte_size(_get_fmt(col.value_format_uri))
		for col in ci.columns
	]
	col_offset: int = 0
	col_offsets: list[int] = []
	n_skip = ci.offset or 0
	for cell_size in col_cell_sizes:
		col_offsets.append(col_offset + n_skip * cell_size)
		col_offset += cell_size * ci.n_rows
	return col_offsets


def _n_rows_to_fetch(ci: CodecInfo) -> int:
	n_rows = ci.n_rows - (ci.offset or 0)
	if ci.length: n_rows = min(n_rows, ci.length)
	return n_rows


def _subfolder_path(ci: CodecInfo) -> str:
	return ci.obj_format_uri.split("/")[-1]

class RegexCol(TypedDict):
	regex: re.Pattern[str]
	col: DatasetCol

class ColumnLookupByLabel:
	def __init__(self, ds_cols: list[DatasetCol], ds_spec_uri: URI) -> None:
		if len(ds_cols) == 0:
			raise Exception(f"Dataset specification '{ds_spec_uri}' has no columns")
		self._ds_spec_uri = ds_spec_uri
		self._default_actual_cols: list[str] = [col.col_title for col in ds_cols if not (col.is_optional or col.is_regex)]
		self._verbatim_lookup: dict[str, DatasetCol] = {col.col_title: col for col in ds_cols if not col.is_regex}
		self._regex_cols: list[RegexCol] = [
			{"regex": re.compile(col.col_title), "col": col}
			for col in ds_cols if col.is_regex
		]

	@property
	def default_actual_cols(self) -> list[str]:
		res = self._default_actual_cols
		if len(res) == 0:
			raise Exception(f"No mandatory verbatim columns in dataset spec '{self._ds_spec_uri}'")
		return res

	def lookup_column(self, col_label: str) -> DatasetCol | None:
		val_format = self._verbatim_lookup.get(col_label)
		if val_format: return val_format
		for re_col in self._regex_cols:
			if re_col["regex"].match(col_label):
				return re_col["col"]

_fmt_uri_to_fmt = {
	'int32':'INT',
	'float32': 'FLOAT',
	'float64': 'DOUBLE',
	'bmpChar': 'CHAR',
	'string': 'STRING',
	'boolean': 'BYTE',
	'iso8601date': 'INT',
	'etcDate': 'INT',
	'iso8601month': 'INT',
	'iso8601timeOfDay': 'INT',
	'iso8601dateTime': 'DOUBLE',
	'isoLikeLocalDateTime': 'DOUBLE',
	'etcLocalDateTime': 'DOUBLE'
}

def _get_fmt(fmt_uri: str) -> str:
	return _fmt_uri_to_fmt[fmt_uri.split("/")[-1]]

def _type_post_process(arr: NDArray[Any], fmt: URI) -> NDArray[Any]:
	fmt_str = fmt.split("/")[-1]
	if fmt_str == "bmpChar":
		return arr.astype('>u4').view(dtype='>U1')
	elif fmt_str in ["iso8601date", "etcDate"]:
		return arr.astype('>i8').view(dtype=np.dtype('>datetime64[D]'))
	elif fmt_str == "iso8601month":
		return (arr - 1970 * 12).astype('>i8').view(dtype=np.dtype('>datetime64[M]'))
	elif fmt_str == "iso8601timeOfDay":
		return arr.astype('>i8').view(dtype=np.dtype('>timedelta64[s]'))
	elif fmt_str in ["iso8601dateTime", "isoLikeLocalDateTime", "etcLocalDateTime"]:
		return arr.astype('>i8').view(dtype=np.dtype('>datetime64[ms]'))
	else:
		return arr


_fmt_to_dtype: dict[str, np.dtype[Any]] = {
	'INT': np.dtype('>i4'),
	'FLOAT': np.dtype('>f4'),
	'DOUBLE': np.dtype('>f8'),
	'SHORT': np.dtype('>i2'),
	'CHAR': np.dtype('>u2'),
	'BYTE': np.dtype('i1'),
}

def _get_format_dtype(fmt: str) -> np.dtype[Any]:
	try:
		return _fmt_to_dtype[fmt]
	except KeyError:
		raise ValueError(f"Unsupported cpb value format {fmt}")

_fmt_to_byte_size = {
	'INT': 4,
	'FLOAT': 4,
	'DOUBLE': 8,
	'SHORT': 2,
	'CHAR': 2,
	'BYTE': 1,
	'STRING': 4
}

def _get_byte_size(fmt: str) -> int:
	return _fmt_to_byte_size[fmt]

