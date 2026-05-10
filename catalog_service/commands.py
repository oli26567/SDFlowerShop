from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

class AddFlowerCommand(Command):
    def __init__(self, repository, name, color, price, stock):
        self.repository = repository
        self.name = name
        self.color = color
        self.price = price
        self.stock = stock

    def execute(self):
        return self.repository.add_flower(self.name, self.color, self.price, self.stock)

class UpdateStockCommand(Command):
    def __init__(self, repository, flower_id, new_stock):
        self.repository = repository
        self.id = flower_id
        self.stock = new_stock

    def execute(self):
        return self.repository.update_stock(self.id, self.stock)