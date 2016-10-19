# TeNOR client

Registering images to deploy VNF and NS on an Openstack (proof of concept using TeNOR)

## Installation and execution

```
$ virtualenv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
(venv) $ python orchestapi.py
```

## Examples (access to a TeNOR instance required)

```
$ curl -XPOST http://localhost:5000/service/instance -H { Content-Type: application.json } --data-binary @./samples/catalog_v2.json
$ curl -XPOST http://localhost:5000/service/instance -H { Content-Type: application.json } --data-binary @./samples/catalog_v2-new.json
```

