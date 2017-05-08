#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()



from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import requests
import math

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    print(request.headers['hostname'])
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r



def processRequest(req):
    url = "http://"+request.headers['hostname']+"/awsMessage" 
    actionName = req.get("result").get("action")
    if actionName == "totalEnergy": 
        payload = "{\"requests\":[{\"message\":\"GetRollup\",\"node\":\"slot:/TestPoints/Bangalore\",\"data\":\"n:history\",\"timeRange\":\"today\",\"rollup\":\"sum\"}]}"
    elif actionName == "demand":
        payload = "{\"requests\":[{\"message\":\"GetValue\",\"node\":\"slot:/TestPoints/LakeForest\",\"data\":\"hs:power\",\"timeRange\":\"today\",\"rollup\":\"max\"}]}"
    elif actionName == " allAlarmCount":
        payload = "{\n\taction : \"getAllAlarmListCount\",\n\tparams : []\n}"
    elif actionName == "allCriticalAlarms":
        payload = "{action : \"getAllCriticalAlarms\",params : []}"
    elif actionName == "alarmInstruction":
        alarmIndex = req.get("result").get("parameters")
        payload = "{action : \"getAlarmInstruction\",params : [" + alarmIndex + "]}"
    elif actionName == "similarAlarm":
        payload = "{action : \"getSimilarAlarms\",params : []}"
    elif actionName == "controlLogic":
        payload = "{\"requests\":[{\"message\":\"GetValue\",\"node\":\"slot:/TestPoints/LakeForest\",\"data\":\"hs:power\",\"timeRange\":\"today\",\"rollup\":\"max\"}]}"
    elif actionName == "yes":
        payload = "{action : \"yesAction\",params : []}"
    headers = {
        'authorization': 'Basic R0h0ZXN0OlRyaWRpdW0xMjM=',
        'cache-control': 'no-cache',
        'postman-token': '92f011e4-edb2-ef79-a30c-2181b4159a08'
        }
    response = requests.request("POST", url, data=payload, headers=headers)
    data= json.loads(response.text)
    print("data:")
    print(data)
    res = makeSpeechResponse(actionName,data)
    return res

def makeSpeechResponse(actionName,data):
    if actionName == "totalEnergy": 
        total = data.get("responses")[0].get("value")
        print("Total is : " + total)
        total = math.ceil(float(total))
        speech = "The total energy consumption for Bangalore orion campus today is " + str(total)
    elif actionName == "demand": 
        total = data.get("responses")[0].get("value")
        print("Total is : " + total)
        total = math.ceil(float(total))
        speech = "The current demand is " + str(total)
    elif actionName == "allAlarmCount" or actionName == "allCriticalAlarms"  or actionName == "alarmInstruction" or actionName == "similarAlarm" or actionName == "yes":
        speech = data.get("message")[0]
        print("Speech is : " + speech)
    return {
        "speech": speech,
        "displayText": speech,
        "source": "Niagara"
           }   
    
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
