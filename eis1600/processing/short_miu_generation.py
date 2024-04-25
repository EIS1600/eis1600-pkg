
import ujson as json
from importlib_resources import files

ids_path = files('eis1600.processing.persistent_ids').joinpath('short_long_ids_mapping.json')

#NOTE
from itertools import product
# len(list(product("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", repeat=5)))
# 60_466_176


class IdsMapping:
    def __init__(self):
        self.key_value_map = {}
        self.value_key_map = {}

        with open(ids_path) as fp:
            data = json.load(fp)
        for k, v in data.items():
            self.add(k, v)

    def add(self, key, value):
        self.key_value_map[key] = value
        self.value_key_map[value] = key

    def remove(self, key):
        if key in self.key_value_map:
            value = self.key_value_map.pop(key)
            del self.value_key_map[value]

    def contains_key(self, key):
        return key in self.key_value_map

    def contains_value(self, value):
        return value in self.value_key_map

    def get_value(self, key):
        return self.key_value_map.get(key, None)

    def get_key(self, value):
        return self.value_key_map.get(value, None)


IDS_MAPPING = IdsMapping()


def get_short_miu(old_id: str) -> str:
    print(IDS_MAPPING.key_value_map)
    print(IDS_MAPPING.value_key_map)
    return "1"
