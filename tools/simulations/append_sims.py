"""Append scored simulations from one or more sims_*.py modules to gtplaybook/data/simulations.json.

Usage (from the project root):  python3 tools/simulations/append_sims.py sims_k sims_l
Refuses to add an id that already exists, so nothing in the JSON is replaced.
"""

import importlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from build_core import build_scored  # noqa: E402

TARGET = HERE.parents[1] / "gtplaybook" / "data" / "simulations.json"


def main(module_names):
    data = json.loads(TARGET.read_text(encoding="utf-8"))
    ids = {sim["id"] for sim in data}
    added = 0
    for name in module_names:
        for spec in importlib.import_module(name).SIMS:
            if spec["id"] in ids:
                raise SystemExit(f"'{spec['id']}' already exists; rename it before appending")
            data.append(dict(build_scored(spec), mode="basic"))
            ids.add(spec["id"])
            added += 1
    TARGET.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"added {added}; total {len(data)}")


if __name__ == "__main__":
    main(sys.argv[1:])
