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
    elif actionName == "allAlarmCount":
        payload = "{\n\taction : \"getAllAlarmListCount\",\n\tparams : []\n}"
    elif actionName == "allCriticalAlarms":
        payload = "{action : \"getAllCriticalAlarms\",params : []}"
    elif actionName == "alarmInstructions":
        alarmIndex = req.get("result").get("parameters").get("alarmIndex")
        payload = "{action : \"getAlarmInstruction\",params : [" + alarmIndex + "]}"
    elif actionName == "similarAlarm":
        payload = "{action : \"getSimilarAlarms\",params : []}"
    elif actionName == "controlLogic":
        payload = "{\"requests\":[{\"message\":\"GetValue\",\"node\":\"slot:/TestPoints/LakeForest\",\"data\":\"hs:power\",\"timeRange\":\"today\",\"rollup\":\"max\"}]}"
    elif actionName == "yes":
        payload = "{action : \"yesAction\",params : []}"
    elif actionName == "setVAVStatus":
        vavStatus = req.get("result").get("parameters").get("vav-status")
        temp = "false"
        if vavStatus == "on":
            temp = "true"
        payload = "{action : \"setVAVStatus\",params : ["+ temp +"]}"
    elif actionName == "readCurrentTemperature":
        payload = "{action : \"readCurrentTemperature\",params : []}"
    elif actionName == "setTemperature":
        temperature = req.get("result").get("parameters").get("temperature")
        payload = "{action : \"setTemperature\",params : ["+ temperature +"]}"
    elif actionName == "setLightIntensity":
        lightIntensity = req.get("result").get("parameters").get("lightIntensity")
        payload = "{action : \"setLightIntensity\",params : ["+ lightIntensity +"]}"
    elif actionName == "setBlinds":
        position = req.get("result").get("parameters").get("position")
        payload = "{action : \"setBlinds\",params : ["+ position +"]}"
    elif actionName == "setMediaStatus":
        mediaStatus = req.get("result").get("parameters").get("media-status")
        temp = "false"
        if mediaStatus == "on":
            temp = "true"
        payload = "{action : \"setMediaStatus\",params : ["+ temp +"]}"
    elif actionName == "increaseLightIntensity":
        payload = "{action : \"setLightIntensityRel\",params : [\"5\"]}"
    elif actionName == "reduceLightIntensity":
        payload = "{action : \"setLightIntensityRel\",params : [\"-5\"]}"
    elif actionName == "zeroLightIntensity":
        payload = "{action : \"setLightIntensityRel\",params : [\"-x\"]}"
    elif actionName == "fullLightIntensity":
        payload = "{action : \"setLightIntensityRel\",params : [\"+x\"]}"
    elif actionName == "increaseCurtainPosition":
        payload = "{action : \"setBlindsRel\",params : [\"5\"]}"
    elif actionName == "reduceCurtainPosition":
        payload = "{action : \"setBlindsRel\",params : [\"-5\"]}"
    elif actionName == "increaseTemperature":
        payload = "{action : \"setTemperatureRel\",params : [\"1\"]}"
    elif actionName == "decreaseTemperature":
        payload = "{action : \"setTemperatureRel\",params : [\"-1\"]}"
    elif actionName == "closeCurtainPosition":
        payload = "{action : \"setBlindsRel\",params : [\"x\"]}"
    elif actionName == "openCurtainPosition":
        payload = "{action : \"ssetBlindsRel\",params : [\"-x\"]}"
    headers = {
        'authorization': 'Basic R0h0ZXN0OlRyaWRpdW0xMjM=',
        'cache-control': 'no-cache',
        'postman-token': '92f011e4-edb2-ef79-a30c-2181b4159a08'
        }
    print("The payload is"+ payload)
    response = requests.request("POST", url, data=payload, headers=headers)
    data= json.loads(response.text)
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
    elif actionName == "allAlarmCount" or actionName == "allCriticalAlarms"  or actionName == "similarAlarm" or actionName == "setVAVStatus" or actionName == "readCurrentTemperature" or actionName == "setTemperature" or actionName == "setLightIntensity" or actionName == "setBlinds" or actionName == "setMediaStatus" or actionName == "increaseLightIntensity" or actionName == "reduceLightIntensity" or actionName == "zeroLightIntensity" or actionName == "fullLightIntensity" or actionName == "increaseCurtainPosition" or actionName == "reduceCurtainPosition" or actionName == "increaseTemperature" or actionName == "decreaseTemperature" or actionName == "closeCurtainPosition" or actionName == "openCurtainPosition" or actionName == "yes" :
        speech = data.get("message")[0]
        print("Speech is : " + speech)
    elif actionName == "alarmInstructions":
        speech = data.get("message")[0] + ". Do you want to execute this action" 
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
