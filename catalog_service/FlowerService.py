from commands import AddFlowerCommand, UpdateStockCommand
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

    def get_catalog(self, color=None, sort_by=None):
        return self.repository.get_filtered_sorted(color, sort_by)

    def add_new_flower(self, user_role, user_email, name, color, price, stock):
        if user_role == "Admin":
            cmd = AddFlowerCommand(self.repository, name, color, price, stock)
            cmd.execute()
            self.notify("CREATED", f"Flower: {name}", user_email)
        else:
            raise PermissionError("Only Admins can add flowers.")

    def update_flower_stock(self, user_role, user_email, flower_id, new_stock):
        if user_role in ["Admin", "Florist"]:
            flower = self.repository.get_by_id(flower_id)
            if flower:
                self.repository.update_stock(flower_id, new_stock)
                self.notify("UPDATED", f"Stock for {flower.name} set to {new_stock}", user_email)
        else:
            raise PermissionError("Unauthorized to update stock.")

    def delete_flower(self, user_role, user_email, flower_id):
        if user_role == "Admin":
            flower = self.repository.get_by_id(flower_id)
            if flower:
                self.repository.delete_flower(flower_id)
                self.notify("DELETED", f"Flower: {flower.name}", user_email)

    def update_flower_details(self, user_role, user_email, flower_id, name, color, price, stock):
        if user_role == "Admin":
            self.repository.update_flower(flower_id, name, color, price, stock)
            self.notify("UPDATED", f"Modified details for {name} (ID: {flower_id})", user_email)
        else:
            raise PermissionError("Only Admins can modify flower details.")