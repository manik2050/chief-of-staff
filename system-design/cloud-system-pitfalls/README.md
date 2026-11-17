# Cloud system pitfalls

Learning evidence for Day 39 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Cloud computing gives managed services that improve reliability, but small
mistakes spread quickly: one incorrect setting, a missing tag policy, or a
bad scaling rule can affect many environments at once. Teams hit similar
problems because cloud platforms behave differently from on-premise systems.
Neo Kim and Magdalena walk through 15 pitfalls; the public text names the
first 11 below. Goal: systems that adapt to change instead of breaking
under it, and that stay reliable when things go wrong.

Creation is easy; deletion is usually manual, so unused disks, IPs,
snapshots, and forgotten PoC VMs keep billing. Defaults, copy-pasted IaC,
and fast releases ship wrong autoscaling limits, public buckets, and missing
encryption. Specialists drift. One all-in-one tool feels simple, then cannot
span accounts, hybrid setups, or new services. Usage-based store, move, and
process costs surprise teams who assumed transfers were free. Lift-and-shift
keeps fixed-size servers and network-only security. Missing tags, names, and
monitoring. Identity is the real boundary, not the subnet. Hardcoded clusters
miss peaks and waste quiet hours. Cloning prod into dev is not control.
Without cost ownership, spend is a mystery.

1. Orphaned resources — tags (owner, purpose, expiry); automate cleanup.
2. Misconfigurations — version-control and review; policy-as-code; drift checks.
3. Poor team communication — owners, ADRs, cross-team reviews; you build it,
   you run it.
4. One tool for everything — choose by fit; APIs and modular pipelines.
5. Weak cloud mechanics — cost calculators, load tests, prototypes; know SLAs.
6. Rebuilding on-prem in the cloud — modernize stepwise; cloud-native where
   it reduces effort; identity as the security boundary.
7. No tags, names, or monitoring — mandatory tags; governance as architecture.
8. Network as the main security layer — IAM first; network extra; zero-trust.
9. Static designs — autoscaling, serverless, event-driven; IaC; canary;
   chaos tests.
10. Dev identical to prod — cheaper non-prod; separate permissions, budgets,
    retention; synthetic data.
11. No cost visibility — cost owners; Cost Explorer / Cost Management /
    Billing Reports; budgets and anomaly alerts.

The remaining four of 15 sit behind the paid cutoff after #11.

```python
# Toy for pitfall 9 (and #2: wrong autoscaling limits). python3 - <<'PY' ... PY
def handle(load, min_n, max_n):
    n = min(max(load, min_n), max_n)     # desired machines, clamped
    return n, max(0, load - n)           # size, dropped

peak = 10
print("fixed 3", handle(peak, 3, 3))     # hardcoded / min=max
print("autoscale cap 8", handle(peak, 1, 8))
print("quiet autoscale", handle(2, 1, 8))
print("cap helps", handle(peak, 1, 8)[1] < handle(peak, 3, 3)[1])
# fixed 3 (3, 7)
# autoscale cap 8 (8, 2)
# quiet autoscale (2, 0)
# cap helps True
```

One interface is easier to learn, then becomes a hidden dependency and a
single point of failure. Lift-and-shift is the fastest migration and then
pays for fixed-size iron without elasticity. Cloning prod into dev "keeps
things consistent" and in the letter's example pushed development cost
toward half of production. A closed subnet does not stop an identity-based
attack, the most common breach type in the letter. Hardcoded clusters look
stable, then drop peak traffic and keep paying in quiet periods; autoscaling
with limits is the letter's fix. Speed without tags creates mystery spend.
Cloud hides infrastructure details; it does not remove usage-based cost.
Treat identity as the first layer and the network as extra. Do not make
dev look like prod. Adopt managed services where they reduce effort.
Design for elasticity. Choose tools by fit, not standardization. Treat
governance as core architecture. Use cost calculators and load tests early;
prototype before scaling up. This toy used load 10 vs a fixed 3 and an
autoscale cap of 8 (counts are from the toy, not the article).

Sources: Neo Kim and Magdalena,
[A Systematic Breakdown of 15 Cloud Architecture Pitfalls](https://newsletter.systemdesign.one/p/cloud-system-design)
(#102, 23 Nov 2025; public text: orphaned resources; misconfigurations;
poor communication; one-tool lock-in; weak cloud mechanics; lift-and-shift;
missing governance; network vs identity; static designs; dev cloned as
prod; no cost visibility; tags; policy-as-code; you-build-it-you-run-it;
zero-trust; autoscaling with limits; synthetic data; Cost Explorer).
