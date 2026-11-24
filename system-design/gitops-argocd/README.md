# GitOps with ArgoCD

Learning evidence for Day 44 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Once a CI/CD deployment finishes, the pipeline has no idea what happens
inside the cluster afterward. Someone could edit a Deployment with
`kubectl`, apply a hotfix during an incident, or update a resource by
hand; those changes bypass Git and the pipeline. As they pile up, the
cluster drifts from Git until production no longer matches the last
reviewed configuration.

GitOps makes a Git repository the single source of truth: every
application or cluster change is a commit, reviewed and merged like
code, not applied directly to the cluster. An agent compares the live
cluster with the desired state in Git and reconciles differences. CI
still builds, tests, and publishes the image, then commits the new image
tag to the config repo. ArgoCD detects the change and diffs it with the
live resources; with automated sync it applies, with manual sync it
waits for an operator.

```
drift              kubectl / hotfix outside Git; live != last reviewed config
GitOps             Git is single source of truth; changes via reviewed commits
OpenGitOps (CNCF)  Declarative; Versioned and Immutable;
                   Pulled Automatically; Continuously Reconciled
1 Declarative      YAML/Helm/Kustomize: end state, not a how-to script
2 Versioned        desired-state change = Git commit; rollback = revert commit
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
# Toy reconcile loop; versions, ticks, policy switch are toy. python3 - <<'PY' ... PY
git, live = {"web": "v1"}, {"web": "v1"}  # desired (Git) vs live (cluster)

def reconcile(t, policy, note):
    want, have = git["web"], live["web"]
    if want == have:
        print(f"t={t} {policy}: {note}, Synced {have}")
    elif policy == "manual":
        print(f"t={t} {policy}: {note}, OutOfSync live={have} git={want}, waits")
    else:
        live["web"] = want  # sync policy corrects the diff
        print(f"t={t} {policy}: {note}, OutOfSync, applied {have} -> {want}")

reconcile(0, "manual", "start")
git["web"] = "v2"                  # CI commits new image tag to Git
reconcile(1, "manual", "CI commit")
reconcile(2, "auto", "CI commit")
live["web"] = "hotfix"             # kubectl edit outside Git
reconcile(3, "manual", "drift")
reconcile(4, "auto", "drift")
# t=0 manual: start, Synced v1
# t=1 manual: CI commit, OutOfSync live=v1 git=v2, waits
# t=2 auto: CI commit, OutOfSync, applied v1 -> v2
# t=3 manual: drift, OutOfSync live=hotfix git=v2, waits
# t=4 auto: drift, OutOfSync, applied hotfix -> v2
```

GitOps with ArgoCD makes Git the handoff: CI produces the image and
records the intended version; ArgoCD applies it. In push-based CD the
cluster credentials live inside CI, so a compromised pipeline is
effectively a compromised cluster, often with cluster-admin access. In
pull-based CD, ArgoCD runs in the cluster with scoped RBAC and no cluster
credentials leave it; a compromised CI could modify Git, but ArgoCD still
has to pull the change, and the commit is reviewable first. Redis is a
cache, not a primary store: if it goes down, performance suffers but
reconciliation continues. The Repo Server stays apart from the
Application Controller because rendering is often CPU-intensive and
occasionally unstable.

Sources: Neo Kim and Ayaan,
[GitOps Deep Dive: How ArgoCD Works](https://newsletter.systemdesign.one/p/how-argocd-works-gitops-kubernetes)
(System Design Newsletter #196: Part 5 - DevOps Mastermind, 26 Oct 2026;
paid letter: drift, GitOps principles, push vs pull CD, the security
boundary, and the five ArgoCD components are public; reconciliation
internals, sync policies, self-healing, hooks, ApplicationSets, and
production topics are paid and not covered).
