#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from oauth2client.service_account import ServiceAccountCredentials
from oauth2client.client import _get_application_default_credential_from_file

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import base64
import json
import os
import requests
import math
import argparse

from flask import Flask
from flask import request
from flask import make_response

from google.cloud import pubsub

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
#     print(request.headers['hostname'])
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def receive_message(topicName, subscriptionName):
    """Receives a message from a pull subscription."""
    pubsub_client = pubsub.Client()
    topic = pubsub_client.topic(topicName)
    subscription = topic.subscription(subscriptionName)

    # Change return_immediately=False to block until messages are
    # received.
    results = subscription.pull(return_immediately=True)

    print('Received {} messages.'.format(len(results)))
    speech = ''
    for ack_id, message in results:
        # print('* {}: {}, {}'.format(
        #     message.message_id, message.data, message.attributes))
        speech = message.data.decode("utf-8")
        print(speech)

    # Acknowledge received messages. If you do not acknowledge, Pub/Sub will
    # redeliver the message.
    if results:
        subscription.acknowledge([ack_id for ack_id, message in results])

    return speech

def processRequest(req):
    # url = "http://"+request.headers['hostname']+"/awsMessage"
    actionName = req.get("result").get("action")
    if actionName == "totalEnergy":
        topicName ="totalEnergy"
        subscriptionName ="Energy"
        # payload = "{\"requests\":[{\"message\":\"GetRollup\",\"node\":\"slot:/TestPoints/Bangalore\",\"data\":\"n:history\",\"timeRange\":\"today\",\"rollup\":\"sum\"}]}"
    elif actionName == "demand":
        topicName =" totalDemand"
        subscriptionName ="Demand"
        # payload = "{\"requests\":[{\"message\":\"GetValue\",\"node\":\"slot:/TestPoints/LakeForest\",\"data\":\"hs:power\",\"timeRange\":\"today\",\"rollup\":\"max\"}]}"
    elif actionName == "allAlarmCount":
        topicName ="alarmCount"
        subscriptionName ="Count"
        # payload = "{\n\taction : \"getAllAlarmListCount\",\n\tparams : []\n}"
    elif actionName == "allCriticalAlarms":
        topicName ="criticalAlarms"
        subscriptionName ="Critical"
        # payload = "{action : \"getAllCriticalAlarms\",params : []}"
    elif actionName == "alarmInstructions":
        topicName ="alarmInstructions"
        subscriptionName ="Instructions"
        # alarmIndex = req.get("result").get("parameters").get("alarmIndex")
        # payload = "{action : \"getAlarmInstruction\",params : [" + alarmIndex + "]}"
    elif actionName == "similarAlarm":
        topicName ="similarAlarm"
        subscriptionName ="Similar"
        # payload = "{action : \"getSimilarAlarms\",params : []}"
    elif actionName == "controlLogic":
        topicName ="controlLogic"
        subscriptionName ="Logic"
        # payload = "{\"requests\":[{\"message\":\"GetValue\",\"node\":\"slot:/TestPoints/LakeForest\",\"data\":\"hs:power\",\"timeRange\":\"today\",\"rollup\":\"max\"}]}"
    elif actionName == "yes":
        topicName ="yesAction"
        subscriptionName ="Yes"
        # payload = "{action : \"yesAction\",params : []}"
    elif actionName == "setVavStatus":
        topicName ="vavStatus"
        subscriptionName ="Vav"
        # vavStatus = req.get("result").get("parameters").get("vav-status")
        # temp = "false"
        # if vavStatus == "on":
            # temp = "true"
        # payload = "{action : \"setVAVStatus\",params : ["+ temp +"]}"
    elif actionName == "readCurrentTemperature":
        topicName ="currentTemp"
        subscriptionName ="Current"
        # payload = "{action : \"readCurrentTemperature\",params : []}"
    elif actionName == "setTemperature":
        topicName ="setTemp"
        subscriptionName ="Set"
        # temperature = req.get("result").get("parameters").get("temperature")
        # payload = "{action : \"setTemperature\",params : ["+ temperature +"]}"
    elif actionName == "setLightIntensity":
        topicName ="lightIntensity"
        subscriptionName ="Light"
        # lightIntensity = req.get("result").get("parameters").get("lightIntensity")
        # payload = "{action : \"setLightIntensity\",params : ["+ lightIntensity +"]}"
    elif actionName == "setBlinds":
        topicName ="setBlinds"
        subscriptionName ="Blinds"
        # position = req.get("result").get("parameters").get("position")
        # payload = "{action : \"setBlinds\",params : ["+ position +"]}"
    elif actionName == "setMediaStatus":
        topicName ="mediaStatus"
        subscriptionName ="Media"
        # mediaStatus = req.get("result").get("parameters").get("media-status")
        # temp = "false"
        # if mediaStatus == "on":
            # temp = "true"
        # payload = "{action : \"setMediaStatus\",params : ["+ temp +"]}"
    elif actionName == "increaseLightIntensity":
        topicName ="increaseLight"
        subscriptionName ="Increase"
        # temp = "5"
        # payload = "{action : \"setLightIntensityRel\",params : ["+ temp +"]}"
    elif actionName == "reduceLightIntensity":
        topicName ="reduceLight"
        subscriptionName ="Reduce"
        # temp = "-5"
        # payload = "{action : \"setLightIntensityRel\",params : ["+ temp +"]}"
    elif actionName == "zeroLightIntensity":
        topicName ="zeroLight"
        subscriptionName ="Zero"
        # temp = "-x"
        # payload = "{action : \"setLightIntensityRel\",params : ["+ temp +"]}"
    elif actionName == "fullLightIntensity":
        topicName ="fullLight"
        subscriptionName ="Full"
        # temp = "x"
        # payload = "{action : \"setLightIntensityRel\",params : ["+ temp +"]}"
    elif actionName == "increaseCurtainPosition":
        topicName ="curtainPosition"
        subscriptionName ="Curtain"
        # temp = "5"
        # payload = "{action : \"setBlindsRel\",params :["+ temp +"]}"
    elif actionName == "reduceCurtainPosition":
        topicName ="reduceCurtain"
        subscriptionName ="RedCurtain"
        # temp = "-5"
        # payload = "{action : \"setBlindsRel\",params : ["+ temp +"]}"
    elif actionName == "increaseTemperature":
        topicName ="increaseTemperature"
        subscriptionName ="incTemp"
        # temp = "1"
        # payload = "{action : \"setTemperatureRel\",params : ["+ temp +"]}"
    elif actionName == "decreaseTemperature":
        topicName ="decreaseTemperature"
        subscriptionName ="decTemp"
        # temp = "-1"
        # payload = "{action : \"setTemperatureRel\",params : ["+ temp +"]}"
    elif actionName == "closeCurtainPosition":
        topicName ="closeCurtain"
        subscriptionName ="Close"
        # temp = "-x"
        # payload = "{action : \"setBlindsRel\",params :["+ temp +"]}"
    elif actionName == "openCurtainPosition":
        topicName ="openCurtain"
        subscriptionName ="Open"
        # temp = "x"
        # payload = "{action : \"setBlindsRel\",params : ["+ temp +"]}"
    # headers = {
    #     'authorization': 'Basic R0h0ZXN0OlRyaWRpdW0xMjM=',
    #     'cache-control': 'no-cache',
    #     'postman-token': '92f011e4-edb2-ef79-a30c-2181b4159a08'
    #     }
    # print("The payload is"+ payload)
    # response = requests.request("POST", url, data=payload, headers=headers)
    # data= json.loads(response.text)
    # res = makeSpeechResponse(actionName,data)
    res = makeSpeechResponse(actionName,topicName,subscriptionName)
    return res

