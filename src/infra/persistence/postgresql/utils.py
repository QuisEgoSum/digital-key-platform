from sqlalchemy.exc import IntegrityError


def is_unique_error(ex: IntegrityError) -> bool:
    return ex.orig.pgcode == "23505"  # type: ignore
