from pathlib import Path

from flask import Flask, request, send_from_directory
from queries import FlowerQueryService
from repositories import FlowerRepository
from FlowerService import FlowerService, NotificationService
from api_errors import register_error_handlers
from controllers.api_controller import ApiController

try:
    from flask_socketio import SocketIO, emit
except ImportError:
    SocketIO = None
    emit = None

CLIENT_DIR = Path(__file__).resolve().parent.parent / "client"

app = Flask(__name__, static_folder=None)
app.secret_key = 'flower'
register_error_handlers(app)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "http://localhost:5002")
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    return response

socketio = SocketIO(
    app,
    cors_allowed_origins=["http://localhost:5002", "http://127.0.0.1:5002"],
) if SocketIO else None

repo = FlowerRepository()
query_service = FlowerQueryService(repo)
flower_service = FlowerService(repo, query_service)
flower_service.attach(NotificationService())

api_controller = ApiController(flower_service, query_service, repo)

@app.route('/api/<path:_path>', methods=['OPTIONS'])
def api_options(_path):
    return "", 204


@app.route('/api/login', methods=['POST'])
def api_login():
    return api_controller.login()


@app.route('/api/visitor', methods=['POST'])
def api_visitor_access():
    return api_controller.visitor_access()


@app.route('/api/logout', methods=['POST'])
def api_logout():
    return api_controller.logout()


@app.route('/api/session')
def api_session():
    return api_controller.session_info()


@app.route('/api/flowers')
def api_flowers():
    return api_controller.list_flowers()


@app.route('/api/flowers', methods=['POST'])
def api_create_flower():
    return api_controller.create_flower()


@app.route('/api/flowers/<int:flower_id>', methods=['PUT'])
def api_update_flower(flower_id):
    return api_controller.update_flower(flower_id)


@app.route('/api/flowers/<int:flower_id>/stock', methods=['PATCH'])
def api_update_stock(flower_id):
    return api_controller.update_stock(flower_id)


@app.route('/api/flowers/<int:flower_id>', methods=['DELETE'])
def api_delete_flower(flower_id):
    return api_controller.delete_flower(flower_id)


@app.route('/api/export/<fmt>')
def api_export_data(fmt):
    return api_controller.export_data(fmt)


@app.route('/app')
@app.route('/app/<path:path>')
def client_app(path='index.html'):
    if path and (CLIENT_DIR / path).exists():
        return send_from_directory(CLIENT_DIR, path)
    return send_from_directory(CLIENT_DIR, 'index.html')


if socketio:
    @socketio.on('chat_message')
    def handle_chat_message(data):
        from datetime import datetime

        sender = str(data.get('sender') or 'Visitor').strip()[:80]
        text = str(data.get('text') or '').strip()[:500]
        if not text:
            return
        emit('chat_message', {
            'sender': sender,
            'text': text,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, broadcast=True)

@app.route('/')
def index():
    return send_from_directory(CLIENT_DIR, 'index.html')


if __name__ == '__main__':
    if socketio:
        socketio.run(app, port=5002, debug=True, allow_unsafe_werkzeug=True)
    else:
        app.run(port=5002, debug=True)
