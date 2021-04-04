import time

class Room:
    def __init__(self, roomname, users):
        self.roomname = roomname
        self.users = users
        self.messages = []
        self.created_at = time.time()  # unix timestamp (seconds since 1970)

    def profile(self):
        """ returns profile of room same format as user profile
        """
        res = self.users[0].profile
        for u in self.users[1:]:
            _, vals = zip(*u.profile)
            res = [(k, v1+v2) for (k, v1), v2 in zip(res, vals)]
        return res

    def score(self, profile):
        return sum(map(lambda x: x[0][1] + x[1][1], zip(self.profile(), profile)))

    def add(self, user):
        self.users.append(user)

    def remove(self, user):
        self.users.remove(user)

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
