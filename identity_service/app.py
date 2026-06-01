from flask import Flask
from repositories import UserRepository
from UserService import UserService
from controllers.user_controller import UserController
from api_errors import register_error_handlers

app = Flask(__name__)
register_error_handlers(app)

user_repo = UserRepository()
user_service = UserService(user_repo)

controller = UserController(user_service)

@app.route('/login', methods=['POST'])
def login():
    return controller.login()


if __name__ == '__main__':
    app.run(port=5001)
