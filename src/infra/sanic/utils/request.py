from infra.sanic.http.request import AppRequest


def get_request_ip_address(request: AppRequest) -> str:
    """Returns the client IP address from the request."""
    server_cfg = request.app.ctx.server_cfg

    if server_cfg.trust_proxy_headers:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()

    return request.ip
