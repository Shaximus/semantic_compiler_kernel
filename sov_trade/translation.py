"""Semantic translation layer. Never mutates a signed source SAE."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .assertion import SignedAssertionEnvelope
from .canonical import canonical_json
from .crypto import ALG_ED25519, sha256
from .custody import KeyStore
from .identity import Principal
from .types import ActorKind, MappingType, ReasonCode, TradeError

# Fields that are compared byte-for-byte and never translated (section 9).
PROTECTED_FIELDS = frozenset(
    {
        "signatures",
        "source_hash",
        "issued_at",
        "not_before",
        "not_after",
        "authority_chain",
        "assertion_id",
        "domain",
        "challenge",
        "status_ref",
    }
)


@dataclass
class MappingEntry:
    source_term: str
    target_term: str
    mapping_type: MappingType
    field: str
    legal_category_change: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_term": self.source_term,
            "target_term": self.target_term,
            "mapping_type": self.mapping_type.value,
            "field": self.field,
            "legal_category_change": self.legal_category_change,
        }


@dataclass
class MappingRegistry:
    """Owned by the receiving nation; reviewed by the sending nation."""

    owner_domain: str
    version: int
    effective_at: int
    entries: list[MappingEntry]
    review_history: list[dict[str, Any]] = field(default_factory=list)
    signature: str = ""
    key_id: str = ""

    def payload(self) -> dict[str, Any]:
        return {
            "owner_domain": self.owner_domain,
            "version": self.version,
            "effective_at": self.effective_at,
            "entries": [e.to_dict() for e in self.entries],
            "review_history": list(self.review_history),
        }

    def sign(self, store: KeyStore, signer: Principal, *, now: int) -> None:
        sig = store.sign(signer.key_id, canonical_json(self.payload()), now=now)
        self.signature = sig.hex()
        self.key_id = signer.key_id

    def lookup(self, field: str, source_term: str) -> MappingEntry | None:
        for entry in self.entries:
            if entry.field == field and entry.source_term == source_term:
                return entry
        return None


@dataclass
class TranslationRecord:
    source_hash: str
    sae_hash: str
    mapping_version: int
    output: dict[str, Any]
    field_tags: dict[str, str]
    flags: list[str]
    human_confirmed_class_changes: list[str]
    signature: str = ""
    key_id: str = ""

    def payload(self) -> dict[str, Any]:
        return {
            "source_hash": self.source_hash,
            "sae_hash": self.sae_hash,
            "mapping_version": self.mapping_version,
            "output": self.output,
            "field_tags": dict(self.field_tags),
            "flags": list(self.flags),
            "human_confirmed_class_changes": list(self.human_confirmed_class_changes),
        }

    def to_dict(self) -> dict[str, Any]:
        body = self.payload()
        body["signature"] = self.signature
        body["key_id"] = self.key_id
        return body

    def digest(self) -> str:
        return sha256(canonical_json(self.to_dict()))


def translate(
    envelope: SignedAssertionEnvelope,
    registry: MappingRegistry,
    store: KeyStore,
    translator: Principal,
    *,
    now: int,
    confirmed_class_changes: list[str] | None = None,
) -> TranslationRecord:
    if translator.kind is not ActorKind.TRANSLATION_SIGNER:
        raise TradeError(
            ReasonCode.VERIFIER_SIGNED_ASSERTION,
            "only a translation signer (no chain to a national root) may sign a Translation Record",
        )
    confirmed = set(confirmed_class_changes or [])
    # Work on a copy; the envelope is never modified.
    source = dict(envelope.fields)
    original_source_hash = source["source_hash"]
    sae_hash = envelope.envelope_hash()
    output: dict[str, Any] = {}
    tags: dict[str, str] = {}
    flags: list[str] = []

    def _translate_value(field: str, value: Any) -> Any:
        if field in PROTECTED_FIELDS:
            return value
        if isinstance(value, str):
            entry = registry.lookup(field, value)
            if entry is None:
                flags.append(f"unmapped:{field}:{value}")
                tags[field] = MappingType.NO_EQUIVALENT.value
                return value  # pass through untouched, flagged, never guessed
            if entry.legal_category_change and entry.source_term not in confirmed:
                raise TradeError(
                    ReasonCode.CLASS_CHANGE_UNCONFIRMED,
                    f"legal/regulatory category change for {field} requires confirmation",
                )
            tags[field] = entry.mapping_type.value
            if entry.mapping_type is not MappingType.EXACT:
                flags.append(f"non_exact:{field}:{entry.mapping_type.value}")
            return entry.target_term
        if isinstance(value, dict):
            return {k: _translate_value(f"{field}.{k}" if field else k, v) for k, v in value.items()}
        if isinstance(value, list):
            return [_translate_value(field, item) for item in value]
        return value

    for key, value in source.items():
        output[key] = _translate_value(key, value)

    # Integrity: the original SAE and its source_hash must be unchanged.
    if envelope.fields["source_hash"] != original_source_hash:
        raise TradeError(ReasonCode.TRANSLATION_ALTERED_SOURCE, "source hash mutated")
    if envelope.envelope_hash() != sae_hash:
        raise TradeError(ReasonCode.TRANSLATION_ALTERED_SOURCE, "signed envelope mutated")

    record = TranslationRecord(
        source_hash=original_source_hash,
        sae_hash=sae_hash,
        mapping_version=registry.version,
        output=output,
        field_tags=tags,
        flags=flags,
        human_confirmed_class_changes=sorted(confirmed),
    )
    sig = store.sign(translator.key_id, canonical_json(record.payload()), now=now)
    record.signature = sig.hex()
    record.key_id = translator.key_id
    return record


def provenance_round_trip(
    record: TranslationRecord,
    envelope: SignedAssertionEnvelope,
    institutional_record: bytes,
) -> ReasonCode:
    """R-14: translated output points back to the original institutional record."""
    if record.sae_hash != envelope.envelope_hash():
        return ReasonCode.TRANSLATION_ALTERED_SOURCE
    if record.source_hash != envelope.fields["source_hash"]:
        return ReasonCode.TRANSLATION_ALTERED_SOURCE
    if record.source_hash != sha256(institutional_record):
        return ReasonCode.TRANSLATION_ALTERED_SOURCE
    return ReasonCode.OK
