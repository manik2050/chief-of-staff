# GitOps with ArgoCD

Learning evidence for Day 44 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

A finished pipeline typically does not watch the cluster afterward. A
manual `kubectl` change, a hotfix, or any apply outside Git can leave
production different from the last reviewed config. GitOps makes Git the
single source of truth: application and cluster changes go through
commits, reviewed like code, not applied by hand. An in-cluster agent
compares live state with Git and reconciles differences. CI still
typically builds, tests, and publishes an image; with ArgoCD it then
commits the new image tag to a config repo. ArgoCD detects the change,
diffs it with live, and either applies (automated sync) or waits
(manual). The letter is paid; only the public preview is cited.
Reconciliation internals, sync policies, self-healing, hooks,
ApplicationSets, secrets, access control, progressive delivery, and
disaster recovery are paid and not covered.

```
drift              kubectl / hotfix outside Git; live != last reviewed config
GitOps             Git is single source of truth; changes via reviewed commits
OpenGitOps (CNCF)  Declarative; Versioned and Immutable;
                   Pulled Automatically; Continuously Reconciled
1 Declarative      YAML/Helm/Kustomize: end state, not a how-to script
2 Versioned        desired-state change = Git commit; rollback can be a revert
3 Pulled auto      in-cluster agent pulls Git; pipeline does not apply
4 Reconciled       compare live vs Git; report or correct per sync policy
push CD            pipeline kubectl apply / helm upgrade; creds live in CI
ArgoCD CD          CI builds image, pushes registry, commits tag to config repo
                   ArgoCD diffs live; auto-sync applies, manual waits
push vs pull       push: CI holds cluster keys; pull: cluster holds them
API Server         user requests (UI, CLI); authn and authz
Repo Server        clone Git; render YAML, Helm, Kustomize, Jsonnet
App Controller     reconciles desired vs live; StatefulSet
Redis              cache, not a primary store; degrades without it
Notifications      Slack, email, PagerDuty, webhook
```

```python
# Toy reconcile loop; ticks and names are toy. python3 - <<'PY' ... PY
git, live = {"web": "v1"}, {"web": "v1"}  # desired Git; live cluster

def tick(t, policy):
    drift = {k: (git[k], live[k]) for k in git if git[k] != live[k]}
    if not drift:
        print(f"t={t} {policy} Synced")
        return
    k, (want, have) = next(iter(drift.items()))
    if policy == "manual":
        print(f"t={t} {policy} OutOfSync {k} live={have} git={want}")
        return
    live[k] = want  # automated sync; toy self-heal
    print(f"t={t} {policy} heal {k} {have} -> {want}")

tick(0, "manual")
live["web"] = "hotfix"  # kubectl-style drift
tick(1, "manual")       # report only
tick(2, "auto")         # corrects drift
# t=0 manual Synced
# t=1 manual OutOfSync web live=hotfix git=v1
# t=2 auto heal web hotfix -> v1
```

GitOps with ArgoCD fits when Git should be the handoff: CI records the
intended image; the cluster pulls and applies. Push-based CD can be
simpler, but cluster credentials typically live in CI, so a compromised
pipeline can often reach the cluster. Pull-based CD typically keeps those
credentials in-cluster; a compromised pipeline can still change Git, but
ArgoCD still has to pull, and the commit is reviewable first. Redis is a
cache: ArgoCD can typically keep reconciling without it, with worse
performance. Manual sync reports OutOfSync; automated sync can apply.

Sources: Neo Kim and Ayaan,
[GitOps Deep Dive: How ArgoCD Works](https://newsletter.systemdesign.one/p/how-argocd-works-gitops-kubernetes)
(System Design Newsletter #196, Part 5 - DevOps Mastermind, 26 Oct 2026;
paid letter, public preview only).
