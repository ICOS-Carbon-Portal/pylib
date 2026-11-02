# icoscp_core changelog

## 0.3.13
- #### metadata
    - Fix URI protocol rewriting.

## 0.3.12
- #### metacore
    - Regenerate from the current Scala backend: remove the `Network`
      class, update `CityNetwork` literals, and add `empty_dict_to_none`
      JSON preprocessing.
- #### cpb
    - Fix flag column resolution. Regex-pattern flag column names from
      metadata were passed through as-is instead of being matched
      against the actual column names, so lookups failed.
- #### packaging
    - Switch the build backend from `flit` to `hatch`.
    - Add a changelog link to `[project.urls]` for PyPI.
    - Update the maintainer list and email addresses.

## 0.3.11
- #### dependencies
    - Remove the `numpy < 2` limit.
- #### metaclient
    - Fix station URI handling by converting between `http` and `https`
      where needed.

## 0.3.10
- #### cpb
    - Add a boolean value format.
- #### modules
    - Fix a circular import.

## 0.3.9
- #### release
    - Released the same day as `0.3.8`, with no separately recorded
      changes.

## 0.3.8
- #### dataclient
    - Report a clear error when fetching the content of a data object
      without having accepted the licence terms.
- #### modules
    - Fix a circular import.

## 0.3.7
- #### http
    - Overhaul request handling.
- #### cpb
    - Best-effort reporting of the user for Jupyter `cpb` access.
- #### queries
    - Simplify the SPARQL query by dropping `filter exists` inside
      `optional`.
- #### typing
    - Assorted type annotation fixes.

## 0.3.6
- #### collection metadata
    - Add `parentCollections` to `StaticCollection`.
    - Add `coverage` to `StaticCollection`, declared as
      `Optional[GeoFeatureWithGeo]` so it carries GeoJSON.
    - Make `StaticCollection.members` lighter when sub-collections are
      present. Values can now be either `PlainStaticObject` or
      `PlainStaticCollection`; the two differ in their fields (`name`
      versus `title`), so test at runtime, as a collection can contain
      both objects and other collections.
- #### documentation
    - Update the `meta.get_collection_meta` examples accordingly.

## 0.3.5
- #### dependencies
    - Limit the dependency to `numpy < 2`.
- #### documentation
    - Minor README update.

## 0.3.4
- #### metaclient
    - Correct Carbon Portal ontology URLs from `https` to `http`.
    - Add `format` to `DobjSpecLite` and document the class.
- #### dataclient
    - Add an `auth` property.
- #### cpb
    - Fix a typo in date format post-processing.

## 0.3.3
- #### metaclient
    - Add `get_collection_meta()`.
- #### auth
    - Improve error messages and documentation.

## 0.3.2
- #### geo
    - Add a geographical filter, with examples and a new bootstrap
      method.
    - Fix `polygon_to_wkt`.
- #### documentation
    - Rework the introductory part of the README.

## 0.3.1
- #### metacore
    - Metadata updates accompanying CF-compliant NetCDF preview support.

## 0.3.0
- #### dependencies
    - Drop the `requests` dependency.
- #### http
    - Rework the module along more systematic lines.
- #### cpb
    - Improve binary fetch performance.
    - Return arrays with more consistent endianness.

## 0.2.2
- #### cpb
    - Inject flags in non-batch data fetch.
    - Set bad values to `NaN` by default.

## 0.2.1
- #### cpb
    - Add flag columns to batch data fetch, preparing for good/bad flag
      filtering.
    - Byte-swap on little-endian systems for pandas compatibility.
- #### metacore
    - Use frozen dataclasses; fix person and role metadata.
- #### documentation
    - Update the `DataClient` documentation.

## 0.2.0
- #### cpb
    - Parse binaries with `numpy`.
    - Support file access event logging.
- #### metacore
    - Make all dataclasses immutable.
    - Add extensions for `GeoFeature` classes with a `geo` field.
- #### jupyter
    - Basic support for deployment on Jupyter.
- #### documentation
    - Expand the documentation, in particular for the authentication
      mechanisms.

## 0.1.2
- #### cpb
    - Add batch fetching of binary tabular data.
    - Add fetching of the binary of a single data object.
    - Convert unicode and time types, and keep track of column indices
      when some columns are filtered out.
- #### metaclient
    - Enhance `DataObjectLite` and `StationLite`, and document more of
      the client.
- #### bootstrap
    - Hide the `envri` module behind the bootstrapping code.

## 0.1.1
- #### release
    - Released the same day as `0.1.0`, with no separately recorded
      changes.

## 0.1.0
- #### initial release
    - Metadata access through `MetaClient`, including data type and
      station listings.
    - Data access through `DataClient`, with the `cpb` binary format
      reader.
    - Authentication, and bootstrapping for the ICOS, SITES and ICOS
      Cities repositories.
