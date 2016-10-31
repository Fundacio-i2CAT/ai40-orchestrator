#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR Virtual Deployment Unit Representation Class and Client"""

class TenorVDU(object):
    """Represents a TeNOR VDU"""

    def __init__(self,
                 vm_image='6b9b14cc-d106-4d07-8b43-22035a3265fe',
                 vm_image_format='openstack_id',
                 shell='#!/bin/bash\\n',
                 storage_amount=6,
                 vcpus=1):
        self.vm_image = vm_image
        self.vm_image_format = vm_image_format
        self.shell = shell
        self.storage_amount = storage_amount
        self.vcpus = vcpus

    def __repr__(self):
        return '{0} ({1})'.format(self.vm_image, self.vm_image_format)

if __name__ == "__main__":
    VDU = TenorVDU()
    print VDU