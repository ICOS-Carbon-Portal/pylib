from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal, Type, TypeAlias, TypeVar, Any
from dacite import Config, from_dict
import json

Orcid: TypeAlias = str
DoiMeta: TypeAlias = object
Instant: TypeAlias = str
URI: TypeAlias = str
CountryCode: TypeAlias = str
Sha256Sum: TypeAlias = str
LocalDate: TypeAlias = str
JsValue: TypeAlias = object

PinKind: TypeAlias = Literal["Sensor" , "Other"]

@dataclass(frozen=True)
class FeatureCollection:
	features: list[GeoFeature]
	label: Optional[str]
	uri: Optional[URI]


@dataclass(frozen=True)
class Position:
	lat: float
	lon: float
	alt: Optional[float]
	label: Optional[str]
	uri: Optional[URI]


@dataclass(frozen=True)
class LatLonBox:
	min: Position
	max: Position
	label: Optional[str]
	uri: Optional[URI]


@dataclass(frozen=True)
class GeoTrack:
	points: list[Position]
	label: Optional[str]
	uri: Optional[URI]


@dataclass(frozen=True)
class Polygon:
	vertices: list[Position]
	label: Optional[str]
	uri: Optional[URI]


@dataclass(frozen=True)
class Circle:
	center: Position
	radius: float
	label: Optional[str]
	uri: Optional[URI]


@dataclass(frozen=True)
class Pin:
	position: Position
	kind: PinKind


@dataclass(frozen=True)
class FeatureWithGeoJson:
	feature: GeoFeature
	geoJson: str


GeoFeature: TypeAlias = FeatureCollection | Position | LatLonBox | GeoTrack | Polygon | Circle | Pin | FeatureWithGeoJson

@dataclass(frozen=True)
class TimeInterval:
	start: Instant
	stop: Instant


@dataclass(frozen=True)
class TemporalCoverage:
	interval: TimeInterval
	resolution: Optional[str]


@dataclass(frozen=True)
class PlainStaticCollection:
	res: URI
	hash: Sha256Sum
	title: str


@dataclass(frozen=True)
class PlainStaticObject:
	res: URI
	hash: Sha256Sum
	name: str


@dataclass(frozen=True)
class StaticCollection:
	res: URI
	hash: Sha256Sum
	members: list[PlainStaticItem]
	creator: Organization
	title: str
	description: Optional[str]
	previousVersion: Optional[URI]
	nextVersion: Optional[URI | list[URI]]
	latestVersion: URI | list[URI]
	parentCollections: list[UriResource]
	doi: Optional[str]
	coverage: Optional[GeoFeature]
	documentation: Optional[PlainStaticObject]
	references: References


PlainStaticItem: TypeAlias = PlainStaticCollection | PlainStaticObject

DataItemCollection: TypeAlias = StaticCollection

DataItem: TypeAlias = PlainStaticItem | DataItemCollection

@dataclass(frozen=True)
class UriResource:
	uri: URI
	label: Optional[str]
	comments: list[str]


@dataclass(frozen=True)
class LinkBox:
	name: str
	coverImage: URI
	target: URI
	orderWeight: Optional[int]


@dataclass(frozen=True)
class WebpageElements:
	self: UriResource
	coverImage: Optional[URI]
	linkBoxes: Optional[list[LinkBox]]


@dataclass(frozen=True)
class Organization:
	self: UriResource
	name: str
	email: Optional[str]
	website: Optional[URI]
	webpageDetails: Optional[WebpageElements]


@dataclass(frozen=True)
class Person:
	self: UriResource
	firstName: str
	lastName: str
	email: Optional[str]
	orcid: Optional[Orcid]


@dataclass(frozen=True)
class Site:
	self: UriResource
	ecosystem: UriResource
	location: Optional[GeoFeature]


@dataclass(frozen=True)
class Project:
	self: UriResource
	keywords: Optional[list[str]]


@dataclass(frozen=True)
class DataTheme:
	self: UriResource
	icon: URI
	markerIcon: Optional[URI]


@dataclass(frozen=True)
class ObjectFormat:
	self: UriResource
	goodFlagValues: Optional[list[str]]


