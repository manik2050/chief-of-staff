# LLM inference

Learning evidence for Day 47 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

You type a question into a chat product and hit Enter. A moment later tokens
start appearing. Behind that, an inference system is already working. It
has three hard problems: generate tokens quickly when each step needs a huge
model; serve many users without running out of GPU memory and capacity; make
responses fast without wasting expensive hardware ([src]). Training learns
weights; once deployed those weights are typically fixed. Inference uses
them to produce a response and does not retrain on the prompt ([src]).

The request cannot stay English. Tokenization splits text into tokens —
sometimes a whole word, sometimes part of one — and maps each to a vocabulary
id; API pricing, context windows, and generation speed are typically measured
in tokens ([src]). Prefill processes the prompt in parallel, fills a KV
cache, and yields the first output token. Decode then generates one token at
a time, reusing that cache. Streaming can send pieces while generation
continues ([src]). Batching, memory management, and distributed serving are
named as the rest of the path; the public letter stops before those details.

```
text -> tokenize -> prefill (parallel; KV cache; first token / TTFT)
     -> decode (autoregressive; reuse KV; append newest token)
     -> stream (SSE or WebSocket; optional chunk buffering)

tokenize     BPE or SentencePiece; exact split depends on the tokenizer
context      max tokens at once; prompt plus history, tools, output limits
prefill      stacked layers; causal attention; keys and values into KV cache
decode       sequential; compute KV only for the newest token; logits; stop
stream       does not make decode faster; changes when tokens reach the user
batch/mem    named for many users on shared GPUs; internals paid, not covered
```

```python
# Toy KV work; prompt and decode lengths are toy. python3 - <<'PY' ... PY
prompt = 6  # toy prompt tokens, not a real tokenizer split
steps = 4   # toy decode tokens
naive = prompt
cached = prompt
for t in range(steps):
    naive += prompt + t + 1  # recompute every previous token plus the new one
    cached += 1              # reuse KV cache; compute only the newest token
print("naive", naive)
print("cached", cached)
print("saved", naive - cached)
# naive 40
# cached 10
# saved 30
```

During prefill every prompt token already exists, so the GPU could process
positions in parallel; ordinary autoregressive decode waits for the previous
token, so it stays sequential ([src]). The KV cache avoids recomputing key
and value projections for earlier tokens at every generation step ([src]).
Streaming is a second tradeoff: smaller, more frequent chunks feel smoother;
grouping more tokens into each chunk cuts send overhead ([src]). SSE keeps a
one-way HTTP connection open; WebSockets allow both sides to send, which
could matter for a voice assistant ([src]). A larger context window increases
compute and memory; the model also could retrieve middle-of-prompt
information less well than the beginning or end ([src]). Moving a large
model's weights through GPU memory on each decode step could become a major
bottleneck ([src]).

Sources: Neo Kim,
[How LLM Inference Works][src]
(System Design Newsletter #199, 3 Nov 2026; paid letter: training vs
inference, tokenization, context window, prefill, decode, KV cache at a
high level, TTFT, streaming via SSE/WebSockets, and chunk buffering are
public; closer KV-cache internals, batching, memory management, distributed
serving, and the promised real-world architecture, scale, reliability, and
performance deep dives are paid and not covered).

[src]: https://newsletter.systemdesign.one/p/how-llm-inference-works
