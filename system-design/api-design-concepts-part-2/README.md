# API design concepts, part 2

Learning evidence for Day 30 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Part 1 ([API design concepts, part 1](../api-design-concepts-part-1/))
covers REST through pagination. Neo Kim's #185 continues from JWT through
error handling (concepts 18-33). The public teaser defines JWT through
microservices, sketched here (WebSockets through error handling are named
there, not defined here). A JWT is a signed token in three dotted parts:
a header that names the algorithm, a payload of claims (user 42, expires
at noon, admin), and a signature so the server verifies with a key it
already holds and skips a session store. Throttling delays a caller
instead of turning them away: a rate limiter rejects over the cap with
429, a throttle queues the work or sends Retry-After so the call still
happens later. An endpoint is the URL for one resource (`/users`,
`/users/42`, `/users/42/orders`); the path names the resource and the
method names the action; a wrong path is 404. Request-response is send,
wait, read one reply: method, path, headers, optional body in; status and
usually a body out. Headers are key-value pairs about the message, not
the body (Content-Type, Authorization, Cache-Control, Accept,
User-Agent). OpenAPI is one YAML or JSON file of every endpoint,
parameter, and response; machines generate docs, clients, mocks, and
contract tests from it. A timeout is the longest a caller will wait:
connect to reach the server, read to hear back. Microservices split one
app into services that each own a job and its data and talk over APIs.

```
  client
     |
     |  GET /users/42
     |  Authorization: Bearer header.payload.signature
     v
+------------------+  JWT: verify sig, read claims, no session store
|  /users/42       |  throttle: queue or Retry-After (not 429)
|                  |  timeout: fail fast vs hang
+------------------+  OpenAPI: the contract file
     |  slow work
     v
  202 Accepted; finish in the background
```

```python
# Toy JWT, not a library. python3 - <<'PY' ... PY
import hmac, hashlib, json, base64
def b64(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
def mint(claims, secret):
    h = b64(b'{"alg":"HS256"}')
    p = b64(json.dumps(claims, separators=(",", ":")).encode())
    s = b64(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
    return f"{h}.{p}.{s}"
def verify(token, secret):
    h, p, s = token.split(".")
    expect = b64(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
    if s != expect:
        return "invalid"
    return json.loads(base64.urlsafe_b64decode(p + "=" * (-len(p) % 4)))
tok = mint({"sub": 42, "role": "admin"}, b"key")
print("parts", len(tok.split(".")), verify(tok, b"key"))
print("tamper", verify(tok[:-4] + "xxxx", b"key"))
# parts 3 {'sub': 42, 'role': 'admin'}
# tamper invalid
```

JWT cannot be revoked easily: fire someone at nine and the token still
opens doors until it expires; the payload is signed, not encrypted, so
anyone holding it can read the claims. Keep expiry short, secrets out of
the payload, and use a refresh token; use JWT for stateless auth across
microservices and as the access token OAuth providers hand back. A
throttled queue holds connections and delay can hide a struggling
service, so cap the queue and alert on delay; use it for expensive work,
shared infra, and bursts you would rather absorb than reject (Envoy,
Kong, message queues). Endpoint names drift (`/users` vs `/getUser`);
plural nouns, verb in the method. Request-response blocks: work that
takes two minutes leaves a spinner; accept, return 202, finish in the
background. Forgotten headers cause Content-Type bugs; proxies strip
them silently; set Content-Type every time. A hand-written OpenAPI file
drifts within weeks; generate it from code or test code against it
(public APIs, partner integrations; Swagger UI, Redoc, Stoplight). A
tight timeout kills healthy slow calls, then retries double load on a
service having a bad minute; measure the ninety-ninth percentile and set
the timeout above it. Microservices turn in-memory calls into network
calls that can time out, arrive twice, or vanish; a bug spans four
services and six log files; start with a monolith and split when the
pain is real. Primer: HTTP is a request/response protocol; a request is
a verb plus a resource (endpoint); REST identifies a resource by URI and
changes it with verbs, headers, and body; microservices are independently
deployable services that talk through a lightweight mechanism.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([API Design Concepts - Part 2](https://newsletter.systemdesign.one/p/api-concepts-for-software-engineers)
— Neo Kim, #185: concepts 18-33 JWT through error handling; public
teaser defines JWT through microservices; three-part token, no session
store, signed not encrypted, refresh token; throttle vs 429; endpoint
URL; send/wait/reply, 202; headers; OpenAPI contract; connect/read
timeout; microservices own data);
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Communication: HTTP request/response, verb plus resource/endpoint;
REST URI, verbs, headers, body; Application layer: microservices as
independently deployable services, lightweight mechanism).
