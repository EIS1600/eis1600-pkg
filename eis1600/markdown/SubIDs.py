class SubIDs:

    def __init__(self, uid):
        self.id = 0
        self.uid = str(uid)

    def get_id(self):
        id_as_str = str(self.id)
        while len(id_as_str) < 5:
            id_as_str = '0' + id_as_str

        self.id += 10

        return self.uid + '-' + id_as_str
