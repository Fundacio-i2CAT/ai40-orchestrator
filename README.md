# Orquestrador Plataforma Anella Industrial 4.0

## Requirements

[TeNOR SEG-version](https://stash.i2cat.net/projects/AI40/repos/tenor/browse) installed and running

## Start:

```
$ virtualenv venv
$ source venv/bin/activate
(venv) $ python start.py
```

## Register a VNF

See [ovnf_example.json](tenor_client/samples/ovnf_example.json)

```
curl -XPOST http://localhost:8082/orchestrator/api/v0.1/vnf -H "Content-Type: application/json" --data-binary @tenor_client/samples/ovnf_example.json
```

```
{
    "state": "PROVISIONED",
    "vnf_id": 1899
}
```

## Register a NS related to the VNF id in ons_example.json

See [ons_example.json](tenor_client/samples/ons_example.json)

```
curl -XPOST http://localhost:8082/orchestrator/api/v0.1/ns -H "Content-Type: application/json" --data-binary @tenor_client/samples/ons_example.json
```

```
{
    "state": "PROVISIONED",
    "ns_id": 1899
}
```

## Instantiate the Network Service providing consumer configuration in onsi_example.json

See [onsi_example.json](tenor_client/samples/onsi_example.json)

```
curl -XPOST http://localhost:8082/orchestrator/api/v0.1/ns/1899 -H "Content-Type: application/json" --data-binary @tenor_client/samples/onsi_example.json
```

```
{
    "service_instance_id": "581c43c1df67b55665000003",
    "state": "PROVISIONED"
}
```


## Post a new service creating new VNF, NS and NSI in a single round (see [example json file](tenor_client/samples/another.json))

```
$ curl -XPOST http://localhost:8082/orchestrator/api/v0.1/service/instance -H "Content-Type: application/json" --data-binary @tenor_client/samples/another.json
```


```
{"state": "PROVISIONED", "id": "580f12c7df67b515c8000007"}
```


## List all services deployed


```
$ curl -XGET http://localhost:8082/orchestrator/api/v0.1/service/instance
```

```
[
    {
        "ns_instance_id": "580f130edf67b515c8000008",
        "state": "PROVISIONED"
    },
    {
        "ns_instance_id": "580f0647df67b515c8000005",
        "addresses": [
            {
                "OS-EXT-IPS:type": "fixed",
                "addr": "192.85.141.3"
            },
            {
                "OS-EXT-IPS:type": "floating",
                "addr": "172.24.4.140"
            },
            {
                "OS-EXT-IPS:type": "fixed",
                "addr": "192.118.223.3"
            },
            {
                "OS-EXT-IPS:type": "floating",
                "addr": "172.24.4.139"
            }
        ],
        "state": "RUNNING"
    },
    {
        "ns_instance_id": "580f064bdf67b515c8000006",
        "addresses": [
            {
                "OS-EXT-IPS:type": "fixed",
                "addr": "192.150.153.3"
            },
            {
                "OS-EXT-IPS:type": "floating",
                "addr": "172.24.4.142"
            },
            {
                "OS-EXT-IPS:type": "fixed",
                "addr": "192.9.250.3"
            },
            {
                "OS-EXT-IPS:type": "floating",
                "addr": "172.24.4.141"
            }
        ],
        "state": "DEPLOYED"
    }
]
```

## List one service by its id

```
$ curl -XGET http://localhost:8082/orchestrator/api/v0.1/service/instance/580f064bdf67b515c8000006
```

```
{
    "ns_instance_id": "580f064bdf67b515c8000006",
    "addresses": [
        {
            "OS-EXT-IPS:type": "fixed",
            "addr": "192.150.153.3"
        },
        {
            "OS-EXT-IPS:type": "floating",
            "addr": "172.24.4.142"
        },
        {
            "OS-EXT-IPS:type": "fixed",
            "addr": "192.9.250.3"
        },
        {
            "OS-EXT-IPS:type": "floating",
            "addr": "172.24.4.141"
        }
    ],
    "state": "DEPLOYED"
}
```

## Start/Stop a service

```
$ curl -XPUT http://localhost:8082/orchestrator/api/v0.1/service/instance/580f064bdf67b515c8000006 -H "Content-Type: application/json" --data '{"state": "running"}'
200
{
    "message": "Successfully sent state signal"
}
$ curl -XPUT http://localhost:8082/orchestrator/api/v0.1/service/instance/580f064bdf67b515c8000006 -H "Content-Type: application/json" --data '{"state": "running"}'
200
{
    "message": "Successfully sent state signal"
}
$ curl -XPUT http://localhost:8082/orchestrator/api/v0.1/service/instance/580f064bdf67b515c8000006 -H "Content-Type: application/json" --data '{"state": "deployed"}'
409
{
    "message": "Conflict: 580f064bdf67b515c8000006 stopped(running)"
}
```
