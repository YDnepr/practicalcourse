# -*- coding: utf-8 -*-
"""
Created on Mon May 16 22:53:45 2016

@author: Ghareeb
"""

from bokeh.io import vform,hplot
from bokeh.embed import components
from bokeh.models import CustomJS, ColumnDataSource, Select, DatePicker, TextInput, Toggle,DataTable, TableColumn,Slider
from bokeh.plotting import Figure

import BeautifulSoup
from PythonStarterApp import readHtmlFile

import folium
from folium import plugins

########################################################################
################################# HTML #################################

def generateMapIFrame(data):
    max = int(data[0][len(data[0]) - 1])
    result = []
    
    for row in data:
        result.append([float(row[2].replace(',','.')), float(row[3].replace(',','.')),  float(row[4]) / max])
    
    new_york_coo = [40.712495, -73.988651]
    f = folium.element.Figure()
    map = folium.Map(new_york_coo, tiles='stamentoner', zoom_start=13)
    map.add_to(f)
    map.add_children(plugins.HeatMap(result))
    
    iframe = folium.element.IFrame(width=700, height=700)
    f.add_to(iframe)
    
    return iframe.render()
    
def appendElementContent(htmlPage, newContent, elementType = 'div', elementId = 'bokehContent'):
    soup = BeautifulSoup.BeautifulSoup(htmlPage)
    if not elementId is None:
        element = soup.find(elementType, id = elementId)
    else:
        element = soup.find(elementType)
    extraSoup = BeautifulSoup.BeautifulSoup(newContent)
    element.append(extraSoup)

    return str(soup)
    
def insertScriptIntoHeader(htmlPage, script):
    return appendElementContent(htmlPage, script, "head", None)
    
def plotHistogram(fileName, initData, stations, dateRange, bokehPlaceholderId='bokehContent'):
    data = {'xs':[initData['bins']], 'ys':[initData['values']],'ss':[1,2], 'es':[3,4] }#ss and es are for test purposes we'll add  other values of the controlles e.g. age, usertype, Gender coming fetshed from initdata 

    source = ColumnDataSource(data=data)
    stations.insert(0, "All")
    selectSS = Select(title="Start Station:", value="All", options=stations)
    selectES = Select(title="End Station:", value="All", options=stations)
    
    selectUT = Select(title="User Type:", value="All", options=["All", "Subscriber", "Customer"])
    selectGender = Select(title="Gender:", value="All", options=["All", "Male", "Female"])
    sliderAge = Slider(start=8, end=100, value=30, step=1, title="Age")    
    
    startDP = DatePicker(title="Start Date:", min_date=dateRange[0] ,max_date=dateRange[1], value=dateRange[0])
    endDP = DatePicker(title="End Date:", min_date=dateRange[0] ,max_date=dateRange[1], value=dateRange[1])
    binSize = TextInput(value="15", title="Bin Size (Days):")
    AddButton = Toggle(label="Add", type="success")
    DeleteButton = Toggle(label="delete", type="success")
    
    
    columns = [TableColumn(field="ss", title="Start Station"),TableColumn(field="es", title="End Station")]# add other columns contains values of other controllers
    data_table = DataTable(source=source, columns=columns, width=650, height=300)
    
    model = dict(source=source, selectSS = selectSS, selectES = selectES, startDP = startDP, endDP = endDP, binSize = binSize,selectUT=selectUT,selectGender=selectGender,sliderAge=sliderAge)
    plot = Figure(plot_width=650, plot_height=400, x_axis_type="datetime")
    plot.multi_line('xs', 'ys', source=source, line_width='width', line_alpha=0.6, line_color='color')
    
    callback = CustomJS(args=model, code="""
            //alert("callback");
            var startStation = selectSS.get('value');
            var endStation = selectES.get('value');
            var startDate = startDP.get('value');
            
            if ( typeof(startDate) !== "number")
                startDate = startDate.getTime();
                
            var endDate = endDP.get('value');
            
            if ( typeof(endDate) !== "number")
                endDate = endDate.getTime();            
            
            var binSize = binSize.get('value');
            
            var gender
            if (selectGender.get('value')=='Male')
                gender = '1';
            else if (selectGender.get('value')=='Female')
                gender = '2';
            else if (selectGender.get('value')=='All')
                gender='All'
            var userType = selectUT.get('value');
            var age = sliderAge.get('value');

            //alert(startStation + " " + endStation + " " + startDate + " " + endDate + " " + binSize);
            var xmlhttp;
            xmlhttp = new XMLHttpRequest();
            
            xmlhttp.onreadystatechange = function() {
                if (xmlhttp.readyState == XMLHttpRequest.DONE ) {
                    if(xmlhttp.status == 200){
                        var data = source.get('data');
                        var result = JSON.parse(xmlhttp.responseText);
                        var temp=[];
                        
                        for(var date in result.x) {
                            temp.push(new Date(result.x[date]));
                        }
                        
                        data['xs'].push(temp);
                        data['ys'].push(result.y);
                        source.trigger('change');
                    }
                    else if(xmlhttp.status == 400) {
                        alert(400);
                    }
                    else {
                        alert(xmlhttp.status);
                    }
                }
            };
        var params = {ss:startStation, es:endStation, sd:startDate, ed:endDate, bs: binSize, g:gender, ut:userType, age:age};
        url = "/histogram?" + jQuery.param( params );
        xmlhttp.open("GET", url, true);
        xmlhttp.send();
        """)
        
    
    AddButton.callback = callback
    #DeleteButton.on_click(callback1)
    layout1 = vform (startDP,endDP,binSize)
    layout2 = vform(plot,DeleteButton,data_table)
    layout3 = vform(selectSS, selectES,selectUT,selectGender,sliderAge,AddButton)
    layout = hplot(layout1,layout2,layout3)
    script, div = components(layout)
    html = readHtmlFile(fileName)
    html = insertScriptIntoHeader(html, script)
    html = appendElementContent(html, div, "div", "bokehContent")

    return html  
    
