# Live streaming system

Learning evidence for Day 46 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

A live streaming platform must capture a high-quality video feed, process
it in near real time, and deliver it to millions of viewers across phones,
laptops, and TVs ([src]). Traffic could surge within seconds when a match
starts or a key moment occurs ([src]). Every stage adds latency, and every
bottleneck puts the stream at risk ([src]). This note follows a design for
50 million concurrent viewers ([src]).

Viewers can watch live matches, and video must be streamed based on device
type and network bandwidth ([src]). End-to-end latency is targeted at 4 to
30 seconds ([src]). Traffic could rise or fall sharply during a live event
([src]). At 50 million viewers and a 5 Mbps average bitrate, outgoing
bandwidth is 250 Tbps, so a central server cannot efficiently deliver the
stream ([src]). The architecture uses video compression, adaptive bitrate
streaming, and a CDN ([src]).

```
ingest -> transcode/ABR ladder -> packaging/HLS segments -> CDN -> player

ingest      camera, PCR encoder (H.264/H.265), RTMP/SRT on a dedicated link
transcode   many resolutions and bitrates (the ABR ladder)
packaging   HLS segments (typically 2 to 4 s) and .m3u8 playlists
CDN         edge cache; origin fill on miss
player      master playlist -> pick a rung -> media playlist -> segments
```

```python
# Toy ABR picker; rung names from the letter; ranks are toy. python3 - <<'PY' ... PY
ladder = (("480p", 1), ("720p", 2), ("1080p", 3))
samples = (1, 2, 3, 3, 2, 1)  # toy bandwidth ranks, not Mbps
prev_i = None
for bw in samples:
    i = max(k for k, (_, need) in enumerate(ladder) if need <= bw)
    name = ladder[i][0]
    if prev_i is None:
        move = "start"
    elif i > prev_i:
        move = "up"
    elif i < prev_i:
        move = "down"
    else:
        move = "hold"
    print(f"{move} bw={bw} {name}")
    prev_i = i
# start bw=1 480p
# up bw=2 720p
# up bw=3 1080p
# hold bw=3 1080p
# down bw=2 720p
# down bw=1 480p
```

HLS divides encoded video into segments; shorter segments could reduce
latency but increase request overhead, while longer segments reduce request
frequency but increase playback delay ([src]). For conventional HTTP-based
live streaming, segment durations range from around 2 to 10 seconds,
depending on the configuration ([src]). RTMP runs over TCP, so packet loss
could increase latency through head-of-line blocking; SRT runs over UDP and
attempts to recover lost packets within a configured latency window
([src]). The design can use RTMP/SRT from the venue to processing, then HLS
to reach viewers; if ultra-low-latency playback becomes a requirement,
WebRTC or specialized low-latency delivery protocols should be evaluated,
since SRT is not a direct replacement for HLS across millions of consumer
devices ([src]). Cached CDN content could become stale; live segments are
typically immutable once published, so they suit caching, while frequently
updated manifests require shorter cache durations ([src]). When bandwidth
increases, the player switches to a higher-bitrate rendition; when it
decreases, a lower one; when conditions stabilize, it continues at a
suitable quality level. Switches typically happen at segment boundaries
([src]).

Sources: Neo Kim and Mandeep Singh Shekhawat,
[System Design Interview: Design Live Streaming System][src]
(System Design Newsletter #200, 6 Nov 2026).

[src]: https://newsletter.systemdesign.one/p/live-streaming-system-design
