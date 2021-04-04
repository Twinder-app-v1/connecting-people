import json
import bcrypt
import unittest
import os.path

class User:
    def __init__(self, username, password_hash, profile=[0.]*6):
        self.username = username
        if isinstance(password_hash, bytes):
            self.password_hash = password_hash
        elif isinstance(password_hash, str):
            self.password_hash = bytes(password_hash, "utf-8")
        self.profile = profile

    def __iter__(self):
        yield self.username
        yield self.password_hash.decode("utf-8")
        yield self.profile

    def validate(self, password):
        return bcrypt.checkpw(bytes(password, "utf-8"), self.password_hash)

class Users:
    DATA_PATH = "users.db" # users.db is a dictionary of username to user tuple

    def __init__(self):
        self.users = {}
        if not os.path.isfile(Users.DATA_PATH):
            with open(Users.DATA_PATH, "w") as f:
                f.write("{}")
        self.load()

    def __len__(self):
        return len(self.users)

    def __contains__(self, username):
        return username in self.users

    def __getitem__(self, username):
        return self.users[username]

    def add(self, username, password):
        if username == "":
            raise Exception("Invalid username: username cannot be empty")
        if username in self:
            raise Exception("Username taken")
        password_hash = bcrypt.hashpw(bytes(password, "utf-8"), bcrypt.gensalt())
        self.users[username] = User(username, password_hash)
        self.save()

    def remove(self, username):
        if username in self:
            del self.users[username]

    def load(self):
        with open(Users.DATA_PATH, "r") as f:
            d = f.read()
        self.users = dict(map(lambda u: (u[0], User(*u[1])), json.loads(d).items()))

    def save(self):
        d = json.dumps(dict(map(lambda u: (u[0], tuple(u[1])), self.users.items())), indent=4)
        with open(Users.DATA_PATH, "w") as f:
            f.write(d)

class UserTest(unittest.TestCase):
    def setUp(self):
        self.users = Users()

    def test_add(self):
        self.users.remove("johndoe")
        before = len(self.users)
        self.users.add("johndoe", "password123")
        after = len(self.users)
        self.assertEqual(before+1, after)

    def test_validate(self):
        self.users.remove("kay")
        self.users.add("kay", "password123")
        f = self.users["kay"].validate("password")
        t = self.users["kay"].validate("password123")
        self.assertFalse(f)
        self.assertTrue(t)

if __name__ == "__main__":
    unittest.main()
