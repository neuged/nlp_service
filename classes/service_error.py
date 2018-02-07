from flask import jsonify


class ServiceError(Exception):
    error_code = 200
    message = ""

    def __init__(self, message, error_code=400):
        self.error_code = error_code
        self.message = message

    def build(self):
        return jsonify(dict({
            "message": self.message,
            "code": self.error_code
        })), self.error_code