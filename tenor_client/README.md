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
$ curl -XGET http://localhost:5000/orchestrator/api/v0.2/service/instance
$ curl -XPOST http://localhost:5000/orchestrator/api/v0.2/service/instance -H "Content-Type: application/json" --data-binary @./tenor_client/samples/catalog_input_v2.json
$ curl -XPOST http://localhost:5000/orchestrator/api/v0.2/service/instance -H "Content-Type: application/json" --data-binary @./tenor_client/samples/catalog_input_v2-new.json
```

## Starting/stopping all VNF Instances associated with a Network Service instance
## (access to a TeNOR SEG-forked instance required)

580861e7df67b5156e000000 <- Example TeNOR Network Service Instance ID

```
$ curl -XPUT http://localhost:5000/orchestrator/api/v0.2/service/instance/580861e7df67b5156e000000/state -H "Content-Type: application/json" --data '{ "state": "STaRT"}'
$ curl -XPUT http://localhost:5000/orchestrator/api/v0.2/service/instance/580861e7df67b5156e000000/state -H "Content-Type: application/json" --data '{ "state": "StOP"}'
```

### Stop/start issue with TeNOR

```
http://localhost:4000/ns-instances/5807748adf67b505c8000000/stop
http://localhost:4000/ns-instances/5807748adf67b505c8000000/start
```

add openstack call at tenor/vnf-provisioning/routes/vnf.rb

```
    # @method post_vnf_provisioning_instances_id_config
    # @overload post '/vnf-provisioning/vnf-instances/:vnfr_id/config'
    #   Request to execute a lifecycle event
    #   @param [String] vnfr_id the VNFR ID
    #   @param [JSON]
    # Request to execute a lifecycle event
    put '/vnf-instances/:vnfr_id/config' do |vnfr_id|
```

we will also need some cloud-init abled images 
