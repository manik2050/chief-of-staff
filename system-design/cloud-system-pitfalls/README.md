# Cloud system pitfalls

Learning evidence for Day 39 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Cloud computing gives managed services that improve reliability, but small
mistakes spread quickly: one incorrect setting, a missing tag policy, or a
bad scaling rule can affect many environments at once. Teams hit similar
problems because cloud platforms behave differently from on-premise systems.
Neo Kim and Magdalena walk through 15 pitfalls, each with the pattern, why it
happens, its impact, and how to prevent it. The goal: systems that adapt to
change instead of breaking under it, and stay reliable when things go wrong.

The causes repeat. Creating resources is easy but deleting them is manual,
so unattached disks, unused IPs, old snapshots, and forgotten proof-of-concept
VMs keep billing. Defaults and copy-pasted IaC templates ship wrong
autoscaling limits, public buckets, and missing encryption. Everything is
usage-based (data stored, moved, processed), which surprises teams who assumed
transfers were free. Lift-and-shift keeps fixed-size servers and network-only
security, while identity and permissions are now the real security boundary.
The sketch lists the 11 pitfalls in the public text with a first fix for each.

```
pitfall                          first fix in the letter
1  orphaned resources            tags (owner, purpose, expiry); auto cleanup
2  misconfigurations             version control; policy-as-code; drift checks
3  poor team communication       owners; ADRs; you build it, you run it
4  one tool for everything       choose by fit; APIs and modular pipelines
5  weak cloud mechanics          cost calculators, load tests, prototypes
6  rebuilding on-prem            modernize step by step; identity boundary
7  no tags, names, monitoring    governance as core architecture
8  network as main security      identity first; network extra; zero-trust
9  static designs                autoscaling with limits; IaC; canary; chaos
10 dev identical to prod         cheaper tiers; separate permissions, budgets
11 no cost visibility            cost owners; budgets; anomaly alerts
```

```python
# Toy units, not a measurement. python3 - <<'PY' ... PY
def run(load, low, high):
    n = min(max(load, low), high)          # machines, clamped to limits
    return n, max(0, load - n), max(0, n - load)  # machines, unserved, idle

for name, low, high in [("fixed 3", 3, 3), ("autoscale 1-8", 1, 8)]:
    print(f"{name}: peak {run(10, low, high)}, quiet {run(2, low, high)}")
# fixed 3: peak (3, 7, 0), quiet (3, 0, 1)
# autoscale 1-8: peak (8, 2, 0), quiet (2, 0, 0)
```

Each shortcut trades later pain for early speed. One tool means one interface
to learn, then hidden dependencies and large breakage if it fails.
Lift-and-shift is the fastest route, then pays for fixed-size servers.
Cloning prod into dev "to keep things consistent" pushed one company's dev
cost to almost half of production. A closed subnet did not stop a compromised
CI/CD credential from reaching data through APIs; the letter calls
identity-based attacks the most common breach type. Fixed clusters struggle
at peaks and waste money in quiet periods; the letter's fix is autoscaling
with limits. So: treat identity as the first layer and the network as an
extra one, give dev cheaper tiers and its own permissions, choose tools by
fit, treat governance as core architecture, and use cost calculators and
load tests early. The toy's load of 10 and limits of 3 and 1-8 are toy
numbers, not the letter's.

Sources: Neo Kim and Magdalena,
[A Systematic Breakdown of 15 Cloud Architecture Pitfalls](https://newsletter.systemdesign.one/p/cloud-system-design)
(System Design Newsletter #102, 23 Nov 2025; pitfalls 1-11 in the public
text; dev cost almost half of prod; identity-based attacks the most common
breach type; autoscaling with limits).
