# API testing techniques

Learning evidence for Day 27 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

The academy's Part 1 article names 25 API test types; its public section
defines seven, sketched here (negative through authorization are named
there, not defined here). Smoke is the first CI gate: a health check, a
login, or a basic read; did the API respond at all? A pass is not
correctness; a fail stops everything else. Functional holds each endpoint
to its spec, happy and unhappy paths (missing fields, bad token, bad
payload). Unit isolates a handler, validator, or transformer with mocked
dependencies; fastest, but mocks do not always reflect reality.
Integration chains create/read/update/delete against realistic stores and
finds seam bugs. E2E walks a real user journey against real services.
Regression reruns existing tests on every merge. Acceptance asks whether
the API does what was promised. Primer has no API-testing chapter; closest
are HTTP health checks in service discovery and A/B testing as a DNS
routing method.

```
  new build / deployment
     |
     v
+---------+  fail -> stop everything else
|  smoke  |  pass -> it responded (not: it is correct)
+---------+
     |
     v
  unit, functional, integration     (logic, spec, seams)
  regression: every merge            E2E: critical journeys only
  acceptance: final sign-off before a feature ships
```

```python
# Toy in-process handler. python3 - <<'PY' ... PY
def valid_name(name):
    return isinstance(name, str) and 1 <= len(name) <= 8

def handle(method, path, body=None):
    if path == "/health":
        return 200, "ok"
    if method == "POST" and path == "/items":
        name = (body or {}).get("name")
        if not valid_name(name):
            return 400, "bad name"
        return 201, name
    return 404, "no route"

print("unit", valid_name("mug"), valid_name(""))
print("smoke", handle("GET", "/health")[0])
print("func", handle("POST", "/items", {"name": "mug"}))
print("func", handle("POST", "/items", {}))
# unit True False
# smoke 200
# func (201, 'mug')
# func (400, 'bad name')
```

Smoke is the cheapest guard and not a safety net. Functional tests become
a tax if they assert incidental details instead of what clients need.
Unit tests enable fearless refactoring but cannot find serialization or
auth propagation bugs; integration tests can, at the cost of time, infra,
and flake. E2E is the most realistic and the most expensive to maintain.
Run smoke first in every pipeline, unit on pure logic, a small integration
suite per workflow (heavier nightly), E2E only on critical journeys,
regression on every merge (block on failure), acceptance as sign-off.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([API Testing Types](https://newsletter.systemdesign.one/p/api-testing-types)
— smoke first in CI; functional spec; unit + mocks; integration seams;
E2E small; regression on merge; acceptance as sign-off);
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(no API testing types; HTTP health checks; DNS A/B testing as routing).
