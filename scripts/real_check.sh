#!/usr/bin/env bash
set -euo pipefail
# Opt-in only. Requires a running native Ollama and gateway on loopback.
jev doctor
jev smoke --tier small
jev smoke --tier medium
