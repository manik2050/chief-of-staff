# API security best practices

Learning evidence for Day 24 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

HTTP sends data in plaintext; HTTPS is HTTP plus TLS. The academy's
two-person startup shipped sensitive data in the clear, then public APIs
failed under spikes, then security lagged as features grew. Day 10
[security](../security/) is the primer basics (encrypt, sanitize, bind SQL,
least privilege). This note is the eight API practices: HTTPS,
authentication, authorization, rate limiting and throttling, input
validation, logging, security audits, and dependency management.

```
  client
     |
     | HTTPS (TLS: cert -> CA check -> shared key)
     v     HSTS Strict-Transport-Security; AES / ChaCha20
+------------------+  OAuth token; OIDC; MFA; short-lived
|  authn           |
|  authz (RBAC)    |  role -> permissions; least privilege
|  rate limiter    |  IP / user / API key; over -> 429
|                  |  or throttle: queue and delay, do not drop
|  schema/sanitize |  expected structure; then strip unsafe
+------------------+
     |
     v
  handler; log IP, time, headers (no secrets); SIEM
  audit: fuzz / stress; deps: Dependabot, Snyk, npm audit
```

```python
# Toy API checks, not a product. python3 - <<'PY' ... PY
roles = {"k1": {"read"}, "k2": {"read"}}
seen, queue = {}, []

def log_meta(meta):
    return {k: v for k, v in meta.items() if k != "secret"}

def handle(client, token, action, body):
    if not token:
        return "no token"                   # unverified: no access
    if action not in roles.get(client, ()):
        return "forbidden"                  # in the building, not that room
    seen[client] = seen.get(client, 0) + 1
    if seen[client] > 2:
        return "429 Too Many Requests"      # drop once the window is full
    if set(body) != {"id"}:
        return "bad schema"                 # structure first
    return "ok"

def throttle(req):
    queue.append(req)                       # delay, do not drop
    return "queued " + queue.pop(0)

print("log", log_meta({"ip": "n", "secret": "x"}))
print(handle("k1", None, "read", {"id": 1}))
print(handle("k1", "t", "write", {"id": 1}))
print(handle("k1", "t", "read", {"id": 1}))
print(handle("k1", "t", "read", {"id": 1}))
print(handle("k1", "t", "read", {"id": 1}))
print(handle("k2", "t", "read", {"id": 1, "x": 2}))
print(throttle("slow"))
# log {'ip': 'n'}
# no token
# forbidden
# ok
# ok
# 429 Too Many Requests
# bad schema
# queued slow
```

Use the latest TLS the platform supports. HSTS (`Strict-Transport-Security`)
tells the browser to stay on HTTPS for a period; AES or ChaCha20 keep the
session strong. Authentication verifies identity. OAuth: the client asks, the
authorization server issues a token, the API checks it. OIDC is
authentication on top of OAuth. MFA adds a second check (password, then
authenticator app) before the token. Keep tokens short-lived and refresh
them so a stolen one ages out. Authorization is what that identity may do
(rooms after the building). RBAC groups by function, puts permissions on the
role, assigns users, and checks the role before an action; write who/what/when
and review as jobs change; least privilege. Rate limiting counts per IP, user
ID, or API key in a window and returns 429; the counter resets after the
window. Throttling queues and delays instead of dropping. Both need
configuration for a usable API. Schema validation checks structure;
sanitization with proven libraries strips unsafe content (scripts, SQL
injection, malformed data). Primer: bind SQL parameters — Day 10. Log
metadata only; SIEM gathers logs across services and raises alerts. Audit
with fuzz (unexpected input) and stress (overload). Track third-party code
with Dependabot, Snyk, or npm audit; patch early; drop unused dependencies —
a system is only as secure as its weakest part.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([Best Practices for API Security](https://newsletter.systemdesign.one/p/api-security-best-practices)
— HTTP plaintext vs HTTPS as HTTP plus TLS; cert, CA, shared key; latest TLS,
HSTS, AES/ChaCha20; OAuth token check, OIDC, MFA, short-lived refresh; authn
vs authz; RBAC, policies, least privilege; rate limit by IP/user/API key, 429,
window reset vs throttle queue; schema then sanitize; log IP/time/headers not
secrets, SIEM; fuzz and stress audits; Dependabot, Snyk, npm audit, patch,
remove unused);
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Security: encrypt in transit and at rest; sanitize inputs against XSS and
SQL injection; parameterized queries; least privilege).
