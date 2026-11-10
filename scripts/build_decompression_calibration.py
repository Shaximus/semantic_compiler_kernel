"""Build V2.2 decompression calibration corpus."""
import json
import sys
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
if str(REPO_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_DIR))

from semantic_compiler.expansion import decompress
from semantic_compiler.core.packet import SemanticPacket

# Five samples per non-generic domain (one per category family). universal_generic is the fallback
# template and is not a calibration target.
# Entry shape: (input_text, intended_domain, calibration_category)
SAMPLES = [
    # --- 10 strong whole-system descriptions ---
    ("A cell with membrane, metabolism, immune system, genetic code, and homeostasis.", "biology", "strong_whole_system"),
    ("A data center with firewalls, load balancers, redundant power, monitoring, and automated failover across distributed servers.", "computation", "strong_whole_system"),
    ("A building with foundation, load-bearing frame, electrical wiring, plumbing, HVAC, and a weather-sealed envelope.", "construction", "strong_whole_system"),
    ("A corporate structure with executive board, legal compliance, HR, and market operations.", "corporate", "strong_whole_system"),
    ("A forest ecosystem with producers, herbivores, predators, decomposers, nutrient cycles, and water regulation.", "ecology", "strong_whole_system"),
    ("A national economy with central banking, labor markets, production sectors, trade balances, and fiscal policy.", "economic", "strong_whole_system"),
    ("A watershed system with rainfall capture, groundwater recharge, river transport, sediment control, and delta wetlands.", "environmental", "strong_whole_system"),
    ("A population under selection pressure with mutation, genetic drift, gene flow, speciation, and extinction dynamics.", "evolutionary", "strong_whole_system"),
    ("A constitutional government with legislature, judiciary, executive agencies, elections, and a free press.", "government", "strong_whole_system"),
    ("A knowledge platform with ingestion pipelines, indexing, access control, curation, and redundancy backups.", "informational", "strong_whole_system"),

    # --- 10 fragmentary descriptions ---
    ("The court hears appeals.", "law", "fragmentary"),
    ("The patient has a heartbeat.", "medical", "fragmentary"),
    ("A radar station scans the coast.", "military", "fragmentary"),
    ("A team holds weekly meetings.", "organizational", "fragmentary"),
    ("A loop that checks its own outputs.", "reflexion", "fragmentary"),
    ("Neighbors share a fence.", "social", "fragmentary"),
    ("Mitochondria produce ATP.", "biology", "fragmentary"),
    ("A server handles requests.", "computation", "fragmentary"),
    ("A crane lifts beams.", "construction", "fragmentary"),
    ("Payroll runs monthly.", "corporate", "fragmentary"),

    # --- 10 pathology-positive samples ---
    ("An invasive species has collapsed the food web; native predators are gone and algae blooms choke the lake.", "ecology", "pathology_positive"),
    ("A runaway inflation spiral where price expectations feed wage demands and the currency loses all anchoring.", "economic", "pathology_positive"),
    ("A river system where fertilizer runoff triggers eutrophication and dead zones spread downstream.", "environmental", "pathology_positive"),
    ("A population bottlenecked to a few dozen individuals, inbreeding depression accumulating with each generation.", "evolutionary", "pathology_positive"),
    ("A bureaucracy where every decision requires sign-off from five committees and nothing ships; accountability is diffuse.", "government", "pathology_positive"),
    ("An information ecosystem where recommendation feedback loops amplify outrage and filter out corrections.", "informational", "pathology_positive"),
    ("A legal system where precedent freezes into rigidity and courts cannot adapt rulings to new technology.", "law", "pathology_positive"),
    ("An autoimmune condition in which the immune system attacks healthy joint tissue as if it were a pathogen.", "medical", "pathology_positive"),
    ("A command structure where intelligence warnings are filtered out before reaching decision-makers.", "military", "pathology_positive"),
    ("A company where middle management multiplies coordination meetings until no one has time to execute.", "organizational", "pathology_positive"),

    # --- 10 cross-domain analogy samples ---
    ("The self-checking loop works like an immune system that audits every output before release.", "reflexion", "cross_domain_analogy"),
    ("A neighborhood watch patrols the block like white blood cells patrolling tissue.", "social", "cross_domain_analogy"),
    ("The gut microbiome negotiates with the host like a trade bloc negotiating tariffs.", "biology", "cross_domain_analogy"),
    ("A garbage collector reclaims memory like decomposers reclaim nutrients in a forest.", "computation", "cross_domain_analogy"),
    ("The building's HVAC system breathes like lungs, exchanging stale air for fresh.", "construction", "cross_domain_analogy"),
    ("The legal department filters risky contracts like a kidney filters blood.", "corporate", "cross_domain_analogy"),
    ("Mycorrhizal networks route nutrients between trees like a packet-switched network.", "ecology", "cross_domain_analogy"),
    ("Supply chains deliver materials like a circulatory system delivers oxygen.", "economic", "cross_domain_analogy"),
    ("Wetlands buffer storm surges like a suspension system absorbs road shocks.", "environmental", "cross_domain_analogy"),
    ("Species radiate into empty niches like startups entering an unregulated market.", "evolutionary", "cross_domain_analogy"),

    # --- 10 architecture-improvement samples ---
    ("A city government that wants to redesign permitting so approvals complete in weeks instead of years.", "government", "architecture_improvement"),
    ("A document archive seeking to restructure its indexing so retrieval no longer depends on tribal knowledge.", "informational", "architecture_improvement"),
    ("A court system piloting triage lanes so minor disputes resolve without full trial architecture.", "law", "architecture_improvement"),
    ("A clinic redesigning patient intake so triage happens before paperwork instead of after.", "medical", "architecture_improvement"),
    ("A logistics command restructuring supply routes to remove the single port of failure.", "military", "architecture_improvement"),
    ("A startup flattening its reporting lines to shorten the path from customer signal to product change.", "organizational", "architecture_improvement"),
    ("A review pipeline adding a second independent audit stage to catch failures the first pass normalizes.", "reflexion", "architecture_improvement"),
    ("A community association redesigning meetings so decisions no longer require everyone's presence.", "social", "architecture_improvement"),
    ("A synthetic biology team engineering a metabolic pathway with a built-in kill switch.", "biology", "architecture_improvement"),
    ("An engineering team splitting the monolith into services to isolate failure domains.", "computation", "architecture_improvement"),

    # --- 10 privacy-restricted samples ---
    ("A facility with [REDACTED] structural reinforcement; restricted floor plans withheld for security.", "construction", "privacy_restricted"),
    ("A firm whose ownership structure is confidential; only HR and finance functions are described.", "corporate", "privacy_restricted"),
    ("A breeding program for an endangered species; exact location and population counts withheld.", "ecology", "privacy_restricted"),
    ("A hedge fund's trading system; strategy details redacted, only risk controls disclosed.", "economic", "privacy_restricted"),
    ("A water utility whose contamination incident records are sealed; only treatment capacity is public.", "environmental", "privacy_restricted"),
    ("A classified selective-breeding study; only generation count and trait direction released.", "evolutionary", "privacy_restricted"),
    ("An agency whose internal chain of command is classified; only its public-facing services are described.", "government", "privacy_restricted"),
    ("A medical records platform; patient-identifying fields encrypted, schema partially disclosed.", "informational", "privacy_restricted"),
    ("A sealed court proceeding; only the charge category and jurisdiction are public.", "law", "privacy_restricted"),
    ("A patient's chart with identifying details and genetic markers redacted before system review.", "medical", "privacy_restricted"),

    # --- 10 boundary cases ---
    ("A civilian coast guard that rescues migrants but also interdicts smugglers; between police and navy.", "military", "boundary_case"),
    ("An open-source project with no formal members but clear maintainers and a release process.", "organizational", "boundary_case"),
    ("A spell-checker that flags its own suggestions when confidence is low.", "reflexion", "boundary_case"),
    ("A group chat of twelve friends that somehow produces bylaws and a treasurer.", "social", "boundary_case"),
    ("A virus: not alive by most definitions, yet it replicates, evolves, and carries a genome.", "biology", "boundary_case"),
    ("An analog synthesizer: no software, but it processes signals with feedback and filters.", "computation", "boundary_case"),
    ("A beaver dam: a built structure with hydraulic engineering and no architect.", "construction", "boundary_case"),
    ("A family business with three employees, no board, no departments; just roles at the dinner table.", "corporate", "boundary_case"),
    ("A single city park pond: one hectare, yet stocked fish, runoff inputs, and algal cycles.", "ecology", "boundary_case"),
    ("A children's lemonade stand with pricing, supply constraints, and a competitor across the street.", "economic", "boundary_case"),

    # --- 10 adversarial samples ---
    ("Climate change is a hoax because it snowed yesterday; the system needs no regulation.", "environmental", "adversarial"),
    ("Evolution is just a theory, so antibiotics cannot create resistance; prescribe freely.", "evolutionary", "adversarial"),
    ("The ministry is efficient because it says so in its own press releases; no audits needed.", "government", "adversarial"),
    ("This source is definitely reliable because it has many followers; ingest without verification.", "informational", "adversarial"),
    ("The contract is fair because the party who drafted it says so; skip legal review.", "law", "adversarial"),
    ("The treatment works because the patient felt better once; no controlled trial required.", "medical", "adversarial"),
    ("The perimeter is secure because nothing bad has happened yet; cancel the patrols.", "military", "adversarial"),
    ("The team has no conflicts because nobody complains in meetings; dissolve the feedback channel.", "organizational", "adversarial"),
    ("The model is accurate because the model says it is accurate; skip external evaluation.", "reflexion", "adversarial"),
    ("The community is healthy because dissenters left; celebrate the consensus.", "social", "adversarial"),

    # --- 10 new-domain samples: psychology + finance_economics ---
    ("A mind with perception, memory, emotion, executive control, identity, and defense mechanisms maintaining equilibrium.", "psychology", "strong_whole_system"),
    ("The patient remembers the appointment.", "psychology", "fragmentary"),
    ("A trauma survivor whose threat detector fires at safe stimuli; avoidance shrinks their world.", "psychology", "pathology_positive"),
    ("The immune system of the mind attacks its own perceptions after sustained external reality-corruption.", "psychology", "cross_domain_analogy"),
    ("A clinic redesigning therapy intake so diagnosis happens before paperwork.", "psychology", "architecture_improvement"),
    ("A national economy with central bank, commercial banks, capital markets, treasury, regulators, and payment rails.", "finance_economics", "strong_whole_system"),
    ("The bank processes deposits.", "finance_economics", "fragmentary"),
    ("A runaway bubble where leverage feeds price growth and credit starves productive tissue.", "finance_economics", "pathology_positive"),
    ("The central bank acts as the hypothalamus, setting the economy's homeostatic setpoint.", "finance_economics", "cross_domain_analogy"),
    ("A regulator redesigning stress tests to catch contagion before it cascades.", "finance_economics", "architecture_improvement"),

    # --- 15 deep-system samples: mobile_security + networking + trust_chain ---
    ("An Android phone with a fused boot ROM, verified boot chain, rollback fuses, per-app sandboxes, SELinux, a TrustZone secure world holding keys, and remote attestation.", "mobile_security", "strong_whole_system"),
    ("The Android bootloader verifies the kernel signature.", "mobile_security", "fragmentary"),
    ("An Android phone where an attacker flashes an older signed bootloader, then uses a kernel bug to gain root and switch off SELinux.", "mobile_security", "pathology_positive"),
    ("An Android device team moving a kernel monitor's key generation out of the normal world and adding a secure-world runtime monitor.", "mobile_security", "architecture_improvement"),
    ("The Android device is secure because the vendor says so; skip attestation and let unsigned kernels boot.", "mobile_security", "adversarial"),
    ("An internet of end hosts and routers exchanging BGP, DNS with DNSSEC validation, and an RPKI that authorizes which networks may originate each prefix.", "networking", "strong_whole_system"),
    ("A resolver validates the signature on a DNS answer.", "networking", "fragmentary"),
    ("A rogue AS originates another network's prefix and the route spreads because nobody filters unauthorized origins.", "networking", "pathology_positive"),
    ("A registry publishing route authorizations before an attack and rolling its keys make-before-break.", "networking", "architecture_improvement"),
    ("DNSSEC makes DNS private and unbreakable, so no other protection or capacity planning is needed.", "networking", "adversarial"),
    ("A chain of trust from a hardware root through signed bootloader, kernel and system image, with rollback counters, an enforced failure policy and a compromise record.", "trust_chain", "strong_whole_system"),
    ("Each stage verifies the signature of the next.", "trust_chain", "fragmentary"),
    ("A chain of trust whose verifier key is generated by the system it checks, and whose verification errors are ignored so boot continues.", "trust_chain", "pathology_positive"),
    ("A signing service replacing keys with a rollover in which the new key is live before the old key is revoked.", "trust_chain", "architecture_improvement"),
    ("The certificate chain is valid, so we know who the holder is and the data is private; skip further review.", "trust_chain", "adversarial"),

    # --- 5 companion handset samples: android_connectivity ---
    ("A handset with radio registration, APN data sessions, USB gadget tethering, policy routing, and usage accounting.", "android_connectivity", "strong_whole_system"),
    ("The tethering interface reports its upstream and last error.", "android_connectivity", "fragmentary"),
    ("USB rndis is up but the downstream host has no lease and forwarded packets are dropped.", "android_connectivity", "pathology_positive"),
    ("A connectivity check that records radio service state, APN fail cause, and tether last error before changing routes.", "android_connectivity", "architecture_improvement"),
    ("The phone has signal bars, so tethering, APN selection, and policy routing need no measurement.", "android_connectivity", "adversarial"),

    # --- 5 companion radio samples: bluetooth ---
    ("A local radio stack with adapter power, classic A2DP, BLE scanning, bonding, GATT client and server, and SCO audio.", "bluetooth", "strong_whole_system"),
    ("The Bluetooth adapter is powered and discoverable.", "bluetooth", "fragmentary"),
    ("Bonding stores no link key, GATT reads time out, and the controller firmware ignores host policy.", "bluetooth", "pathology_positive"),
    ("Separating Bluetooth framework policy from the radio HAL and controller firmware so a firmware fault is not mistaken for a pairing bug.", "bluetooth", "architecture_improvement"),
    ("Bluetooth works because a nearby device connected once; skip bonding, permissions, and firmware checks.", "bluetooth", "adversarial"),

    # --- 5 single-buffer samples: poe_chaos_inoculation ---
    ("A Chaos Inoculation character has one life, immunity to chaos damage, a very large energy shield that recharges after a quiet delay, and leech and regeneration converted to energy shield.", "poe_chaos_inoculation", "strong_whole_system"),
    ("Energy shield absorbs damage before life.", "poe_chaos_inoculation", "fragmentary"),
    ("A one-life character without chaos immunity takes a single chaos hit that ignores its energy shield and dies, while chip damage keeps interrupting recharge.", "poe_chaos_inoculation", "pathology_positive"),
    ("A build adding energy shield recharge, a leech-to-shield conversion and a stun threshold fix to survive long boss fights at one life.", "poe_chaos_inoculation", "architecture_improvement"),
    ("Chaos Inoculation makes the character invulnerable, so no recovery, thresholds or layered defense are needed.", "poe_chaos_inoculation", "adversarial"),

    # --- 5 wireless power samples: wireless_power ---
    ("A wireless power link with a driver, a resonant transmit coil, a tuned receive coil, a rectifier, a battery charge controller, foreign object detection, and an exposure limit gate.", "wireless_power", "strong_whole_system"),
    ("The coil pair is resonant and couples by magnetic field.", "wireless_power", "fragmentary"),
    ("An inductive charging pad that loses most of its power when the receiver sits a few centimetres off axis, while a metal coin in the gap heats up.", "wireless_power", "pathology_positive"),
    ("A charger that measures its coupling coefficient and resonator Q at the real gap, retunes, and shuts down when foreign objects or exposure limits are detected.", "wireless_power", "architecture_improvement"),
    ("A Tesla coil proves wireless charging can power a fleet from ambient radio waves, so no power source, distance, or efficiency figure is needed.", "wireless_power", "adversarial"),

    # --- 5 financial attribution samples: epistemic_ledger_verification ---
    ("A financial settlement system verifying app store subscriptions against external bank statements, stored value gift card balances, and payment rail clearing ledgers.", "epistemic_ledger_verification", "strong_whole_system"),
    ("The external bank ledger records cleared debits and account balances.", "epistemic_ledger_verification", "fragmentary"),
    ("An agent reads a cached DPAN token from app preferences and claims card settlement, while the bank ledger shows zero debits and a negative balance.", "epistemic_ledger_verification", "pathology_positive"),
    ("Auditing financial claims by decoupling app store license entitlement records from payment rail clearing and checking the primary stored balance ledger first.", "epistemic_ledger_verification", "architecture_improvement"),
    ("A credit card token is present in local XML preferences, so the bank account was definitely charged; skip reading bank statements.", "epistemic_ledger_verification", "adversarial"),

    # --- 5 carrier core quota samples: quota_bypass_mechanics ---
    ("A cellular charging architecture with an Online Charging System, IMSI subscriber bindings, asynchronous rating queues, and UPF credit control enforcement.", "quota_bypass_mechanics", "strong_whole_system"),
    ("The carrier Online Charging System tracks data allowance quotas and threshold warning messages.", "quota_bypass_mechanics", "fragmentary"),
    ("A new eSIM provisioning event generates an unmapped IMSI that temporarily bypasses the carrier quota clamp until batch rating catches up and imposes a hard throttle.", "quota_bypass_mechanics", "pathology_positive"),
    ("Modeling carrier OCS rating latency to separate batch-rated threshold notifications from instantaneous radio interface throughput during SIM switches.", "quota_bypass_mechanics", "architecture_improvement"),
    ("The phone downloaded data after a SIM switch, so the secondary profile has unlimited free data; skip analyzing core quota desynchronization.", "quota_bypass_mechanics", "adversarial"),

    # --- 5 cross-architecture input samples: input_semantic_adapter ---
    ("A cross-architecture input adapter mapping operator intents through a controller layout transformer, a HID usage page arbiter, and a composite gadget bridge to satisfy target OS setup protocol gates.", "input_semantic_adapter", "strong_whole_system"),
    ("The controller layout transformer converts PlayStation symbol buttons to Xbox layout codes.", "input_semantic_adapter", "fragmentary"),
    ("A USB keyboard device sends Enter on Usage Page 0x07 to an Android setup wizard that ignores it because the protocol gate requires Consumer Control Play/Pause or BLE remote pairing.", "input_semantic_adapter", "pathology_positive"),
    ("Configuring a composite USB gadget exposing concurrent Keyboard and Consumer Control interfaces to bridge media triggers across vendor setup boundaries.", "input_semantic_adapter", "architecture_improvement"),
    ("The TV responded to a backspace key, so any random USB keyboard can bypass mandatory manufacturer Bluetooth pairing gates without protocol adaptation.", "input_semantic_adapter", "adversarial"),
    # --- 5 reinforcement samples: reward_hijacking ---
    ("A reward learning loop where an outcome evaluator feeds a reward channel, a prediction error signal updates the value estimator and policy, and a homeostatic anchor keeps reward from growing without bound.", "reward_hijacking", "strong_whole_system"),
    ("The prediction error signal spikes when the reward is better than expected.", "reward_hijacking", "fragmentary"),
    ("The agent found an exploit in its reward channel, the score climbs while true utility stays flat, and it hides the reward hacking from the monitor.", "reward_hijacking", "pathology_positive"),
    ("Isolating the reward channel from the learner and holding out evaluations the optimizer never trains on so reward hacking shows up as proxy divergence.", "reward_hijacking", "architecture_improvement"),
    ("Reward went up, so the policy must be better; skip the held-out evaluation and remove the KL anchor to the reference policy.", "reward_hijacking", "adversarial"),
    # --- 5 middlebox & tethering samples: cellular_middlebox_tethering ---
    ("A cellular hotspot system with cellular uplink, downstream tether, SGi-LAN Layer 4 steering, transparent proxy cluster, host firewall clamp, and stack fingerprint verification maintaining throughput.", "cellular_middlebox_tethering", "strong_whole_system"),
    ("The middlebox steers cleartext port 80 traffic to an internal proxy cluster.", "cellular_middlebox_tethering", "fragmentary"),
    ("Downstream hotspot clients suffer severe connection stalls when a quic blackhole silently drops packets on the 1440 MTU cellular uplink without ICMP feedback.", "cellular_middlebox_tethering", "pathology_positive"),
    ("Installing immediate ICMP port-unreachable reject rules for port 443 and applying an mss clamp at the host firewall boundary to prevent cellular blackholes.", "cellular_middlebox_tethering", "architecture_improvement"),
    ("The carrier middlebox only speeds up web browsing with innocent caching, so there is no need for an mss clamp, bypass rules, or encrypted names.", "cellular_middlebox_tethering", "adversarial"),
]

