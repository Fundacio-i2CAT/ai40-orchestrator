from bson.objectid import ObjectId
from database import mongodb
from bson.dbref import DBRef


def decoder_list(dct):
    for item in dct:
        if '_id' in item:
            item['_id'] = str(item['_id'])
        if 'service_description' in item:
            item['service_description'] = mongodb.db.dereference(item['service_description'])
            item['service_description']['_id'] = str(item['service_description']['_id'])
            item['service_description']['context'] = str(item['service_description']['context'])
    return dct


def decoder_item(item):
    if '_id' in item:
        item['_id'] = str(item['_id'])
    if 'service_description' in item:
        item['service_description'] = mongodb.db.dereference(item['service_description'])
        item['service_description']['_id'] = str(item['service_description']['_id'])
        item['service_description']['context'] = str(item['service_description']['context'])
    return item


def encode_item(item):
    if '_id' in item:
        item['_id'] = ObjectId(item['_id'])
    return item


def generate_insert(item):
    data = {'activated': True,
            "service_description":
                DBRef(mongodb.collection_sd,
                      ObjectId(item['service_description_id']))

    }
    return data