def plotDayOfWeekTimeline(fileName, initData, bokehPlaceholderId='bokehContent'):    

    source = ColumnDataSource(data=initData)
    selectDOW = Select(title="Days:", value="Monday", options=["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
    selectUT = Select(title="User Type:", value="All", options=["All", "Subscriber", "Customer"])
    model = dict(source=source, select_dow = selectDOW, select_ut = selectUT)
    plot = Figure(plot_width=1200, plot_height=400, x_axis_type="datetime")
    plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)
    
    callback = CustomJS(args=model, code="""
          var dayOfWeek = select_dow.get('value')
            var userType = select_ut.get('value')
            var xmlhttp;
            xmlhttp = new XMLHttpRequest();
            
            xmlhttp.onreadystatechange = function() {
                if (xmlhttp.readyState == XMLHttpRequest.DONE ) {
                    if(xmlhttp.status == 200){
                        var data = source.get('data');
                        var result = JSON.parse(xmlhttp.responseText);
                        var temp=[];
                        
                        for(var date in result.x) {
                            temp.push(new Date(result.x[date]));
                        }
                        
                        data['x'] = temp;
                        data['y'] = result.y;
                        source.trigger('change');
                    }
                    else if(xmlhttp.status == 400) {
                        alert(400);
                    }
                    else {
                        alert(xmlhttp.status);
                    }
                }
            };
        var params = {dow:dayOfWeek, ut:userType};
        url = "/select?" + jQuery.param( params );
        xmlhttp.open("GET", url, true);
        xmlhttp.send();
        """)
        
    selectDOW.callback = callback
    selectUT.callback = callback
    layout = vform(selectDOW, selectUT, plot)
    script, div = components(layout)
    html = readHtmlFile(fileName)
    html = insertScriptIntoHeader(html, script)
    html = appendElementContent(html, div, "div", "bokehContent")

    return html
    
    