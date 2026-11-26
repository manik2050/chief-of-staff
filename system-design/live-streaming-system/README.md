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
frequency but increase playback delay ([src]). Conventional HTTP-based live
streaming uses segment durations around 2 to 10 seconds ([src]). RTMP runs
over TCP, so packet loss could increase latency via head-of-line blocking
([src]). SRT runs over UDP with selective retransmission inside a configured
latency window ([src]). Cached CDN content could become stale; live segments
are typically immutable once published, so they cache well, while frequently
updated manifests need shorter cache durations ([src]). When bandwidth
increases, the player switches to a higher-bitrate rendition; when it
decreases, a lower one; when conditions stabilize, it stays ([src]).
Switches typically happen at segment boundaries ([src]).

Use this pipeline for live events with mixed devices and sharp concurrent
viewer spikes, and when 4 to 30 seconds of latency is the target ([src]).
Use RTMP or SRT to move video from the venue to processing, then HLS to
reach consumer players and CDNs ([src]). If ultra-low-latency playback
becomes a requirement, evaluate WebRTC or specialized low-latency protocols;
SRT is not a direct replacement for HLS across millions of consumer devices
([src]).

Sources: [System Design Interview: Design Live Streaming System][src]
(#200, 6 Nov 2026).

[src]: https://newsletter.systemdesign.one/p/live-streaming-system-design

## One-page note

What. Day 46 learning note: ingest, transcode/ABR ladder, HLS packaging,
CDN, and player. Toy ABR picker from bandwidth samples.

Why. 50 million viewers at 5 Mbps is 250 Tbps; a central origin cannot
efficiently serve that ([src]).

Tradeoffs. Shorter HLS segments could cut latency but raise request load
([src]). RTMP/TCP could add HOL delay; SRT/UDP retransmits inside a latency
window ([src]). CDN cache could go stale; published segments are typically
immutable, so manifests use shorter cache ([src]).

When. Live events with mixed devices and sharp spikes, at 4 to 30 seconds
of latency ([src]). RTMP/SRT for contribution; HLS for playback. Evaluate
WebRTC if ultra-low latency is required ([src]).

Cites. https://newsletter.systemdesign.one/p/live-streaming-system-design
