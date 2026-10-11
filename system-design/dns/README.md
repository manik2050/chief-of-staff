# Domain Name System

Learning evidence for Day 6 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

DNS translates a domain name such as www.example.com to an IP address. The
client never talks to the name; it talks to an address. A recursive resolver
walks the hierarchy — root, TLD, then the zone's authoritative servers —
unless a cache still holds the answer for that record's TTL. That is how a
name stays the stable handle while the address behind it can move.

```
  stub (OS / browser)
       |
       | miss
       v
+------------------+   cache hit: return A/AAAA until TTL
| recursive        | -------------------------------------> reply
| resolver         |
+------------------+
       | cold cache: iterative referrals
       v
    root  -->  TLD (.com)  -->  authoritative (example.com)
                               NS, then A at the leaf
```

```
# cache the answer for the record's TTL; a miss walks root -> TLD -> auth
def resolve(name):
    hit = cache.get(name)
    if hit is not None and not expired(hit):
        return hit.ip                 # skip the hierarchy
    answer = recursive_lookup(name)   # root, then TLD, then authoritative
    cache.put(name, answer, ttl=answer.ttl)
    return answer.ip
```

The first hop of almost every request is this lookup. Caching and a TTL make
it cheap after the first miss; they also make a cutover wait until every
cache expires. A recursive resolver is a SPOF for the clients that only ask
it. The protocol is a DDoS surface: flood the resolver or the authoritative
servers and names stop resolving even when origin is up.

Use a plain A (or AAAA) when one name maps to one address, and a CNAME when
a name should follow another name. Use managed DNS with weighted, latency,
or geolocation policies when you need to split traffic, fail over, or steer
clients. A CNAME cannot sit at the zone apex.

Sources: [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Domain name system: hierarchy, TTL cache, A/CNAME, managed routing,
disadvantages);
[Wikipedia: Domain Name System](https://en.wikipedia.org/wiki/Domain_Name_System)
(hierarchical lookup, recursive vs authoritative, record caching);
[Amazon Route 53: routing policies](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html)
(simple, weighted, latency, geolocation);
[Amazon Route 53: alias vs CNAME](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resource-record-sets-choosing-alias-non-alias.html)
(no CNAME at the zone apex).
