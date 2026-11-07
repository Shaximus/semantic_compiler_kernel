# Proxy Execution Family — Docker/Totem and Workers/Trap

Status: canonical founder-reference mappings

## Docker -> Spell Totem

### Preserved invariant

Direct execution is converted into execution by a separately instantiated, bounded proxy that carries the linked payload and acts on behalf of the host.

### Mapping

- host operating system -> player
- packaged application -> linked spell
- Docker Engine/runtime -> Spell Totem Support
- running container -> summoned totem
- container start -> totem placement
- container resource/health envelope -> totem life
- process exit -> totem death
- restart policy -> resummoning
- replica limit -> totem limit
- startup latency -> placement time
- application throughput -> totem cast rate
- image digest -> deterministic skill/version configuration
- namespace, cgroup, seccomp, and capability policy -> proxy defensive/authority envelope

### Performance law

Docker does not grant unconditional single-worker throughput. Its gains are isolation, reproducibility, replaceability, availability, and horizontal scaling. Duplicate model, KV, CUDA-context, or cache allocations are reservation penalties, not free replicas.

### Falsification

Reject this mapping if the application executes directly in the host process without an independently bounded proxy lifecycle.

---

## Cloudflare Workers -> Trap Support

### Preserved invariant

A payload is pre-deployed, dormant until a matching event arrives, then activates independently and executes under strict per-invocation limits.

### Mapping

- deploy Worker -> place trap
- dormant edge deployment -> armed inactive trap
- route match/request -> trigger-radius event
- handler invocation -> linked skill activation
- cold start -> arming/activation delay
- route pattern -> trigger condition
- CPU/wall-time limit -> activation lifetime
- concurrent invocation quota -> bounded active-trigger capacity
- Service Binding chain -> chained triggered execution
- Durable Object state -> persistent state attached to otherwise invocation-scoped execution
- geographic edge placement -> distributed field placement

### Performance law

Edge proximity and failover are topology gains. They MUST be benchmarked and MUST NOT be asserted as fixed percentage DPS improvements without measured regional latency, failure, and load data.

### Residual mismatch

A Path of Exile trap is consumed when triggered, whereas the Worker deployment persists and creates repeated independent invocations. The invocation is trap-like; the deployment is a reusable trap factory.

### Falsification

Reject this mapping when the service is a continuously running colocated process rather than dormant event-triggered execution.

---

## Category ruling

```text
Docker / Totem  = persistent colocated proxy execution
Workers / Trap  = pre-deployed event-triggered distributed execution
```

They are sibling mechanics in the proxy-execution family, not competing universal replacements.
