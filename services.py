class FlowerService:
    def __init__(self, repository):
        self.repository = repository

    def get_catalog(self, user_role, color=None, sort_by=None):
        return self.repository.get_filtered_sorted(color, sort_by)

    def add_new_flower(self, user_role, name, color, price, stock):
        if user_role == "Admin" :
            from entities import Flower
            if price < 0:
                raise ValueError("Price cannot be negative")
            new_flower = Flower(None, name, color, price, stock)
            self.repository.add_flower(new_flower)
        else:
            raise PermissionError("Only admin can add new flowers")

    def update_flower_stock(self, user_role, flower_id, amount):
        if user_role in ["Admin", "Florist"] :
            self.repository.update_flower_stock(flower_id, amount)
        else:
            raise PermissionError("Only Admin or Florist can update the stock")

    def delete_flower(self, user_role, flower_id):
        if user_role == "Admin" :
            self.repository.delete_flower(flower_id)
        else:
            raise PermissionError("Only Admin can delete flowers")