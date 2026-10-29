# Colab serving notebook

`day1_vllm.ipynb` runs on an explicitly selected Colab GPU runtime. First create a source archive from a **committed** local revision:

```bash
git archive --format=zip -o jev-source.zip HEAD
shasum -a 256 jev-source.zip
```

Enter the archive SHA-256 in the notebook and upload the zip. This pins the notebook to the exact uploaded source without publishing a local commit. The notebook installs the gateway package from that archive, checks GPU allocation, installs vLLM in a notebook-local environment, starts a loopback server, checks readiness, sends two bounded requests, downloads a JSON result, and stops the server. Colab execution has not occurred; GPU, quota, and wheel compatibility are unknown. Do not turn this into a public tunnel.

The notebook's vLLM version is a starting pin, not a verified Colab combination. If installation fails, record the actual GPU/CUDA/Python/wheel facts and update the pin in a new checkpoint; do not report the experiment as run.
