# Arcanist Brand — Cached Expert Staging Lifecycle

Status: canonical founder-reference mapping

## Preserved invariant

A payload exists inertly outside the execution surface, attaches to an execution target, activates repeatedly while attached, then detaches or expires and may later be staged again.

## State machine

```text
HOST_RESIDENT_INERT
  -> PREFETCH_REQUESTED
  -> DMA_STAGING
  -> VRAM_HOT
  -> REUSED_N_TIMES
  -> EVICTED
  -> HOST_RESIDENT_INERT
```

## Mapping

- unattached brand -> expert resident in host RAM and unable to execute
- attachment -> expert staged into the VRAM hot cache
- attachment/activation delay -> DMA plus decompression and synchronization latency
- repeated activations -> repeated forward-pass use while cached
- brand duration -> cache residency TTL or policy window
- detachment/expiration -> eviction
- later attachment -> restaging on future demand
- Brand Recall -> explicit forced cache relocation and immediate activation
- predictive controller -> automation that issues the equivalent of Recall before the miss becomes visible
- maximum brands -> bounded hot-cache capacity

## Compound ruling

Blood Magic and Arcanist Brand model different typed layers:

- Blood Magic defines which resource ledger pays for persistent residency.
- Arcanist Brand defines the inert -> staged -> reusable -> evicted lifecycle.

The canonical compound is therefore:

```text
Blood Magic + Arcanist Brand
= alternate-pool residency + staged reusable execution
```

## Residual mismatches

A brand is already an instantiated executable effect, while host-resident expert weights are non-executable data. Brand attachment also carries spatial and enemy-target semantics absent from ordinary memory staging.

## Falsification

Reject this mapping if the payload is consumed on first activation, never reused while staged, or has no return/eviction path to an inert state.
