import os
import re
import shutil
from urllib.parse import urlsplit, unquote
from typing import Iterator, Tuple

from .metaclient import MetadataClient
from .metacore import DataObject
from .queries.dataobjlist import DataObjectLite
from .envri import EnvriConfig
from .auth import AuthTokenProvider, http_auth_request
from .cpb import Codec, TableRequest, ArraysDict, codec_from_dobj_meta, codecs_from_dobjs
from .cpb import Dobj, to_dobj_uri
from .portaluse_client import report_cpb_file_read
from .http import HTTPResponse


class DataClient:
	def __init__(
		self,
		conf: EnvriConfig,
		auth: AuthTokenProvider,
		data_folder_path: str | None
	) -> None:
		self._conf = conf
		self._auth = auth
		self._meta = MetadataClient(conf)
		self._data_folder_path = data_folder_path

	@property
	def meta(self) -> MetadataClient:
		return self._meta

	@property
	def auth(self) -> AuthTokenProvider:
		return self._auth

	def get_file_stream(self, dobj: str | DataObjectLite) -> Tuple[str, HTTPResponse]:
		"""
		Fetches the original verbatim content of a data- or document
		object. The method is HTTP-backed and requires authentication
		if fetching data-, not document, objects.

		:param dobj:
			the landing page URI of the object, or a DataObjectLite
			instance
		:returns:
			a tuple of object filename and the HTTPResponse with
			contents, which can be either saved to disk or directly sent
			for processing
		"""

		dobj_uri = to_dobj_uri(dobj)
		url = self._conf.data_service_base_url + urlsplit(dobj_uri).path
		resp = http_auth_request(url, 'Fetching data object', self._auth)

		filename: str
		if type(dobj) is DataObjectLite:
			filename = dobj.filename
		else:
			disp_head = resp.getheader("Content-Disposition") or ""
			fn_match = re.search(r'filename="(.*)"', disp_head)
			if not fn_match:
				raise Exception(f"No filename information in response from {url}")
			filename = unquote(fn_match.group(1))

		return filename, resp

	def save_to_folder(self, dobj_uri: str | DataObjectLite, folder_path: str) -> str:
		"""
		Downloads the original verbatim content of a data- or document
		object, and saves it to a folder in a file named according to
		object's metadata. If the file already exists, it gets
		overwritten.

		Requires authentication for data object downloads, even on a
		Jupyter notebook with data storage folder access.

		:param dobj_uri:
			the landing page URI of the object, or a DataObjectLite
			instance
		:param folder_path:
			path to the target folder

		:returns:
			the name of the file used to save the object
		"""

		filename, resp_buffer = self.get_file_stream(dobj_uri)

		save_path = os.path.join(folder_path, filename)
		with resp_buffer as reader:
			with open(save_path, "wb") as writer:
				shutil.copyfileobj(reader, writer)
				return filename


	def get_csv_byte_stream(
		self,
		dobj: str | DataObjectLite,
		cols: list[str] = [],
		limit: int | None = None,
		offset: int | None = None
	) -> HTTPResponse:
		"""
		Fetches a standardized plain CSV serialization of a tabular
		data object (that has columnar metadata and has been ingested by
		the data portal).

		This method always requires authentication, even if used from a
		Jupyter notebook with access to the data storage folder.

		:param dobj:
			the landing page URI of the data object, or a
			DataObjectLite instance
		:param cols:
			list of columns to be included; if omitted, all known
			columns will be returned
		:param limit:
			limits the number of table rows to be returned
		:param offset:
			number of rows to skip

		:return:
			HTTPResponse with a stream of CSV bytes. Can be readily
			parsed with `pandas.read_csv`
		"""

		dobj_hash = to_dobj_uri(dobj).split('/')[-1]

		return http_auth_request(
			url = self._conf.data_service_base_url + "/csv/" + dobj_hash,
			error_hint = 'Fetching CSV',
			auth=self._auth,
			data={
				"col": cols,
				"offset": offset,
				"limit": limit
			}
		)


	def get_columns_as_arrays(
		self,
		dobj: DataObject,
		columns: list[str] | None = None,
		keep_bad_data: bool = False,
		offset: int | None = None,
		length: int | None = None
	) -> ArraysDict:
		"""
		Fetches a binary tabular data object and returns it as a
		dictionary of numpy arrays with variable names as keys.

		:param dobj:
			a DataObject instance with detailed data object metadata
			(obtainable from `MetaClient`'s method `get_dobj_meta`)
		:param cols:
			list of columns to be included; if None, all known columns
			will be returned; if the requested columns have accompanying
			quality flag columns, the latter will be automatically
			included.
		:param keep_bad_data:
			flag to force including numeric values that have been
			flagged as not good in corresponding quality flag columns;
			by default these values are set to NaN
		:param offset:
			number of heading rows to skip; if None, does not skip any
			row
		:param length:
			number of rows to return; if None, return all rows

		:return:
			a dictionary mapping column names to numpy arrays. The
			dictionary can be readily sent to `pandas.DataFrame`
			constructor.
		"""

		req = TableRequest(desired_columns=columns, offset=offset, length=length)
		codec = codec_from_dobj_meta(dobj, req)
		res = self._get_columns_as_arrays(codec, keep_bad_data)

		if self._data_folder_path is not None:
			report_cpb_file_read(self._conf, self._auth, hashes = [dobj.hash[:24]], columns=columns)

		return res


	def batch_get_columns_as_arrays(
		self,
		dobjs: list[Dobj],
		columns: list[str] | None = None,
		keep_bad_data: bool = False
	) -> Iterator[Tuple[Dobj, ArraysDict]]:
		"""
		Efficient batch-fetching version of `get_columns_as_arrays`
		method. Can only be used with groups of data objects of the same
		data type, or whose data types share a dataset specification.

		:param dobjs:
			either a list of data object landing page URIs, or a list of
			`DataObjectLite` instances (obtainable from `MetaClient`'s
			method `list_data_objects`)

		:param columns:
			a list of names of columns to be fetched, or `None` for all
			preview-available columns in the data objects. If the
			requested columns have accompanying quality flag columns,
			the latter will be automatically included.

		:param keep_bad_data:
			flag to force including numeric values that have been
			flagged as not good in corresponding quality flag columns;
			by default these values are set to NaN

		:return:
			a lazy iterable of pairs of the data objects (echoed back
			from the `dobjs` input) and a dictionary mapping column
			names to numpy arrays.
		"""
		req = TableRequest(columns, None, None)
		dobj_codecs = codecs_from_dobjs(dobjs, req, self._meta)

		if self._data_folder_path is not None:
			hashes = [to_dobj_uri(dobj).split('/')[-1] for dobj, _ in dobj_codecs]
			report_cpb_file_read(self._conf, self._auth, hashes=hashes, columns=columns)

		for dobj, codec in dobj_codecs:
			yield dobj, self._get_columns_as_arrays(codec, keep_bad_data)


	def _get_columns_as_arrays(self, codec: Codec, keep_bad_data: bool) -> ArraysDict:
		if self._data_folder_path is not None:
			return codec.parse_cpb_file(self._data_folder_path, keep_bad_data)

		resp = http_auth_request(
			url=self._conf.data_service_base_url + '/cpb',
			error_hint="Fetching binary",
			auth=self._auth,
			method="POST",
			headers={"Accept": "application/octet-stream"},
			data=codec.json_payload
		)
		return codec.parse_cpb_response(resp.fp, keep_bad_data)
