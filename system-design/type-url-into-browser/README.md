# What happens when you type a URL into your browser

Learning evidence for Day 18 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

The browser never talks to the name. It talks to an IP, then to a process
behind that IP. Pressing Enter starts five client-visible steps: DNS, TCP
handshake, TLS (HTTPS), HTTP request/response, then render. At internet
scale the address from DNS is not origin. A CDN, load balancer, or reverse
proxy is the public hop. The app then reads cache, and only a miss hits
the database. The response walks the same hops back.

```
  type https://www.example.com  + Enter
       |
       | 1 DNS: browser -> OS -> resolver; miss walks root -> TLD -> auth
       v
     IP of the public hop
       |
       | 2 TCP: SYN, SYN-ACK, ACK
       | 3 TLS: server cert, CA check, session keys (HTTPS, port 443)
       | 4 HTTP GET verb + path; headers; optional body
       v
+------------------+   static / edge hit    +--------+
| CDN / LB /       | ---------------------> | client |
| reverse proxy    |                        +--------+
+------------------+
       | miss / dynamic
       v
+------------------+   cache hit            +--------+
| application      | ---------------------> | client |
| (web, then app)  |                        +--------+
+------------------+
       | miss
       v
+------------------+
| database         |  then back: HTTP status + body, render HTML/CSS/JS
+------------------+
```

```
# one public address; work is behind it. unused hops drop out.
def fetch(url):
    ip = dns_resolve(url.host)       # TTL cache skip; else root, TLD, auth
    tcp_handshake(ip, port=443)      # SYN, SYN-ACK, ACK
    tls_session()                    # cert + CA; then encrypted
    req = http_get(url.path)         # self-contained; can pass LB/cache
    hop = public_front()             # CDN, load balancer, or reverse proxy
    if hop.can_serve(req):           # static, cached, or edge copy
        return hop.reply(req)
    app = hop.pick_backend(req)      # LB: one of many; RP: one is enough
    hit = app.cache.get(req)
    if hit is not None:
        return hit                   # skip the database
    row = app.db.read(req)
    app.cache.put(req, row)
    return row                       # HTTP response back the same path
```

DNS caches the mapping until TTL: a cutover waits. TLS encrypts the hop
so HTTP is not plaintext (academy: HTTPS on 443, HTTP on 80). A reverse
proxy is useful with one app — hide backends, terminate TLS, serve
static. A load balancer is for a pool of equivalent backends; one
balancer is a SPOF unless paired. A CDN is a nearby copy of static files
so origin never sees the hit. Cache-aside puts the app in charge of the
miss. Walk this path when the site is "down" or you are placing the
public face. Drop hops you do not need: no CDN for a personalized API
next to origin; no balancer for one healthy process.

Sources: [systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([What Happens When You Type a URL Into Your Browser?](https://systemdesign.one/what-happens-when-you-type-url-into-your-browser/)
— DNS cache then root/TLD/auth, TCP three-way handshake, HTTPS/TLS
upgrade, HTTP request/response, browser render; CDN, load balancer, and
reverse proxy as scale hops);
[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Domain name system; Content delivery network; Load balancer, including
SSL termination; Reverse proxy; Application layer; Cache; Database;
Communication: HTTP and TCP; Security: encrypt in transit).
