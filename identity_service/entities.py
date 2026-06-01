class User:
    def __init__(self, user_id, name, email, password, role):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.role = role #admin, florist, visitor

    def to_dict(self):
        return {
            "id": self.user_id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
        }
