# SC-SOV-TRADE-001 verification. See scripts/sov_trade/verify.sh.
.PHONY: verify verify-quick verify-docker

# Full run: fresh venv from the locks, SoftHSM2 test token, full suite
# (-rs -v, SOV_TRADE_REQUIRE_FUNCTIONAL=1), unittest, validate_catalog,
# fuzz (5000 examples), HSM evidence, OpenSSL cross-checks, mutation check,
# static checks, dogfood regression diff. Output: verify-out/.
verify:
	bash scripts/sov_trade/verify.sh

# Same, without the mutation check and with a 500-example fuzz pass.
verify-quick:
	SKIP_MUTATION=1 SOV_TRADE_FUZZ_EXAMPLES=500 bash scripts/sov_trade/verify.sh

# Containerised run (Debian trixie: OpenSSL 3.5, SoftHSM2 2.6).
verify-docker:
	docker build -f scripts/sov_trade/Dockerfile -t sov-trade-verify .
	docker run --rm -v "$(CURDIR)/verify-out:/src/semantic_compiler/verify-out" sov-trade-verify
