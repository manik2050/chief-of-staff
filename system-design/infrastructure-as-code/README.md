# Infrastructure as Code

Learning evidence for Day 45 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Infrastructure as Code manages networks, servers, and access rules through
configuration files in Git instead of console clicks. A change starts as a
pull request; Git keeps history; the same files recreate another environment
with different values. An imperative script lists how: create the network,
save its ID, create the subnet, launch the server; run it again and it needs
checks to skip duplicates and to handle partial failure. A declarative tool
such as Terraform describes the desired end state in HCL. Core reads every
`.tf` file in the working directory as one configuration (file layout does
not set order), follows references to build a dependency graph, diffs that
desired state against recorded state and the live platform, and plans which
objects to create, update, or remove. Providers perform platform operations.
State maps a resource address to the real object; Terraform inspects live
infrastructure only when you run a command, so a console edit is not
auto-fixed. Shared runs store state in a remote backend with locking.

```
IaC            files in Git; PR before cloud; describes what should exist
imperative     ordered how-to; re-run needs duplicate and failure checks
declarative    desired end state; tool diffs and orders the work
Terraform      HCL; one workflow across clouds; providers do platform APIs
.tf files      one dir = one config; layout is not execution order
resource       owned object (VM, DNS); data source reads without owning
provider       gRPC plugin; create, read, update, delete
module         grouped resources so the same setup is not copied
meta           count/for_each: many instances; depends_on: hidden edges
config         what should exist; live checked only when a command runs
state          address -> real ID, attributes, outputs
Core           eval, load state, graph, plan; apply records state
backend        local default; remote + lock for shared runs; state not in Git
implicit dep   subnet uses vpc.id => create the VPC first
graph          independents together; destroy reverses; cycle is an error
```

```python
# Toy plan/apply graph; names and ids are toy. python3 - <<'PY' ... PY
deps = {"dns": set(), "vpc": set(), "subnet": {"vpc"}, "server": {"subnet"}}
ids = {"dns": "dns-1", "vpc": "vpc-1", "subnet": "sub-1", "server": "srv-1"}
want, state = set(deps), {}

def waves(names, reverse=False):
    left, out = set(names), []
    while left:
        ready = sorted(n for n in left if not (
            {c for c in left if n in deps[c]} if reverse else deps[n] & left))
        if not ready:
            print("cycle"); return []
        out.append(ready)
        left -= set(ready)
    return out

def run():
    create = sorted(n for n in want if n not in state)
    delete = sorted(n for n in state if n not in want)
    print("plan create", " ".join(create) or "-", "delete", " ".join(delete) or "-")
    for w in waves(create):
        print("apply create", " ".join(w))
        for n in w: state[n] = ids[n]
    for w in waves(delete, reverse=True):
        print("apply delete", " ".join(w))
        for n in w: del state[n]

run()
run()
want.remove("server")
run()
print("state", " ".join(f"{k}={state[k]}" for k in sorted(state)))
# plan create dns server subnet vpc delete -
# apply create dns vpc
# apply create subnet
# apply create server
# plan create - delete -
# plan create - delete server
# apply delete server
# state dns=dns-1 subnet=sub-1 vpc=vpc-1
```

Use IaC when a second environment must match the first and a console click
is too easy to miss in review. Prefer declarative Terraform when the same
graph spans networks, databases, and DNS on more than one platform: Core
orders by references, so a server that uses a subnet in another file still
waits, and independent resources proceed together. Reach for `depends_on`
only when no value is referenced; extra edges make resources wait even
when they could run in parallel. Local state is enough for one person
learning; shared engineers or pipelines need a remote backend and locking
so two applies do not write the same records. Restrict who can read state,
encrypt it, and never commit it; `.terraform.lock.hcl` records provider
versions and does belong in Git. Removing a resource block does not delete
the cloud object until a later plan uses the leftover state entry. A
written definition is a comparison, not a guard: someone can still click
in the console or merge a bad setting.

Sources: Neo Kim and Ayaan,
[Infrastructure as Code - A Deep Dive](https://newsletter.systemdesign.one/p/how-terraform-works-internally)
(System Design Newsletter #202: Part 6 - DevOps Mastermind, 12 Nov 2026).
