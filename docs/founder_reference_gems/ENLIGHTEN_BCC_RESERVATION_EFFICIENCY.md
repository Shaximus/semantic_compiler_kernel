# Founder Reference Gem — Enlighten / BCC Reservation Efficiency

Status: PROPOSED FOUNDER-REFERENCE CANON
Compiler target: Semantic Compiler V3 / gem_decode + Gem Forge
Source class: independently derived structural mapping

## Canonical identity

**PoE-side gem:** Enlighten Support

**Compute-side mechanic:** compression or representation change that reduces the resident memory cost of linked persistent payloads.

**Primary Reflexion implementation:** BCC-compressed expert weights.

## Structural mapping

| PoE mechanic | Compute mechanic |
|---|---|
| Linked skill reservation multiplier | Linked payload resident-memory multiplier |
| Reduced reservation | Reduced bytes retained in the active residency pool |
| Gem level changes multiplier | Codec/configuration level changes compression ratio |
| Aura remains active | Expert remains available to the inference architecture |
| Reservation saved permits additional auras | Memory saved permits additional experts, KV, activations, or concurrency |

## Executable modifier schema

The canonical record MUST store the operation, base pool, and measured fraction. Labels are display metadata only.

```yaml
founder_reference_id: FRG_ENLIGHTEN_BCC_001
source_gem: Enlighten Support
layer: Support gem
compute_component: BCC expert-weight compression
applies_to_pool: expert_weight_residency
operation: multiply
memory_used_multiplier: 0.1677852349
compression_ratio: 5.96
fraction_of_original: 0.1677852349
percent_of_original: 16.77852349
measurement_status: measured_or_claimed_pending_receipt
scope_rule: linked_pool_only
```

Invariant:

```text
fraction_of_original = 1 / compression_ratio
```

For 5.96x compression:

```text
1 / 5.96 = 0.1677852349
             = 16.78% of original
```

## Dragonfly modifier distinction

A prose label such as `50% increased efficiency` is non-canonical until converted into an operation.

### Case A — efficiency divisor

```yaml
operation: divide_by_efficiency_factor
increased_efficiency: 0.50
efficiency_factor: 1.50
```

Result with BCC:

```text
0.1677852349 / 1.5 = 0.1118568233
                    = 11.19% of original
                    = 8.94x effective capacity
```

### Case B — measured 50% less memory used

```yaml
operation: multiply
memory_used_multiplier: 0.50
```

Result with BCC:

```text
0.1677852349 * 0.5 = 0.08389261745
                    = 8.39% of original
                    = 11.92x effective capacity
```

### Canonical ruling

When implementation evidence shows that bytes used are halved, store:

```yaml
operation: multiply
memory_used_multiplier: 0.50
semantic_label: 50% less memory used
reported_alias: 50% increased efficiency
```

The reported alias MUST NOT control arithmetic.

## Pool-separation law

Direct multiplication is valid only when both modifiers apply independently to the same pool.

```text
same pool + independent depth
=> multipliers may compose
```

Otherwise compute total memory by pool:

```text
M_total = M_expert_weights
        + M_KV
        + M_activations
        + M_runtime_overhead
        + M_fragmentation
```

Example:

```text
M_total = W_experts / 5.96
        + f_dragonfly(KV)
        + A_activations
        + O_runtime
```

Do not apply the BCC ratio to unrelated pools.

## Hidden costs / residual mismatches

1. **Decompression latency**
   - BCC lowers residency cost but adds decode/decompression work.
   - Saved reservation is not free throughput.

2. **Alternate-pool travel time**
   - CPU-pinned memory is an alternate resource pool only when transfer and decompression complete before demand.
   - Late prefetch converts the pool from `alternate` to `remote and blocking`.

3. **Allocator non-linearity**
   - Dragonfly-style allocator gains may decay near high occupancy.
   - Fragmentation must be measured as occupancy rises.

4. **Quality preservation**
   - Compression is valid only if expert behavior remains within the accepted output-quality envelope.

## Required benchmark sequence

```text
Baseline
-> BCC only
-> Dragonfly only
-> BCC + Dragonfly
-> BCC + Dragonfly + Precognition
```

Measure separately:

- expert-weight residency;
- KV residency;
- activation workspace;
- pinned host memory;
- allocator fragmentation ratio;
- decompression latency p50/p95/p99;
- PCIe transfer latency and bandwidth;
- prefetch lead and deadline misses;
- expert-cache hit rate;
- wasted expert loads;
- accepted tokens per verifier pass;
- accepted tokens/second;
- output parity and quality.

## Breakpoint law

The support gem is beneficial only when:

```text
memory_value_saved
>
decompression_cost
+ transfer_stall
+ cache-insertion cost
+ quality-loss cost
```

For precognition to hide the alternate-pool cost:

```text
prefetch_lead_p95
>= decompression_p95
 + transfer_p95
 + cache_insertion_p95
```

## Classification

```yaml
mapping_class: STRUCTURAL_ANALOGY
confidence: high
preserved_invariants:
  - linked payload cost reduction
  - persistent-capacity expansion
  - multiplier composition only under shared scope
  - breakpoint dependence on hidden execution cost
residuals:
  - PoE reservation is abstract and immediate
  - compressed weights require decompression and transfer
  - allocator fragmentation has no exact single-gem equivalent
```

## Founder-reference role

This record belongs in the missing founder-curated reference set. The all-gem corpus teaches broad vocabulary; this reference teaches an exact executable invariant:

> A memory-efficiency claim is not a percentage. It is an operation over a named resource pool.
