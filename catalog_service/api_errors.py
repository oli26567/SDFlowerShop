from datetime import datetime, timezone

from flask import jsonify


class ApiError(Exception):
    status_code = 400
    code = "BAD_REQUEST"

    def __init__(self, message, code=None, status_code=None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code


class ValidationApiError(ApiError):
    status_code = 400
    code = "VALIDATION_ERROR"


class UnauthorizedApiError(ApiError):
    status_code = 401
    code = "UNAUTHORIZED"


class ForbiddenApiError(ApiError):
    status_code = 403
    code = "FORBIDDEN"


class NotFoundApiError(ApiError):
    status_code = 404
    code = "NOT_FOUND"


def error_payload(message, code):
    return {
        "message": message,
        "code": code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return jsonify(error_payload(error.message, error.code)), error.status_code

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        return jsonify(error_payload(str(error), "VALIDATION_ERROR")), 400

    @app.errorhandler(PermissionError)
    def handle_permission_error(error):
        return jsonify(error_payload(str(error), "FORBIDDEN")), 403

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify(error_payload("The requested resource was not found.", "NOT_FOUND")), 404

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception(error)
        return jsonify(error_payload("Something went wrong. Please try again.", "INTERNAL_ERROR")), 500
