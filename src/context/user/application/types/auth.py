from typing import Literal

type UserRegisterStatus = Literal[
    "email_verification_required",
    "logged_in",
]
type UserLoginStatus = Literal[
    "email_verification_required",
    "logged_in",
]
type UserConfirmStatus = Literal[
    "confirmed",
    "logged_in",
]
