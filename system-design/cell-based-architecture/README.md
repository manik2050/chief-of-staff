# Cell-based architecture

Learning evidence for Day 32 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

A cell is a self-contained instance of the application — services, load
balancers, and databases — independently deployable and observable. A
thin cell router sends each request to one cell. Cells share no state,
so one cell's failure stays inside that cell (Neo Kim / System Design).
The article's blast-radius example: 10 cells serving 100 requests; one
cell down affects about 10% of requests — only the customers placed
there.

```
  customers
     |
     v
+----------------+  partition key = Customer ID
|  cell router   |  keep thin (DNS, or gateway + mapping)
|  hash / range  |
+----------------+
   |     |     |
   v     v     x cell-2 down
 cell-0 cell-1 cell-2 ... cell-9
 each: app + LB + DB, own state, own subset of traffic
```

```python
# Toy router, not a platform. python3 - <<'PY' ... PY
N_CELLS = 10

def cell_of(customer_id):
    return customer_id % N_CELLS  # partition key: Customer ID

cells = {i: [] for i in range(N_CELLS)}
for cid in range(100):
    cells[cell_of(cid)].append(cid)

down = 2
ok = sum(len(v) for i, v in cells.items() if i != down)
print("cell sizes", [len(cells[i]) for i in range(N_CELLS)])
print("down cell", down, "affected", len(cells[down]), "of", 100)
print("others still served", ok)
# cell sizes [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
# down cell 2 affected 10 of 100
# others still served 90
```

Customer placement maps a partition key onto a cell; Customer ID is
the usual key. The router stays thin and horizontally scalable so it
does not become the failure. Each cell has a fixed maximum size so
scale-out is add-a-cell, not grow-without-limit, and stress tests stay
repeatable. Deploy in waves: one cell first, watch metrics, roll back
or continue. A cell can be a monolith, microservices, or serverless
inside a bounded context — a copy of that environment, not a
replacement for microservices. Slack, DoorDash, and Amazon run it
(article names them; no metrics invented here). Cost and complexity
rise because of infrastructure redundancy; use it when the blast radius
matters.

When: high availability, systems too big to fail, low RTO, many test
combinations with insufficient coverage, poison-pill containment,
buggy-deploy isolation. Anti-patterns the article names: unbounded
cell growth, deploy to every cell at once, shared state, complex
routing logic, chatty cells. Keep dependencies between cells to a
minimum; no shared databases.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([How 0.1% Companies Do Hyperscaling](https://newsletter.systemdesign.one/p/cell-based-architecture)
— Neo Kim / System Design; academy C technologies, first C item after
Bloom Filter: cells + thin router; self-contained instance; no shared
state; 10 cells / 100 requests → ~10% blast radius; Customer ID
partition key; fixed max cell size; wave deploys; not a microservices
replacement; Slack / DoorDash / Amazon named);
[AWS Well-Architected](https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/reducing-scope-of-impact-with-cell-based-architecture.html)
(Reducing the Scope of Impact with Cell-Based Architecture; optional
cross-check: bulkheads / fault isolation at workload scale);
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(no cell-based architecture section).
