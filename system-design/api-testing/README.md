# API testing techniques

Learning evidence for Day 27 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

The academy's Part 1 article lists 25 API test types. The public section
covers seven. The other names (negative through authorization) are listed
there, not defined here. Primer has no API-testing chapter. Closest: HTTP
health checks in service discovery, and A/B testing as a DNS routing method.

Smoke is the first CI gate: health, login, or a basic read — did the API
respond at all? A pass is not correctness; a fail stops the pipeline.
Functional checks the spec (status, body, missing fields, bad token, bad
payload). Unit isolates a handler, validator, or transformer with mocks:
fastest, and mocks can still lie. Integration chains create/read/update/
delete against realistic stores and finds seam bugs. E2E walks a real user
journey; keep it small. Regression reruns old tests on every merge.
Acceptance asks if the API does what the business promised; too coarse
for every commit.

```
  new build
     |
     v
+---------+  fail -> stop CI (responded? not: correct?)
|  smoke  |
+---------+
     |
     v
  unit -> functional -> integration
  then: regression on merge; E2E + acceptance on critical journeys
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

Smoke is cheap and not a safety net. Functional is the client-facing
contract; it becomes a tax if it asserts incidental details. Unit tests
let you refactor logic and miss serialization and auth propagation.
Integration and E2E catch those seams and cost time and flake. Use smoke
first in every pipeline, unit on pure logic, functional on the spec, a
small integration suite per workflow (heavier nightly), E2E only on
critical journeys, regression on every merge, acceptance as sign-off.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([API Testing Types](https://newsletter.systemdesign.one/p/api-testing-types)
— smoke first in CI; functional spec; unit + mocks; integration seams;
E2E small; regression on merge; acceptance as sign-off);
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(no API testing types; HTTP health checks; DNS A/B testing as routing).
