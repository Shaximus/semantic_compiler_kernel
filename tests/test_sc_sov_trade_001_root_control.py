"""t617u: national-root grants need three distinct officers and the 3-of-5 ceremony.

Shax t617u: neither APPROVE+SIGN nor APPROVE+DEPLOY as a pair. A national-root
grant requires one officer holding APPROVE, a different officer holding SIGN,
and a third holding DEPLOY. The grant is signed through the existing Shamir
ceremony path, not only the in-memory key. generate_root and root revoke use
the same three-officer rule (provisional, flagged for Shax).
"""

from __future__ import annotations

import pytest

from tests.sov_trade_deps import CRYPTOGRAPHY_SKIP, have_cryptography

pytestmark = pytest.mark.skipif(not have_cryptography(), reason=CRYPTOGRAPHY_SKIP)


def _nation():
    from semantic_compiler.sov_trade.clock import FrozenClock
    from semantic_compiler.sov_trade.nation import Nation

    return Nation.create("nation-a", FrozenClock(1_700_000_000))


def _issuer_scope():
    from semantic_compiler.sov_trade.authority import DelegationScope
    from semantic_compiler.sov_trade.types import DocClass

    return DelegationScope(
        doc_classes=frozenset({DocClass.CERTIFICATE_OF_ORIGIN.value}),
        commodity_codes=frozenset(),
        counterparty_domains=frozenset(),
        value_ceiling=100,
    )


def _grant(nation, *, first=None, second=None, signer=None, ceremony=None, shares=None, grantee=None):
    from semantic_compiler.sov_trade.types import ActorKind

    first = first or nation.officers["alpha"]
    second = second or nation.officers["bravo"]
    now = nation.clock.now_ts()
    if grantee is None:
        grantee = nation.identity.create_principal(
            ActorKind.INSTITUTIONAL_ISSUER,
            "probe",
            nation.officers["alpha"],
            nation.officers["bravo"],
            parent=nation.root.identifier,
        )
    kwargs = dict(
        grantor=nation.root,
        grantee=grantee,
        scope=_issuer_scope(),
        mode="institutional",
        not_before=now,
        not_after=now + 3600,
        now=now,
        parent=None,
        first=first,
        second=second,
        signer=signer,
    )
    if ceremony is not None:
        kwargs["ceremony"] = ceremony
    if shares is not None:
        kwargs["shares"] = shares
    return nation.authority.issue(**kwargs)


def test_happy_root_grant_with_three_officers_and_ceremony() -> None:
    nation = _nation()
    issuer = nation.add_issuer("customs")
    rec = nation.authority.current_for(issuer.identifier)
    assert rec is not None
    assert rec.grantor == nation.root.identifier


def test_same_officer_in_two_roles_is_rejected() -> None:
    """The same officer cannot fill two of APPROVE, SIGN, DEPLOY."""
    from semantic_compiler.sov_trade.types import ReasonCode, TradeError

    nation = _nation()
    ceremony = nation.root_ceremony
    assert ceremony is not None
    shares = list(ceremony.shares[: ceremony.threshold])
    with pytest.raises(TradeError) as info:
        _grant(
            nation,
            first=nation.officers["alpha"],
            second=nation.officers["bravo"],
            signer=nation.officers["alpha"],
            ceremony=ceremony,
            shares=shares,
        )
    assert info.value.reason is ReasonCode.DUAL_CONTROL_REQUIRED
    assert "distinct" in str(info.value).lower() or "two roles" in str(info.value).lower()


def test_two_officer_pair_cannot_cover_three_roles() -> None:
    """A pair that jointly holds all three roles still cannot cover a root act."""
    from semantic_compiler.sov_trade.types import CustodyError, ReasonCode

    nation = _nation()
    needed = __import__("semantic_compiler.sov_trade.types", fromlist=["Role"]).Role
    roles = frozenset({needed.APPROVE, needed.SIGN, needed.DEPLOY})
    with pytest.raises(CustodyError) as info:
        nation.store.require_dual_control(
            nation.officers["alpha"], nation.officers["bravo"], roles
        )
    assert info.value.reason is ReasonCode.DUAL_CONTROL_REQUIRED


