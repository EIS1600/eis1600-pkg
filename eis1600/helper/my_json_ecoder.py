from json import dumps, JSONEncoder


class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        elif isinstance(obj, list):
            return [dumps(elem, cls=MyJSONEncoder, indent='\t', ensure_ascii=False) for elem in obj]
        else:
            return JSONEncoder.default(self, obj)
