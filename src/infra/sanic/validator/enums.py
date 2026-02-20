import enum


class TargetNameType(enum.Enum):
    QUERY = "query"
    BODY = "body"
    PARAMS = "params"
    UNION = "union"
    HEADERS = "headers"
