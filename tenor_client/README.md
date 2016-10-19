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
$ curl -XPOST http://localhost:5000/orchestrator/api/v0.2/service/instance -H "Content-Type: application/json" --data-binary @./tenor_client/samples/catalog_v2.json
$ curl -XPOST http://localhost:5000/orchestrator/api/v0.2/service/instance -H "Content-Type: application/json" --data-binary @./tenor_client/samples/catalog_v2-new.json
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

