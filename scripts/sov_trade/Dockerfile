# SC-SOV-TRADE-001 reproducible verification image.
# Build from the repository root:
#   docker build -f scripts/sov_trade/Dockerfile -t sov-trade-verify .
#   docker run --rm sov-trade-verify
# Debian trixie ships OpenSSL 3.5 (needed for the ML-DSA cross-check),
# SoftHSM2 2.6 and OpenSC. Only TEST tokens/keys are created inside.
FROM debian:trixie-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      python3 python3-venv python3-pip git make openssl ca-certificates \
      softhsm2 opensc bsdextrautils \
 && rm -rf /var/lib/apt/lists/*
# The repository root is the `semantic_compiler` package.
COPY . /src/semantic_compiler
WORKDIR /src/semantic_compiler
ENV SOV_VERIFY_HOST_KIND=docker-debian-trixie
CMD ["bash", "scripts/sov_trade/verify.sh"]
