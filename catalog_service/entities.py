class Flower:
    def __init__(self, flower_id, name, color, price, stock):
        self.id = flower_id
        self.name = name
        self.color = color
        self.price = price
        self.stock = stock

class User:
    def __init__(self, user_id, name, email, password, role):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.role = role #admin, florist, visitor