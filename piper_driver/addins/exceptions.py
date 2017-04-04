class PiperException(Exception):
    pass


class ModelException(PiperException):
    pass


class ModelInvalidValueException(ModelException):
    pass


class JobOnlyExpressionException(PiperException):
    pass
