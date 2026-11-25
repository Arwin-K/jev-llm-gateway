# Colab serving notebook

`day1_vllm.ipynb` runs on an explicitly selected Colab GPU runtime. First create a source archive from a **committed** local revision:

```bash
git archive --format=zip -o jev-source.zip HEAD
shasum -a 256 jev-source.zip
git rev-parse HEAD
```

Enter the archive SHA-256 in the notebook and upload the zip. This pins the notebook to the exact uploaded source without publishing a local commit. The notebook installs the gateway package from that archive, checks GPU allocation, installs vLLM in a notebook-local environment, starts a loopback server, checks readiness, sends two bounded requests, downloads a JSON result, and stops the server. Colab execution has not occurred; GPU, quota, and wheel compatibility are unknown. Do not turn this into a public tunnel.

For `day6_nvidia.ipynb`, also paste the full `git rev-parse HEAD` value as `SOURCE_REVISION`. Its environment record keeps both that revision and the archive digest; the digest verifies the uploaded bytes, while the revision identifies the committed source. The Day 6 notebook generates synthetic serving prompts and saves bounded benchmark/profile artifacts separately from the Day 1 smoke notebook.

The notebook's vLLM version is a starting pin, not a verified Colab combination. If installation fails, record the actual GPU/CUDA/Python/wheel facts and update the pin in a new checkpoint; do not report the experiment as run.

## DistilBERT training notebook

`day3_distilbert.ipynb` is a user-started virtual GPU workflow. Commit the source first, make a SHA-256-verified source zip, and upload private train/validation label JSONL files separately. The notebook checks CUDA before and after installing dependencies, validates the three-tier recorded-cost labels and split separation without printing prompt text, uses the pinned model revision shown in the notebook, and downloads the trained artifact plus runtime metadata. It does not provision compute, create labels, use the held-out test split, or run paid services. The current project audit found no trainable labels yet; see `docs/STATUS.md` and `docs/EXPERIMENTS.md`.
