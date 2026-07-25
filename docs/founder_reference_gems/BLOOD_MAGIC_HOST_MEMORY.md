# Founder Reference Gem — Blood Magic / Host-Memory Ledger Conversion

Status: PROPOSED FOUNDER-REFERENCE CANON
Compiler target: Semantic Compiler V3 / gem_decode + Gem Forge
Source class: independently derived structural mapping

## Canonical identity

**PoE-side mechanic:** Blood Magic

**Compute-side mechanic:** move persistent payload residency from scarce device memory into a separate host-memory ledger, while preserving an explicit activation cost to stage the payload back onto the executable device.

## Structural mapping

| PoE mechanic | Compute mechanic |
|---|---|
| Mana pool | GPU VRAM budget |
| Life pool | Host RAM budget |
| Reservation | Persistent expert-weight residency |
| Paying life instead of mana | Charging residency to host RAM instead of VRAM |
| Life recovery | Host-memory reclamation and cache eviction |
| Low life | Host-memory pressure threshold |
| Lethal reservation | Host OOM / operating-system instability |

## Executable schema

```yaml
founder_reference_id: FRG_BLOOD_MAGIC_HOST_MEMORY_001
source_gem: Blood Magic
layer: Support gem
compute_component: host-memory expert residency
mechanic_family: resource_pool_conversion
source_pool: gpu_vram
source_charge: persistent_residency
destination_pool: page_locked_host_ram
destination_charge: persistent_residency
execution_surface: gpu_vram
activation_costs:
  - dma_transfer
  - decompression
  - cache_insertion
scope_rule: linked_payload_only
measurement_status: architecture_rule
```

## Dual-ledger law

```text
V_used = V_fixed + V_KV + V_workspace + V_hot_cache + V_staging
H_used = H_OS + H_runtime + H_expert_store + H_pinned_buffers
```

The host-memory ledger does not erase the device-memory ledger. A payload resident in host RAM remains non-executable until staged onto the device.

## Breakpoint law

```text
visible_stall = max(0, activation_latency - prefetch_lead)
activation_latency = dma + decompression + cache_insertion + synchronization
```

Blood Magic is successful only when the alternate pool makes the build possible without causing host-memory failure or exposing more activation latency than the scheduler can hide.

## Failure modes

- `host_oom`: pinned residency leaves insufficient RAM for the OS or runtime.
- `false_capacity`: host RAM is counted as if it were directly executable VRAM.
- `pci_exsanguination`: cache misses consume PCIe bandwidth faster than it replenishes.
- `late_lifetap`: the expert arrives after verifier demand.
- `double_counted_enlighten`: compression is applied to pools it does not modify.

## Residual mismatch

PoE life directly pays a skill cost. Host RAM does not directly perform competitive GPU tensor execution. The mapping is exact for the resource ledger, not for the complete expert lifecycle.
