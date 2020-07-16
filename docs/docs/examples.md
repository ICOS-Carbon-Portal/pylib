# Examples


## Digital Object

For the example below, we assume that you know how to get hold of 
the URI use at the Carbon Portal. You can read more about this in the Modules section. The following examples will use the URI [https://meta.icos-cp.eu/objects/lNJPHqvsMuTAh-3DOvJejgYc](https://meta.icos-cp.eu/objects/lNJPHqvsMuTAh-3DOvJejgYc): ICOS Atmosphere Level 2 data, Norunda, release 2019-1. Go to the landing page find more information.

<hr>

### DataFrame

	from icoscp.cpb.dobj import Dobj

	dobj = Dobj('https://meta.icos-cp.eu/objects/lNJPHqvsMuTAh-3DOvJejgYc')
	data = dobj.get()
	data.head(10) 
	
Printing the first 10 rows of the data (data.head(10)) should yield the following table:

id |  Flag |  NbPoints | Stdev  |           TIMESTAMP |          ch4
-- | ----- | --------- | ------ |---------------------| ------------
0  |     N |         0 | -9.990 | 2017-04-01 00:00:00 |          NaN
1  |     N |         0 | -9.990 | 2017-04-01 01:00:00 |          NaN
2  |     O |         9 |  0.079 | 2017-04-01 02:00:00 |  1948.660034
3  |     O |        16 |  1.070 | 2017-04-01 03:00:00 |  1950.900024
4  |     O |        17 |  0.817 | 2017-04-01 04:00:00 |  1953.229980
5  |     O |        16 |  0.271 | 2017-04-01 05:00:00 |  1956.319946
6  |     O |        16 |  0.590 | 2017-04-01 06:00:00 |  1957.810059
7  |     O |        16 |  0.736 | 2017-04-01 07:00:00 |  1960.550049
8  |     O |        16 |  0.429 | 2017-04-01 08:00:00 |  1962.540039
9  |     O |        17 |  0.861 | 2017-04-01 09:00:00 |  1965.349976

<hr>

### Minimalistic Plot

This first example shows how to extract a data file and create a plot. It is the easiest way to load the data into a Pandas DataFrame in your Python environment. The DataFrame contains the following columNames:
Flag, NbPoints, Stdev, TIMESTAMP, ch4. Let's load the data and create a plot for measured methan concentrations over time.

	import matplotlib.pyplot as plt
	from icoscp.cpb.dobj import Dobj

	dobj = Dobj('https://meta.icos-cp.eu/objects/lNJPHqvsMuTAh-3DOvJejgYc')
	data = dobj.get()
	data.plot(x='TIMESTAMP', y='ch4', grid=True)

	plt.show()

![Result](img/dobj_minimal.png)

<hr>

### Plot with Title and Units
To get a useful plot, at least we should have a title and the unit of measurement is absolutely paramount:

	import matplotlib.pyplot as plt
	from icoscp.cpb.dobj import Dobj

	dobj = Dobj('https://meta.icos-cp.eu/objects/lNJPHqvsMuTAh-3DOvJejgYc')
	data = dobj.get()

	# extract information from the dobj meta data
	# look at dobj.info() for a full list 
	unit = dobj.info[1].unit[dobj.info[1]['colName'] =='ch4'].values[0]
	title = dobj.info[0].specLabel[0]
	title = dobj.info[2].stationName[0] + ' (' + dobj.info[2].stationId[0] + ')'
	title = title + '\n'  + dobj.info[0].specLabel[0]

	plot = data.plot(x='TIMESTAMP', y='ch4', grid=True, title=title)
	plot.set(ylabel=unit)

	plt.show()
	
![Result](img/dobj_title.png)

<hr>cd20200715