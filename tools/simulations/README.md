# Simulation sources

`simulations.json` in `gtplaybook/data/` is generated from these files. To change a simulation, edit its spec in `sims_*.py` (scored trees: rounds, options with scores and reasons, and chance branches), then rebuild:

    python3 tools/simulations/build_all.py gtplaybook/data/simulations.json
    make build

`gen_sims.py` holds the seven original state-based simulations. Run `python3 -m unittest discover -s tests` afterwards to confirm every simulation still has reachable victory and failure paths.
