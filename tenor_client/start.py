#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
import requests 
import json

app = Flask(__name__)
api = Api(app)

class Register(Resource):

    def post(self):
        data = request.get_json()
        print data
        service = data['service']
        descriptor = data['descriptor']
        headers = {
            'Content-Type': 'application/json',
        }
        r = requests.post('http://localhost:4000/{0}'.format(service), 
                          headers=headers, 
                          json=descriptor)
        return r.status_code

class Nsd(Resource):

    def get(self):
        r = requests.get('http://localhost:4000/network-services')
        nsds = json.loads(r.text)
        ids = []
        for i in nsds:
            ids.append({"id": i['nsd']['id'],'date': i['updated_at']})
        return ids

    def post(self,ns_id=None):
        r = requests.get('http://localhost:4000/network-services')
        nsds = json.loads(r.text)
        if not ns_id:
            ns_id = nsds[-1]['nsd']['id']
        headers = {
            'Content-Type': 'application/json',
        }
        data = {
            "ns_id": ns_id,
            "callbackUrl": "http://example.com", "flavour": "basic", "pop_id": "26"
        }
        r = requests.post('http://localhost:4000/ns-instances', 
                          headers=headers, 
                          json=data)
        return r.text

api.add_resource(Register,'/register')
api.add_resource(Nsd, '/nsd')

if __name__ == "__main__":
    print "Tablecloth demo ..."
    app.run(debug=True)
