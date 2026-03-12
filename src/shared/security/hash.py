import hashlib
import hmac

import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def compute_scoped_hmac(value: str, secret: str, scope: str) -> str:
    return hmac.new(
        key=secret.encode("utf-8"),
        msg=f"{scope}:{value}".encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()
