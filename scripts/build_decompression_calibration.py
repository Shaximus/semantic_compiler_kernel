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

# 80 calibration samples: 8 categories x 10, distributed across the 16
# non-generic domains (exactly 5 samples per domain).
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
        f"- Categories: {len(category_counts)} (10 each)",
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
