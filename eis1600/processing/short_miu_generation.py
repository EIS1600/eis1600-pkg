
import ujson as json
from tqdm import tqdm
from random import choices
from string import ascii_letters, digits
from importlib_resources import files
from eis1600.repositories.repo import TEXT_REPO, JSON_REPO, get_ready_and_double_checked_files


ids_path = files('eis1600.processing.persistent_ids').joinpath('long_short_ids_mapping.json')
deprecated_ids_path = files('eis1600.processing.persistent_ids').joinpath('deprecated_long_short_ids_mapping.json')

SYMBOLS = ascii_letters + digits


def generate_id(size: int = 5) -> str:
    """
    len(list(itertools.product(string.ascii_letters + string.digits, repeat=4)))
    14_776_336
    len(list(itertools.product(string.ascii_letters + string.digits, repeat=5)))
    916_132_832
    """
    return "".join(choices(SYMBOLS, k=size))


class IdsMapping:
    def __init__(self):
        self.old_new_map = {}
        self.new_old_map = {}

        with ids_path.open(encoding='utf-8') as fp:
            data = json.load(fp)
        for k, v in data.items():
            self.add(k, v)

    def add(self, old, new: str):
        self.old_new_map[old] = new
        self.new_old_map[new] = old

    def remove(self, old: str):
        if old in self.old_new_map:
            new = self.old_new_map.pop(old)
            del self.new_old_map[new]

    def contains_old_id(self, old: str):
        return old in self.old_new_map

    def contains_new_id(self, new: str):
        return new in self.new_old_map

    def get_old(self, new: str):
        return self.new_old_map.get(new, None)

    def get_new(self, old):
        return self.old_new_map.get(old, None)


IDS_MAPPING = IdsMapping()


def get_short_miu(old_id: str) -> str:
    if new_id := IDS_MAPPING.get_new(old_id):
        return new_id
    while IDS_MAPPING.contains_new_id(new_id := generate_id()):
        pass
    IDS_MAPPING.add(old_id, new_id)
    return new_id


def save_ids():
    with ids_path.open(mode="w", encoding='utf-8') as outfp:
        json.dump(IDS_MAPPING.old_new_map, outfp)


#
def clean_unused_old_ids():
    files_ready, files_double_checked = get_ready_and_double_checked_files()
    infiles = [f.replace(TEXT_REPO, JSON_REPO).replace(".EIS1600", ".json")
               for f in files_ready + files_double_checked]
    print("Collect all UIDs in json files")
    uids = set()
    for infile in tqdm(infiles):
        with open(infile, encoding='utf-8') as fp:
            data = json.load(fp)
        for miu in data:
            uids.add(miu["yml"]["UID"])
    print("Remove old UIDs that are not any more used and save in deprecated mapping")
    to_remove = {}
    for old_id, new_id in IDS_MAPPING.old_new_map.items():
        if old_id not in uids:
            to_remove[old_id] = new_id
    with deprecated_ids_path.open(mode="a", encoding='utf-8') as outfp:
        for old_id, new_id in to_remove.items():
            IDS_MAPPING.remove(old_id)
            outfp.write(json.dumps({"old": old_id, "new": new_id}))
            outfp.write("\n")
    save_ids()
