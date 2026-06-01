import requests
from flask import jsonify, request, session, Response

from api_errors import ForbiddenApiError, NotFoundApiError, UnauthorizedApiError, ValidationApiError
from exporters import CsvExport, JsonExport


class ApiController:
    def __init__(self, flower_service, query_service, repo):
        self.flower_service = flower_service
        self.query_service = query_service
        self.repo = repo

    def _current_user(self):
        return {
            "name": session.get("username", "Visitor"),
            "email": session.get("email", "guest@flowershop.com"),
            "role": session.get("role", "Visitor"),
        }

    def _require_login(self):
        if "role" not in session or session.get("role") == "Visitor":
            raise UnauthorizedApiError("Please log in to perform this action.")
        return self._current_user()

    def _require_admin(self):
        user = self._require_login()
        if user["role"] != "Admin":
            raise ForbiddenApiError("Only administrators can perform this action.")
        return user

    def _require_stock_manager(self):
        user = self._require_login()
        if user["role"] not in ["Admin", "Florist"]:
            raise ForbiddenApiError("Only administrators and florists can update stock.")
        return user

    def _flower_payload(self):
        data = request.get_json(silent=True) or {}
        missing = [field for field in ["name", "color", "price", "stock"] if field not in data]
        if missing:
            raise ValidationApiError(f"Missing required field: {', '.join(missing)}.")
        try:
            return {
                "name": str(data["name"]).strip(),
                "color": str(data["color"]).strip(),
                "price": float(data["price"]),
                "stock": int(data["stock"]),
            }
        except (TypeError, ValueError):
            raise ValidationApiError("Price must be a number and stock must be an integer.")

    def login(self):
        data = request.get_json(silent=True) or {}
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            raise ValidationApiError("Email and password are required.")
        try:
            resp = requests.post(
                "http://localhost:5001/login",
                json={"email": email, "password": password},
                timeout=3,
            )
        except requests.RequestException:
            raise ValidationApiError("Identity service is unavailable. Please start it and try again.")

        if resp.status_code != 200:
            raise UnauthorizedApiError("Invalid email or password.")

        user_data = resp.json()
        session["role"] = user_data["role"]
        session["email"] = user_data["email"]
        session["username"] = user_data["name"]
        return jsonify({"user": self._current_user()})

    def visitor_access(self):
        session["role"] = "Visitor"
        session["email"] = "guest@flowershop.com"
        session["username"] = "Visitor"
        return jsonify({"user": self._current_user()})

    def logout(self):
        session.clear()
        return jsonify({"message": "Logged out successfully."})

    def session_info(self):
        return jsonify({
            "user": self._current_user(),
            "authenticated": session.get("role") in ["Admin", "Florist"],
            "entered": "role" in session,
        })

    def list_flowers(self):
        flowers = self.query_service.get_catalog(request.args.get("color"), request.args.get("sort"))
        return jsonify({"flowers": [flower.to_dict() for flower in flowers]})

    def create_flower(self):
        user = self._require_admin()
        payload = self._flower_payload()
        flower_id = self.flower_service.add_new_flower(
            user["role"],
            user["email"],
            payload["name"],
            payload["color"],
            payload["price"],
            payload["stock"],
        )
        flower = self.repo.get_by_id(flower_id)
        return jsonify({"flower": flower.to_dict()}), 201

    def update_flower(self, flower_id):
        user = self._require_admin()
        if not self.repo.get_by_id(flower_id):
            raise NotFoundApiError("Flower not found.")
        payload = self._flower_payload()
        self.flower_service.update_flower(
            user["role"],
            user["email"],
            flower_id,
            payload["name"],
            payload["color"],
            payload["price"],
            payload["stock"],
        )
        return jsonify({"flower": self.repo.get_by_id(flower_id).to_dict()})

    def update_stock(self, flower_id):
        user = self._require_stock_manager()
        data = request.get_json(silent=True) or {}
        if "stock" not in data:
            raise ValidationApiError("Stock is required.")
        try:
            stock = int(data["stock"])
        except (TypeError, ValueError):
            raise ValidationApiError("Stock must be an integer.")
        if not self.repo.get_by_id(flower_id):
            raise NotFoundApiError("Flower not found.")
        self.flower_service.update_flower_stock(user["role"], user["email"], flower_id, stock)
        return jsonify({"flower": self.repo.get_by_id(flower_id).to_dict()})

    def delete_flower(self, flower_id):
        user = self._require_admin()
        if not self.repo.get_by_id(flower_id):
            raise NotFoundApiError("Flower not found.")
        self.flower_service.delete_flower(user["role"], user["email"], flower_id)
        return jsonify({"message": "Flower deleted successfully."})

    def export_data(self, fmt):
        flowers = self.query_service.get_catalog()
        strategies = {"json": JsonExport(), "csv": CsvExport()}
        if fmt not in strategies:
            raise ValidationApiError("Invalid export format.")
        mimetype = "application/json" if fmt == "json" else "text/csv"
        return Response(strategies[fmt].export(flowers), mimetype=mimetype)
