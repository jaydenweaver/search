from fastapi import status

class AppError(Exception):
    """ base class for all application level exceptions. """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "An unexpected error occurred."

    def __init__(self, message=None, status_code=None):
        super().__init__(message or self.message)
        if status_code:
            self.status_code = status_code


class ExternalServiceError(AppError):
    """ for failures when calling openai, supabase, or qdrant. """
    status_code = status.HTTP_502_BAD_GATEWAY
    message = "A downstream service is currently unavailable."


class RateLimitExceeded(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    message = "The request rate limit has been exceeded."


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    message = "The requested resource was not found."