# def makeSpeechResponse(actionName,data):
def makeSpeechResponse(actionName,topicName,subscriptionName):
    # if actionName == "totalEnergy":
    #     total = data.get("responses")[0].get("value")
    #     print("Total is : " + total)
    #     total = math.ceil(float(total))
    #     speech = "The total energy consumption for Bangalore orion campus today is " + str(total)
    # elif actionName == "demand":
    #     total = data.get("responses")[0].get("value")
    #     print("Total is : " + total)
    #     total = math.ceil(float(total))
    #     speech = "The current demand is " + str(total)
    if actionName == "allAlarmCount" or actionName == "allCriticalAlarms"  or actionName == "similarAlarm" or actionName == "setVavStatus" or actionName == "readCurrentTemperature" or actionName == "setTemperature" or actionName == "setLightIntensity" or actionName == "setBlinds" or actionName == "setMediaStatus" or actionName == "increaseLightIntensity" or actionName == "reduceLightIntensity" or actionName == "zeroLightIntensity" or actionName == "fullLightIntensity" or actionName == "increaseCurtainPosition" or actionName == "reduceCurtainPosition" or actionName == "increaseTemperature" or actionName == "decreaseTemperature" or actionName == "closeCurtainPosition" or actionName == "openCurtainPosition" or actionName == "yes" :
        speech = receive_message(topicName, subscriptionName)
        print("Speech is : " + speech)
    # elif actionName == "alarmInstructions":
    #     speech = data.get("message")[0] + ". Do you want to execute this action"
    #     print("Speech is : " + speech)
    return {
        "speech": speech,
        "displayText": speech,
        "source": "Niagara"
           }

if __name__ == '__main__':
    cred=os.environ.get("GOOGLE_CREDENTIALS_BASE64")
    fpath=os.environ.get("GOOGLE_CREDENTIALS")
    if (cred != None and fpath != None):
        with open(fpath,'w') as f:
            f.write(base64.decodestring(cred))
                
    #os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="Deeksha Project-5204d514b418.json"
    #scopes = ['https://www.googleapis.com/auth/sqlservice.admin']
    #credentials = ServiceAccountCredentials.from_json_keyfile_name('Deeksha Project-5204d514b418.json', scopes=scopes)
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
