# Welcome to the ICOS Carbon Portal Python Library 

## ICOS

The Integrated Carbon Observation System, ICOS, is a European-wide greenhouse gas research infrastructure. ICOS produces standardised data on greenhouse gas concentrations in the atmosphere, as well as on carbon fluxes between the atmosphere, the earth and oceans. This information is being used by scientists as well as by decision-makers in predicting and mitigating climate change. The ICOS Station Network consists of over 170 measurement stations in three domains located in 16 countries in Europe. For more information please visit [https://www.icos-cp.eu/](https://www.icos-cp.eu/).


## icoscp Python library
This library provides easy access to data hosted at the ICOS Carbon Portal ([https://data.icos-cp.eu/](https://data.icos-cp.eu/)). By using this library you can load data files directly into memory. The purpose of this library is to free you from downloading and maintaining a local copy of data files and if you choose to use our Jupyter Hub services, you don't even need computational power.

If you prefer the conventional "download the data" approach, to store and use the data locally, we recommend using [data portal](https://data.icos-cp.eu/) web application to find, preview and download the data.

## The history and the new role of the library
This library has a history of being developed somewhat empirically, resulting in mismatch with the Carbon Portal metadata model and APIs, and suboptimal performance. Starting from version `0.2.0`, it is being put on a more principled foundation in the form of a new library **[icoscp_core](https://pypi.org/project/icoscp_core/)**, also developed by the Carbon Portal. The new library is now a dependency of **icoscp**, meaning that by installing **icoscp** one automatically gains access to all the functionality of **icoscp_core**. As the latter happens to have all the functionality expected to be *required* by most use cases, the majority of **icoscp** code written prior to version `0.2.0` is being assigned a legacy status. Legacy in this context means that it is not recommended for new projects, but will be preserved to keep all the existing code, that depends on older versions of **icoscp**, working in the foreseeable future.

For new projects, developers are advised to consider
**[icoscp_core](https://pypi.org/project/icoscp_core/)** as the first choice, unless it is explicitly known that some specific **icoscp** feature is required.

However, it should be recognized that **icoscp_core**, though making possible to achieve with little code things that were previously impossible or lengthy with **icoscp**, is a somewhat lower-level library. Notably, **icoscp_core** does not depend on **pandas** library, which means the developers who want to work with pandas DataFrames, may need to take one extra step (albeit short and easy) to produce them from **icoscp_core** outputs. Additionally, **icoscp_core** was designed to serve not only ICOS, but also other data repositories based on Carbon Portal server software, which makes it inappropriate to add much ICOS-specific functionality to **icoscp_core**.

Hence, the new role of **icoscp** library is three-fold:

- keeping the legacy functionality intact, to prevent breakage of Jupyter notebooks and Python scripts that depend on the older library versions
- providing convenient high-level ICOS-specific functionality, built on top of **icoscp_core**; future examples of that are
  * the latest near-real-time data for comparison across stations
  * concatenation of latest L2 release with corresponding latest near-real-time dataset
- making all the **icoscp_core** functionality available as a dependency

## ICOS data licence
Please be aware, that by either downloading or accessing the data directly through this library, you acknowledge that all ICOS data are provided under a <a href="https://data.icos-cp.eu/licence" target="_blank">CC BY 4.0 licence <img src="https://www.icos-cp.eu/sites/default/files/inline-images/creativecommons.png"></a>, and accept the licence. When using the library standalone (not on a Carbon-Portal-provided Jupyter instance) to access the *data*, you are required to authenticate as a user with ICOS licence accepted in your Carbon Portal profile ([https://cpauth.icos-cp.eu/](https://cpauth.icos-cp.eu/)). *Metadata* access, on the other hand, is provided for anonymous users as well as for registered ones.


## (older) Notes

The ICOS Carbon Portal provides persistent digital object identifiers for each data set or file to improve the FAIR-ness of data and to give all the users easy to use tools for provenance, citation and reproducibility, etc. Hence you only need to store a list of PID's (persistent digital object identifiers), or you can use one of the built-in SPARQL queries, to reproduce always the same result, regardless of the computer you run it on. You can share your code with colleagues, without the need of moving data around. You bring the software to the data, rather than data to the software. This is especially true if you create a Jupyter Notebook hosted at the Carbon Portal.

You can follow the development on the [GitHub repository](https://github.com/ICOS-Carbon-Portal/pylib). Create an issue to report bugs or request new features. The library has not been thoroughly tested on many different operating systems and environments, hence we appreciate feedback.

The library is developed with  Python 3.10, and we assume that any
recent Python distribution should work. If you have any trouble running the library, we would like to hear about it. Please get in touch: jupyter-info@icos-cp.eu
