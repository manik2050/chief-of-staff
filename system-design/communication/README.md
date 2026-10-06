# Communication

Learning evidence for Day 9 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

HTTP is a request/response protocol: a client sends a verb and a resource,
the server returns a status and a body. It is an application-layer encoding
that can pass through hops that load-balance, cache, encrypt, or compress
because each message is self-contained. Under it sits a transport. TCP
opens a connection with a handshake, then delivers packets in order and
uncorrupted, retrying until it drops the connection. UDP sends a datagram
with no handshake and no delivery promise. RPC makes a remote procedure
look local; the call is still slower and less reliable than a local one.
REST exposes resources over HTTP verbs. That is how a call stops being
both a raw socket and an in-process function.

```
TCP (connection)                    UDP (datagram)
  client                              client
    |                                   |
    | SYN / SYN-ACK / ACK               | one datagram
    | then request, wait ACK            | no handshake
    v                                   v
+--------+                          +--------+
| server |  ordered, retried        | server |  may drop / reorder
+--------+                          +--------+
```

```
# same job: RPC names the procedure; REST names the resource
def rpc_add_item(person_id, item_id):
    return stub.addItemToUsersItemsList(person_id, item_id)

def rest_add_item(person_id, item_id):
    return http.post("/persons/%s/items" % person_id, {"itemid": item_id})
```

TCP when every byte must arrive (web servers, database info, SMTP, FTP,
SSH). UDP when late data is worse than loss (VoIP, video, realtime games)
or you need a broadcast before the peer has an IP (DHCP). REST for public
HTTP APIs: resources, stateless and cacheable, uniform verbs, weaker
coupling. RPC for internal calls you want to hand-craft; clients couple
to the procedure, and a new operation is a new API. Stay REST while the
data is a hierarchy of resources. Stay RPC when the job is a behavior
that does not map cleanly onto GET, POST, PUT, DELETE, or PATCH.

Sources: [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Communication: HTTP, TCP, UDP, RPC, REST);
[systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([What Happens When You Type a URL Into Your Browser?](https://systemdesign.one/what-happens-when-you-type-url-into-your-browser/),
[How Remote Procedure Call Works](https://newsletter.systemdesign.one/p/how-rpc-works)).
