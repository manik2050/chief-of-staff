# Application layer

Learning evidence for Day 8 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

The application layer (also called the platform layer) sits behind the web
tier and runs the actual work. Split web from app so you can scale and
configure them independently: a new API can mean more app servers without
more web servers. Workers here also enable asynchronism. Microservices
take the split further — independently deployable processes, each serving
one business goal over a lightweight call. Service discovery (Consul,
etcd, ZooKeeper) tracks names, addresses, and ports so those processes
can find each other as instances move. Health checks, often an HTTP
endpoint, keep the list honest.

```
  clients
     |
     v
+-----------+                      +-----------+
| web layer | --- lookup "feed" -->|  registry |
|  servers  | <--- healthy addrs --+ Consul /  |
+-----------+                      | etcd / zk |
     |                             +-----------+
     |  HTTP to a live app               ^
     v                                   | register + /health
+-----------+   +-----------+       +-----------+
|  profile  |   |   feed    |       |  workers  |
+-----------+   +-----------+       +-----------+
```

```
# announce yourself; stay listed only while the health check passes
def register(name, addr):
    registry.put(name, addr)
    registry.probe(addr, path="/health")  # drop the row on a failed check

def call(name, path):
    live = [a for a in registry.get(name) if a.healthy]
    if not live:
        fail()
    return http.get(choose(live), path)   # hop; not an in-process call
```

Independent scale and deploys are the win. The cost is extra network hops,
a registry that is now a critical dependency, and failure modes a monolith
never had: a stale lookup can still send traffic to a dead instance, and
ops plus process have to change. Use the split when web and app grow at
different rates, or when instances come and go under autoscaling and
rolling deploys. Stay a monolith while one process still fits —
hard-coded addresses are cheaper until they actually move.

Sources: [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Application layer: web vs platform, microservices, service discovery,
health checks); [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([What Is Service Discovery?](https://systemdesign.one/what-is-service-discovery/),
[22 Microservices Design Patterns](https://newsletter.systemdesign.one/p/microservices-design-patterns)).
