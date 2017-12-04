class PiperException(Exception):
    pass


class JobExpressionException(PiperException):
    pass


class FacadeException(PiperException):
    pass


class FacadeNotFound(FacadeException):
    pass


class FacadeUnauthorized(FacadeException):
    pass


class FacadeInvalidAction(FacadeException):
    pass


class FacadeInvalidSchema(FacadeException):
    pass


class FacadeIntegrityError(FacadeException):
    pass


class ShellException(PiperException):
    pass


class WebhookParseException(PiperException):
    pass
