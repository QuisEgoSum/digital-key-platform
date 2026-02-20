from shared.errors.base import ValidationError


class CookieDomainResolutionError(ValidationError):
    message = "Host is not allowed for cookie domain resolution."
    code = 20
