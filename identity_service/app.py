from flask import Flask, request, jsonify
from repositories import UserRepository
from UserService import UserService
app = Flask(__name__)
user_repo = UserRepository()
user_service = UserService(user_repo)


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_info = user_service.login(data['email'], data['password'])

    if user_info:
        return jsonify(user_info), 200
    return jsonify({'error': 'Unauthorized'}), 401


if __name__ == '__main__':
    app.run(port=5001)