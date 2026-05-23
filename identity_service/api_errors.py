from datetime import datetime, timezone

from flask import jsonify


def error_payload(message, code):
    return {
        "message": message,
        "code": code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def register_error_handlers(app):
    @app.errorhandler(400)
    def handle_bad_request(error):
        return jsonify(error_payload("Invalid request.", "BAD_REQUEST")), 400

    @app.errorhandler(401)
    def handle_unauthorized(error):
        return jsonify(error_payload("Invalid email or password.", "UNAUTHORIZED")), 401

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        app.logger.exception(error)
        return jsonify(error_payload("Something went wrong. Please try again.", "INTERNAL_ERROR")), 500
