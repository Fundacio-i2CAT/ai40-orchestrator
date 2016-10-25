# Orquestrador Plataforma Anella Industrial 4.0

## Start:

```
$ virtualenv venv
$ source venv/bin/activate
(venv) $ python orchestapi.py
```

## Post a new service (see [example json file](tenor_client/samples/another.json))

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
        "id": "580f130edf67b515c8000008",
        "instances": [
            {
                "state": "PROVISIONED"
            }
        ]
    },
    {
        "id": "580f0647df67b515c8000005",
        "instances": [
            {
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
                "state": "ACTIVE"
            }
        ]
    },
    {
        "id": "580f064bdf67b515c8000006",
        "instances": [
            {
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
                "state": "ACTIVE"
            }
        ]
    },
    {
        "id": "580f12c7df67b515c8000007",
        "instances": [
            {
                "state": "PROVISIONED"
            }
        ]
    }
]
```

## List one service by its id

```
$ curl -XGET http://localhost:8082/orchestrator/api/v0.1/service/instance/580f064bdf67b515c8000006
```

```
{
    "id": "580f064bdf67b515c8000006",
    "instances": [
        {
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
            "state": "ACTIVE"
        }
    ]
}
```

## Start/Stop a service

```
$ curl -XPUT http://localhost:8082/orchestrator/api/v0.1/service/instance/580f064bdf67b515c8000006 -H "Content-Type: application/json" --data '{"state": "stop"}'
{
	"status": "200", 
	"message": "OK"
}
$ curl -XPUT http://localhost:8082/orchestrator/api/v0.1/service/instance/580f064bdf67b515c8000006 -H "Content-Type: application/json" --data '{"state": "start"}'
{
	"status": "200", 
	"message": "OK"
}
$ curl -XPUT http://localhost:8082/orchestrator/api/v0.1/service/instance/580f064bdf67b515c8000006 -H "Content-Type: application/json" --data '{"state": "start"}'
{
  "message": "Conflict:  580f064bdf67b515c8000006 is stopped(running) can't stop(run) again", 
  "status": 409
}
```
