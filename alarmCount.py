#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from google.oauth2 import service_account

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

def publish_message(projectName, topicName, data):
    """Publishes a message to a Pub/Sub topic with the given data."""
    credentials = service_account.Credentials.from_service_account_file('Deeksha Project-f64b77ee6386.json')
    pubsub_client = pubsub.Client()
    topic = pubsub_client.topic(topic_name)

    # Data must be a bytestring
    data = data.encode('utf-8')

    message_id = topic.publish(data)

    print('Message {} published.'.format(message_id))

def receive_message(projectName, topicName, subscriptionName):
    """Receives a message from a pull subscription."""
    credentials = service_account.Credentials.from_service_account_file('Deeksha Project-f64b77ee6386.json')
    pubsub_client = pubsub.Client(project=projectName,credentials=credentials)
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
    projectName = "deeksha-project"
    topicName = ""
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
    elif actionName == "setVavStatus":
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
        temp = "5"
        payload = "{action : \"setLightIntensityRel\",params : ["+ temp +"]}"
    elif actionName == "reduceLightIntensity":
        temp = "-5"
        payload = "{action : \"setLightIntensityRel\",params : ["+ temp +"]}"
    elif actionName == "zeroLightIntensity":
        temp = "-x"
        payload = "{action : \"setLightIntensityRel\",params : ["+ temp +"]}"
    elif actionName == "fullLightIntensity":
        temp = "x"
        payload = "{action : \"setLightIntensityRel\",params : ["+ temp +"]}"
    elif actionName == "increaseCurtainPosition":
        temp = "5"
        payload = "{action : \"setBlindsRel\",params :["+ temp +"]}"
    elif actionName == "reduceCurtainPosition":
        temp = "-5"
        payload = "{action : \"setBlindsRel\",params : ["+ temp +"]}"
    elif actionName == "increaseTemperature":
        temp = "1"
        payload = "{action : \"setTemperatureRel\",params : ["+ temp +"]}"
    elif actionName == "decreaseTemperature":
        temp = "-1"
        payload = "{action : \"setTemperatureRel\",params : ["+ temp +"]}"
    elif actionName == "closeCurtainPosition":
        temp = "-x"
        payload = "{action : \"setBlindsRel\",params :["+ temp +"]}"
    elif actionName == "openCurtainPosition":
        temp = "x"
        payload = "{action : \"setBlindsRel\",params : ["+ temp +"]}"
    # headers = {
    #     'authorization': 'Basic R0h0ZXN0OlRyaWRpdW0xMjM=',
    #     'cache-control': 'no-cache',
    #     'postman-token': '92f011e4-edb2-ef79-a30c-2181b4159a08'
    #     }
    # print("The payload is"+ payload)
    # response = requests.request("POST", url, data=payload, headers=headers)
    # data= json.loads(response.text)
    # res = makeSpeechResponse(actionName,data)
    if actionName == "getNiagaraMessage":
        topicName = "NiagaraPub"
        subscriptionName = "NiagaraSub"
        res = makeSpeechResponse(actionName,projectName,topicName,subscriptionName,None)
    else:
        topicName = "WebhookPub"
        res = makeSpeechResponse(actionName,projectName,topicName,None,payload)
    return res

# def makeSpeechResponse(actionName,data):
def makeSpeechResponse(actionName,projectName,topicName,subscriptionName,payload):
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
        publish_message(projectName, topicName, payload)
        speech = "Your request has been sent to Niagara."
        print("Speech is : " + speech)
    elif actionName == "getNiagaraMessage":
        speech = receive_message(projectName, topicName, subscriptionName)
        print("Speech is : "+ speech)
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
    fpath=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if (cred != None and fpath != None):
        with open(fpath,'w') as f:
            f.write(base64.b64decode(cred))
            
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
