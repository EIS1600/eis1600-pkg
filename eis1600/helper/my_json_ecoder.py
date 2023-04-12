from json import JSONEncoder


class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        else:
            return JSONEncoder.default(self, obj)
