#!/usr/bin/env bash
set -euo pipefail
# Opt-in only. Requires a running native Ollama and gateway on loopback.
laya doctor
laya smoke --tier small
laya smoke --tier medium
