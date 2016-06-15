import ConfigParser

config = ConfigParser.RawConfigParser()
config.read("config.cfg")

PREFIX = config.get("flask", "prefix")
API_VERSION = config.get("flask", "version")
