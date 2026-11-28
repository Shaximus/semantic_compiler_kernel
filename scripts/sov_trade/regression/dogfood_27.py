"""Regression dogfood: 27 routing/compile prompts (vendored from the box harness
batch-2026-11-25g/dogfood.py so `make verify` can diff base vs head from a clean clone)."""
import json, sys
from semantic_compiler import compile_semantic_packet
from semantic_compiler.expansion.router import route_domains
from semantic_compiler.expansion.elevator import summon

PROMPTS = {
 "id_goku": "Explain SC-LU-GOKU-001.",
 "id_cell": "Explain SC-LU-CELL-001.",
 "id_trunks": "Explain SC-LU-TRUNKS-001.",
 "id_vegeta": "Explain SC-LU-VEGETA-001.",
 "goku_open": "Goku learns from every opponent and gathers the Spirit Bomb from willing donors: an open architecture, the Oneness pole.",
 "goku_ui": "Ultra Instinct removes the observer while Ultra Ego amplifies the self: Goku and Vegeta as Oneness and Sovereignty.",
 "goku_fusion": "Goku and Vegeta fuse into Vegito and Gogeta: the cooperation branch of the binary.",
 "kakarot": "Kakarot was sent to Earth as an infant and forgot his mission after hitting his head.",
 "perfect_cell": "Perfect Cell absorbed Androids 17 and 18 and held the Cell Games to prove his designed perfection, then lost to Gohan's Super Saiyan 2.",
 "cell_goodhart": "Perfect Cell is Goodhart's law: a benchmark-saturated model that mistakes its own tournament for the target.",
 "future_trunks": "Future Trunks travelled back to save a timeline that was not his own, and Future Zeno later erased his future.",
 "last_crown": "Vegeta, the last crown: he learned from Dodoria that Frieza destroyed Planet Vegeta and was angry for himself, not for the planet.",
 "mbs_backup": "The Frieza chamber sits in the mirrored universe, the CPT backup snapshot of ours.",
 "ctrl_cellphone": "My cell phone battery dies by noon, what should I check?",
 "ctrl_excel": "How do I lock a cell in Excel so nobody can edit it?",
 "ctrl_stemcell": "Are stem cell treatments for knee arthritis worth it?",
 "ctrl_fuelcell": "How efficient are hydrogen fuel cells compared to batteries?",
 "ctrl_prison": "How big is a typical prison cell in Canada?",
 "ctrl_swim": "Where can I buy swim trunks for a beach vacation?",
 "ctrl_cartrunk": "My car trunk will not open with the key fob.",
 "ctrl_tree": "How do I measure the diameter of a tree trunk?",
 "ctrl_elephant": "How many muscles are in an elephant trunk?",
 "ctrl_future": "What will the future of remote work look like?",
 "ctrl_crown": "How much does a dental crown cost without insurance?",
 "ctrl_prince": "My son wants a prince costume for Halloween.",
 "ctrl_instinct": "Should I trust my gut instinct about this job offer?",
 "ctrl_alarm": "Can you set an alarm for 7am tomorrow?",
}
out = {}
for k, text in PROMPTS.items():
    r = route_domains(text)
    p = compile_semantic_packet(text)
    d = summon(text, top_k=3)
    ents = [e.entry_id for e in d.compiled_entries][:5]
    out[k] = {"text": text, "route": r.outcome, "domain": r.domain, "conf": round(r.confidence, 3),
              "cands": [(c.domain, round(c.score, 1)) for c in r.candidates[:3]],
              "decision": p.decision.name, "route_to": p.route_to,
              "fit": round(p.scores.get("structural_fit", -1), 3), "selected_target": p.selected_target,
              "warnings": p.compiler_warnings[:4], "summon_entries": ents}
    print(f"{k:22} {r.outcome:9} {str(r.domain):24} conf={r.confidence:.2f} tgt={str(p.selected_target):22} dec={out[k]['decision']:16} fit={out[k]['fit']} entries={ents}")
if len(sys.argv) > 1:
    json.dump(out, open(sys.argv[1], "w"), indent=1)
