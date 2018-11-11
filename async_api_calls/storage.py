import struct

MAXBYTE = 255
MAXBYTE32 = 4294967295

BYTES_PER_ID = 5
GROUP_UNFETCHED = MAXBYTE

class Storage:
    def __init__(self, fst_id, lst_id, bytes_per_id):
        self.data = None
        self.fst_id = fst_id
        self.lst_id = lst_id
        self.bytes_per_id = bytes_per_id

    def create_empty(self):
        self.data = bytearray((MAXBYTE for _ in range(self.bytes_per_id * (self.lst_id + 1 - self.fst_id))))

    def load(self, filename):
        with open(filename, "rb") as f:
            self.data = bytearray(f.read())

    def dump(self, filename):
        with open(filename, "wb") as f:
            f.write(self.data)

    def iterate_values(self):
        start = 0
        end = self.bytes_per_id
        last_byte = self.lst_id * self.bytes_per_id
        counter = self.fst_id

        while start < last_byte:
            val = self.data[start : end]

            if len(val) > 0:
                yield val

            start += self.bytes_per_id
            end += self.bytes_per_id
            counter += 1

    def get_by_id(self, id_get):
        offset = (id_get - self.fst_id) * self.bytes_per_id
        return self.data[offset:offset + self.bytes_per_id]

    def update_by_id(self, id_update, value):
        offset = (id_update - self.fst_id) * self.bytes_per_id
        for i, x in enumerate(value, offset):
            self.data[i] = x

    def __len__(self):
        return self.lst_id - self.fst_id + 1

group_types = {
    1: "open_group",
    2: "public_page",
    3: "event",
    4: "closed_group",
    5: "banned",
    6: "deleted",
    10: "unknown",
}

class Storage_groups(Storage):
    def __init__(self, fst_id, lst_id):
        super(Storage_groups, self).__init__(fst_id, lst_id, BYTES_PER_ID)

    def get_undone(self):
        for i, x in enumerate(self.iterate_values(), self.fst_id):
            group_type = x[0]
            if group_type == GROUP_UNFETCHED:
                yield i

    def update_group_info(self, group_id, group_type, group_members):
        group_type_b = bytes([group_type])
        group_members = MAXBYTE32 if group_members is None else group_members
        group_members_b = struct.pack("<L", group_members)
        self.update_by_id(group_id, group_type_b + group_members_b)

    def get_group_info(self, group_id):
        value = self.get_by_id(group_id)
        group_type = value[0]
        members_count = struct.unpack("<L", value[1:])[0]

        return group_type, members_count

    def groups_iterate(self):
        for i in range(self.fst_id, self.lst_id + 1):
            g_type, g_size = self.get_group_info(i)
            yield i, g_type, g_size
