from pymongo import MongoClient

client = MongoClient()
ns_provisioning = client['ns_provisioning']
ns_provisioning.nsrs.remove()
vnf_provisioning = client['vnf_provisioning']
vnf_provisioning.vnfrs.remove()
vnf_provisioning.cachedimgs.remove()

ns_catalogue = client['ns_catalogue']
ns_catalogue.ns.remove()
vnf_catalogue = client['vnf_catalogue']
vnf_catalogue.ns.remove()
