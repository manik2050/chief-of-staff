# Code review best practices

Learning evidence for Day 35 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

A code review is a second set of eyes on every change before it merges.
Neo Kim's letter (#100) lists 42 practices from "top 0.1% engineering
teams". The goal is code health, not a fast rubber stamp and not a
performance evaluation. Small PRs are easier to understand and create
fewer problems later. Keep reviews short: it is hard to stay focused
after reading 100+ lines; split a big change or review one section at a
time. Ask for a review only after tests and builds pass.

```
  small PR + what/why + CI green
     |
     v
+-----------+  tests, linters, static analysis
|    CI     |  fail -> do not ask for review
+-----------+
     | pass
     v
+-----------+  checklist: design, readability,
|  review   |  security, testing
|  100+ ln  |  must vs nit; out-of-scope logged
+-----------+  critical: at least two reviewers
     |
     v
  layers: design then details
```

The checklist (design, readability, security, testing) keeps reviews
consistent. Automate the easy parts so reviewers spend time on logic and
architecture. Label comments essential or optional so the author can
prioritize. Stay in scope; log outside issues separately. Pick code
owners or domain experts; if you assign many reviewers, each needs a
clear job or the PR stalls. Critical changes: at least two reviewers.
AI can summarize or flag issues; it does not replace a human. Rotate
reviewers so knowledge spreads and people do not burn out.

```python
# Toy triage. FOCUS=100 is the letter. Line numbers and PR sizes are
# invented. python3 - <<'PY' ... PY
FOCUS = 100  # letter: hard to stay focused after 100+ lines
CHECKLIST = {"design", "readability", "security", "testing"}

def triage(name, loc, comments):
    print(name, "loc", loc)
    for line, item, sev, in_scope in comments:
        if not in_scope:
            print(f"  L{line} {item} log-separately")
            continue
        if item not in CHECKLIST and sev == "nit":
            print(f"  L{line} {item} let-pass")
            continue
        focus = "focused" if line <= FOCUS else "unfocused"
        print(f"  L{line} {item} {sev} {focus}")

triage("small", 40, [
    (12, "design", "must", True),
    (18, "testing", "must", True),
    (22, "readability", "nit", True),
    (30, "style", "nit", True),
])
triage("big", 180, [
    (20, "security", "must", True),
    (150, "testing", "must", True),
    (160, "perf", "must", False),
])
# small loc 40
#   L12 design must focused
#   L18 testing must focused
#   L22 readability nit focused
#   L30 style let-pass
# big loc 180
#   L20 security must focused
#   L150 testing must unfocused
#   L160 perf log-separately
```

The small PR stays inside the 100-line focus window, so every checklist
item is still focused. A style nit that is not on the checklist is let
through (letter: correctness and clarity, not personal style). The
180-line PR leaves a testing must past line 100 as unfocused, and an
out-of-scope performance note is logged separately so the review does
not grow. Toy values except FOCUS=100. Measure review time, bug rates,
and PR size, then adjust; what works at one company may not at another.

When: review every change, even small ones, after CI is green. Get early
feedback on large features. Run complex or critical code locally. Do not
use reviews to score people. Do not send a broken build. Primer has no
code-review section; its Security basics (sanitize inputs, parameterized
queries, least privilege) are the class of issue the letter's security
checklist item is watching for.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([Code Review Best Practices](https://newsletter.systemdesign.one/p/code-review-best-practices)
— Neo Kim, The System Design Newsletter #100, 15 Nov 2025, "I Studied
How Top 0.1% Engineering Teams Do Code Reviews"; 42 practices; small
PRs; 100+ lines; checklist design/readability/security/testing; CI
before review; must vs nit; in-scope; two reviewers for critical; AI
helper not replacement; no performance evaluations);
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(no code-review section; Security: sanitize against XSS and SQL
injection; parameterized queries; least privilege).
