from flask import request, jsonify
from api_errors import error_payload


class UserController:
    """
    Controller layer — parses HTTP requests and delegates
    authentication logic to the UserService.
    """

    def __init__(self, user_service):
        self.user_service = user_service

    def login(self):
        data = request.get_json(silent=True) or {}
        if not data.get('email') or not data.get('password'):
            return jsonify(error_payload('Email and password are required.', 'VALIDATION_ERROR')), 400
        user_info = self.user_service.login(data['email'], data['password'])
        if user_info:
            return jsonify(user_info), 200
        return jsonify(error_payload('Invalid email or password.', 'UNAUTHORIZED')), 401
