from flask import jsonify


class Error(Exception):
    def __init__(self, code, correlation_id=None, message=None, status=None):
        """
        Custom error class to raise for logger in the event of an error
        :param code: The HTTP status code of the error
        :param correlation_id: The context thread used for debugging
        :param message: The message to display for an error to be handled
        :param status: The HTTP status code of the error
        """
        self.code = code
        self.message = message or code.message
        self.status = status or code.status
        self.correlation_id = correlation_id

    def as_dict(self):
        return {'code': self.code, 'message': self.message}

    def as_response(self):
        return jsonify(self.as_dict()), self.status
