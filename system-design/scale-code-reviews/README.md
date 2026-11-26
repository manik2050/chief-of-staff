# Scale code reviews

Learning evidence for Day 34 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

A code review is someone other than the author reading the change before
it merges. The letter's startup skipped that until quality and bugs got
worse; adding reviews then hurt velocity (nitpicks, time zones), started
preference fights, and overloaded reviewers who still missed bugs in large
PRs. Scale with guidelines plus PR -> CI -> review -> update -> deploy.

Author: follow the style guide; keep the change small; self-review first;
reuse existing patterns when style is unspecified; tag the fewest
reviewers; write a clear message; settle design with facts, not opinions.
Reviewer: respond within 24 hours; reserve at least one calendar slot a
day; stay polite and constructive; use a documented checklist; talk
disagreements through, then write the decision down; share docs in
comments; approve when it is good enough and let minor issues land later.
Reviews are progress, not perfection: each change should keep or improve
codebase health.

```
  branch + self-review + few reviewers + clear message
     |
     v
+-----------+  lint, tests, static analysis, security scans
|    CI     |  fail -> author fixes
+-----------+
     | pass   so reviewers can focus on high-level feedback
     v
+-----------+  first response within 24 hours
|  review   |  checklist; good-enough approve
+-----------+
     |
     v
  same PR, CI again -> one approval -> merge -> CD
```

GitHub and GitLab give inline comments, approvals, and automated checks;
Gerrit is named for advanced workflows. Automation (editor extensions,
suggested fixes, summaries) helps; CI checks catch style, smells, and
vulns so the reviewer spends the slot on high-level feedback. Humans
still approve.

```python
# Toy queue. SLOT, RATE, sizes are invented — not letter claims.
# DEADLINE=24 is the letter. python3 - <<'PY' ... PY
DEADLINE_H, SLOT_H, RATE = 24, 1.0, 200  # toy slot + lines/hour

def run(label, prs):
    used = 0.0
    print(label)
    for name, loc, ci, self in prs:
        if not ci:
            print(f"  {name:6} blocked-ci")  # lint/tests/static/scans
            continue
        if not self:
            print(f"  {name:6} blocked-self")
            continue
        first = (used / SLOT_H) * 24
        used += loc / RATE
        flag = "within-24h" if first <= DEADLINE_H else "missed-24h"
        print(f"  {name:6} loc={loc} first={first:.0f}h {flag}")

run("small-prs", [("a", 100, True, True), ("b", 100, True, True),
                  ("c", 100, True, True)])
run("one-big", [("lint", 40, False, True), ("big", 800, True, True),
                ("d", 100, True, True)])
# small-prs
#   a      loc=100 first=0h within-24h
#   b      loc=100 first=12h within-24h
#   c      loc=100 first=24h within-24h
# one-big
#   lint   blocked-ci
#   big    loc=800 first=0h within-24h
#   d      loc=100 first=96h missed-24h
```

Small PRs share one daily slot and still get a first look within 24 hours.
CI failure never queues. One large PR fills several days of slots, so the
PR behind it misses the deadline — a toy queue effect of "keep the changes
small", not a measurement from the post.

Sources: Neo Kim,
[How to Do Code Review](https://newsletter.systemdesign.one/p/how-to-do-code-review)
(The System Design Newsletter #78, 25 Jul 2025, "How Great Software
Engineers Do Code Reviews"; "How to Scale Code Reviews" is the page H1
and academy title for this URL; author and reviewer guidelines;
24-hour response; daily calendar slot; PR -> CI -> review -> update ->
deploy; lint, tests, static analysis, security scans; GitHub, GitLab,
Gerrit; automation complements humans).