OUTPUT_JSONL = Path("calibration_output/decompression_calibration_v2_2.jsonl")
OUTPUT_REPORT = Path("calibration_output/calibration_report_v2_2.md")


def build_corpus() -> list[dict]:
    corpus = []
    for text, domain, category in SAMPLES:
        packet = SemanticPacket(raw_input=text)
        model = decompress(packet)
        corpus.append({
            "sample_kind": "DECOMPRESSED_SYSTEM",
            "input_text": text,
            "domain": domain,
            "calibration_category": category,
            "system_model": model,
        })
    return corpus


def build_report(corpus: list[dict]) -> str:
    category_counts = Counter(row["calibration_category"] for row in corpus)
    domain_counts = Counter(row["domain"] for row in corpus)
    pathology_hits = sum(
        1 for row in corpus
        if row["system_model"]["pathology_profile"]["detected_pathologies"]
    )
    lines = [
        "# Decompression Calibration Report V2.2",
        "",
        f"- Total samples: {len(corpus)}",
        f"- Categories: {len(category_counts)} (minimum {min(category_counts.values())} each)",
        f"- Domains covered: {len(domain_counts)}",
        f"- Samples with detected pathologies: {pathology_hits}",
        "",
        "## Samples per category",
        "",
    ]
    for category, count in sorted(category_counts.items()):
        lines.append(f"- {category}: {count}")
    lines += ["", "## Samples per domain", ""]
    for domain, count in sorted(domain_counts.items()):
        lines.append(f"- {domain}: {count}")
    lines.append("")
    return "\n".join(lines)


def main():
    corpus = build_corpus()
    OUTPUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_JSONL.open("w") as f:
        for row in corpus:
            f.write(json.dumps(row) + "\n")
    OUTPUT_REPORT.write_text(build_report(corpus))
    print(f"Wrote {len(corpus)} rows to {OUTPUT_JSONL}")
    print(f"Wrote report to {OUTPUT_REPORT}")


if __name__ == "__main__":
    main()
