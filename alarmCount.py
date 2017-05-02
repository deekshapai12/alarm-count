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



def processRequest(req):
    #baseurl = Request("http://52bcca08.ngrok.io/na")
    #baseurl.add_header("Authorization","Basic R0h0ZXN0OlRyaWRpdW0xMjM=")
    #post_fields = {'requests':[{'message':'GetRollup','node':'station slot:/TestPoints/Bangalore','data':'n:history','timeRange':'today','rollup':'sum'}]}
    #print("Firing request for data")
    #r=urlopen(baseurl, json.dumps(post_fields))
    #result=r.read().decode()
   # result = urlopen(baseurl).read().decode()
    url = "http://52bcca08.ngrok.io/na"

    payload = "{'requests':[{'message':'GetRollup','node':'station slot:/TestPoints/Bangalore','data':'n:history','timeRange':'today','rollup':'sum'}]}"
    headers = {
        'authorization': 'Basic R0h0ZXN0OlRyaWRpdW0xMjM=',
        'cache-control': 'no-cache',
        'postman-token': '92f011e4-edb2-ef79-a30c-2181b4159a08'
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    
    print("Response is :")
    print(response)
    data= json.loads(response)
    print("Data is :")
    print(data)
    actionName = req.get("result").get("action")
    res = makeWebhookResult(actionName,data,parameters)
    return res




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

    elif actionName == "getAlarm" or actionName == "getLatestAlarm":
        alarm = data.get("alarms")[0]
        ack = alarm.get("Ack State")
        if ack.beginswith("un"):
            ack="unacknowledged"
        else:
            ack="acknowledged"
        priority_class=" ".join(alarm.get("Alarm Class").split("_")[:2])
        speech="This alarm is "+alarm.get("Source State")+", "+ack+" and "+priority_class+" with a priority of "+alarm.get("Priority")

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
