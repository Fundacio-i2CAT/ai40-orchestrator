#!/usr/bin/python
# -*- coding: utf-8 -*-
from api import create_app
from common import config_parser

app = create_app()

if __name__ == "__main__":
    app.run(host=config_parser.config.get("flask", "url"), port=int(config_parser.config.get("flask", "port")))
