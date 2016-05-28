# -*- coding: utf-8 -*-
"""
Created on Tue May 17 01:01:31 2016

@author: Ghareeb
"""

from PythonStarterApp import app
import os

if 'VCAP_APP_PORT' in os.environ:
    appPort = os.environ['VCAP_APP_PORT']
else:
    appPort = 5000

if 'VCAP_APP_HOST' in os.environ:
    appHost = os.environ['VCAP_APP_HOST']
else:
    appHost = '0.0.0.0'
    
if __name__ == '__main__':
    app.run(host=appHost,port=appPort, debug=False, threaded=True)