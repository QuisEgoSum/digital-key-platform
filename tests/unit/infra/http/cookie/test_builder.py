from typing import Literal

import pytest

from infra.http.cookie.builder import build_cookie_delete, build_cookie_set
from infra.http.cookie.config import (
    CookieConfig,
    CookieDefaultsConfig,
    CookieDefaultsOverrideConfig,
    CookieDomainConfig,
    CookiePolicyConfig,
    CookiePolicyOverrideConfig,
)
from infra.http.cookie.errors import CookieDomainResolutionError


def make_policy(
    *,
    mode: Literal["host", "fixed", "allow_list"] = "host",
    fixed: str | None = None,
    allow_list: frozenset[str] = frozenset(),
    host_map: dict[str, str] | None = None,
    defaults: CookieDefaultsConfig | None = None,
) -> CookiePolicyConfig:
    return CookiePolicyConfig(
        domain=CookieDomainConfig(
            mode=mode,
            fixed=fixed,
            allow_list=allow_list,
            host_map={} if host_map is None else host_map,
        ),
        defaults=CookieDefaultsConfig() if defaults is None else defaults,
    )


@pytest.mark.parametrize(
    "server_policy, request_host, override, expected_domain, expected_error",
    [
        (make_policy(mode="host"), "example.com", None, None, None),
        (
            make_policy(mode="fixed", fixed=".example.com"),
            "example.com",
            None,
            ".example.com",
            None,
        ),
        (
            make_policy(mode="allow_list", allow_list=frozenset({"example.com"})),
            "example.com",
            None,
            "example.com",
            None,
        ),
        (
            make_policy(
                mode="allow_list",
                allow_list=frozenset({"example.com"}),
                host_map={"example.com": ".example.com"},
            ),
            "example.com",
            None,
            ".example.com",
            None,
        ),
        (
            make_policy(mode="allow_list", allow_list=frozenset({"example.com"})),
            "other.com",
            None,
            None,
            CookieDomainResolutionError,
        ),
        (
            make_policy(
                mode="allow_list",
                allow_list=frozenset({"example.com"}),
                host_map={"example.com": ".example.com"},
            ),
            "example.com:443",
            None,
            ".example.com",
            None,
        ),
    ],
)
def test_build_cookie_set_domain_resolution(
    server_policy: CookiePolicyConfig,
    request_host: str,
    override: CookiePolicyOverrideConfig | None,
    expected_domain: str | None,
    expected_error: type[Exception],
) -> None:
    cookie = CookieConfig(
        name="auth",
        max_age=3600,
        policy_override=override,
    )

    if expected_error:
        with pytest.raises(expected_error):
            build_cookie_set(
                cookie=cookie,
                value="token",
                server_policy=server_policy,
                request_host=request_host,
            )
    else:
        dto = build_cookie_set(
            cookie=cookie,
            value="token",
            server_policy=server_policy,
            request_host=request_host,
        )

        assert dto.domain == expected_domain


def test_build_cookie_set_merges_defaults_override() -> None:
    server_policy = make_policy(
        mode="host",
        defaults=CookieDefaultsConfig(
            path="/",
            secure=True,
            httponly=True,
            samesite="None",
        ),
    )

    override = CookiePolicyOverrideConfig(
        defaults=CookieDefaultsOverrideConfig(httponly=False),
    )

    cookie = CookieConfig(
        name="auth",
        max_age=3600,
        policy_override=override,
    )

    dto = build_cookie_set(
        cookie=cookie,
        value="token",
        server_policy=server_policy,
        request_host="example.com",
    )

    assert dto.httponly is False
    assert dto.secure is True
    assert dto.path == "/"
    assert dto.samesite == "None"


def test_build_cookie_delete() -> None:
    server_policy = make_policy(
        mode="fixed",
        fixed=".example.com",
        defaults=CookieDefaultsConfig(
            path="/api",
            secure=True,
            httponly=True,
            samesite="Lax",
        ),
    )

    cookie = CookieConfig(name="auth", max_age=3600, policy_override=None)

    dto = build_cookie_delete(
        cookie=cookie,
        server_policy=server_policy,
        request_host="example.com",
    )

    assert dto.name == "auth"
    assert dto.domain == ".example.com"
    assert dto.path == "/api"
