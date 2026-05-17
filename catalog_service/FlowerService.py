from commands import AddFlowerCommand, UpdateStockCommand, DeleteFlowerCommand
from queries import FlowerQueryService
from abc import ABC, abstractmethod


class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def notify(self, action, detail, user_email):
        for observer in self._observers:
            observer.update(action, detail, user_email)


class NotificationService:
    def update(self, action, detail, user_email):
        print(f"\n--- EMAIL SIMULATION ---")
        print(f"To: {user_email}\nEvent: {action}\nDetail: {detail}\n")


class FlowerService(Subject):
    def __init__(self, repository, query_service):
        super().__init__()
        self.repository = repository
        self.query_service = query_service

    def _validate(self, price=None, stock=None):
        if price is not None and price <= 0:
            raise ValueError("Price must be greater than 0.")
        if stock is not None and stock < 0:
            raise ValueError("Stock quantity cannot be negative.")

    def get_catalog(self, color=None, sort_by=None):
        return self.repository.get_filtered_sorted(color, sort_by)

    def add_new_flower(self, user_role, user_email, name, color, price, stock):
        if user_role == "Admin":
            self._validate(price=price, stock=stock)
            cmd = AddFlowerCommand(self.repository, name, color, price, stock)
            cmd.execute()
            self.notify("CREATED", f"Flower: {name}", user_email)
        else:
            raise PermissionError("Only Admins can add flowers.")

    def update_flower_stock(self, user_role, user_email, flower_id, new_stock):
        if user_role in ["Admin", "Florist"]:
            self._validate(stock=new_stock)
            flower = self.repository.get_by_id(flower_id)
            if flower:
                cmd = UpdateStockCommand(self.repository, flower_id, new_stock)
                cmd.execute()
                self.notify("UPDATED", f"Stock for {flower.name} set to {new_stock}", user_email)
        else:
            raise PermissionError("Unauthorized to update stock.")

    def delete_flower(self, user_role, user_email, flower_id):
        if user_role == "Admin":
            flower = self.repository.get_by_id(flower_id)
            if flower:
                cmd = DeleteFlowerCommand(self.repository, flower_id)
                cmd.execute()
                self.notify("DELETED", f"Flower: {flower.name}", user_email)
        else:
            raise PermissionError("Only Admins can delete flowers.")

    def execute_command(self, command):
        return command.execute()
