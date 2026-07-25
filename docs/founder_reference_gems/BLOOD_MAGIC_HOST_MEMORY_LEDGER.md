# Blood Magic — Host-Memory Resource Conversion

Status: canonical founder-reference mapping

## Preserved invariant

A payload that cannot remain resident in the scarce primary resource pool is assigned to a separate, larger resource ledger. The alternate pool does not become the execution surface; activation still requires transport into executable memory.

## Mapping

- mana / primary reservation pool -> GPU VRAM
- life / alternate resource pool -> host RAM
- reservation conversion -> persistent expert payload stored in host memory rather than permanent VRAM
- activation cost -> DMA, decompression, synchronization, and cache insertion
- lethal reservation -> host OOM, paging collapse, or insufficient operating-system headroom

## Accounting law

VRAM and host RAM MUST remain separate ledgers.

```text
VRAM_used = fixed_weights + KV + workspace + hot_cache + staging
RAM_used  = OS + runtime + expert_store + pinned_buffers
```

Compression may multiply with Blood Magic only when it demonstrably transforms the same host-resident payload. Transport optimizations do not reduce reservation and MUST NOT be counted as memory multipliers.

## Residual mismatch

Life can directly pay a skill cost in Path of Exile. Host RAM cannot execute GPU tensor operations at competitive speed. The expert must be staged into VRAM before execution.

## Falsification

Reject this mapping if the implementation executes the payload directly from the alternate pool without a distinct executable-memory transition, or if it merely compresses the same VRAM allocation rather than moving it to another resource ledger.
