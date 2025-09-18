from common.logging.error.error_code import ErrorCode

INVALID_REQUEST = ErrorCode(code="INVALID_REQUEST",
                            message="The request to the route is invalid",
                            status=400)
INTERNAL_SERVICE_ERROR = ErrorCode(code="INTERNAL_SERVICE_ERROR",
                                   message="There was a problem processing the request",
                                   status=500)
SERVICE_TIMEOUT = ErrorCode(code="SERVICE TIMEOUT",
                            message="A timeout in processing has occurred",
                            status=408)
USER_NOT_FOUND = ErrorCode(code="USER_NOT_FOUND",
                           message="No user exists with this email and password",
                           status=401)
INVALID_PASSWORD = ErrorCode(code="INVALID_PASSWORD",
                             message="Invalid password for user email",
                             status=401)
WEBSCRAPING_ISSUE = ErrorCode(code="WEBSCRAPING_ISSUE",
                              message='There was an issue harvesting data from the website',
                              status=500)
AWS_CONNECTION_ISSUE = ErrorCode(code="AWS_CONNECTION_ISSUE",
                                 message='There was an issue connecting to AWS',
                                 status=500)
INVALID_INVITATION = ErrorCode(code="INVALID_INVITATION",
                               message='The invitation UUID provided in the signup request is invalid',
                               status=400)
INVALID_CUSTOMER = ErrorCode(code='INVALID_CUSTOMER',
                             message='The customer credentials are invalid',
                             status=400)
INVALID_BULK_CSV_FILE = ErrorCode(code='INVALID_BULK_CSV_FILE',
                                  message="The .csv file uploaded by the user is invalid. Please try again.",
                                  status=400)
DELETION_ISSUE = ErrorCode(code='DELETION_ISSUE',
                           message='The customer subscription could not be canceled',
                           status=500)
HOME_BOT_AI_ERROR = ErrorCode(code='HOME_BOT_AI_ERROR',
                              message='There was an issue booting up HomeBot',
                              status=500)
