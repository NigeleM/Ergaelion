"""Build data/simulations.json from the scored specs and the seven original simulations."""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import gen_sims  # noqa: E402
import sims_a  # noqa: E402
import sims_b  # noqa: E402
import sims_c  # noqa: E402
import sims_d  # noqa: E402
import sims_e  # noqa: E402
import sims_f  # noqa: E402
import sims_g  # noqa: E402
import sims_h  # noqa: E402
import sims_i  # noqa: E402
import sims_j  # noqa: E402
import sims_k  # noqa: E402
import sims_l  # noqa: E402
import sims_m  # noqa: E402
import sims_n  # noqa: E402
import sims_o  # noqa: E402
import sims_p  # noqa: E402
import sims_q  # noqa: E402
import sims_r  # noqa: E402
from build_core import build_scored  # noqa: E402
from full_rules import FULL_RULES  # noqa: E402
from state_games import build_state_game  # noqa: E402

LEGACY_FAMILIES = {
    "salary-negotiation": ["Work games", "Negotiation and fairness", "Life games"],
    "vs-tit-for-tat": ["Games against AI", "Classic game theory"],
    "commons-two-seasons": ["Public goods and environment", "Life games"],
    "regime-survival": ["Government and politics", "Society and groups"],
    "nonviolent-campaign": ["Government and politics", "Society and groups"],
    "cult-exit-decision": ["Society and groups", "Life games"],
    "sealed-bid-auction": ["Business and markets", "Economics and finance"],
}


LIVE_LEGACY = {"vs-tit-for-tat"}


def legacy():
    out = []
    for make in (gen_sims.salary, gen_sims.tit_for_tat, gen_sims.commons, gen_sims.regime,
                 gen_sims.campaign, gen_sims.cult_exit, gen_sims.auction):
        defn = make()
        built = gen_sims.build(defn)
        out.append({
            "id": defn["id"],
            "name": defn["name"],
            "families": LEGACY_FAMILIES[defn["id"]],
            "summary": defn["summary"],
            "start": built["start"],
            "mode": "live" if defn["id"] in LIVE_LEGACY else "basic",
            "nodes": built["nodes"],
        })
    return out


def main(out_path):
    specs = sims_a.SIMS + sims_b.SIMS + sims_c.SIMS + sims_d.SIMS + sims_e.SIMS + sims_f.SIMS + sims_g.SIMS + sims_h.SIMS + sims_i.SIMS + sims_j.SIMS + sims_k.SIMS + sims_l.SIMS + sims_m.SIMS + sims_n.SIMS + sims_o.SIMS + sims_p.SIMS + sims_q.SIMS + sims_r.SIMS
    scored = [dict(build_scored(spec), mode="basic") for spec in specs]
    live = [build_state_game(spec) for spec in FULL_RULES]
    # The snapshot holds every simulation as it stands in the data file, including hand edits made
    # after generation. An id in the snapshot always wins; the scripts only add ids it does not have.
    snapshot = json.loads((HERE / "kept_sims.json").read_text(encoding="utf-8"))
    kept_ids = {sim["id"] for sim in snapshot}
    generated = [sim for sim in legacy() + scored + live if sim["id"] not in kept_ids]
    everything = snapshot + generated
    ids = [s["id"] for s in everything]
    assert len(ids) == len(set(ids)), "duplicate simulation ids"
    Path(out_path).write_text(json.dumps(everything, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(everything)} simulations ({len(scored)} basic, {len(live)} live) to {out_path}")


if __name__ == "__main__":
    main(sys.argv[1])
