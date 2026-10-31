# Local replica contract

`gateway.yaml` starts two ARM gateway pods in the `jev-gateway` namespace on the
named `jev-gateway-day5` kind cluster. The Service is internal; access it with a
loopback `kubectl port-forward`. Both pods use the same *external* generation
URLs, so replicas do not add model-serving capacity. The current pod check
resolved `host.docker.internal` to `192.168.65.254`, then failed to connect to
native Ollama with `Network is unreachable`. `/readyz` says that the process can
serve requests; it explicitly reports backend availability as unchecked.

The manifest leaves `JEV_CACHE_PATH` empty and paid execution disabled. No FAISS
files are shared. If a local cache is enabled later, give each replica its own
pod-local directory and treat entries as independent; never mount one writable
FAISS directory into both pods. Jev and frontier spending counters are local to
each process. A shared positive spending cap requires a coordinated ledger or
an external provider cap before paid multi-replica traffic.

A trained DistilBERT artifact is absent. To require it, mount the same immutable
artifact read-only into every pod, set `JEV_ROUTER_ARTIFACT` and the matching
`JEV_ROUTER_TRAINING_FINGERPRINT`, and set
`JEV_REQUIRE_TRAINED_FALLBACK=true`. With that flag, readiness returns 503 if
the compatible fallback fails to load. Current `always-small` routing is an
explicit local deployment choice, not evidence of Jev or DistilBERT success.
