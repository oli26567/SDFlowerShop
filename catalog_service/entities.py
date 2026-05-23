class Flower:
    def __init__(self, flower_id, name, color, price, stock):
        self.id = flower_id
        self.name = name
        self.color = color
        self.price = price
        self.stock = stock

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "price": self.price,
            "stock": self.stock,
        }
