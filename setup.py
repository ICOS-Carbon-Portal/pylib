import setuptools

def readme():
    try:
        with open('readme.md') as f:
            return f.read()
    except:
        pass


setuptools.setup(
    name='icoscp',
    version='0.1.0rc2',
	license='GPLv3+',
    author="Claudio D'Onofrio, ICOS Carbon Portal",
    author_email='claudio.donofrio@nateko.lu.se, info@icos-cp.eu',
    description='Access to ICOS data objects hosted at https://data.icos-cp.eu',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://www.icos-cp.eu/',
    project_urls={
            'Source':'https://github.com/ICOS-Carbon-Portal/jupyter/tree/master/pytools',
            'DataPortal':'https://data.icos-cp.eu/portal/',
            'SparqlEndpoint':'https://meta.icos-cp.eu/sparqlclient/?type=CSV'},
    packages=setuptools.find_packages(),
    install_requires=['pandas','requests','tqdm'],
    classifiers=[
        'Programming Language :: Python :: 3',
		'Development Status :: 4 - Beta', 
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Intended Audience :: Science/Research',
		'Intended Audience :: Developers',
		'Intended Audience :: Education',
		'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: GIS',
		'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Utilities',        
    ],
)






