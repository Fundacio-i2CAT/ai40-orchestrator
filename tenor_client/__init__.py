#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask

from orchestapi import api_v2_bp
from common.config_parser import PREFIX, API_VERSION
PREFIX = "/orchestrator/api"
API_VERSION = "0.2"

def create_app():
    app = Flask(__name__)

    app.register_blueprint(
        api_v2_bp,
        url_prefix='{prefix}/v{version}'.format(
            prefix=PREFIX,
            version=API_VERSION))
    print '{prefix}/v{version}'.format(
            prefix=PREFIX,
            version=API_VERSION)

    return app
