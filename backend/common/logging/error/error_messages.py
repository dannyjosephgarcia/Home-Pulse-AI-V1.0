from error_code import ErrorCode

INVALID_REQUEST = ErrorCode(code="INVALID_REQUEST",
                            message="The request to the route is invalid",
                            status=400)
INTERNAL_SERVICE_ERROR = ErrorCode(code="INTERNAL_SERVICE_ERROR",
                                   message="There was a problem processing the request",
                                   status=500)
SERVICE_TIMEOUT = ErrorCode(code="SERVICE TIMEOUT",
                            message="A timeout in processing has occurred",
                            status=408)
