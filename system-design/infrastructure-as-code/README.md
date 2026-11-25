# Infrastructure as Code

Learning evidence for Day 45 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Infrastructure as Code creates and manages networks, servers, and access
rules through configuration files instead of console clicks. The files stay
in Git, so a change starts as a pull request, Git keeps the history, and the
same files help recreate another environment with different values. An
imperative script lists how: create the network, save its ID, create the
subnet, launch the server. Run it again and it needs extra checks to avoid
duplicates and to handle steps that succeed while others fail. A
declarative tool such as Terraform describes the desired final state.

Terraform reads all `.tf` files in the working directory as one HCL
configuration; file layout does not control creation order. Core evaluates
variables and expressions, loads existing state, follows references to
build a dependency graph, and plans which objects to create, update,
replace, or remove. Provider plugins handle platform-specific operations.
State maps each resource address to its real object. Terraform only checks
infrastructure when you run a command and does not automatically detect
and fix every change made outside its configuration. By default state is a
local file; shared runs use a remote backend, and some backends lock state.

```
IaC            files in Git; PR before cloud; describes what should exist
imperative     ordered how-to; re-run needs duplicate and failure checks
declarative    desired final state; tool works out order and changes
Terraform      HCL; same workflow across platforms; providers do APIs
.tf files      one dir = one config; layout is not execution order
resource       managed object (VM, DNS); data source reads, does not own
provider       separate process over gRPC; create, read, update, delete
module         grouped resources so the same setup is not repeated
meta           count/for_each: many instances; depends_on: hidden edges
config         what should exist; live checked only when a command runs
state          address -> real ID, attributes, outputs
Core           eval, load state, graph, plan; apply records state
backend        local default; remote for shared runs; some lock state
implicit dep   subnet uses vpc.id => create the VPC first
graph          independents can run in parallel; destroy reverses; cycle errors
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

Most ordering comes from references: a subnet that uses `aws_vpc.main.id`
waits for the VPC even when it sits in another file, while independent
resources could be created in parallel. Use `depends_on` only for a
dependency no reference shows, such as an IAM policy attachment an
instance needs; unnecessary edges can leave resources waiting even when
Terraform could create them in parallel. Local state works for learning or
a small project alone. When many engineers or CI/CD pipelines share
infrastructure, a remote backend gives them one state file, and supported
backends lock it so only one run modifies it at a time. State can hold
sensitive values, so restrict access to it and keep it out of Git;
`.terraform.lock.hcl` records provider versions and checksums and normally
belongs in Git. Removing a resource block does not immediately delete the
cloud object; the leftover state entry tells the next plan what to delete.
The written definition does not stop a console edit or an approved bad
setting, but it gives a clear reference to compare against.

Sources: Neo Kim and Ayaan,
[Infrastructure as Code - A Deep Dive](https://newsletter.systemdesign.one/p/how-terraform-works-internally)
(System Design Newsletter #202: Part 6 - DevOps Mastermind, 12 Nov 2026).