def test_root_grant_with_no_signer_is_rejected() -> None:
    from semantic_compiler.sov_trade.types import ReasonCode, TradeError

    nation = _nation()
    ceremony = nation.root_ceremony
    assert ceremony is not None
    with pytest.raises(TradeError) as info:
        _grant(nation, signer=None, ceremony=ceremony, shares=list(ceremony.shares[:3]))
    assert info.value.reason is ReasonCode.DUAL_CONTROL_REQUIRED
    assert "signer" in str(info.value).lower()


def test_signer_without_sign_role_is_rejected() -> None:
    """bravo holds APPROVE+DEPLOY, not SIGN, and must not be the signer."""
    from semantic_compiler.sov_trade.types import ReasonCode, TradeError

    nation = _nation()
    ceremony = nation.root_ceremony
    assert ceremony is not None
    # Three distinct officers, but the nominated signer does not hold SIGN.
    with pytest.raises(TradeError) as info:
        _grant(
            nation,
            first=nation.officers["alpha"],
            second=nation.officers["charlie"],
            signer=nation.officers["bravo"],
            ceremony=ceremony,
            shares=list(ceremony.shares[:3]),
        )
    assert info.value.reason is ReasonCode.ROLE_SEPARATION
    assert "SIGN" in str(info.value)


def test_root_grant_without_ceremony_is_rejected() -> None:
    from semantic_compiler.sov_trade.types import ReasonCode, TradeError

    nation = _nation()
    with pytest.raises(TradeError) as info:
        _grant(nation, signer=nation.officers["charlie"], ceremony=None, shares=None)
    assert info.value.reason is ReasonCode.FAIL_CLOSED
    assert "ceremony" in str(info.value).lower()


def test_generate_key_refuses_national_root() -> None:
    from semantic_compiler.sov_trade.types import ActorKind, CustodyError, ReasonCode

    nation = _nation()
    with pytest.raises(CustodyError) as info:
        nation.store.generate_key(
            "should-not-exist",
            ActorKind.NATIONAL_ROOT,
            nation.officers["alpha"],
            nation.officers["bravo"],
        )
    assert info.value.reason is ReasonCode.DUAL_CONTROL_REQUIRED


def test_generate_root_requires_three_officers() -> None:
    from semantic_compiler.sov_trade.types import CustodyError, ReasonCode

    nation = _nation()
    with pytest.raises(TypeError):
        nation.store.generate_root(  # type: ignore[misc]
            "nation-a:extra-root",
            nation.officers["alpha"],
            nation.officers["bravo"],
        )


def test_revoke_root_requires_three_officers() -> None:
    from semantic_compiler.sov_trade.types import CustodyError, ReasonCode

    nation = _nation()
    with pytest.raises(CustodyError) as info:
        nation.store.revoke(
            nation.root.key_id,
            nation.officers["alpha"],
            nation.officers["bravo"],
            now=nation.clock.now_ts(),
        )
    assert info.value.reason is ReasonCode.DUAL_CONTROL_REQUIRED
    nation.store.revoke(
        nation.root.key_id,
        nation.officers["alpha"],
        nation.officers["bravo"],
        third=nation.officers["charlie"],
        now=nation.clock.now_ts(),
    )
    from semantic_compiler.sov_trade.types import CustodyError as CE

    with pytest.raises(CE):
        nation.store.sign(
            nation.root.key_id,
            b"x",
            now=nation.clock.now_ts(),
            signer=nation.officers["alpha"],
        )


def test_store_sign_root_requires_signer_holding_sign() -> None:
    from semantic_compiler.sov_trade.types import CustodyError, ReasonCode

    nation = _nation()
    with pytest.raises(CustodyError) as info:
        nation.store.sign(nation.root.key_id, b"msg", now=nation.clock.now_ts(), signer=None)
    assert info.value.reason is ReasonCode.DUAL_CONTROL_REQUIRED
    with pytest.raises(CustodyError) as info:
        nation.store.sign(
            nation.root.key_id,
            b"msg",
            now=nation.clock.now_ts(),
            signer=nation.officers["bravo"],
        )
    assert info.value.reason is ReasonCode.ROLE_SEPARATION
    sig = nation.store.sign(
        nation.root.key_id, b"msg", now=nation.clock.now_ts(), signer=nation.officers["alpha"]
    )
    assert nation.store.public_for(nation.root.key_id).verify(b"msg", sig)
