# Welcome to the ICOS Carbon Portal Python Library 

## ICOS

The Integrated Carbon Observation System, ICOS, is a European-wide greenhouse gas research infrastructure. ICOS produces standardised data on greenhouse gas concentrations in the atmosphere, as well as on carbon fluxes between the atmosphere, the earth and oceans. This information is being used by scientists as well as by decision makers in predicting and mitigating climate change. The high-quality and open ICOS data is based on the measurements from 134 stations across 12 European countries. For more information please visit [https://www.icos-cp.eu/](https://www.icos-cp.eu/)

This library provides an easy access to data hosted at the ICOS Carbon Portal ([https://data.icos-cp.eu/](https://data.icos-cp.eu/) ). By using this library you can load data files directly into memory.  The approach of this library is to free you from downloading and maintaining a local copy of data files and if you choose to use our Jupyter Hub services, you don't even need computational power.

If you would rather stick to the conventional "download the data" approach, to store and use the data locally, we suggest you go to the data portal website and "download" the data.

The ICOS Carbon Portal provides persistent digital object identifiers for each data set or file to improve the FAIR-ness of data and to give all the users easy tools for provenance, citation and reproducibility, etc.. Hence you only need to store a list of pid's (persistent digital object identifiers), or you can use one of the built in sparql queries, to reproduce always exactly the same result, regardless on which computer you run it. You can share your code with colleges, without the need of moving data around. Basically you bring the software to the data, rather then data to the software. This is especially true, if you create a Jupyter Notebook hosted at the Carbon Portal.

## Changelog

- 2020/07/15 publish first version to pypi.org
- 2020/10/01 release 0.1.3

	- Add module 'collection' to support loading data products. See [Modules / collection](modules.md#collection)
	- Change behaviour of Dobj to keep data persistent. The pandas data frame is now persistent stored as pandas dataframe in the object. Older versions did query the server every time for the data. A new attribute is available: `Dobj.data` which returns the pandas dataframe. This change in behaviour is controlled with `Dobj._datapersistent = True` (default), and can be reverted by setting it to False. 
	- A new attribute `Dobj.id` is available (which is equivalent to Dobj.dobj) but is more human understandable. Dobj.id retrieves or sets the PID/URI.





