import enum

from enum import StrEnum
from typing import Any, Self, cast


class OpenapiRouteParameterEnum(enum.Enum):
    query = "query"
    path = "path"
    header = "header"
    cookie = "cookie"


class OpenapiRouteContentSchema:
    schema: dict[str, Any]

    def __init__(self, schema: dict[str, Any]) -> None:
        self.schema = schema

    def to_dict(self) -> dict[str, Any]:
        return {"schema": self.schema}


class OpenapiRouteContent:
    description: str | None
    content: dict[str, OpenapiRouteContentSchema]
    headers: dict[str, Any]

    def __init__(
        self,
        content: dict[str, OpenapiRouteContentSchema] | None = None,
        description: str | None = None,
        headers: dict[str, Any] | None = None,
    ):
        self.description = description
        self.content = content or {}
        self.headers = headers or {}

    @staticmethod
    def _has_schema(
        one_of: list[dict[str, Any]],
        expected_schema: dict[str, Any],
    ) -> bool:
        return any(schema == expected_schema for schema in one_of)

    def add_schema(self, content_type: str, schema: dict[str, Any]) -> Self:
        if content_type not in self.content:
            self.content[content_type] = OpenapiRouteContentSchema(schema)
        elif self.content[content_type].schema == schema:
            return self
        else:
            current_content = self.content[content_type]
            if "oneOf" in current_content.schema:
                if "oneOf" in schema:
                    for child_schema in schema["oneOf"]:
                        if not self._has_schema(
                            one_of=current_content.schema["oneOf"],
                            expected_schema=child_schema,
                        ):
                            self.content[content_type].schema["oneOf"].append(
                                child_schema,
                            )
                else:
                    if not self._has_schema(
                        one_of=current_content.schema["oneOf"],
                        expected_schema=schema,
                    ):
                        self.content[content_type].schema["oneOf"].append(schema)
            else:
                schemas = []
                if "oneOf" in schema:
                    schemas = schema["oneOf"]
                else:
                    schemas.append(schema)
                self.content[content_type] = OpenapiRouteContentSchema(
                    {"oneOf": [*schemas, current_content.schema]},
                )
        return self

    def merge(self, content: Self) -> Self:
        if content is None:
            return self
        if content.content is not None:
            for content_type in cast("dict[str, Any]", content.content):
                target_content = cast("dict[str, Any]", content.content)[content_type]
                self.add_schema(content_type, target_content.schema)
        if self.description is None and content.description is not None:
            self.description = content.description
        self.headers.update(content.headers)
        return self

    def to_dict(self) -> dict[str, Any]:
        content: dict[str, Any] = {}
        if self.content is not None:
            for key in self.content:
                content[key] = self.content[key].to_dict()
        result: dict[str, Any] = {"content": content}
        if self.description is not None:
            result["description"] = self.description
        if self.headers:
            result["headers"] = self.headers
        return result


class OpenapiRouteParameter:
    location: OpenapiRouteParameterEnum
    name: str
    required: bool
    schema: dict[str, Any]
    description: str | None

    def __init__(
        self,
        location: OpenapiRouteParameterEnum,
        name: str,
        required: bool,
        schema: dict[str, Any],
        description: str | None = None,
    ) -> None:
        self.location = location
        self.name = name
        self.required = required
        self.schema = schema
        self.description = description

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "in": self.location.name,
            "name": self.name,
            "required": self.required,
            "schema": self.schema,
        }
        if self.description is not None:
            result["description"] = self.description
        return result


class OpenapiRouteTagOptions:
    name: str
    includes: str | None
    excludes: str | None

    def __init__(
        self,
        name: str,
        includes: str | None = None,
        excludes: str | None = None,
    ) -> None:
        self.name = name
        self.includes = includes
        self.excludes = excludes


