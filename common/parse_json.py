from bson.objectid import ObjectId


def decoder_list(dct):
    for item in dct:
        for k, v in item.items():
            if ObjectId.is_valid(v):
                item[k] = str(item[k])
    return dct


def decoder_item(item):
    for k, v in item.items():
        if ObjectId.is_valid(v):
            item[k] = str(item[k])
    return item


def encode_item(item):
    for k, v in item.items():
        if ObjectId.is_valid(v):
            item[k] = ObjectId(item[k])
    return item
