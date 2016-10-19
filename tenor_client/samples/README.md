# Sample request configuration files

## TeNOR

- vnfd_example.json: Basic Virtual Network Function Descriptor
- nsd_example.json: Basic Network Service Descriptor
- vnfd_existing.json: VNF Descriptor corresponding to an image already on openstack
- nsd_existing.json: NS Descriptor corresponding to previous VNF

## Demo Catalog inputs

- catalog_input.json: Input sample for the orchestrator working directly with openstack APIs
- catalog_input_v2.json: Input sample for the orchestrator using TeNOR (using an image already on openstack)
- catalog_input_v2-new.json: Same as last one using an URL where openstack would access the image in qcow2 format
