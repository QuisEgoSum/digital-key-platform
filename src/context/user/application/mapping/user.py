from context.user.application.dtos.entity.user import (
    UserDTO,
    UserLoginDetailsDTO,
    UserMeDTO,
)
from context.user.application.dtos.entity.user_email import UserEmailDTO


def map_login_details_to_user_me(login_details: UserLoginDetailsDTO) -> UserMeDTO:
    return UserMeDTO(
        id=login_details.id,
        name=login_details.name,
        locale=login_details.locale,
        timezone=login_details.timezone,
        emails=login_details.emails,
        created_at=login_details.created_at,
        updated_at=login_details.updated_at,
    )


def map_register_user_data_to_user_me(
    user: UserDTO,
    user_email: UserEmailDTO,
) -> UserMeDTO:
    return UserMeDTO(
        id=user.id,
        name=user.name,
        locale=user.locale,
        timezone=user.timezone,
        emails=[user_email],
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
