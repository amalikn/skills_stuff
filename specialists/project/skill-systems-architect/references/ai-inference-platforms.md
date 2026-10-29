---
Title: Self-hosted AI inference platforms
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: >-
  Sizing self-hosted LLM inference: weight and KV-cache memory, prefill vs decode, time to first token and tokens per second per user, batching
  (vLLM paged attention, continuous batching), Apple silicon with Ollama or llama.cpp, GPU vs CPU, and queueing for N users, with a worked example.
---

# Self-hosted AI inference platforms

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Memory: weights and KV cache](#memory-weights-and-kv-cache)
- [Speed: prefill, decode and batching](#speed-prefill-decode-and-batching)
- [Serving engines and hardware](#serving-engines-and-hardware)
- [Queueing for N users](#queueing-for-n-users)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Sizing memory, throughput and latency for a self-hosted large language model (LLM) serving N users; choosing the engine and hardware class.
- First-order arithmetic only: the formulas give bounds and a shortlist. Benchmarks on the real model, prompt mix and engine decide.
- Model choice, prompt design and evaluation quality are out of scope; so is training. Power and cooling go to [compute-and-facilities][compute-and-facilities-url]; network bandwidth between nodes to
  skill-network-architect.
- Product facts (engine flags, defaults) are dated; re-check them against the engine release you deploy.

## Decision rules

| Decision                | Rule and threshold                                                                                               | Evidence                                        |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| Weight memory           | params x bytes per param: FP16/BF16 2, FP8/INT8 1, 4-bit about 0.5 to 0.6 (format overhead)                      | Arithmetic; sizes check against [ollama-tags]   |
| KV cache per token      | 2 x layers x kv_heads x head_dim x bytes per element (2 x for K and V)                                           | Arithmetic from the model's config.json         |
| Fits in memory          | weights + KV for the planned concurrent tokens + runtime overhead must stay under the accelerator memory         | Design rule; measure overhead per engine        |
| Decode speed ceiling    | tokens/s per sequence <= memory bandwidth / bytes read per step (weights + that batch's KV)                      | Roofline bound, UNVERIFIED as a measurement     |
| Prefill cost            | about 2 x params floating-point operations per prompt token; compute-bound                                       | Standard approximation, UNVERIFIED per model    |
| Concurrency to plan     | Little's law: concurrent requests = arrival rate x time per request                                              | [capacity-and-performance](capacity-and-performance.md) |
| Many users on one model | Use an engine with continuous batching and paged KV (vLLM; llama.cpp server slots); one-at-a-time serving queues | VERIFIED_PRIMARY [vllm-paper] [llamacpp-server] |
| Ollama for many users   | Raise `OLLAMA_NUM_PARALLEL` (default 1); memory scales with parallel x context length                            | VERIFIED_PRIMARY [ollama-faq]                   |

## Memory: weights and KV cache

Model shapes (from config.json, VERIFIED_SECONDARY: ungated mirrors of the Meta repositories [llama8b-config] [llama70b-config], checked 2026-10-29):

| Model         | Layers | Attention heads | KV heads | Hidden size | head_dim (hidden / heads) | KV per token at 2 bytes        |
| ------------- | ------ | --------------- | -------- | ----------- | ------------------------- | ------------------------------ |
| Llama 3.1 8B  | 32     | 32              | 8        | 4096        | 128                       | 2 x 32 x 8 x 128 x 2 = 128 KiB |
| Llama 3.1 70B | 80     | 64              | 8        | 8192        | 128                       | 2 x 80 x 8 x 128 x 2 = 320 KiB |

- Grouped-query attention (8 KV heads instead of 32 or 64) is why these models need 4 to 8 times less KV memory than their head count suggests.
- One 8,192-token sequence holds 1 GiB of KV on the 8B model and 2.5 GiB on the 70B model at 2 bytes per element.
- KV grows with every token generated; reserve for prompt plus maximum output, per concurrent sequence.

Weight files in Ollama's library (VERIFIED_PRIMARY [ollama-tags], checked 2026-10-29):

| Model   | Q4_K_M | Q8_0   | FP16   | Check against params x bytes                 |
| ------- | ------ | ------ | ------ | -------------------------------------------- |
| 3.1 8B  | 4.9 GB | 8.5 GB | 16 GB  | 8.0e9 x 2 = 16 GB (FP16)                     |
| 3.1 70B | 43 GB  | 75 GB  | 141 GB | 70.6e9 x 2 = 141 GB; 43 GB = ~4.9 bits/param |

- Quantisation trades quality for memory and speed. Measure quality on your own tasks before accepting a 4-bit model (UNVERIFIED in general).

```text
Accelerator memory budget for one model (fill in; every box must fit)

+------------------------------------------------------------------------------------+
| accelerator memory (GPU VRAM, or Apple unified memory minus OS and apps)          |
|  +-------------------+  +-----------------------------------+  +----------------+  |
|  | weights           |  | KV cache: concurrent sequences x  |  | runtime,       |  |
|  | params x bytes    |  | (prompt + output tokens) x KV/tok |  | activations,   |  |
|  +-------------------+  +-----------------------------------+  | CUDA graphs    |  |
|                                                                 +----------------+  |
+------------------------------------------------------------------------------------+
X KV does not fit: the engine preempts or queues requests; latency jumps, it does not fail cleanly
Legend: boxes are additive shares of one memory pool   X failure and its effect
```

## Speed: prefill, decode and batching

- Prefill reads the whole prompt in parallel; it is compute-bound and sets time to first token (TTFT).
- Decode emits one token per step per sequence; each step reads all weights plus that batch's KV from memory, so it is bandwidth-bound.
- Batching shares one weight read across every sequence in the step, so aggregate tokens/s rises with batch size until compute or KV bandwidth saturates. Per-user tokens/s falls slowly as the batch
  grows.
- vLLM's PagedAttention stores KV in fixed blocks, giving near-zero KV waste and sharing; the paper reports 2-4x throughput at the same latency against FasterTransformer and Orca (VERIFIED_PRIMARY
  [vllm-paper], checked 2026-10-29).
- vLLM V1 enables chunked prefill by default: it schedules pending decodes first and splits long prompts into chunks within `max_num_batched_tokens`, balancing TTFT against inter-token latency
  (VERIFIED_PRIMARY [vllm-optim], checked 2026-10-29).
- When KV space runs out, vLLM preempts requests and recomputes them later; frequent preemption means the KV budget is too small [vllm-optim].

| Metric                     | What sets it                                    | Typical user expectation (UNVERIFIED, set per service) |
| -------------------------- | ----------------------------------------------- | ------------------------------------------------------ |
| Time to first token        | queue wait + prefill of the prompt              | about 1-2 s for chat                                   |
| Tokens/s per user (decode) | bandwidth / bytes per step, shared by the batch | faster than reading speed, roughly 10-20 tokens/s      |
| Aggregate tokens/s         | batch size x step rate                          | must exceed arrival rate x output tokens               |

## Serving engines and hardware

| Engine           | Licence (checked 2026-10-29) | Fits                                                   | Concurrency model                                                                         |
| ---------------- | ---------------------------- | ------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| vLLM             | Apache-2.0                   | NVIDIA/AMD GPU servers, many users, multi-GPU (TP/PP)  | continuous batching, PagedAttention, chunked prefill [vllm-optim]                         |
| llama.cpp server | MIT                          | Apple silicon, CPU, consumer GPU; GGUF                 | `-np` slots (default auto), continuous batching on by default, unified KV                 |
|                  |                              |   quantised models                                     |   buffer [llamacpp-server]                                                                |
| Ollama           | MIT                          | single host, developer and small-team use              | `OLLAMA_NUM_PARALLEL` (default 1), `OLLAMA_MAX_QUEUE` (default 512) then                  |
|                  |                              |                                                        |   rejects [ollama-faq]                                                                    |

Memory bandwidth decides decode speed (VERIFIED_PRIMARY vendor specification pages, checked 2026-10-29):

| Hardware                          | Memory               | Bandwidth | Decode ceiling, 8B Q4 (4.9 GB) | Decode ceiling, 70B Q4 (43 GB) |
| --------------------------------- | -------------------- | --------- | ------------------------------ | ------------------------------ |
| Mac Studio M5 Max (40-core GPU)   | up to 128 GB unified | 614 GB/s  | <= 125 tokens/s                | <= 14 tokens/s                 |
| Mac Studio M5 Ultra (80-core GPU) | up to 512 GB unified | 1.2 TB/s  | <= 245 tokens/s                | <= 28 tokens/s                 |
| NVIDIA L40S                       | 48 GB GDDR6          | 864 GB/s  | <= 176 tokens/s                | does not fit one card          |
| NVIDIA H100 SXM                   | 80 GB HBM3           | 3.35 TB/s | <= 680 tokens/s                | <= 78 tokens/s                 |

- Ceilings are single-sequence bandwidth bounds (bandwidth / weight bytes); real engines reach a fraction of them. Measure.
- Apple silicon: unified memory lets one box hold a 70B model, but GPU memory is shared with macOS and apps, and prefill compute is far below data-centre GPUs, so long prompts and many users raise
  TTFT sharply (UNVERIFIED magnitude; Apple publishes no tensor FLOPS figure).
- CPU-only inference: workable for small models and a few users; bandwidth of server DDR is the ceiling, as above.
- A laptop is not a server: sleep, thermals and battery apply ([macos-and-endpoints](macos-and-endpoints.md)).

## Queueing for N users

```text
N users to accelerator slots: where waiting time comes from

  N users --(think time Z between requests)--> arrivals lambda = N / (Z + R)
                                                   |
                                                   v
                       +---------------- queue (OLLAMA_MAX_QUEUE / engine waiting list) ----------------+
                       |  wait grows without bound when lambda x W exceeds the slots c                   |
                       +----------------------------------------------------------------------------------+
                                                   |
                                                   v
                 +-------------- c batch slots, each: prefill (TTFT) then decode (output / tok/s) ---------+

  Concurrent requests L = lambda x W, where W = TTFT + output tokens / per-user tokens/s
X L above c: requests queue; TTFT includes the queue wait
Legend: --> request flow   X failure and its effect
```

- Arrival rate for a closed group of N users: lambda = N / (Z + R), with think time Z and response time R. Treat Z as USER_STATED or measured.
- Required aggregate decode rate = lambda x average output tokens. Required prefill rate = lambda x average prompt tokens.
- Size slots c at least L with headroom for bursts (for example 1.5 x L, a design assumption); then confirm KV fits c sequences.

## Patterns and anti-patterns

| Pattern                                        | Use when                     | Anti-pattern                                   | Why it fails                                    |
| ---------------------------------------------- | ---------------------------- | ---------------------------------------------- | ----------------------------------------------- |
| Size KV for concurrent tokens, not one chat    | any shared server            | "the model file fits, so we are done"          | KV for 20 sequences can exceed the weights      |
| Continuous batching engine for many users      | more than a handful of users | Ollama with `OLLAMA_NUM_PARALLEL=1` for a team | every request waits for the one before it       |
| Smallest model that passes the task evaluation | cost and latency matter      | 70B by default                                 | 8 to 9 times the memory and bandwidth per token |
| Separate TTFT and tokens/s targets             | chat and agent workloads     | one "tokens per second" number                 | long prompts hide in prefill; users feel TTFT   |
| Load test with the real prompt-length mix      | before buying hardware       | single-request benchmark                       | batching and queueing behaviour is invisible    |

## Failure modes and tests

| Failure                       | Signal                                                    | Proving test                                                              |
| ----------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------- |
| KV exhausted                  | vLLM preemption warnings; Ollama unloads or queues        | ramp concurrent sessions to c and 1.5c; record preemptions and TTFT p95   |
| Queue saturation              | TTFT rises without bound; Ollama rejects after 512 queued | step load until TTFT p95 crosses target; that is the capacity             |
| Long prompt starves decodes   | inter-token latency spikes when a large prompt arrives    | mix 1 long prompt with 20 decoding sessions; check chunked prefill effect |
| Unified memory pressure (Mac) | swap, memory pressure red, tokens/s collapses             | run at target concurrency with the normal desktop load present            |
| Thermal throttling            | tokens/s falls over 10-30 minutes                         | 60-minute soak at target load; compare first and last 5 minutes           |
| Model reload churn            | periodic multi-second stalls                              | serve two models over the memory limit; watch load and unload events      |

## Worked example

50 users of an internal assistant. Assumptions (USER_STATED for the example): each user sends a request every 60 s of think time, prompt 2,000 tokens, answer 300 tokens, targets TTFT p95 under 2 s and
at least 15 tokens/s per user. KV reserved at 4,096 tokens per sequence.

1. Arrivals: lambda = 50 / (60 + about 20) = 0.625 requests/s (R about 20 s, from step 2).
2. Time per request: W = TTFT (target under 2 s) + 300 / 15 = up to 22 s. Concurrency L = 0.625 x 22 = about 14. Plan c = 21 slots (1.5 x L).
3. Load: decode 0.625 x 300 = 188 tokens/s aggregate; prefill 0.625 x 2,000 = 1,250 prompt tokens/s.
4. 8B model, FP16 on one L40S (48 GB): weights 16 GB + KV 21 x 4,096 x 128 KiB = 10.5 GiB (11.3 GB) = about 27 GB plus runtime overhead. It fits. A decode step reads about 16 GB + 21 x 2,300 x 128 KiB
   (6.3 GB) = 22 GB, so at most 864 / 22 = about 39 steps/s, that is up to about 39 tokens/s per user with all 21 slots busy: above the 15 target. Prefill: 2 x 8e9 x 1,250 = 20 TFLOP/s, well inside a
   data-centre GPU.
5. 8B model, Q4 on a Mac Studio M5 Max: weights 4.9 GB; ceiling 125 tokens/s single stream. Set `OLLAMA_NUM_PARALLEL` to about 21, or use llama.cpp server with `-np 21`; memory scales with parallel x
   context. Plausible, but TTFT under concurrent 2,000-token prompts must be measured.
6. 70B model: KV 21 x 4,096 x 320 KiB = 26.3 GiB (28.2 GB). FP16 weights 141 GB + 28 GB = 169 GB, over two H100s (160 GB) before overhead. With FP8 weights (about 71 GB, 1 byte per param) on two
   H100s: 71 + 28 = 99 GB of 160 GB. A step reads about 71 + 21 x 2,300 x 320 KiB (15.8 GB) = 87 GB across 2 x 3.35 TB/s, so at most about 77 steps/s. Prefill: 2 x 70.6e9 x 1,250 = 177 TFLOP/s, which
   needs data-centre GPUs.
7. 70B on one Mac Studio M5 Ultra (Q4, 43 GB): the decode ceiling is 28 tokens/s for one stream and the weight read is shared, but 177 TFLOP/s of prefill is far beyond it (UNVERIFIED: no published
   figure). Reject for 50 users; acceptable for a few.
8. Decision: 8B on one L40S-class GPU with vLLM meets the targets on paper; 70B needs two H100-class GPUs with FP8. Load-test both before buying, with the real prompt mix, and record TTFT p95 and
   tokens/s per user at c = 21.

All step results are derived bounds from the arithmetic above, not measurements.

## Review checklist

- [ ] Model shape (layers, KV heads, head_dim) taken from the model's own config.json; KV per token computed.
- [ ] Memory budget shows weights + KV for c concurrent sequences + overhead, under accelerator memory.
- [ ] Arrival rate, think time, prompt and output lengths stated with evidence labels; L and c computed with Little's law.
- [ ] Separate TTFT p95 and per-user tokens/s targets; load test at c and 1.5c with the real prompt mix recorded.
- [ ] Engine supports continuous batching at the planned concurrency (vLLM, llama.cpp `-np`, or Ollama `OLLAMA_NUM_PARALLEL` raised).
- [ ] Queue limit and rejection behaviour are known and alerted; a 60-minute soak shows no thermal or memory-pressure collapse.
- [ ] Quantisation level justified by a task-quality check, not by memory alone.

## Further reading

Engines:
- [vllm-paper] [Efficient Memory Management for LLM Serving with PagedAttention][2309-06180-url] - read this for why KV paging raises throughput (VERIFIED_PRIMARY, checked 2026-10-29).
- [vllm-optim] [vLLM optimisation and tuning][optimization-url] - read this for chunked prefill, preemption and parallelism (VERIFIED_PRIMARY, checked 2026-10-29).
- [llamacpp-server] [llama.cpp server README][llamacpp-url] - read this for slots, continuous batching and KV options (VERIFIED_PRIMARY, checked 2026-10-29).
- [ollama-faq] [Ollama FAQ: concurrent requests](https://docs.ollama.com/faq) - read this for parallel, queue and loaded-model limits (VERIFIED_PRIMARY, checked 2026-10-29).
- [ollama-tags] [Ollama llama3.1 tags](https://ollama.com/library/llama3.1/tags) - read this for quantised file sizes (VERIFIED_PRIMARY, checked 2026-10-29).

Model cards and hardware:
- [llama8b-config] [Llama 3.1 8B config][l8url] and [llama70b-config] [Llama 3.1 70B config][l70url] - read these for layer and head counts (VERIFIED_SECONDARY, mirrors of the gated Meta repositories,
  checked 2026-10-29).
- [Mac Studio technical specifications](https://www.apple.com/mac-studio/specs/) - read this for unified memory and bandwidth (VERIFIED_PRIMARY, checked 2026-10-29).
- [NVIDIA L40S][l40s-url] and [NVIDIA H100][h100-url] - read these for memory and bandwidth (VERIFIED_PRIMARY, checked 2026-10-29).

[llamacpp-url]: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md

[l8url]: https://huggingface.co/unsloth/Meta-Llama-3.1-8B-Instruct/blob/main/config.json

[l70url]: https://huggingface.co/unsloth/Meta-Llama-3.1-70B-Instruct/blob/main/config.json

[compute-and-facilities-url]: compute-and-facilities.md

[2309-06180-url]: https://arxiv.org/abs/2309.06180

[optimization-url]: https://docs.vllm.ai/en/latest/configuration/optimization.html

[l40s-url]: https://www.nvidia.com/en-us/data-center/l40s/

[h100-url]: https://www.nvidia.com/en-us/data-center/h100/
