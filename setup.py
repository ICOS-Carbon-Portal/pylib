import setuptools


def readme():
    try:
        with open('README.md') as f:
            return f.read()
    except:
        pass

setuptools.setup(
    name='icoscp',
    version='0.1.17',
	license='GPLv3+',
    author="Claudio D'Onofrio, Zois Zogopoulos, Anders Dahlner, ICOS Carbon Portal",
    author_email='claudio.donofrio@nateko.lu.se, zois.zogopoulos@nateko.lu.se, anders.dahlner@nateko.lu.se, info@icos-cp.eu',
    packages=setuptools.find_packages(),
    include_package_data=True,
    data_files=[('icoscp/.', ['icoscp/countries.json'])],
    description='Access to ICOS data objects hosted at https://data.icos-cp.eu',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://www.icos-cp.eu/',
    project_urls={
            'Source':'https://github.com/ICOS-Carbon-Portal/pylib',
			'Documentation':'https://icos-carbon-portal.github.io/pylib/',
            'DataPortal':'https://data.icos-cp.eu/portal/',
            'SparqlEndpoint':'https://meta.icos-cp.eu/sparqlclient/?type=CSV'},
    install_requires=['pandas','requests','tqdm', 'folium'],
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






