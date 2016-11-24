#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Template management and scp routine"""

from jinja2 import Environment, FileSystemLoader
import os
import paramiko

def create_ssh_client(server, user, key):
    """Returns the ssh client"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, username=user,
                    key_filename=key,
                    timeout=15)
    return client

def render_template(templ_fn, context):
    """Process the template"""
    path = '/tmp/'
    templ_env = Environment(
        autoescape=False,
        loader=FileSystemLoader(path),
    trim_blocks=False)
    return templ_env.get_template(templ_fn).render(context).encode('utf8')
