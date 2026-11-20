# Microservices interview questions

Learning evidence for Day 42 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Microservices split one application into small services, each running in
its own process and deployed independently. They solve coordination: a
group ships its service without waiting for a shared release. They also
let a busy service get more instances while the rest stay small. They
create network problems (a call can be slow, fail, or arrive twice) and
data problems (no single database transaction spans services, so sagas
or eventual consistency). They need service discovery, tracing, and
automated deployment before the first service goes live. Skip them for a
small product with a handful of engineers.

```
1  microservices       independently deployed processes; talk over APIs
2  API gateway         one entry: token, rate limit, validate, route, merge
3  service discovery   client queries the registry; or a router does
4  database per service own store; others use the API or events, not tables
5  saga                local commits; compensating undo if a later step fails
6  circuit breaker     closed / open / half-open; fail-fast; not a retry
7  monolith            one deployable; start here with five engineers
8  sidecar / mesh      proxy per service: encryption, retries, timeouts, metrics
9  observability       logs, metrics, traces joined by a shared trace ID
10 SOA                 large shared services + ESB; microservices own data
11 bounded context     split where words change meaning, not by layer
12 rate limiting       per user/key; shared counter; over -> HTTP 429
13 REST                resources + HTTP methods; POST needs idempotency key
```

```python
# Toy circuit breaker in call counts, not a measurement. python3 - <<'PY' ... PY
trip, cool = 2, 2  # toy consecutive fails; toy fail-fasts before a test
fails, cooled, state = 0, 0, "closed"
hits = iter([True, False, False, False, True, True])  # payment, only if called
for n in range(1, 9):
    if state == "open":
        cooled += 1
        if cooled < cool:
            print(n, "open fail-fast")
            continue
        state = "half-open"
    shown = state
    ok = next(hits)
    if ok:
        state, fails, cooled = "closed", 0, 0
        print(n, shown, "ok")
    else:
        fails += 1
        if shown == "half-open" or fails >= trip:
            state, fails, cooled = "open", 0, 0
        print(n, shown, "fail")
# 1 closed ok
# 2 closed fail
# 3 closed fail
# 4 open fail-fast
# 5 half-open fail
# 6 open fail-fast
# 7 half-open ok
# 8 closed ok
```

A handful of engineers on a product that will still change shape should
keep one codebase, one pipeline, and one deploy, with clean module
boundaries. Split along business capabilities; if two services always
deploy together or call each other on every request, they belong in one
service. Put a gateway at the edge. Pair a breaker with a timeout and a
fallback; on its own it only turns slow errors into fast ones. A mesh
pays off with many services in many languages; at five services a
library covers retries and timeouts. Match the architecture to the size
of the group and the product. The toy's 2 and 2 are toy numbers, not
the letter's.

Sources: Neo Kim,
[Top 13 Microservices Interview Questions Answered](https://newsletter.systemdesign.one/p/microservices-interview-questions)
(System Design Newsletter #205, 20 Nov 2026).
