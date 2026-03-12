import secrets


def generate_numeric_token(length: int = 6) -> str:
    upper = 10**length
    return str(secrets.randbelow(upper)).zfill(length)


def generate_urlsafe_token(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)
