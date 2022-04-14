error_code = [
    "APPLICATION_ERROR",
    "DB_ERROR",
    "NODATA_ERROR",
    "HTTP_ERROR",
    "SERVICETIME_OUT",
    "INVALID_REQUEST_PARAMETER_ERROR",
    "NO_MANDATORY_REQUEST_PARAMETERS_ERROR",
    "NO_OPENAPI_SERVICE_ERROR",
    "SERVICE_ACCESS_DENIED_ERROR",
    "TEMPORARILY_DISABLE_THE_SERVICEKEY_ERROR",
    "LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR",
    "SERVICE_KEY_IS_NOT_REGISTERED_ERROR",
    "DEADLINE_HAS_EXPIRED_ERROR",
    "UNREGISTERED_IP_ERROR",
    "UNSIGNED_CALL_ERROR",
    "UNKNOWN_ERROR"]


class ApiException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class CheckErr:
    def __init__(self, n):
        code = int(n)
        if code == 0:
            return

        raise ApiException(error_code[code])
