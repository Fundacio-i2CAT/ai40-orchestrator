#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask

from instances.controller import api_v1_bp
from common.config_parser import PREFIX, API_VERSION


def create_app():
    app = Flask(__name__)

    app.register_blueprint(
        api_v1_bp,
        url_prefix='{prefix}/v{version}'.format(
            prefix=PREFIX,
            version=API_VERSION))

    return app