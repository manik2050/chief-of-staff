# Troubleshoot website access

Learning evidence for Day 17 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

When one site fails, walk the request path instead of guessing. A name
has to become an IP before TCP can handshake and HTTP can return a
status. The academy's layers sit on that path: client, local network,
DNS, intermediate hops (CDN, reverse proxy), then the server.

```
  client --> DNS --> CDN / edge --> LB --> app --> origin (files / DB)
    |         |          |           |      |         |
  cache,    name->IP   hop in      pick   HTTP     data behind
  4xx,      miss /     path        a live 5xx      the app
  other     stale TTL  (VPN can    backend
  browser              reroute)
  other site
```

Client: stale cache or an extension; DevTools 4xx is the client, 5xx is
the server; try another browser or a popular site. Local net: can this
machine reach the internet, loopback, and the home router, or does
another network work. DNS: resolve the name (dig / nslookup); try
another resolver; flush a stale cache. Intermediate: ping the IP;
traceroute to name the hop. Server: HTTP 5xx, or origin is down.

```python
# Toy decision tree, not a packet capture. python3 - <<'PY' ... PY
def diagnose(obs):
    if obs.get("dns") == "miss":
        return "dns-miss"            # name never became an IP
    if obs.get("tcp") == "refused":
        return "tcp-refused"         # handshake never completed
    if obs.get("http") == "5xx":
        return "http-5xx"            # origin answered a server error
    return "ok"

print(diagnose({"dns": "miss"}))
print(diagnose({"dns": "ok", "tcp": "refused"}))
print(diagnose({"dns": "ok", "tcp": "ok", "http": "5xx"}))
print(diagnose({"dns": "ok", "tcp": "ok", "http": "ok"}))
# dns-miss
# tcp-refused
# http-5xx
# ok
```

Walk layers in order: a DNS miss never reaches TCP; a refused handshake
never reaches HTTP; a 5xx means the path opened and the origin failed.
Isolate with another network (local vs remote), another resolver (this
DNS vs the name), or a VPN (this hop vs another path). Flushing a cache
drops a stale mapping; waiting for TTL does the same without touching
the client. This diagnoses one site. It is not a capacity plan.

Adjacent, already boarded: dns (Day 6) and communication (Day 9).

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([How to Troubleshoot if You Can't Access a Particular Website?](https://systemdesign.one/how-to-troubleshoot-if-you-cannot-access-a-website/)
(layers: client, local network, DNS, intermediate hops, server;
4xx vs 5xx; dig / nslookup; traceroute; VPN reroute));
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Domain name system: name to IP, browser/OS cache and TTL;
Communication: HTTP request/response with status, flows through load
balancing; TCP handshake, timeouts drop the connection).
