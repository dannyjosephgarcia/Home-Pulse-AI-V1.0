class ErrorCode:
    def __init__(self, code, message, status):
        """
        Customer ErrorCode object to be passed to the Error class for custom exception handling
        :param code: The code associated with the error
        :param message: The message to be surfaced within the logs
        :param status: The HTTP status code of the request
        """
        self.code = code
        self.message = message
        self.status = status


