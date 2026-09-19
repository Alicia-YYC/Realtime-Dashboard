# Refresh benchmark results

Measured on September 19, 2026 in a Linux x86-64 environment with Python 3.12.14.
The live API requests used the execution environment's HTTPS proxy. Network
paths, provider caches, connection reuse, and rate limits affect the live results.

## Method

- Time the complete `DataManager.refresh_once` call, including fetches, snapshots,
  and bounded health-history updates. UI rendering and between-cycle pauses are
  outside the timed region.
- Use the same source adapters and failure handling for both modes. Sequential
  mode invokes each adapter in order; concurrent mode uses one thread per source.
- Give each mode its own manager and HTTP sessions. Run one unmeasured warm-up
  pair before recording results, and alternate which mode runs first.
- Keep a measured pair only if **all four sources are healthy in both modes**.
  Partial responses, stale fallbacks, and errors disqualify the entire pair.
- Calculate reduction as `100 × (1 − concurrent median / sequential median)`
  over eligible pairs. This compares medians, not the median of pairwise ratios.
- Retain every pair, source status, error, warm-up, and unrounded timing in JSON.

## Controlled I/O measurement

The four fetchers simulate blocking I/O with `time.sleep` delays of 0.1, 0.2,
0.3, and 0.4 seconds. No external requests are made. This isolates the effect of
overlapping waits; it is not evidence of live API, CPU-work, or production speed.

| Metric | Result |
| --- | ---: |
| Measured / eligible pairs | 20 / 20 |
| Sequential median | 1.000785 s |
| Concurrent median | 0.401711 s |
| Median refresh-time reduction | 59.8604% |
| Speedup | 2.4913× |

Command:

```bash
python benchmark.py --mode controlled --rounds 20 --warmup 1 --output docs/benchmark-controlled.json
```

[Raw controlled results](benchmark-controlled.json)

## Live API measurement

Sources were Open-Meteo (Pittsburgh), Yahoo Finance (AAPL, GOOGL, MSFT, NVDA),
CoinGecko (Bitcoin), and Hacker News (five stories). Requests used the default
8-second timeout. A source poll can contain multiple HTTP requests.

The recorded run used a **5-second pause between cycles**. Three measured pairs
received CoinGecko HTTP 429 responses in both modes, causing stale fallbacks.
Those pairs are preserved in the report but excluded from timing comparisons.
The tool now defaults to a 60-second pause for optional live runs; this does not
guarantee that a provider's quota will be sufficient.

| Metric | Result |
| --- | ---: |
| Measured / eligible pairs | 5 / 2 |
| Excluded pairs | 3 |
| Sequential median, eligible pairs | 1.718763 s |
| Concurrent median, eligible pairs | 0.765653 s |
| Observed reduction, eligible pairs | 55.4533% |

Recorded command (retain for provenance; use a longer pause for future runs):

```bash
python benchmark.py --mode live --rounds 5 --warmup 1 --pause 5 --output docs/benchmark-live.json
```

[Raw live results](benchmark-live.json)

**Interpretation:** two eligible pairs are insufficient to support a stable
live-performance claim on a résumé. The rate-limit observations instead show
why visible source state and last-known-good retention matter. The controlled
59.9% figure is reproducible but must always be labeled as a simulated I/O
benchmark if quoted. Neither result is an end-user latency or SLA measurement.
