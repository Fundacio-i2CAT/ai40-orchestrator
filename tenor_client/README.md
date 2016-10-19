# TeNOR client

Registering images to deploy VNF and NS over Openstack (proof of concept using TeNOR)

## Installation and execution (from orchestrator root directory)

```
$ virtualenv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
(venv) $ python -m tenor_client.orchestapi
```

## Examples (access to a TeNOR instance required)

```
$ curl -XGET http://localhost:5000/orchestrator/api/v0.2/service/instance -H { Content-Type: application.json } --data-binary @./samples/catalog_v2.json
$ curl -XPOST http://localhost:5000/orchestrator/api/v0.2/service/instance -H { Content-Type: application.json } --data-binary @./samples/catalog_v2.json
$ curl -XPOST http://localhost:5000/orchestrator/api/v0.2/service/instance -H { Content-Type: application.json } --data-binary @./samples/catalog_v2-new.json
```