class OpenapiRoute:
    responses: dict[int, OpenapiRouteContent]
    summary: str | None
    description: str | None
    tags: set[str]
    requestBody: OpenapiRouteContent | None
    exclude: bool
    deprecated: bool
    parameters: set[OpenapiRouteParameter]
    tags_options: list[OpenapiRouteTagOptions]
    security: dict[str, Any]
    headers: dict[str, str]
    scopes: set[str | StrEnum]

    def __init__(self) -> None:
        self.responses = {}
        self.summary = ""
        self.description = None
        self.requestBody = None
        self.exclude = False
        self.deprecated = False
        self.tags = set()
        self.parameters = set()
        self.tags_options = []
        self.security = {}
        self.headers = {}
        self.scopes = set()

    def add_scope(self, scope: str | StrEnum) -> None:
        self.scopes.add(scope)

    def add_parameters(
        self,
        parameters: list[OpenapiRouteParameter],
    ) -> Self:
        self.parameters = self.parameters.union(parameters)
        return self

    def add_tag_fabric(
        self,
        name: str,
        includes: str | None,
        excludes: str | None,
    ) -> Self:
        if includes is not None or excludes is not None:
            return self.add_tag_options(name, includes, excludes)
        else:
            return self.add_tag(name)

    def add_tag(self, name: str) -> Self:
        self.tags.add(name)
        return self

    def add_tag_options(
        self,
        name: str,
        includes: str | None,
        excludes: str | None,
    ) -> Self:
        self.tags_options.append(OpenapiRouteTagOptions(name, includes, excludes))
        return self

    def add_response_schema(
        self,
        status: int,
        schema: dict[str, Any] | None,
        content_type: str,
        description: str | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Self:
        if schema is not None:
            content = OpenapiRouteContent(
                {content_type: OpenapiRouteContentSchema(schema)},
                description,
                headers,
            )
        else:
            content = OpenapiRouteContent(
                content=None,
                description=description,
                headers=headers,
            )
        return self.add_response_content(
            status,
            content,
        )

    def add_response_content(
        self,
        status: int,
        content: OpenapiRouteContent,
    ) -> Self:
        if status not in self.responses:
            self.responses[status] = content
        else:
            self.responses[status].merge(content)
        return self

    def add_body_schema(self, content_type: str, schema: dict[str, Any]) -> Self:
        if self.requestBody is None:
            self.requestBody = OpenapiRouteContent(
                {content_type: OpenapiRouteContentSchema(schema)},
            )
        else:
            self.requestBody.add_schema(content_type, schema)
        return self

    def merge(self, route: Self) -> Self:
        if route.summary:
            self.summary = route.summary
        if route.description:
            self.description = route.description
        self.parameters = self.parameters.union(route.parameters)
        self.tags = self.tags.union(route.tags)
        self.tags_options = self.tags_options + route.tags_options
        if self.requestBody is not None:
            self.requestBody.merge(cast("OpenapiRouteContent", route.requestBody))
        else:
            self.requestBody = route.requestBody
        if route.exclude is not False:
            self.exclude = route.exclude
        if route.deprecated is not False:
            self.deprecated = route.deprecated
        for code, content in route.responses.items():
            if code not in self.responses:
                self.responses[code] = content
            else:
                self.responses[code].merge(content)
        self.security.update(route.security)
        self.scopes.update(route.scopes)
        return self

    def add_security(self, name: str, scopes: list[str] | None = None) -> None:
        if scopes is None:
            scopes = []
        self.security[name] = scopes

    def resolve_tags(self, url: str, default_tag: str) -> Self:
        if len(self.tags) == 0 and len(self.tags_options) == 0:
            self.tags.add(default_tag)
        elif len(self.tags_options) != 0:
            for options in self.tags_options:
                if options.excludes is not None and options.includes is not None:
                    if options.excludes not in url and options.includes in url:
                        self.tags.add(options.name)
                else:
                    if options.excludes is not None:
                        if options.excludes not in url:
                            self.tags.add(options.name)
                    elif options.includes is not None and options.includes in url:
                        self.tags.add(options.name)
        return self

    def to_dict(self) -> dict[str, Any]:
        responses: dict[Any, Any] = {}
        for status in self.responses:
            responses[status] = self.responses[status].to_dict()
        result: dict[str, Any] = {
            "summary": self.summary,
            "tags": list(self.tags),
            "responses": responses,
        }
        mapped_security = []
        for key, value in self.security.items():
            mapped_security.append({key: value})
        result["security"] = mapped_security
        if self.deprecated is True:
            result["deprecated"] = True
        if len(self.parameters) != 0:
            result["parameters"] = [
                parameter.to_dict() for parameter in self.parameters
            ]
        if self.requestBody is not None:
            result["requestBody"] = self.requestBody.to_dict()
        if self.description is not None:
            result["description"] = self.description
        return result
