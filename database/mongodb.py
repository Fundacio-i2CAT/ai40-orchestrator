from pymongo import MongoClient
from common import config_parser

client = MongoClient(config_parser.config.get("mongodb", "url"))

db = client[config_parser.config.get("mongodb", "database")]

collection_si = config_parser.config.get("mongodb", "collection_si")

collection_sd = config_parser.config.get("mongodb", "collection_sd")
