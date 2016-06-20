import ConfigParser

config = ConfigParser.RawConfigParser()
config.read("config.cfg")

PREFIX = config.get("flask", "prefix")
API_VERSION = config.get("flask", "version")
URL_CATALOG_CONTEXT = config.get("service_description", "url")
