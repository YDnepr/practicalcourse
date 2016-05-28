# -*- coding: utf-8 -*-
"""
Created on Mon May 16 22:31:21 2016

@author: Ghareeb
"""
import ibm_db
import os
import datetime
##########################################################################
##################### Initialize Connection Parameters ###################
##########################################################################

DEFULT_DB_NAME = "BLUDB"
DEFAULT_DB_USER = "dash6346"
DEFAULT_PASSWORD = "hbHoTq5pYMTK"
DEFAULT_HOST = "dashdb-entry-yp-dal09-07.services.dal.bluemix.net"
DEFAULR_PORT = "50000"


if 'VCAP_SERVICES' in os.environ:
    hasVcap = True
    import json
    vcap_services = json.loads(os.environ['VCAP_SERVICES'])
    
    if 'dashDB' in vcap_services:
        hasdashDB = True
        service = vcap_services['dashDB'][0]
        credentials = service["credentials"]
        url = 'DATABASE=%s;uid=%s;pwd=%s;hostname=%s;port=%s;' % \
        ( credentials["db"],credentials["username"],credentials["password"],credentials["host"],credentials["port"])
    else:
        hasdashDB = False
  
else:
    hasVcap = False
    url = 'DATABASE=%s;uid=%s;pwd=%s;hostname=%s;port=%s;' % ( DEFULT_DB_NAME, DEFAULT_DB_USER, DEFAULT_PASSWORD, DEFAULT_HOST, DEFAULR_PORT)
    
######################################
########## Internal Usage ############
connection = None

def convertListToColumnList(normalList):
    result = ""
    
    for index in range(0, len(normalList)):
        result += normalList[index]
        
        if index < len(normalList) - 1:
            result += ","
    
    return result
    
def executeSelect(statement):
    connection = ibm_db.pconnect(url, '', '')
    statement = ibm_db.prepare(connection, statement)
    ibm_db.execute(statement)
    data = ibm_db.fetch_tuple(statement)
    result = []     
    
    while (data):
        result.append(data)
        data = ibm_db.fetch_tuple(statement)
    
    ibm_db.free_stmt(statement)
    ibm_db.close(connection)
    
    return result
    
######################################
########## Data Retrieval ############
    
def getStartStationData():
    COLUMNS = [
        "START_STATION_ID",
        "START_STATION_NAME",
        "START_STATION_LATITUDE",
        "START_STATION_LONGITUDE"
    ]
    
    COUNT_COLUMN_NAME = "Count"
    colsAsList = convertListToColumnList(COLUMNS)
    statement = 'SELECT {0}, count(*) as {1} FROM DASH6346.ORGINAL_TRIPDATA_ALL group by {0} order by {1} desc'.format(colsAsList, COUNT_COLUMN_NAME)            
    
    return executeSelect(statement)
    
def getEndStationData():
    COLUMNS = [
        "END_STATION_ID",
        "END_STATION_NAME",
        "END_STATION_LATITUDE",
        "END_STATION_LONGITUDE"
    ]
    
    COUNT_COLUMN_NAME = "Count"
    colsAsList = convertListToColumnList(COLUMNS)
    statement = 'SELECT {0}, count(*) as {1} FROM DASH6346.ORGINAL_TRIPDATA_ALL group by {0} order by {1} desc'.format(colsAsList, COUNT_COLUMN_NAME)            
    
    return executeSelect(statement)

def getNumberOfTripsOfDOW(dow, ut):
    dowInt = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"].index(dow)
    dowInt += 1
    
    if ut == "All":
        utSelect = ""
    else:
        utSelect = " and USERTYPE = '%s' " % (ut)

    select = 'select DATE(TRIPS.STARTTIME), count(*) from TRIPS where DAYOFWEEK(TRIPS.STARTTIME) = %d %s'\
    'group by DATE(TRIPS.STARTTIME) order by DATE(TRIPS.STARTTIME) asc' % (dowInt, utSelect)
    
    result = executeSelect(select)

    x = [item[0] for item in result]
    y = [item[1] for item in result]
    print "db", x, y
    
    return {'x':x, 'y':y}
    
def getTripsByDate (StartDate,EndDate,StartStationId,EndStationID,gender,userType,age):
    
    StartDate = "'" + StartDate.isoformat() + "'"
    EndDate = "'" + EndDate.isoformat() +  "'"
    rules = ''
    Gender=''
    UserType=''
    Age=''
    
    if StartStationId is not None:
        rules += ' and start_station_id='+str(StartStationId)
    if EndStationID is not None:
        rules += ' and end_station_id='+str(EndStationID)
    if gender !='All':
        Gender = " and gender="+gender
    if userType !='All':
        UserType = " and usertype="+"'"+userType+"'"
    if age !=0:
        Age = 'and (birth year)='+str(2016-age)
        
    select = "select DATE(TRIPS.STARTTIME), count(*) from TRIPS where DATE(TRIPS.STARTTIME) >= %s and DATE(TRIPS.STARTTIME) < %s %s %s %s %s"\
    " group by DATE(TRIPS.STARTTIME) order by DATE(TRIPS.STARTTIME) asc"%(StartDate,EndDate,rules,Gender,UserType,Age)
    print select
    rows = executeSelect(select) 
    
    return rows

def splitDateRangeByDays(startDateInclusive, endDateExclusinve, numDays):
    ranges = []
    prev = startDateInclusive
    nextYear = prev + datetime.timedelta(days = numDays)
    
    if nextYear > endDateExclusinve:
        current = endDateExclusinve
    else:
        current = nextYear
        
    ranges.append({'start':prev, 'end':current})  
    
    
    while nextYear < endDateExclusinve: 
        prev = current
        nextYear = current + datetime.timedelta(days = numDays)
        
        if nextYear > endDateExclusinve:
            current = endDateExclusinve
        else:
            current = nextYear
            
        ranges.append({'start':prev, 'end':current}) 
        
    return ranges
        
def getTripsHistogramByStation(startDate, endDate, startStationId, endStationId, binSize, gender, userType, age):
    delta = endDate - startDate
    numBins = delta.days / binSize
    
    if delta.days % binSize > 0:
        numBins += 1
        
    bins = [0]*numBins
    
    data = getTripsByDate( startDate, endDate, startStationId, endStationId, gender, userType, age)
    
    for trip in data:
        tripDate = trip[0]
        binIndex = (tripDate - startDate).days / binSize
        bins[binIndex] += int(trip[1])
            
    binsDates = splitDateRangeByDays(startDate, endDate, binSize)
    binsDates = [item['start'] for item in binsDates]
    
    return {'bins':binsDates, 'values':bins}
            
def getAllStationNames():
    select1 = 'select STATION_NAME from Stations order by STATION_NAME asc'   
    station_names = executeSelect(select1)
    result = []
    
    for row in station_names:
        result.append(row[0])
        
    return result
    
def getDateRange():
    select = 'select min(DATE(TRIPS.STARTTIME)) , max(DATE(TRIPS.STARTTIME)) from TRIPS'
    MinAndMaxDate = executeSelect(select)
    
    return (MinAndMaxDate[0][0], MinAndMaxDate[0][1])
    
def getStationId(stationName):
    select1 = "select STATION_ID from Stations where station_name = '%s'" % (stationName)
    print select1
    startStationID = executeSelect(select1)
    
    return startStationID[0][0]
