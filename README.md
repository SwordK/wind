# wind : data processor for wind api 

## Dependence:

* WindPy
* pymssql

## Packages: 

### 1. windProcessor

* windDataTransform:

  Usage:

  ​	Transform wind data(wset, wsi, wsd, wss) to list. 

  Return value: 

  1. None: Error occur in the function

  2. list[0]: Result Fields.

  3. list[1]: Results. each elem is a list which corresponding to list[0].

### 2.database

* sqlServer

### 3.windDb

* windDb

  Usage:

  ​	Wind Database Query (Microsoft SqlServer).

### 4.utils

* dateTime:

  Usage:

  ​	Date and time transform functions.