@dataclass(frozen=True)
class DataObjectSpec:
	self: UriResource
	project: Project
	theme: DataTheme
	format: ObjectFormat
	encoding: UriResource
	dataLevel: int
	specificDatasetType: DatasetType
	datasetSpec: Optional[DatasetSpec]
	documentation: list[PlainStaticObject]
	keywords: Optional[list[str]]


@dataclass(frozen=True)
class DatasetSpec:
	self: UriResource
	resolution: Optional[str]


@dataclass(frozen=True)
class DataAcquisition:
	station: Station
	site: Optional[Site]
	interval: Optional[TimeInterval]
	instrument: Optional[UriResource | list[UriResource]]
	samplingPoint: Optional[Position]
	samplingHeight: Optional[float]


@dataclass(frozen=True)
class DataProduction:
	creator: Agent
	contributors: list[Agent]
	host: Optional[Organization]
	comment: Optional[str]
	sources: list[PlainStaticObject]
	documentation: Optional[PlainStaticObject]
	dateTime: Instant


@dataclass(frozen=True)
class DataSubmission:
	submitter: Organization
	start: Instant
	stop: Optional[Instant]


@dataclass(frozen=True)
class StationTimeSeriesMeta:
	acquisition: DataAcquisition
	productionInfo: Optional[DataProduction]
	nRows: Optional[int]
	coverage: Optional[GeoFeature]
	columns: Optional[list[VarMeta]]


@dataclass(frozen=True)
class ValueType:
	self: UriResource
	quantityKind: Optional[UriResource]
	unit: Optional[str]


@dataclass(frozen=True)
class VarMeta:
	model: UriResource
	label: str
	valueType: ValueType
	valueFormat: Optional[URI]
	isFlagFor: Optional[list[URI]]
	minMax: Optional[tuple[float, float]]
	instrumentDeployments: Optional[list[InstrumentDeployment]]


@dataclass(frozen=True)
class SpatioTemporalMeta:
	title: str
	description: Optional[str]
	spatial: GeoFeature
	temporal: TemporalCoverage
	station: Optional[Station]
	samplingHeight: Optional[float]
	productionInfo: DataProduction
	variables: Optional[list[VarMeta]]


@dataclass(frozen=True)
class DataObject:
	hash: Sha256Sum
	accessUrl: Optional[URI]
	pid: Optional[str]
	doi: Optional[str]
	fileName: str
	size: Optional[int]
	submission: DataSubmission
	specification: DataObjectSpec
	specificInfo: SpatioTemporalMeta | StationTimeSeriesMeta
	previousVersion: Optional[URI | list[URI]]
	nextVersion: Optional[URI | list[URI]]
	latestVersion: URI | list[URI]
	parentCollections: list[UriResource]
	references: References


@dataclass(frozen=True)
class DocObject:
	hash: Sha256Sum
	accessUrl: Optional[URI]
	pid: Optional[str]
	doi: Optional[str]
	fileName: str
	size: Optional[int]
	description: Optional[str]
	submission: DataSubmission
	previousVersion: Optional[URI | list[URI]]
	nextVersion: Optional[URI | list[URI]]
	latestVersion: URI | list[URI]
	parentCollections: list[UriResource]
	references: References


@dataclass(frozen=True)
class Licence:
	url: URI
	name: str
	webpage: URI
	baseLicence: Optional[URI]


@dataclass(frozen=True)
class References:
	citationString: Optional[str]
	citationBibTex: Optional[str]
	citationRis: Optional[str]
	doi: Optional[DoiMeta]
	keywords: Optional[list[str]]
	authors: Optional[list[Agent]]
	title: Optional[str]
	temporalCoverageDisplay: Optional[str]
	acknowledgements: Optional[list[str]]
	licence: Optional[Licence]


Agent: TypeAlias = Organization | Person

StaticObject: TypeAlias = DataObject | DocObject

FunderIdType: TypeAlias = Literal["Crossref Funder ID" , "GRID" , "ISNI" , "ROR" , "Other"]

CityNetwork: TypeAlias = Literal["Munich" , "Paris" , "Zurich" , "Barcelona" , "Unspecified"]

IcosStationClass: TypeAlias = Literal["1" , "2" , "Associated"]

