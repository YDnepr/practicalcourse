from flask import Flask
import os

app = Flask(__name__)

####### Tools #########
def staticPath(fileName):
    filePath =  os.path.join(app.static_folder, fileName)
    return filePath
    
def readHtmlFile(fileName):
    filePath = staticPath(fileName)
    content = ''
    
    with open(filePath, "rb") as f:
        content = f.read()
        
    return content        
    
import PythonStarterApp.main
