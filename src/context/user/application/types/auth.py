from typing import Literal

type UserRegisterStatus = Literal["email_verification_required"]
type UserLoginStatus = Literal[
    "email_verification_required",
    "logged_in",
]
