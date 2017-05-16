class PiperException(Exception):
    pass


class ModelException(PiperException):
    pass


class ModelInvalid(ModelException):

    def __init__(self, errors=None):
        super().__init__()
        self.errors = errors


class JobOnlyExpressionException(PiperException):
    pass


class RepositoryException(PiperException):
    pass


class RepositoryNotFound(RepositoryException):
    pass


class RepositoryPermissionDenied(RepositoryException):
    pass
