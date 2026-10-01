# Content delivery networks

Learning evidence for Day 5 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

A CDN is a geographically distributed set of proxy servers. Clients fetch a
copy from a nearby edge, not from origin. Static files (HTML, CSS, JS,
images, video) are the usual payload; some CDNs also cache or pass through
dynamic responses. DNS steers the client to an edge. That is how a static
file stops being both a latency tax on a distant user and a bandwidth bill
on origin.

```
origin-only                         with CDN
  client                              client
    |                                   |
    | every request                     | nearest edge
    v                                   v
+--------+                          +--------+  hit
| origin |                          |  edge  | -----> reply
|  all   |                          | cache  |
+--------+                          +--------+
                                        | miss
                                        v
                                    +--------+
                                    | origin |  fill edge, then reply
                                    +--------+
```

```
# pull CDN: first request fills the edge; later hits skip origin
def get(path):
    edge = nearest_edge(client)
    copy = edge.get(path)
    if copy is not None and not expired(copy):
        return copy                  # hit: origin never sees it
    copy = origin.get(path)          # miss: one trip to origin
    edge.put(path, copy, ttl=copy.ttl)
    return copy
```

Push CDNs take uploads from you when origin changes: you rewrite URLs to the
CDN, origin traffic is low, CDN storage is high. Pull CDNs fetch from origin
on the first miss: storage is only for recently requested files, that first
request is slow, and a short TTL can re-pull unchanged files. Use a CDN when
users are far from origin or static assets dominate the payload. Skip it
when every response is personalized, the audience sits next to origin, or
you cannot tolerate a stale copy until TTL or purge.

Sources: [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Content delivery network: Push CDNs, Pull CDNs; CDN caching);
[MDN: CDN](https://developer.mozilla.org/en-US/docs/Glossary/CDN);
[MDN: HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)
(managed caches);
[Cloudflare: What is a CDN?](https://www.cloudflare.com/learning/cdn/what-is-a-cdn/);
[Cloudflare: origin server](https://www.cloudflare.com/learning/cdn/glossary/origin-server/);
[Amazon CloudFront](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html)
(edge hit vs origin fetch).
