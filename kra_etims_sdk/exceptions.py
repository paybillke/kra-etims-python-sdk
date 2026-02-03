class ValidationException(Exception):
    def __init__(self, message="Validation error", errors=None):
        super().__init__(message)
        self.errors = errors or []


class AuthenticationException(Exception):
    def __init__(self, message="Authentication failed", status_code=401):
        super().__init__(message)
        self.status_code = status_code


class ApiException(Exception):
    def __init__(self, message="API error", status_code=400, error_code=None, details=None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
