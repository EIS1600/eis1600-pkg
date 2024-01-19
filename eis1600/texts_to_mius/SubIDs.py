from typing import Union


class SubIDs:

    def __init__(self, uid: Union[int, str]):
        self.id = 0
        if isinstance(uid, int):
            self.uid_as_str = str(uid)
        else:
            self.uid_as_str = uid

    def get_id(self):
        id_as_str = str(self.id)
        while len(id_as_str) < 8:
            id_as_str = '0' + id_as_str

        self.id += 10

        return self.uid_as_str + '-' + id_as_str
