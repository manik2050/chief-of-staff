# LLM inference

Learning evidence for Day 47 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

You type a question into a chat product and hit Enter. A moment later the
answer starts appearing. Behind that, an inference system is already
working. It has three hard problems: generate tokens quickly when each step
needs a huge model; serve many users without running out of GPU memory and
capacity; make responses fast without wasting expensive hardware ([src]).
Training learns weights; once deployed those weights are typically fixed.
Inference uses them to produce a response and does not retrain on the
prompt ([src]).

The request cannot be handed to the model as English text. Tokenization
splits text into tokens (sometimes a whole word, sometimes part of one) and
maps each to a vocabulary id. API pricing is typically measured in tokens,
context windows are measured in tokens, and generation speed in tokens per
second ([src]). Prefill processes the prompt, fills a KV cache, and leads to
the first output token. Decode then generates one token at a time, reusing
that cache. Streaming lets the server send pieces while generation
continues ([src]). For one request this is manageable; a production service
repeats it for many users whose requests compete for the same hardware
([src]).

```
text -> tokenize -> prefill (parallel; KV cache; first token / TTFT)
     -> decode (autoregressive; reuse KV; append newest token)
     -> stream (SSE or WebSocket; optional chunk buffering)

tokenize     e.g. BPE, SentencePiece; exact split depends on the tokenizer
context      max tokens at once; prompt, history, tools; output limits vary
prefill      stacked layers; normally causal attention; keys, values to KV cache
decode       sequential; compute KV only for the newest token; logits; stop
stream       does not make decode faster; changes when tokens reach the user
many users   requests compete for the same hardware
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
print("no cache, toy KV computes", naive)
print("KV cache, toy KV computes", cached)
print("toy KV computes saved", naive - cached)
# no cache, toy KV computes 40
# KV cache, toy KV computes 10
# toy KV computes saved 30
```

During prefill every prompt token already exists, so the GPU can process
work across prompt positions in parallel; in ordinary autoregressive decode
the next token does not exist until the previous one is selected, so it
stays sequential ([src]). The KV cache means the model does not recompute
the same key and value projections for every previous token at every
generation step ([src]). Buffering is a tradeoff between responsiveness and
communication overhead: smaller, more frequent chunks make the response
appear smoother; grouping more tokens into each chunk reduces some of the
overhead of sending tiny updates ([src]). SSE keeps an HTTP connection open
for one-way server-to-client events; WebSockets let both sides send, which
is useful when the client keeps sending while receiving, as in a real-time
voice assistant ([src]). Longer prompts need more computation and memory,
though the exact cost depends on the model architecture and attention
implementation; a larger context window also does not mean every part is
used equally well, since information in the middle of a long prompt can be
harder to retrieve than information near the beginning or end ([src]). For
large models, moving weights through GPU memory on each decode step could
become a major bottleneck ([src]).

Sources: Neo Kim,
[How LLM Inference Works][src]
(System Design Newsletter #199, 3 Nov 2026; paid letter: training vs
inference, tokenization, context window, prefill, decode, KV cache at a
high level, TTFT, streaming via SSE/WebSockets, and chunk buffering are
public, up to "This is where inference starts becoming a HARD systems
problem"; the memory problem, closer KV-cache internals, batching, memory
management, distributed serving, and the promised real-world architecture,
scale, reliability, and performance deep dives are paid and not covered).

[src]: https://newsletter.systemdesign.one/p/how-llm-inference-works
