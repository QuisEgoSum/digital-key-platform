from infra.http.cookie.config import (
    CookieConfig,
    CookieDefaultsConfig,
    CookieDefaultsOverrideConfig,
    CookieDomainConfig,
    CookiePolicyConfig,
    CookiePolicyOverrideConfig,
)
from infra.http.cookie.dtos import CookieDeleteDTO, CookieSetDTO
from infra.http.cookie.errors import CookieDomainResolutionError


def build_cookie_set(
    *,
    cookie: CookieConfig,
    value: str,
    server_policy: CookiePolicyConfig,
    request_host: str,
) -> CookieSetDTO:
    policy = merge_policy(server_policy, cookie.policy_override)

    normalized_host = normalize_request_host(request_host)
    domain = resolve_cookie_domain(
        domain_cfg=policy.domain,
        request_host=normalized_host,
    )

    defaults = policy.defaults

    return CookieSetDTO(
        name=cookie.name,
        value=value,
        max_age=cookie.max_age,
        path=defaults.path,
        domain=domain,
        secure=defaults.secure,
        httponly=defaults.httponly,
        samesite=defaults.samesite,
    )


def build_cookie_delete(
    *,
    cookie: CookieConfig,
    server_policy: CookiePolicyConfig,
    request_host: str,
) -> CookieDeleteDTO:
    policy = merge_policy(server_policy, cookie.policy_override)

    normalized_host = normalize_request_host(request_host)
    domain = resolve_cookie_domain(
        domain_cfg=policy.domain,
        request_host=normalized_host,
    )

    return CookieDeleteDTO(
        name=cookie.name,
        domain=domain,
        path=policy.defaults.path,
    )


def merge_policy(
    base: CookiePolicyConfig,
    override: CookiePolicyOverrideConfig | None,
) -> CookiePolicyConfig:
    if override is None:
        return base

    domain_cfg = override.domain or base.domain
    defaults_cfg = base.defaults
    if override.defaults is not None:
        defaults_cfg = merge_defaults(base.defaults, override.defaults)

    return CookiePolicyConfig(domain=domain_cfg, defaults=defaults_cfg)


def merge_defaults(
    base: CookieDefaultsConfig,
    override: CookieDefaultsOverrideConfig | None,
) -> CookieDefaultsConfig:
    if override is None:
        return base

    return CookieDefaultsConfig(
        path=base.path if override.path is None else override.path,
        secure=base.secure if override.secure is None else override.secure,
        httponly=base.httponly if override.httponly is None else override.httponly,
        samesite=base.samesite if override.samesite is None else override.samesite,
    )


def resolve_cookie_domain(
    *,
    domain_cfg: CookieDomainConfig,
    request_host: str,
) -> str | None:
    mode = domain_cfg.mode

    if mode == "host":
        return None

    if mode == "fixed":
        return domain_cfg.fixed

    if mode == "allow_list":
        if request_host not in domain_cfg.allow_list:
            raise CookieDomainResolutionError()

        mapped = domain_cfg.host_map.get(request_host)
        return mapped

    return None


def normalize_request_host(host: str) -> str:
    h = host.strip().lower()

    if h.startswith("["):
        end = h.find("]")
        if end != -1:
            return h[1:end]
        return h.strip("[]")

    if ":" in h:
        return h.split(":", 1)[0]

    return h
