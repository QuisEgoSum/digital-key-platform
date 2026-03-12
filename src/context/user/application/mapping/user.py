from context.user.application.dtos.entity.user import UserLoginDetailsDTO, UserMeDTO


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