@dataclass(frozen=True)
class Station:
	org: Organization
	id: str
	location: Optional[Position]
	coverage: Optional[GeoFeature]
	responsibleOrganization: Optional[Organization]
	pictures: list[URI]
	specificInfo: StationSpecifics
	countryCode: Optional[CountryCode]
	funding: Optional[list[Funding]]


@dataclass(frozen=True)
class Funding:
	self: UriResource
	funder: Funder
	awardTitle: Optional[str]
	awardNumber: Optional[str]
	awardUrl: Optional[URI]
	start: Optional[LocalDate]
	stop: Optional[LocalDate]


@dataclass(frozen=True)
class Funder:
	org: Organization
	id: Optional[tuple[str, FunderIdType]]


NoStationSpecifics: TypeAlias = None

@dataclass(frozen=True)
class SitesStationSpecifics:
	sites: list[Site]
	ecosystems: list[UriResource]
	climateZone: Optional[UriResource]
	meanAnnualTemp: Optional[float]
	meanAnnualPrecip: Optional[float]
	operationalPeriod: Optional[str]
	discontinued: bool
	documentation: list[PlainStaticObject]


@dataclass(frozen=True)
class AtcStationSpecifics:
	wigosId: Optional[str]
	theme: Optional[DataTheme]
	stationClass: Optional[IcosStationClass]
	labelingDate: Optional[LocalDate]
	discontinued: bool
	timeZoneOffset: Optional[int]
	documentation: list[PlainStaticObject]


@dataclass(frozen=True)
class OtcStationSpecifics:
	theme: Optional[DataTheme]
	stationClass: Optional[IcosStationClass]
	labelingDate: Optional[LocalDate]
	discontinued: bool
	timeZoneOffset: Optional[int]
	documentation: list[PlainStaticObject]


@dataclass(frozen=True)
class EtcStationSpecifics:
	theme: Optional[DataTheme]
	stationClass: Optional[IcosStationClass]
	labelingDate: Optional[LocalDate]
	discontinued: bool
	climateZone: Optional[UriResource]
	ecosystemType: Optional[UriResource]
	meanAnnualTemp: Optional[float]
	meanAnnualPrecip: Optional[float]
	meanAnnualRad: Optional[float]
	stationDocs: list[URI]
	stationPubs: list[URI]
	timeZoneOffset: Optional[int]
	documentation: list[PlainStaticObject]


@dataclass(frozen=True)
class IcosCitiesStationSpecifics:
	timeZoneOffset: Optional[int]
	network: CityNetwork


EcoStationSpecifics: TypeAlias = SitesStationSpecifics | EtcStationSpecifics

IcosStationSpecifics: TypeAlias = AtcStationSpecifics | OtcStationSpecifics | EtcStationSpecifics

StationSpecifics: TypeAlias = NoStationSpecifics | EcoStationSpecifics | IcosStationSpecifics | IcosCitiesStationSpecifics

@dataclass(frozen=True)
class InstrumentDeployment:
	instrument: UriResource
	station: Organization
	pos: Optional[Position]
	variableName: Optional[str]
	forProperty: Optional[UriResource]
	start: Optional[Instant]
	stop: Optional[Instant]


@dataclass(frozen=True)
class Instrument:
	self: UriResource
	model: str
	serialNumber: str
	name: Optional[str]
	vendor: Optional[Organization]
	owner: Optional[Organization]
	parts: list[UriResource]
	partOf: Optional[UriResource]
	deployments: list[InstrumentDeployment]


DatasetType: TypeAlias = Literal["StationTimeSeries" , "SpatioTemporal"]


CPJson = TypeVar('CPJson')

def parse_cp_json(input_text: str, data_class: Type[CPJson]) -> CPJson:
	def tuple_hook(d: dict[str, Any]) -> Any:
		for k in d.keys():
			if isinstance(d[k], list):
					d[k] = tuple(d[k])

		return d

	def empty_dict_to_none(data: dict[str, dict[str, Any] | None]) -> dict[str, Any]:
		for key, value in data.items():
			if isinstance(value, dict) and not value:
				data[key] = None
			elif isinstance(value, dict):
				empty_dict_to_none(value)
		return data

	input_dict=json.JSONDecoder(object_hook=tuple_hook).decode(input_text)

	processed_input_dict = empty_dict_to_none(input_dict)

	return from_dict(data_class=data_class, data=processed_input_dict, config=Config(cast=[list]))
