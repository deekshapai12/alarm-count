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

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def text2int(textnum, numwords={}):
    if not numwords:
        units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
      ]
        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
        scales = ["hundred", "thousand", "million", "billion", "trillion"]
        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):    numwords[word] = (1, idx)
        for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)
    current = result = 0
    for word in textnum.split():
        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0
    return result + current

def ord2int(textnum):
    ordinal={
        'first':1,
        'second':2,
        'third':3,
        'fourth':4,
        'fifth':5,
        'sixth':6,
        'seventh':7,
        'eighth':8,
        'ninth':9,
        'tenth':10,
        'eleventh':11,
        'twelfth':12,
        'thirteenth':13,
        'fourteenth':14,
        'fifteenth':15,
        'sixteenth':16,
        'seventeenth':17,
        'eighteenth':18,
        'nineteenth':19,
        'twentieth':20,
    }
    return ordinal(textnum)

def processRequest(req):
    baseurl = "http://aacb9261.ngrok.io"
    print("Firing request for data")
    post_fields = {'requests':[{'message':'GetRollup','node':'station slot:/TestPoints/Bangalore','data':'n:history','timeRange':'today','rollup':'sum'}]}
    h = {"Authorization","Basic R0h0ZXN0OlRyaWRpdW0xMjM="}
    result = request.post(baseurl, headers=h, data=json.dumps(post_fields))
    print("Result : ")
    print(result)
    data = json.loads(result)
    responses = req.get("result").get("responses")
    print("responses : ")
    print(responses[0].value)
    #data = filterResult(data,parameters)
    #actionName = req.get("result").get("action")
    #res = makeWebhookResult(actionName,data,parameters)
    #return res


def filterResult(data,parameters):
    sourceState = parameters.get("source-state")
    ackState = parameters.get("ack-state")
    priority = parameters.get("priority")
    numberWord = parameters.get("number")
    ordinal = parameters.get("ordinal")
    if sourceState == '' and ackState == '' and priority == '':
        return data
    result = []
    if sourceState != '':
        for alarm in data.get('alarms'):
            if alarm.get("Source State").lower() == sourceState.lower():
                result.append(alarm)
        data['alarms'] = result
    result = []
    if ackState != '':
        for alarm in data.get('alarms'):
            if alarm.get("Ack State").lower() == ackState.lower():
                result.append(alarm)
        data['alarms'] = result
    result = []
    if priority != '':
        for alarm in data.get('alarms'):
            if alarm.get("Alarm Class").split('_')[0].lower().startswith(priority.split()[0].lower()):
                result.append(alarm)
        data['alarms'] = result
    result = []
    if numberWord != '':
        if numberWord.lower() == 'one':
            if ordinal == '' or ordinal == 'first':
                result = data.get('alarms')[0]
            elif ordinal.lower() == 'last':
                result = data.get('alarms')[-1]
            else:
                number = ord2int(ordinal)
                data['alarms'] = data.get('alarms')[0:number]
        else:
            number = text2int(numberWord)
            if ordinal == '':
                if number < len(data):
                    data['alarms'] = data.get('alarms')[number-1]
            elif ordinal.lower() == 'first':
                if number < len(data):
                    data['alarms'] = data.get('alarms')[0:number]
            elif ordinal.lower() == 'last':
                if number < len(data):
                    data['alarms'] = data.get('alarms')[number-1:len(data)]
    elif ordinal != '':
        if ordinal == 'last':
            data['alarms'] = data.get('alarms')[-1]
        else:
            number = ord2int(ordinal)
            data['alarms'] = data.get('alarms')[number-1]
    return data



def makeWebhookResult(actionName,data,parameters):
    alarms = data.get('alarms')
    if alarms is None:
        return {}
    # print(json.dumps(item, indent=4))
    sourceState = parameters.get("source-state")
    ackState = parameters.get("ack-state")
    priority = parameters.get("priority")
    numberWord = parameters.get("number")
    ordinal = parameters.get("ordinal")
    if actionName == "alarmCount":
        speech = "There"
        count = len(alarms)
        if count == 1:
            speech+=" is 1 alarm"
        else:
            speech+=" are "+str(count)+" alarms"
        if not sourceState and not ackState and not priority:
            speech+=" in total"
        else:
            speech+=" having "
            joint = " "
            count = 0
            if sourceState:
                if count>0:
                    joint=" and "
                speech+=joint+"source state as "+sourceState.upper()
                count+=1
            if ackState:
                if count>0:
                    joint=" and "
                speech+=joint+"acknowledgement state as "+ackState.upper()
                count+=1
            if priority:
                if count>0:
                    joint=" and "
                speech+=joint+"priority as "+priority.split()[0].upper()
                count+=1

    elif actionName == "fixAlarms":
        speech = "The following steps need to be followed to fix the "
        if ordinal != '':
            speech+=ordinal
        speech += " alarm "
        if numberWord != '' :
            speech+=numberWord+" "
        speech+='having '
        joint = " "
        count = 0
        if sourceState:
            if count>0:
                joint=" and "
            speech+=joint+"source state as "+sourceState.upper()
            count+=1
        if ackState:
            if count>0:
                joint=" and "
            speech+=joint+"acknowledgement state as "+ackState.upper()
            count+=1
        if priority:
            if count>0:
                joint=" and "
            speech+=joint+"priority as "+priority.split()[0].upper()
            count+=1
        speech+=" "+data.get("alarms")[0].get("fix")

    # elif actionName == "getAlarm":
    # elif actionName == "getLatestAlarm":


    # print("Response:")
    # print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "random JSON data"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
