#dashDB and Python

For issues that you encounter with this service, go to [**Get help**](https://www.ibmdw.net/bluemix/get-help/) in the Bluemix development community.

You can bind your Python application to the dashDB Service database and work with your data. This topic explains how to get your code running using this method. The sample illustrated here uses the Flask web application framework.
Required components

The following components are required to connect dashDB from a Python application. The are all described in further detail in this topic.

- requirements.txt
- python program

####requirements.txt
The requirements.txt contains information about the app dependencies. Add the following ibm_db and flask dependencies to your requirements.txt file. ibm_db is required to connect to the dashDB database and flask is the web application framework used to run the application.
```
  ibm_db
  flask
```
###Connecting to dashDB from python code

In your application code, parse the VCAP_SERVICES environment variable to retrieve the database connection information. Use this information to connect to the database.

For more information on the structure of the VCAP_SERVICES environment variable see Getting Started with the dashDB Service
```
import json
vcap_services = json.loads(os.environ['VCAP_SERVICES'])
service = vcap_services['dashDB'][0]
credentials = service["credentials"]
url = 'DATABASE=%s;uid=%s;pwd=%s;hostname=%s;port=%s;' % ( credentials["db"],credentials["username"],credentials["password"],credentials["host"],credentials["port"])
```
You can now use this connection information obtained above, to connect and query the database. Here we are constructing an HTML output and returning it.
```
connection = ibm_db.connect(url, '', '')
statement = ibm_db.prepare(connection, 'SELECT TABNAME, TABSCHEMA from SYSCAT.TABLES FETCH FIRST 10 ROWS ONLY')
ibm_db.execute(statement)
out = "<html><table border=\"1\"><tr><td>Table Name</td><td>Table Schema</td>" 
data = ibm_db.fetch_tuple(statement)
while (data):
    out = out + "<tr><td>"+data[0]+"</td><td>"+data[1]+"</td></tr>"
    data = ibm_db.fetch_tuple(statement)

ibm_db.free_stmt(statement)
ibm_db.close(connection)
out = out + "</table></html>"
return out
```
Please download and examine the attached sample for the rest of the code. If you use this sample, please edit the manifest.yml and specify a unique 'host' value.

###Uploading your application
Use 'cf push' command to push your application to Bluemix. Also use the -c option to specify the start command.

```
cf push <app-name>  -c "python dashdbpython.py"
```
###Related Links

- [DB2 Python API](https://code.google.com/p/ibm-db/wiki/APIs)

- [IBM DB2 v10.5 Knowledge Center](https://www-01.ibm.com/support/knowledgecenter/SSEPGG_10.5.0/com.ibm.db2.luw.kc.doc/welcome.html)
- [IBM DB2 developerWorks](http://www.ibm.com/developerworks/data/products/db2/")

