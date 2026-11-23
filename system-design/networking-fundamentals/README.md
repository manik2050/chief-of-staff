# Networking fundamentals

Learning evidence for Day 43 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Computer networking is part of every system an engineer works on. Junior
developers may get by writing code; senior engineers are valued for
understanding how systems communicate and for troubleshooting network
problems: what happens when a connection fails, how data travels between
devices and servers, and how to diagnose slow links, packet loss, and
routing problems.

Inside one local network, Ethernet frames carry IP packets between MAC
addresses, switches forward them by MAC, and Wi-Fi shares one radio
channel. A device gets its IP address by hand or a DHCP reservation
(static) or by leasing one through DHCP. Traffic leaves the network
through a default gateway, follows static routes or routes OSPF works out,
and ICMP and ping report when a path does not answer.

```
1  Ethernet          IP packet in a frame; src/dst MAC; switched; FCS check
2  MAC address       48-bit card id; MAC within a network, IP between; ARP
3  switch            learn src MAC -> port; known dst: that port; else flood
4  Wi-Fi             radio; CSMA/CA; 2.4 / 5 / 6 GHz; lost frames resent
5  static IP         fixed by hand or DHCP reservation; servers, printers
6  DHCP              Discover, Offer, Request, Acknowledge; leased address
7  default gateway   router for off-network traffic with no specific route
8  static route      dest range + next hop; does not learn new paths
9  OSPF              Hello, flood LSAs, link-state DB, Dijkstra; reroutes
10 ICMP              unreachable, TTL exceeded, too big, echo; may be dropped
11 ping              Echo Request / Reply; RTT and share of missing replies
```

```python
# Toy DHCP lease pool, not a server; ticks are toy. python3 - <<'PY' ... PY
pool, lease = ["addr-a", "addr-b"], {}  # free addrs; host -> (addr, until)

def tick(t):  # free each lease that reached its end without a renewal
    for host, (addr, until) in list(lease.items()):
        if t >= until:
            del lease[host]
            pool.append(addr)
            print(f"t={t} expire {host} {addr}, no renewal")

def join(host, t, life=2):  # one line for the whole DORA exchange
    addr = pool.pop(0)
    lease[host] = (addr, t + life)
    print(f"t={t} DORA {host} {addr} until {t + life}")

def renew(host, t, life=2):  # before expiry: same address, later end
    addr, _ = lease[host]
    lease[host] = (addr, t + life)
    print(f"t={t} renew {host} {addr} until {t + life}")

join("laptop", 0)
join("phone", 0)
tick(1)
renew("phone", 1)
tick(2)
join("tablet", 2)
# t=0 DORA laptop addr-a until 2
# t=0 DORA phone addr-b until 2
# t=1 renew phone addr-b until 3
# t=2 expire laptop addr-a, no renewal
# t=2 DORA tablet addr-a until 4
```

Give servers, printers, and routers a static IP or a DHCP reservation so
DNS records and firewall rules can point at them; let laptops and phones
lease through DHCP; devices typically renew before expiry, and a lapsed
lease's address can go to the next device. 2.4 GHz typically reaches
farther with less capacity and more interference; 5 and 6 GHz potentially
run faster over shorter range. A wrong default gateway breaks off-network
traffic while local traffic still works. A static route stays put even
when its path fails, unless something deactivates it; OSPF recalculates,
and how fast depends on failure detection, topology size, and
configuration. ICMP can be blocked or dropped, and a ping reply does not
prove the application on that host is up.

Sources: Neo Kim,
[11 Networking Concepts Explained in 11 Minutes](https://newsletter.systemdesign.one/p/computer-networking-fundamentals-for-software-engineers)
(System Design Newsletter #195, Part 2 - Break Into Computer Networking,
23 Oct 2026).
