import time
import numpy as np

class Room:
    def __init__(self, roomname, users):
        self.roomname = roomname
        self.users = users
        self.messages = []
        self.created_at = time.time()  # unix timestamp (seconds since 1970)

    def combined_users_profile(self):
        profile = np.array([0] * 6)
        for u in self.users:
            profile += u.profile
        return profile / np.linalg.norm(profile)

class Rooms:
    def __init__(self):
        self.rooms = {}

    def __contains__(self, roomname):
        return roomname in self.rooms

    def __getitem__(self, roomname):
        return self.rooms[roomname]

    def __len__(self):
        return len(self.rooms)

    def add(self, roomname, users):
        if roomname == "":
            raise Exception("Invalid roomname: roomname cannot be empty")
        if roomname in self:
            raise Exception("Roomname taken")
        self.rooms[roomname] = Room(roomname, users)

    def has_user(self, username):
        res = []
        for r in self.rooms.values():
            if username in map(lambda u: u.username, r.users):
                res.append(r)
        return res

    def closests_profile_match(self, profile):
        pro = np.array(profile)
        print(self.rooms.values)
        min_room = list(self.rooms.values())[0]
        min_d = float("inf")
        for r in self.rooms.values():
            p = r.combined_users_profile()
            d = np.linalg.norm(p - pro / np.linalg.norm(pro))
            if d < min_d:
                min_d = d
                min_room = r
        return min_room
