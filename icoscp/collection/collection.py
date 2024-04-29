#!/usr/bin/env python

"""
    The collection module is used to explore ICOS data collected for a specific
    project or data product assembly.

    Example usage:

    from icoscp.collection import collection
    collection.getIdList() # returns a pandas data frame with all collections
    
    myCollection = station.get('collectionId') # create a single collection object
    myCollection.info # print information (attributes) about the collection
    myCollection.data # return a list dobj, associated with the collection
    
"""

__author__      = ["Claudio D'Onofrio"]
__credits__     = "ICOS Carbon Portal"
__license__     = "GPL-3.0"
__version__     = "0.1.0"
__maintainer__  = "ICOS Carbon Portal, elaborated products team"
__email__       = ['info@icos-cp.eu', 'claudio.donofrio@nateko.lu.se']
__status__      = "rc1"
__date__        = "20209-09-23"

from icoscp.sparql.runsparql import RunSparql
from icoscp.sparql import sparqls
from icoscp.cpb.dobj import Dobj
from tqdm import tqdm
import pandas as pd
import requests


# ----------------------------------------------
class Collection():
    """ Create an ICOS collection object. This data structure should not be
        instantiated on its own. Please use the collection.get(id) function.
        
        Thec collection object contains the following attributes:
            id: (str) URL Landing Page
            title: (str) Title of the collection
            description: (str) A short description about the collection            
            data: list[dobj] A list of digital data objects, see module cpb.Dobj
            datalink: list[str] A list of PID/URI for all associated datasets
            citation: (str) The citatin string, IF a DOI is associated.
    """
    
    def __init__(self, coll):
        
        self._id = None             # PID, landing page link        
        self._doi = None            # DOI
        self._citation = None       # Citation string IF DOI is available
        self._title = None          # title for the collection
        self._description = None    # description
        self._info = None           # keep the original pandas data frame 
        self._data = None           # a list of dataobjects
        self._datalink = None       # a list of PID's linking to dobj
        
        self.__set__(coll)          # initialize the object with the
                                    # provided pandas dataframe
                                    
    #-------------------------------------
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, id):
        self._id = id
    #-------------------------------------
    @property
    def doi(self):
        return self._doi
    
    @doi.setter
    def doi(self, doi):
        self._doi = doi
    #-------------------------------------
    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, title):
        self._title = title
    #-------------------------------------
    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, description):
        self._description = description
     #-------------------------------------
    @property
    def data(self):
        return self._data
     #-------------------------------------
    @property
    def datalink(self):
        return self._datalink
    #-------------------------------------
    @property
    def citation(self):
        return self._citation
    #-------------------------------------

    def __str__(self):          
        return self._title
    
    def __set__(self, coll):
        
        self._id = coll.collection.values[0]
        self._doi = coll.doi.values[0]
        self._title = coll.title.values[0]
        self._description = coll.description.values[0]
        
        # get data objects for the collection
         
        query = sparqls.collection_items(self._id)
        dolist = RunSparql(query,'pandas').run()
        
        # keep the list of dobj associated with collection
        self._datalink = dolist.dobj.to_list()
        
        # create dobj objects 
        self._data = []
        for dobj in tqdm(self._datalink):
            self._data.append(Dobj(dobj))     
            
        # citation..        
        self._citation = self.getCitation()
        
        # create the info as dictionary
        self._info = {
            "id": self._id,
            "doi": self._doi,
            "citation" : self._citation,
            "title" : self._title,
            "description" : self._description
            }

    def info(self, fmt='dict'):
        """
        Return information about the collection
        (id, doi, citation, title, description).

        Parameters
        ----------
        fmt : STR, optional, define output format:
            ["dict" | 'pandas' | 'html']. The default is 'dict'.

        Returns
        -------
        FMT
        """
    
        if fmt=='dict':
            return self._info
        
        # convert dict to pandas dataframe....use pandas built-in 
        # converters afterwards
        df = pd.DataFrame.from_dict(self._info, orient='index')
        if fmt=='pandas':
            return df
        if fmt=='html':
            return df.to_html()
        else:
            # default if format is not recogized
            return self._info
    

    def getCitation(self, format='apa', lang='en-GB'):
        '''
        Get a citation string from https://citation.crosscite.org/
        You can provide style & language parameters, default is a simple text
        representation, which is stored in the attribute collection.citation
        
        Example to get a Bibtex styled citation :
            getCitation('bibtex','en-US')
        
        Parameters
        ----------
        format : STR, optional. The default is 'apa'.
        lang : STR, optional. The default is 'en-GB'.
    
        Returns
        -------
        STR, Citation for DOI
    
        '''
        # check if a doi is available at all
        if not self._doi:
            self._citation = 'no citation available'
            return self._citation
        
        # get the citation 
        header = {'accept': 'text/plain'}        
        url = 'https://citation.crosscite.org/format?'
        
        doi = ''.join(['doi=',self._doi])
        style = ''.join(['&style=', format])
        
        lang = ''.join(['&lang=', 'en-GB'])
        query = ''.join([url,doi, style, lang])
        
        r = requests.get(query)
        return(r.content.decode('UTF-8'))

               
# --EOF Collection Class-----------------------------------------            
# ------------------------------------------------------------
def get(collectionId):
    """
    Parameters
    ----------
    collectionId : str StationId (the PID for the collection)
                    extract all collection Id's with getIdList()
                
    Returns
    -------
    collectionn : object Returns a collectionn object, containing the meta
                    data for the collection and a list of dobj.

    """
   
    query = sparqls.collections(collectionId)    
    coll = RunSparql(query,'pandas').run()
 
    # make sure we have one and only one collection
    
    if len(coll)==1:
        return Collection(coll)
    else:
        msg = 'No collection found. Check Id.'
        return msg, False

    
def getIdList():
    """
    Returns a list with all known collections.
    A collection is an assembly of data objects. Have a look at
    https://www.icos-cp.eu/data-products

  
    Returns
    -------
    Pandas data frame with collection Id's, DOI's and Title,...
    """    
    
    query = sparqls.collections()
    coll = RunSparql(query,'pandas').run()
    
    # register tqdm with pandas then change .apply to .progress_apply
    # would be nice, but creates warning with future ...
    # tqdm.pandas()    
    
    # add count of data sets
    coll['dobj'] = coll.apply(lambda x : __itemCount(x['collection']), axis=1)
    coll['count'] = coll.apply(lambda x : len(x.dobj), axis=1)
    
    return coll

def __itemCount(id):
    query = sparqls.collection_items(id)
    item = RunSparql(query,'pandas').run()
    return item.dobj.to_list()
    
# ------------------------------------------------------------    
if __name__ == "__main__":
    """
    execute only if run as a script
    """
    
    msg="""
    Example to get a list of all available collections
    from icoscp.collection import collection
    collection.getIdList()
        
    Example to get a collection and print the citation
    """ 
    c = get('https://meta.icos-cp.eu/collections/n7cIMHIyqHJKBeF_3jjgptHP')
    print(c.info('pandas'))
    #print(msg)