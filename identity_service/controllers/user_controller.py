from flask import request, jsonify


class UserController:
    """
    Controller layer — parses HTTP requests and delegates
    authentication logic to the UserService.
    """

    def __init__(self, user_service):
        self.user_service = user_service

    def login(self):
        data = request.json
        user_info = self.user_service.login(data['email'], data['password'])
        if user_info:
            return jsonify(user_info), 200
        return jsonify({'error': 'Unauthorized'}), 401
