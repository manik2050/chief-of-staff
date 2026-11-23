# Networking fundamentals

Learning evidence for Day 43 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

## What

Computer networking sits under every system you will work on. Juniors can
get by writing code; seniors are valued for how systems communicate and
for troubleshooting network problems.

When a connection fails, how does data travel between devices and
servers, and how do you diagnose slow links, packet loss, and routing?
Those questions sit under every reliable, high-performing system.

## Why

Frames and MAC addresses move traffic on a LAN. IP, default gateways,
static routes, and OSPF move it between networks. DHCP and static
addresses decide who holds an IP. ICMP and ping are how you ask whether
a path answers.

## Tradeoffs

2.4 GHz Wi-Fi reaches farther with less capacity and more interference;
5 GHz and 6 GHz are faster, shorter-range, and weaker through obstacles. A
weak client transmits slower and uses more airtime, cutting capacity for
everyone on the channel. A static IP stays put for DNS and firewalls;
DHCP assigns on join and reassigns after a lease expires. A static route
does not learn a new path and still points at a failed one unless
something deactivates it. OSPF recalculates after failures; convergence
depends on detection, topology size, and configuration. ICMP is not
guaranteed to arrive: firewalls and rate limits can drop it.

## When to use / when not

Use a static IP, or a DHCP reservation, for servers, printers, and
routers. Use DHCP for laptops and phones that join and leave. Use a
static route for a known path, including cloud route tables. Use OSPF
inside an autonomous system that must reroute on failure. Use a switch
on the same network and a router between networks. Use ping to test
whether a host answers ICMP and to measure round-trip time. Skip static
routes when paths change under you. A wrong default gateway breaks
off-net access while local still works. A ping reply is not proof an
application is up.

- Ethernet: LAN; wrap an IP packet in a frame with MACs; switch it; check the FCS.
- MAC addresses: 48-bit card id (six hex pairs); IP between nets, MAC within one; ARP then cache.
- Switches: learn source MAC to port; known dest there; unknown floods other VLAN ports.
- Wi-Fi: radio; CSMA/CA; 2.4 / 5 / 6 GHz; retransmit lost frames; poor signal uses airtime.
- Static IPs: fixed by hand or DHCP reservation; same across reboots while valid.
- DHCP: DORA (Discover, Offer, Request, Acknowledge); mask, gateway, DNS; renew or reassign.
- Default gateways: hop when no specific route exists; 192.168.1.10/24 uses 192.168.1.1.
- Static routes: dest range and next hop, e.g. 10.0.2.0/24 via 192.168.1.1; they do not auto-learn.
- OSPF: Hello, flood LSAs, shared link-state DB, Dijkstra lowest-cost paths; reroute on fail.
- ICMP: unreachable, TTL exceeded, packet too big, echo; does not retransmit application data.
- Ping: ICMP Echo Request and Reply; reports RTT and missing replies.

```python
# Toy DHCP lease pool, not a server. Ticks are toy. python3 - <<'PY' ... PY
pool, lease = ["addr-a", "addr-b"], {}

def expire(t):
    for host, (addr, until) in list(lease.items()):
        if t >= until:
            pool.append(addr)
            del lease[host]
            print(f"t={t} expire {host} {addr}")

def dora(host, t, life=2):
    expire(t)
    addr = pool.pop(0)
    until = t + life
    lease[host] = (addr, until)
    print(f"t={t} DORA {host} {addr} until {until}")

dora("laptop", 0)
dora("phone", 0)
dora("tablet", 2)
# t=0 DORA laptop addr-a until 2
# t=0 DORA phone addr-b until 2
# t=2 expire laptop addr-a
# t=2 expire phone addr-b
# t=2 DORA tablet addr-a until 4
```

Ticks and `addr-*` labels are toy. After expire, tablet gets `addr-a` — a
reassigned lease.

Sources: Neo Kim,
[11 Networking Concepts Explained in 11 Minutes](https://newsletter.systemdesign.one/p/computer-networking-fundamentals-for-software-engineers)
(#195, Part 2 - Break Into Computer Networking, 23 Oct 2026).
