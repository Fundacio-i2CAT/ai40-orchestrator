from bson.objectid import ObjectId

def decoder_list(dct):
    for item in dct:
        if '_id' in item:
            item['_id'] = str(item['_id'])
        if 'service_description_id' in item:
            item['service_description_id'] = str(item['service_description_id'])
    return dct


def decoder_item(item):
    if '_id' in item:
        item['_id'] = str(item['_id'])
    if 'service_description_id' in item:
        item['service_description_id'] = str(item['service_description_id'])
    return item


def encode_item(item):
    if '_id' in item:
        item['_id'] = ObjectId(item['_id'])
    if 'service_description_id' in item:
        item['service_description_id'] = ObjectId(item['service_description_id'])
    return item


def add_validated(item):
    if 'activated' not in item:
        item['activated'] = True
    return item
