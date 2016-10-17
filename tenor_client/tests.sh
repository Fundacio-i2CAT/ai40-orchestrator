#!/bin/bash

curl -XPOST http://localhost:5000/register -H "Content-Type: application/json" --data-binary @samples/wvnfd_example.json
curl -XPOST http://localhost:5000/register -H "Content-Type: application/json" --data-binary @samples/wnsd_example.json
curl -XGET http://localhost:5000/nsd
curl -XPOST http://localhost:5000/nsd
