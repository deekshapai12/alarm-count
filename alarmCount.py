#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()



from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

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
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "alarmCount":
        return {}
    baseurl = "https://dl.dropboxusercontent.com/s/l3kdftm9jlq479w/db.json?dl=0"
    result = urlopen(baseurl).read().decode()
    data = json.loads(result)
    parameters = req.get("result").get("parameters")
    data = filterResult(data,parameters)
    res = makeWebhookResult(data,parameters)
    return res


def filterResult(data,parameters):
    sourceState = parameters.get("source-state")
    ackState = parameters.get("ack-state")
    priority = parameters.get("priority")
    result = []
    for alarm in data.get('alarms'):
        if sourceState:
            if alarm.get("Source State").lower() == sourceState.lower():
                result.append(alarm)
    data['alarms'] = result
    for alarm in data.get('alarms'):
        if ackState:
            if ackState.lower().startswith('unack'):
                ackState = 'unacked'
            if ackState.lower().startswith('ack'):
                ackState = 'acked'
            if alarm.get("Ack State").lower() == ackState:
                result.append(alarm)
    data['alarms'] = result
    for alarm in data.get('alarms'):
        if priority:
            if alarm.get("Priority").lower().startswith(priority.split()[0].lower()):
                result.append(alarm)
    data['alarms'] = result
    return data


def makeWebhookResult(data,parameters):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}
    alarms = query.get('alarms')
    if alarms is None:
        return {}
    # print(json.dumps(item, indent=4))
    sourceState = parameters.get("source-state")
    ackState = parameters.get("ack-state")
    priority = parameters.get("priority")
    speech = "There are "+len(alarms)+"having"
    joint = " "
    count = 0
    if sourceState:
        if count>0:
            joint=" and "
        speech+=joint+sourceState+" as source state"
        count+=1
    if ackState:
        if count>0:
            joint=" and "
        speech+=joint+ackState+" as acknowledgement state"
        count+=1
    if priority:
        if count>0:
            joint=" and "
        speech+=joint+priority+" priority"
        count+=1

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')