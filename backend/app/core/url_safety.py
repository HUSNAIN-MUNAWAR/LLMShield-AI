from __future__ import annotations
import ipaddress, socket
from dataclasses import dataclass
from urllib.parse import urlparse
from app.core.config import settings
BLOCKED_EXACT_IPS = {"169.254.169.254", "0.0.0.0"}
ALLOWED_SCHEMES = {"http","https"}
@dataclass(frozen=True)
class URLSafetyResult:
    allowed: bool
    reason: str
    host: str | None = None
def _host_allowed(host: str) -> bool:
    return any(host == item or host.endswith(f".{item}") for item in (settings.endpoint_allowlist or []))
def _resolve_ips(host: str):
    try: return [ipaddress.ip_address(row[4][0]) for row in socket.getaddrinfo(host, None)]
    except Exception:
        try: return [ipaddress.ip_address(host)]
        except Exception: return []
def validate_target_url(url: str, *, allow_private: bool | None = None) -> URLSafetyResult:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES: return URLSafetyResult(False, "Only HTTP/HTTPS endpoints are allowed.")
    if not parsed.hostname: return URLSafetyResult(False, "Endpoint must include a hostname.")
    host = parsed.hostname.lower()
    if not _host_allowed(host): return URLSafetyResult(False, f"Host '{host}' is not in ENDPOINT_ALLOWLIST.", host)
    private_allowed = settings.allow_private_targets if allow_private is None else allow_private
    for ip in _resolve_ips(host):
        ip_text = str(ip)
        if ip_text in BLOCKED_EXACT_IPS: return URLSafetyResult(False, f"Blocked metadata or unsafe IP: {ip_text}", host)
        if (ip.is_private or ip.is_loopback or ip.is_link_local) and not private_allowed and host not in {"localhost","127.0.0.1"}:
            return URLSafetyResult(False, f"Private/link-local address blocked: {ip_text}", host)
    return URLSafetyResult(True, "Allowed by endpoint allowlist and SSRF checks.", host)
