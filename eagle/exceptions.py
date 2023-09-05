

class AppException(Exception):
    ...


class APIAuthFailedException(AppException):
    ...


class APIServerErrorException(AppException):
    ...
