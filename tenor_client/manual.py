#!/usr/bin/python
# -*- coding: utf-8 -*-

from jinja2 import Template
import sys

if __name__ == "__main__":

    if len(sys.argv) < 5 :
        print "\nUsage: "+sys.argv[0]+" vnf_id ns_id vm_image_url name\n"
        exit(0)
    vnf_id = sys.argv[1]
    ns_id = sys.argv[2]
    vm_image_url = sys.argv[3]
    name = sys.argv[4]

    f_src = ""
    with open('templates/min-f.json','r') as f:
        f_src = f.read()    

    n_src = ""
    with open('templates/min-n.json','r') as f:
        n_src = f.read()    
    
    vnfd = Template(f_src)
    with open("outputs/f_{0}.json".format(name),"w") as f:
        f.write(vnfd.render(vnf_id=vnf_id,ns_id=ns_id,vm_image_url=vm_image_url,name=name))

    nsd = Template(n_src)
    with open("outputs/n_{0}.json".format(name),"w") as f:
        f.write(nsd.render(vnf_id=vnf_id,ns_id=ns_id,vm_image_url=vm_image_url,name=name))
