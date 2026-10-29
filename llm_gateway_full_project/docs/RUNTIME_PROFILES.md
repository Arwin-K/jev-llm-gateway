# Runtime profiles and scope map

The Mac runs the gateway, native Ollama small and medium models, portable inference, code sandbox, Docker, and kind. Colab runs bounded GPU serving, DistilBERT training, and NVIDIA profiling with the same source revision. Jev and the frontier model are configured external APIs. Colab servers stay notebook-local; a notebook is never a permanent Mac backend.

| Required original feature | Planned checkpoint range |
| --- | --- |
| Three generation tiers and explicit dispatch | D1-04–D1-18 |
| 2000+ prompt math, choice, code evaluation and cost/latency | D2-01–D2-18 |
| Jev principal router, DistilBERT fallback, prompted and self-hosted decision comparisons, fixed/random baselines, calibration | D3-01–D3-18 |
| Jev verification cascades and verified semantic FAISS cache | D4-01–D4-18 |
| Docker, kind, Prometheus/Grafana, Locust, failure tests, CI | D5-01–D5-18 |
| Colab GPU profiling, held-out comparisons, final report | D6-01–D6-18 |

Sequential model evaluation can collect quality outcomes when memory is tight. It does not establish live multi-tier routing latency. Record Mac and Colab measurements separately, including model revisions and load state. Paid APIs remain off until credentials and an explicit positive request/token/spending cap are configured.
