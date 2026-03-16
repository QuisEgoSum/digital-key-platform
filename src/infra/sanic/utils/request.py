from ipaddress import ip_address

from infra.sanic.http.request import AppRequest


class InvalidRequestIpError(RuntimeError):
    """Request IP address is missing or invalid."""


def get_request_ip_address(request: AppRequest) -> str | None:
    """Returns the client IP address from the request."""
    server_cfg = request.app.ctx.server_cfg

    raw_ip: str | None = None

    if server_cfg.trust_proxy_headers:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            raw_ip = forwarded.split(",")[0].strip()

    if raw_ip is None:
        raw_ip = request.ip

    try:
        return str(ip_address(raw_ip))
    except ValueError:
        return None
