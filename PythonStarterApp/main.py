from flask import  jsonify, request
from PythonStarterApp import app, readHtmlFile
import datetime
import database
import gui
import HTMLParser


##########################################################################
############################### Web Server ###############################

@app.route('/')
def selectRoute():
    fileName = 'index.html'
    initData = database.getNumberOfTripsOfDOW('Monday', 'All')
    result = gui.plotDayOfWeekTimeline(fileName, initData)
    #result = gui.testPlot(fileName, initData)
    
    return result

@app.route('/visualization2')
def testerRoute1():
    fileName = 'viz2.html'
    dateRange = database.getDateRange()
    initData = database.getTripsHistogramByStation(dateRange[0], dateRange[1], None, None, 15, 'All', 'All', 0)
    stations = database.getAllStationNames()
    
    result = gui.plotHistogram(fileName, initData, stations, dateRange)
    
    return result
    
@app.route('/visualization3')
def testerRoute2():
    fileName = 'viz3.html'
    html = readHtmlFile(fileName)
    
    return html
    
@app.route('/select', methods=['GET'])
def selectDayRoute():  
    dow = request.args.get('dow')
    ut = request.args.get('ut')
    initData = database.getNumberOfTripsOfDOW(dow, ut)
    json = jsonify(x = [d.isoformat() for d in initData['x']], y = initData['y'])

    return json
    
@app.route('/histogram', methods=['GET'])
def histogram(): 
    print "route reached"
    html_parser = HTMLParser.HTMLParser()
    ss = request.args.get('ss')
    
    if ss != "All":
        ss = html_parser.unescape(ss)
        ss = database.getStationId(ss)
    else:
        ss = None
        
    es = request.args.get('es')
    
    if es != "All":
        es = html_parser.unescape(es)
        es = database.getStationId(es)
    else:
        es = None
        
    sd = request.args.get('sd')
    sd = datetime.datetime.fromtimestamp(int(sd)/1000).date()    
    ed = request.args.get('ed')    
    ed = datetime.datetime.fromtimestamp(int(ed)/1000).date() 
    bs = int(request.args.get('bs'))
    g = request.args.get('g')
    ut = request.args.get('ut')
    age = int(request.args.get('age'))
    
    initData = database.getTripsHistogramByStation(sd, ed, ss, es, bs, g, ut, age)
    json = jsonify(x = [d.isoformat() for d in initData['bins']], y = initData['values'])
    print initData
    
    return json
    

@app.route('/testt', methods=['GET'])
def test():
    
    result = database.getTripsHistogramByStation(datetime.datetime(2013, 7, 1).date(),
                                        datetime.datetime(2013,8,1).date(), None, None, 18)
    print "bins:\n",result['bins']
    print "values:\n",result['values']
    
    return ""

