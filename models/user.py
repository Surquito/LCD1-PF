class User:
    def __init__(self, id_user=None, username=None, password=None, dcompdate=None):
        self.id_user = id_user
        self.username = username
        self.password = password
        self.dcompdate = dcompdate

    def __str__(self):
        return f"User({self.id_user}, {self.username})"

    def to_dict(self):
        return {
            "id_user": self.id_user,
            "username": self.username,
            "password": self.password
        }
