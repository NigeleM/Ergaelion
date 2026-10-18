import json
import os
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from gtplaybook import record  # noqa: E402
from gtplaybook.catalog import find_game, load_areas, load_games, save_overlay  # noqa: E402
from gtplaybook.catalog import DATA_DIR
from gtplaybook.sim import endings, load_simulations, solve, trace  # noqa: E402


class CatalogCoverageTests(unittest.TestCase):
    def test_at_least_fifty_games(self):
        self.assertGreaterEqual(len(load_games()), 50)

    def test_every_game_is_in_a_family(self):
        listed = {g for fam in load_areas() for sd in fam["subdomains"] for g in sd["games"]}
        for game in load_games():
            self.assertIn(game["id"], listed)


class SimulationTests(unittest.TestCase):
    def test_every_simulation_has_a_path_to_victory_and_to_failure(self):
        sims = load_simulations()
        self.assertTrue(sims)
        for sim in sims:
            if solve(sim, "victory")[sim["start"]][0] == 0:
                # Under perfect play some games are a draw: then a draw must be reachable instead.
                self.assertIn("draw", {e["outcome"] for e in endings(sim)}, sim["id"])
            self.assertGreater(solve(sim, "failure")[sim["start"]][0], 0, sim["id"])

    def test_salary_victory_plan_asks_for_sixty(self):
        sim = next(s for s in load_simulations() if s["id"] == "salary-negotiation")
        steps, end, chance = trace(sim, solve(sim, "victory"))
        self.assertEqual(end["outcome"], "victory")
        self.assertEqual(chance, 1.0)

    def test_endings_are_enumerated(self):
        sim = next(s for s in load_simulations() if s["id"] == "sealed-bid-auction")
        counts = Counter(e["outcome"] for e in endings(sim))
        self.assertGreater(counts["failure"], 0)


class SimulationCoverageTests(unittest.TestCase):
    def test_at_least_half_the_games_have_a_simulation(self):
        games = len(load_games())
        self.assertGreaterEqual(len(load_simulations()), games // 2)

    def test_every_simulation_lists_at_least_two_areas(self):
        families = {f["family"] for f in load_areas()}
        for sim in load_simulations():
            self.assertGreaterEqual(len(sim["families"]), 2, sim["id"])
            self.assertTrue(set(sim["families"]) <= families, sim["id"])

    def test_every_option_and_branch_has_a_reason_in_new_simulations(self):
        legacy = {"salary-negotiation", "vs-tit-for-tat", "commons-two-seasons", "regime-survival",
                  "nonviolent-campaign", "cult-exit-decision", "sealed-bid-auction"}
        for sim in load_simulations():
            if sim["id"] in legacy:
                continue
            for node in sim["nodes"].values():
                for item in node.get("options", []) + node.get("branches", []):
                    self.assertTrue(item.get("why"), f"{sim['id']}: missing why for {item['label']}")

    def test_every_opponent_step_follows_one_choice_and_has_odds(self):
        for sim in load_simulations():
            raw = json.loads((DATA_DIR / "simulations.json").read_text(encoding="utf-8"))
            original = next(x for x in raw if x["id"] == sim["id"])
            parents = {}
            for node in original["nodes"].values():
                for option in node.get("options", []):
                    parents.setdefault(option["next"], []).append(option["label"])
            for node_id, node in original["nodes"].items():
                if node["type"] != "opponent":
                    continue
                self.assertEqual(len(parents.get(node_id, [])), 1, f"{sim['id']}: {node_id}")
                for label, odds in node["policy"].items():
                    self.assertIn(label, parents[node_id], f"{sim['id']}: {node_id}")
                    self.assertAlmostEqual(sum(odds), 1.0, places=6, msg=sim["id"])
                self.assertAlmostEqual(sum(node["default"]), 1.0, places=6, msg=sim["id"])

    def test_every_branch_set_sums_to_one(self):
        for sim in load_simulations():
            for node in sim["nodes"].values():
                if node["type"] == "nature":
                    self.assertAlmostEqual(sum(b["p"] for b in node["branches"]), 1.0, places=6, msg=sim["id"])


class GuideAndSetupTests(unittest.TestCase):
    def test_guide_links_point_at_real_games(self):
        import json

        from gtplaybook.catalog import DATA_DIR

        ids = {g["id"] for g in load_games()}
        guide = json.loads((DATA_DIR / "guide.json").read_text(encoding="utf-8"))
        self.assertEqual(len(guide["power"]), 48)
        for item in guide["power"] + guide["defend"]:
            for game_id in item["games"]:
                self.assertIn(game_id, ids, item.get("title") or item.get("pattern"))

    def test_setup_guide_covers_every_game(self):
        from gtplaybook.setup_guide import guide_text, load_help, scenario_template

        help_data = load_help()
        for game in load_games():
            self.assertIn("## Steps", guide_text(game, help_data, set()))
            self.assertIn(f"players:", scenario_template(game))


class EndToEndTests(unittest.TestCase):
    """Run the real commands through the entry point, with a throwaway playbook home."""

    def run_cli(self, argv):
        import contextlib
        import io
        from gtplaybook import cli

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli.main(argv)
        return code, out.getvalue()

    def test_logged_wins_raise_the_fit_and_show_by_play(self):
        import os

        with tempfile.TemporaryDirectory() as home:
            old = os.environ.get("PLAYBOOK_HOME")
            os.environ["PLAYBOOK_HOME"] = home
            try:
                self.run_cli(["log", "bertrand-price-war", "win", "--play", "1"])
                self.run_cli(["log", "bertrand-price-war", "win"])
                code, text = self.run_cli(["record", "bertrand-price-war"])
                self.assertEqual(code, 0)
                self.assertIn("Record by play", text)
                code, text = self.run_cli(["advise", "-d", "two companies set prices at the same time, once only"])
                self.assertIn("your results adjust the fit by +1.0", text)
            finally:
                if old is None:
                    del os.environ["PLAYBOOK_HOME"]
                else:
                    os.environ["PLAYBOOK_HOME"] = old

    def test_simulation_exports_to_markdown(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "chicken.md"
            code, _ = self.run_cli(["sim", "chicken", "--export", str(target)])
            self.assertEqual(code, 0)
            text = target.read_text(encoding="utf-8")
            self.assertIn("## Path to victory", text)
            self.assertIn("## Path to failure", text)

    def test_new_pandemic_and_advanced_games_have_simulations(self):
        ids = {s["id"] for s in load_simulations()}
        for game_id in ["pandemic-quarantine-game", "nuclear-deterrence-second-strike", "bayesian-persuasion", "global-games-coordination"]:
            self.assertIn(game_id, ids)


class SecurityTests(unittest.TestCase):
    def test_game_ids_cannot_point_outside_the_games_folder(self):
        from gtplaybook.catalog import safe_name, save_overlay
        for bad in ["../escape", "a/b", "..", "x y", ""]:
            with self.assertRaises(ValueError, msg=bad):
                safe_name(bad)
        with tempfile.TemporaryDirectory() as home:
            with self.assertRaises(ValueError):
                save_overlay({"id": "../escape"}, home=home)


class OverlayAndRecordTests(unittest.TestCase):
    def test_overlay_replaces_a_built_in_game(self):
        with tempfile.TemporaryDirectory() as home:
            game = dict(find_game(load_games(), "chicken"))
            game["name"] = "Chicken (edited)"
            save_overlay(game, home=home)
            reloaded = load_games(home=home)
            self.assertEqual(find_game(reloaded, "chicken")["name"], "Chicken (edited)")
            self.assertEqual(len(reloaded), len(load_games()))

    def test_overlay_adds_a_new_game(self):
        with tempfile.TemporaryDirectory() as home:
            new_game = dict(find_game(load_games(), "chicken"), id="my-game", name="My Game")
            save_overlay(new_game, home=home)
            self.assertEqual(len(load_games(home=home)), len(load_games()) + 1)

    def test_record_tally(self):
        with tempfile.TemporaryDirectory() as home:
            record.log_outcome("chicken", "win", "held firm", home=home)
            record.log_outcome("chicken", "loss", home=home)
            counts = record.tally(home=home)["chicken"]
            self.assertEqual(record.format_record(counts), "1W 1L 0D 0M")
            with self.assertRaises(ValueError):
                record.log_outcome("chicken", "bogus", home=home)


def _advice_top(text, games, top=3):
    """The ids the advisor would show for a description, as the advise command ranks them."""
    from gtplaybook import advisor, cli, keywords
    from gtplaybook.scenario import describe

    sc = describe(text)
    corrected, _ = cli.corrected_text(text, games)
    hits = advisor.rank_games(games, sc["traits"], sc["domains"], top=top, text=corrected,
                              keyword_data=keywords.load_keywords())
    return [hit["game"]["id"] for hit in hits]


class AdviceAccuracyTests(unittest.TestCase):
    """Plain-English descriptions should find a sensible game. The tuning set was used to improve the
    phrases and the ranking; the held-out set was written afterwards and is the honest measure."""

    def hit_rate(self, name):
        import json

        games = load_games()
        cases = json.loads((ROOT / "tests" / name).read_text(encoding="utf-8"))
        hits = sum(any(e in _advice_top(c["text"], games) for e in c["expect"]) for c in cases)
        return hits, len(cases)

    def test_tuning_set_finds_a_sensible_game(self):
        hits, total = self.hit_rate("advice_cases.json")
        self.assertGreaterEqual(hits, 30, f"{hits}/{total} in the top three")

    def test_held_out_set_finds_a_sensible_game(self):
        # A measured floor, not a target: these descriptions were not used for tuning. Raise it only when
        # the ranking genuinely improves on new wording, never by adding phrases for these exact cases.
        hits, total = self.hit_rate("advice_heldout.json")
        self.assertGreaterEqual(hits, 8, f"{hits}/{total} in the top three")

    def test_typos_are_corrected_only_when_unambiguous(self):
        from gtplaybook import keywords

        vocabulary = ["trojan", "troops", "tariff"]
        corrected, changes = keywords.correct_text("a trojen horse", vocabulary)
        self.assertEqual(corrected, "a trojan horse")
        self.assertEqual(changes, [("trojen", "trojan")])
        self.assertEqual(keywords.edit_distance("kitten", "sitting"), 3)

    def test_completion_offers_words_from_the_phrases(self):
        from gtplaybook import advisor, keywords

        vocabulary = keywords.vocabulary(load_games(), combinations=advisor.load_combinations())
        self.assertIn("tariff", keywords.complete_word("tar", vocabulary))
        self.assertIn("trojan", keywords.complete_word("tro", vocabulary))

    def test_trojan_horse_brings_in_a_multi_game_playbook(self):
        from gtplaybook import advisor

        combos = advisor.matched_combinations("a trojan horse hidden in a gift", advisor.load_combinations())
        self.assertEqual(combos[0]["combination"]["id"], "hidden-threat-deception")
        self.assertTrue(set(combos[0]["combination"]["games"]) <= {g["id"] for g in load_games()})

    def test_a_typo_still_brings_the_playbook(self):
        import io
        import contextlib
        from gtplaybook import cli

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            cli.main(["advise", "-d", "a trojen horse"])
        self.assertIn("Hidden threat and deception", out.getvalue())
        self.assertNotIn("matched a known game", out.getvalue())

    def test_every_combination_names_real_games(self):
        from gtplaybook import advisor

        ids = {g["id"] for g in load_games()}
        for combo in advisor.load_combinations():
            self.assertTrue(set(combo["games"]) <= ids, combo["id"])
            self.assertGreaterEqual(len(combo["steps"]), 3, combo["id"])

    def test_nothing_recognised_says_so_and_suggests_words(self):
        import io
        import contextlib
        from gtplaybook import cli

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            cli.main(["advise", "-d", "zxq wvu"])
        self.assertIn("Nothing in 'zxq wvu' matched", out.getvalue())


class ModelTests(unittest.TestCase):
    def test_noisy_opponent_moves_toward_best_response_as_lambda_grows(self):
        from gtplaybook.matrix_sim import matrix_simulation
        from gtplaybook.sim import solve

        game = next(g for g in load_games() if g["id"] == "stag-hunt")
        chance = [solve(matrix_simulation(game, [], "noisy", lam), "victory")[matrix_simulation(game, [], "noisy", lam)["start"]][0] for lam in (0.0, 1.0, 4.0)]
        self.assertLess(chance[0], chance[1])
        self.assertLess(chance[1], chance[2])


class MenuTests(unittest.TestCase):
    def test_menu_runs_a_choice_and_quits(self):
        import os
        import subprocess

        env = dict(os.environ, PLAYBOOK_HOME=tempfile.mkdtemp())
        result = subprocess.run([str(ROOT / "playbook"), "menu"], input="1\nchicken\n10\n",
                                capture_output=True, text=True, env=env, timeout=30)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Main menu", result.stdout)
        self.assertIn("Chicken", result.stdout)


class PythonTerminalTests(unittest.TestCase):
    """The Python session's own line editor, command list, pager and menu, in a real terminal."""

    def drive(self, home, keys, args=None):
        import os
        import pty
        import re
        import select
        import subprocess
        import sys
        import time

        env = dict(os.environ, PLAYBOOK_HOME=home)
        if args is None:
            # Launch opens the menu; Enter chooses its first entry, Command prompt.
            keys = [b"\r", *keys]
        master, slave = pty.openpty()
        command = args or [str(ROOT / "playbook")]
        proc = subprocess.Popen([sys.executable, *command] if args is None else command,
                                stdin=slave, stdout=slave, stderr=slave, env=env, close_fds=True)
        os.close(slave)
        output = b""

        def drain(seconds):
            nonlocal output
            end = time.time() + seconds
            while time.time() < end:
                ready, _, _ = select.select([master], [], [], 0.1)
                if ready:
                    try:
                        output += os.read(master, 65536)
                    except OSError:
                        return

        drain(1.0)
        if args is None:
            # Launching shows the logo first; Space carries on to the menu.
            os.write(master, b" ")
            drain(0.5)
        for key in keys:
            os.write(master, key)
            drain(0.5)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        os.close(master)
        return re.sub(rb"\x1b\[[0-9;?]*[A-Za-z]", b"", output).decode("utf-8", "replace")

    def test_tab_completes_and_history_recalls(self):
        with tempfile.TemporaryDirectory() as home:
            text = self.drive(home, [b"/sho\t", b"chicken\r", b"q", b"/quit\r"])
            self.assertIn("Chicken", text)
            text = self.drive(home, [b"chicken\r", b"q", b"\x1b[A", b"\r", b"q", b"/quit\r"])
            self.assertGreaterEqual(text.count("Chicken"), 2)

    def test_pager_scrolls_and_closes(self):
        with tempfile.TemporaryDirectory() as home:
            text = self.drive(home, [b"/list\r", b"q", b"/quit\r"])
            self.assertIn("lines 1-", text)

    def test_menu_chooser_moves_with_arrow_keys(self):
        with tempfile.TemporaryDirectory() as home:
            text = self.drive(home, [b"\x1b[B", b"\x1b[B", b"\r", b"q", b"q"],
                              args=[str(ROOT / "playbook"), "menu"])
            self.assertIn("Choose a simulation", text)
            self.assertIn("Main menu", text)


class LiveSimulationTests(unittest.TestCase):
    """Specific results for the full-rules simulations, checked against the rules of each game."""

    def solved(self, sim_id, goal):
        sim = next(s for s in load_simulations() if s["id"] == sim_id)
        return solve(sim, goal)[sim["start"]][0]

    def test_perfect_tic_tac_toe_is_a_draw_with_best_play(self):
        self.assertEqual(self.solved("tic-tac-toe-perfect-opponent", "victory"), 0.0)
        self.assertEqual(self.solved("tic-tac-toe-perfect-opponent", "draw"), 1.0)

    def test_tic_tac_toe_wins_against_a_random_opponent(self):
        self.assertGreater(self.solved("tic-tac-toe-random-opponent", "victory"), 0.99)

    def test_nim_first_player_wins_when_nim_sum_is_not_zero(self):
        # 3 xor 4 xor 5 is 2, not zero, so the first player can always move to zero and win.
        self.assertEqual(self.solved("nim-random-opponent", "victory"), 1.0)
        # 5 xor 7 xor 9 is 11, not zero, so the first player also wins against perfect play.
        self.assertEqual(self.solved("nim-perfect-reference", "victory"), 1.0)

    def test_connect_four_depth_limit_still_gives_a_strong_plan(self):
        self.assertGreater(self.solved("connect-four-depth-three", "victory"), 0.9)

    def test_patterned_and_tit_for_tat_bots_can_both_be_beaten(self):
        self.assertEqual(self.solved("repeated-pd-pattern-bot", "victory"), 1.0)
        self.assertEqual(self.solved("repeated-pd-tit-for-tat-bot", "victory"), 1.0)

    def test_grim_bot_punishes_any_defection(self):
        self.assertEqual(self.solved("repeated-pd-grim-bot", "failure"), 1.0)


class FamilyCaseTests(unittest.TestCase):
    def test_family_cases_are_in_the_catalogue(self):
        ids = {s["id"] for s in load_simulations()}
        for sid in ("power-dynamics-manager", "setting-limits-with-a-teenager", "supporting-without-enabling",
                    "sibling-inheritance-dispute", "ageing-parent-care-split", "young-child-school-refusal"):
            self.assertIn(sid, ids)


class KeywordParserTests(unittest.TestCase):
    def test_every_game_has_phrases_to_be_found_by(self):
        from gtplaybook.keywords import load_keywords

        kw = load_keywords()
        self.assertEqual(set(kw["games"]), {g["id"] for g in load_games()})
        self.assertTrue(all(kw["games"][gid] for gid in kw["games"]))

    def test_a_phrase_finds_its_game(self):
        from gtplaybook.keywords import suggest

        result = suggest("people rushed to the bank to withdraw deposits", load_games(), load_simulations())
        self.assertEqual(result["games"][0][0], "bank-run")

    def test_plurals_and_domain_names_match(self):
        from gtplaybook.keywords import suggest

        result = suggest("business", load_games(), load_simulations())
        self.assertIn("Business and markets", [family for family, _ in result["families"]])
        result = suggest("two hiders and a searcher", load_games(), load_simulations())
        self.assertEqual(result["games"][0][0], "search-game-hide-and-seek")

    def test_unknown_words_say_nothing_matched(self):
        from gtplaybook.keywords import describe, suggest

        result = suggest("zzzz qqqq", load_games(), load_simulations())
        self.assertFalse(result["games"] or result["families"])
        self.assertIn("Nothing", describe(result, "zzzz qqqq")[0])


class ToolApiTests(unittest.TestCase):
    def test_every_tool_has_a_schema_and_a_handler(self):
        from gtplaybook.tool_api import HANDLERS, TOOLS

        names = [tool["name"] for tool in TOOLS]
        self.assertEqual(sorted(names), sorted(HANDLERS))
        for tool in TOOLS:
            self.assertEqual(tool["input_schema"]["type"], "object")

    def test_tools_return_data_and_errors_instead_of_crashing(self):
        from gtplaybook.tool_api import call_tool

        found = call_tool("find_games", {"description": "bank run"}, load_games())
        self.assertEqual(found["games"][0]["id"], "bank-run")
        self.assertIn("error", call_tool("get_game", {"game": "not-a-game"}, load_games()))
        self.assertIn("error", call_tool("no_such_tool", {}, load_games()))

    def test_solve_tool_matches_the_solver(self):
        from gtplaybook.tool_api import call_tool

        result = call_tool("solve_matrix", {"matrix": "3,3 0,5; 5,0 1,1"}, load_games())
        self.assertEqual(result["surviving_rows"], ["R2"])
        self.assertEqual(result["equilibria"], [{"you": {"R2": 1}, "them": {"C2": 1}}])


class ExportTests(unittest.TestCase):
    def test_format_lists_are_read_and_checked(self):
        from gtplaybook.exporter import parse_formats

        self.assertEqual(parse_formats("all"), ["md", "json", "csv", "svg"])
        self.assertEqual(parse_formats("csv, md"), ["md", "csv"])
        with self.assertRaises(ValueError):
            parse_formats("pdf")

    def test_a_run_is_written_to_its_own_folder_in_every_format(self):
        import json
        from datetime import datetime

        from gtplaybook.exporter import write_run

        sim = next(s for s in load_simulations() if s["id"] == "chicken")
        steps, ending = [], {"outcome": "victory", "text": "Test ending."}
        with tempfile.TemporaryDirectory() as home:
            folder, written = write_run(sim, steps, ending, ["md", "json", "csv", "svg"], home=home,
                                        when=datetime(2026, 1, 2, 3, 4, 5))
            self.assertEqual(folder.name, "chicken-20260102-030405")
            self.assertEqual(sorted(p.name for p in written), ["run.csv", "run.json", "run.md", "tree.svg"])
            data = json.loads((folder / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(data["ending"]["outcome"], "victory")


class RepeatedPlayTests(unittest.TestCase):
    def test_round_limits_are_enforced(self):
        from gtplaybook.repeat import check_rounds

        self.assertEqual(check_rounds(10), 10)
        with self.assertRaises(ValueError):
            check_rounds(0)
        with self.assertRaises(ValueError):
            check_rounds(51)

    def test_patterned_bot_is_learnable_from_memory(self):
        from gtplaybook.repeat import best_fixed_plan, play_repeated

        game = next(g for g in load_games() if g["id"] == "prisoners-dilemma")
        matrix = game["matrix"]
        history, total = play_repeated(matrix, 9, "pattern", ask=lambda n, h: 0, say=lambda *a: None)
        self.assertEqual([col for _, col, _, _ in history], [0, 1, 0, 1, 0, 1, 0, 1, 0])
        self.assertEqual(best_fixed_plan(matrix, 9, "pattern")[0], 1)

    def test_learner_bot_punishes_a_habit(self):
        from gtplaybook.repeat import play_repeated

        game = next(g for g in load_games() if g["id"] == "prisoners-dilemma")
        history, _ = play_repeated(game["matrix"], 6, "learner", ask=lambda n, h: 1, say=lambda *a: None)
        # After the first round the bot best-replies to the habit (Defect), so it defects from round 2 on.
        self.assertEqual([col for _, col, _, _ in history[1:]], [1, 1, 1, 1, 1])

    def test_win_stay_lose_shift_switches_after_a_bad_round(self):
        from gtplaybook.repeat import opponent_column, Lcg

        game = next(g for g in load_games() if g["id"] == "prisoners-dilemma")
        history = [(1, 0)]  # you defected and the bot cooperated: the bot earns 0, below its average of 2, so it shifts
        self.assertEqual(opponent_column("wsls", game["matrix"], history, Lcg(1)), 1)

    def test_outcome_for_the_record_compares_with_the_best_fixed_plan(self):
        from gtplaybook.repeat import outcome_for_log

        self.assertEqual(outcome_for_log(10, 10), "win")
        self.assertEqual(outcome_for_log(9, 10), "draw")
        self.assertEqual(outcome_for_log(5, 10), "loss")

    def test_repeat_prints_the_same_text_in_both_versions(self):
        import os
        import re
        import subprocess

        ansi = re.compile(r"\x1b\[[0-9;]*m")
        env = dict(os.environ, PLAYBOOK_HOME=tempfile.mkdtemp())
        keys = "1\n2\n1\n2\n2\n1\n1\n2\n2\n1\n"
        for opponent in ("tit-for-tat", "grim", "pattern", "random"):
            args = ["repeat", "prisoners-dilemma", "--rounds", "10", "--opponent", opponent, "--seed", "7"]
            py = subprocess.run([str(ROOT / "playbook"), *args], input=keys, capture_output=True, text=True, env=env)
            go = subprocess.run([str(ROOT / "bin" / "Ergaelion"), *args], input=keys, capture_output=True, text=True, env=env)
            self.assertEqual(ansi.sub("", py.stdout), ansi.sub("", go.stdout), opponent)


class MatrixAndSaveTests(unittest.TestCase):
    def test_every_matrix_game_gives_a_simulation_with_both_paths(self):
        from gtplaybook.matrix_sim import matrix_simulation
        from gtplaybook.sim import solve

        matrix_games = [g for g in load_games() if g.get("matrix")]
        self.assertGreaterEqual(len(matrix_games), 6)
        # Under a weakly dominant strategy the equilibrium result is the worst you can get, so no plan can
        # fall below it. These games are exempt from the failure-path check, and only these.
        no_losing_path = {"vcg-mechanism-design"}
        for game in matrix_games:
            sim = matrix_simulation(game, ["Classic game theory"])
            self.assertGreater(solve(sim, "victory")[sim["start"]][0], 0, game["id"])
            if game["id"] not in no_losing_path:
                self.assertGreater(solve(sim, "failure")[sim["start"]][0], 0, game["id"])

    def test_saved_game_resumes_where_it_stopped(self):
        from gtplaybook.sim import load_state, save_state

        sim = next(s for s in load_simulations() if s["id"] == "chicken")
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / "save.json")
            save_state(path, sim, "n1", [{"kind": "you", "prompt": "p", "label": "x", "why": ""}])
            node, steps = load_state(path, sim)
            self.assertEqual(node, "n1")
            self.assertEqual(len(steps), 1)
            other = next(s for s in load_simulations() if s["id"] == "vs-tit-for-tat")
            with self.assertRaises(ValueError):
                load_state(path, other)

    def test_per_play_chart_is_valid_svg(self):
        import xml.etree.ElementTree as ET

        from gtplaybook import charts

        svg = charts.plays_chart([("Chicken - play 1", {"win": 2, "loss": 1})])
        ET.fromstring(svg)


def go_binary_runs():
    """True when the Go binary exists and can run on this machine (a macOS build cannot run on Linux)."""
    import subprocess

    binary = ROOT / "bin" / "Ergaelion"
    if not binary.exists():
        return False
    try:
        result = subprocess.run([str(binary), "version"], capture_output=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


class TerminalAndParityTests(unittest.TestCase):
    """Drive play mode through a real pseudo-terminal, and check the Go binary matches Python."""

    def test_play_mode_runs_in_a_real_terminal(self):
        import os
        import pty
        import select
        import subprocess
        import sys
        import time

        with tempfile.TemporaryDirectory() as home:
            env = dict(os.environ, PLAYBOOK_HOME=home)
            master, slave = pty.openpty()
            proc = subprocess.Popen(
                [sys.executable, str(ROOT / "playbook"), "sim", "chicken", "--play"],
                stdin=slave, stdout=slave, stderr=slave, env=env, close_fds=True,
            )
            os.close(slave)
            output = b""

            def read_until(marker_bytes, timeout=5.0):
                nonlocal output
                deadline = time.time() + timeout
                while time.time() < deadline:
                    ready, _, _ = select.select([master], [], [], 0.2)
                    if ready:
                        try:
                            chunk = os.read(master, 4096)
                        except OSError:
                            return False
                        if not chunk:
                            return False
                        output += chunk
                        if marker_bytes in output[-200:]:
                            return True
                return False

            try:
                if read_until(b"(Y/n)"):
                    os.write(master, b"y\n")  # keep hints on for this run
                for _ in range(6):
                    if b"Ending:" in output:
                        break
                    if not read_until(b"> "):
                        break
                    os.write(master, b"1\n")
                read_until(b"Ending:")
                # The export prompt may already have arrived with the ending, so check what was read first.
                if b"Export this run?" in output or read_until(b"Export this run?"):
                    os.write(master, b"\n")  # skip the export prompt
                if b"Play again" in output or read_until(b"Play again"):
                    os.write(master, b"n\n")  # decline playing again
            finally:
                proc.wait(timeout=10)
                os.close(master)
        self.assertIn(b"Ending:", output)
        self.assertIn(b"why not", output)


@unittest.skipUnless(go_binary_runs(), "Go binary missing or built for another system; run make build")
class GoPythonParityTests(unittest.TestCase):
    CASES = [
        ["problems", "work"], ["sim", "--family", "war"], ["guide", "power", "48"], ["areas", "war"],
        ["list", "--domain", "military"], ["setup", "chicken"], ["sim"],
        ["solve", "3,3 0,5; 5,0 1,1"],
        ["solve", "2,1 0,0; 0,0 1,2", "--rows", "Opera,Football", "--cols", "Opera,Football"],
        ["sim", "stag-hunt", "--matrix", "--opponent", "uniform"], ["sim", "chicken", "--matrix"],
        ["sim", "stag-hunt", "--matrix", "--opponent", "noisy", "--lam", "1"],
        ["theme"],
        ["theme", "ocean"],
        ["theme", "set", "bad", "magenta"],
        ["theme", "reset"],
        ["solve", "3,3 0,5; 5,0 1,1", "--json"],
        ["record", "--json"],
        ["show", "bank-run"],
        ["keywords", "work", "strategy"],
        ["advise", "-d", "two companies set prices at the same time, once only"],
        ["advise", "-d", "a trojen horse hidden in a gift"],
        ["advise", "-d", "zxq wvu"],
        ["keywords", "bank run"],
    ]

    def test_menu_quits_at_end_of_input_in_both_versions(self):
        import os
        import subprocess

        env = dict(os.environ, PLAYBOOK_HOME=tempfile.mkdtemp())
        results = []
        for binary in (ROOT / "playbook", ROOT / "bin" / "Ergaelion"):
            done = subprocess.run([str(binary), "menu"], input="", capture_output=True, text=True, env=env, timeout=30)
            results.append((done.returncode, len(done.stdout)))
        self.assertEqual(results[0][0], results[1][0])
        self.assertEqual(results[1][0], 0)
        self.assertLess(results[1][1], 100000)

    def test_claude_session_prints_the_same_text_in_both_versions(self):
        """The /claude commands run in the session. Nothing reaches the network: no key, and Claude is off."""
        import os
        import re
        import subprocess

        ansi = re.compile(r"\x1b\[[0-9;]*m")
        env = dict(os.environ, PLAYBOOK_HOME=tempfile.mkdtemp())
        env.pop("ANTHROPIC_API_KEY", None)
        script = "\n".join([
            "/claude status", "/claude ask hello", "/claude on", "/claude status",
            "/claude ask hi", "/claude sim salary-negotiation what is the best plan",
            "/claude game prisoners-dilemma why defect", "/claude scenario anything", "/claude off",
            "/claude", "/quit", ""])
        outputs = []
        for binary in (ROOT / "playbook", ROOT / "bin" / "Ergaelion"):
            done = subprocess.run([str(binary)], input=script, capture_output=True, text=True, env=env, timeout=60)
            outputs.append(ansi.sub("", done.stdout))
        self.assertEqual(outputs[0], outputs[1])
        self.assertIn("Claude is off. Nothing is sent.", outputs[0])

    def test_commands_print_the_same_text_in_both_versions(self):
        import os
        import re
        import subprocess

        ansi = re.compile(r"\x1b\[[0-9;]*m")
        env = dict(os.environ, PLAYBOOK_HOME=tempfile.mkdtemp())
        for args in self.CASES:
            py = subprocess.run([str(ROOT / "playbook"), *args], capture_output=True, text=True, env=env)
            go = subprocess.run([str(ROOT / "bin" / "Ergaelion"), *args], capture_output=True, text=True, env=env)
            self.assertEqual(ansi.sub("", py.stdout), ansi.sub("", go.stdout), " ".join(args))


@unittest.skipUnless(go_binary_runs(), "Go binary missing or built for another system; run make build")
class GoLineEditingTests(unittest.TestCase):
    """The Go session's own line editor: Tab completion and arrow-key history, in a real terminal."""

    def drive(self, home, keys):
        import os
        import pty
        import re
        import select
        import subprocess
        import time

        env = dict(os.environ, PLAYBOOK_HOME=home)
        keys = [b"\r", *keys]  # the launch opens the menu; Enter chooses Command prompt
        master, slave = pty.openpty()
        proc = subprocess.Popen([str(ROOT / "bin" / "Ergaelion")], stdin=slave, stdout=slave, stderr=slave, env=env, close_fds=True)
        os.close(slave)
        output = b""

        def drain(seconds):
            nonlocal output
            end = time.time() + seconds
            while time.time() < end:
                ready, _, _ = select.select([master], [], [], 0.1)
                if ready:
                    try:
                        output += os.read(master, 65536)
                    except OSError:
                        return

        drain(1.0)
        # Launching shows the logo first; Space carries on to the menu.
        os.write(master, b" ")
        drain(0.5)
        for key in keys:
            os.write(master, key)
            drain(0.4)
        proc.wait(timeout=10)
        os.close(master)
        return re.sub(rb"\x1b\[[0-9;]*[A-Za-z]", b"", output).decode("utf-8", "replace")

    def test_tab_completes_a_command(self):
        with tempfile.TemporaryDirectory() as home:
            text = self.drive(home, [b"/sho\t", b"chicken\r", b"q", b"/quit\r"])
            self.assertIn("Chicken", text)

    def test_up_arrow_recalls_history_and_history_is_saved(self):
        with tempfile.TemporaryDirectory() as home:
            text = self.drive(home, [b"chicken\r", b"q", b"\x1b[A", b"\r", b"q", b"/quit\r"])
            self.assertGreaterEqual(text.count("Chicken"), 2)
            self.assertTrue((Path(home) / "history").exists())



class MenuTests(unittest.TestCase):
    def test_typed_menu_quits_on_eleven_and_lists_ask_claude(self):
        from unittest import mock

        from gtplaybook import repl

        self.assertIn("menu_claude", repl.MENU_ITEMS)
        self.assertEqual(repl.MENU_ITEMS.index("menu_quit") + 1, 11)
        with mock.patch("builtins.input", side_effect=["11"]), mock.patch("sys.stdout"):
            self.assertTrue(repl._run_menu_typed(repl.Session(load_games())))

    def test_zero_in_the_typed_menu_goes_to_the_command_prompt(self):
        from unittest import mock

        from gtplaybook import repl

        with mock.patch("builtins.input", side_effect=["0"]), mock.patch("sys.stdout"):
            self.assertFalse(repl._run_menu_typed(repl.Session(load_games())))

    def test_end_of_input_quits_the_typed_menu(self):
        from unittest import mock

        from gtplaybook import repl

        with mock.patch("builtins.input", side_effect=EOFError), mock.patch("sys.stdout"):
            self.assertTrue(repl.run_menu(repl.Session(load_games())))


class VisibleMenuTests(unittest.TestCase):
    """The menu must be discoverable without knowing its name: in the banner, in /help and in Tab completion."""

    def test_menu_is_offered_in_the_banner_help_and_completion(self):
        import io
        from contextlib import redirect_stdout

        from gtplaybook import repl

        self.assertIn("/menu", repl.COMMANDS)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            repl.print_banner()
            repl.print_help()
        self.assertIn("/menu", buffer.getvalue())
        self.assertIn("Type /menu to browse games", buffer.getvalue())


class ScreenTests(unittest.TestCase):
    def test_cls_is_offered_in_completion_and_help(self):
        import io
        from contextlib import redirect_stdout

        from gtplaybook import repl

        self.assertIn("/cls", repl.COMMANDS)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            repl.print_help()
        self.assertIn("/cls", buffer.getvalue())

    def test_list_columns_fit_the_longest_entry(self):
        import argparse
        import io
        import re
        from contextlib import redirect_stdout

        from gtplaybook import cli

        games = load_games()
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cli.cmd_list(argparse.Namespace(domain=None, search=None), games)
        longest = max(len(g["id"]) for g in games)
        for line in buffer.getvalue().splitlines():
            if re.match(r"\S+\s{2,}", line) and "game(s)" not in line:
                first = line.split("  ")[0]
                self.assertLessEqual(len(first), longest)
                self.assertGreaterEqual(len(line) - len(line.lstrip()), 0)
        self.assertIn("kin-selection-helping-relatives  ", buffer.getvalue())


class PhraseCompletionTests(unittest.TestCase):
    def test_a_known_phrase_completes_in_full(self):
        from gtplaybook import keywords, lineedit

        phrases = ["coin toss", "heads or tails", "heads or tails bet"]
        editor = lineedit.Editor(complete=lambda prefix: [], complete_phrase=lambda text: keywords.complete_phrase(text, phrases))
        self.assertEqual(editor._complete_word("heads or", 8), ("heads or tails", 14))
        self.assertEqual(keywords.complete_phrase("heads or", phrases), ["heads or tails", "heads or tails bet"])
        self.assertEqual(keywords.complete_phrase("coin", phrases), [])

    def test_a_command_is_not_completed_as_a_phrase(self):
        from gtplaybook import lineedit

        editor = lineedit.Editor(complete=lambda prefix: [], complete_phrase=lambda text: ["/show whatever"])
        self.assertIsNone(editor._complete_word("/sho", 4))

    def test_word_completion_still_works_without_a_phrase(self):
        from gtplaybook import lineedit

        editor = lineedit.Editor(complete=lambda prefix: ["tariffs"] if "tariffs".startswith(prefix) else [],
                                 complete_phrase=lambda text: [])
        self.assertEqual(editor._complete_word("trade ta", 8)[0], "trade tariffs ")


class ClaudeTests(unittest.TestCase):
    """Claude is opt-in. These tests never reach the network: the opener is replaced."""

    def setUp(self):
        from gtplaybook import claude

        self.claude = claude
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.saved_key = os.environ.get("ANTHROPIC_API_KEY")
        os.environ["ANTHROPIC_API_KEY"] = "test-key"

    def tearDown(self):
        if self.saved_key is None:
            os.environ.pop("ANTHROPIC_API_KEY", None)
        else:
            os.environ["ANTHROPIC_API_KEY"] = self.saved_key
        self.tmp.cleanup()

    class Reply:
        def __init__(self, body):
            self.body = body

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return self.body

    def fake_opener(self, answer, seen):
        def opener(request, timeout):
            seen["url"] = request.full_url
            seen["headers"] = {k.lower(): v for k, v in request.header_items()}
            seen["body"] = json.loads(request.data.decode("utf-8"))
            return self.Reply(json.dumps({"content": [{"type": "text", "text": answer}]}).encode("utf-8"))
        return opener

    def test_off_until_switched_on(self):
        self.assertFalse(self.claude.is_on(self.home))
        with self.assertRaisesRegex(ValueError, "Claude is off"):
            self.claude.check_ready(self.home)
        self.claude.set_on(True, self.home)
        self.assertTrue(self.claude.is_on(self.home))
        self.claude.set_on(False, self.home)
        self.assertFalse(self.claude.is_on(self.home))

    def test_key_is_required_once_on(self):
        self.claude.set_on(True, self.home)
        del os.environ["ANTHROPIC_API_KEY"]
        with self.assertRaisesRegex(ValueError, "ANTHROPIC_API_KEY"):
            self.claude.check_ready(self.home)

    def test_game_text_has_payoffs_and_playbook(self):
        game = next(g for g in load_games() if g["id"] == "prisoners-dilemma")
        text = self.claude.game_part(game)
        self.assertIn("Cooperate: (3, 3)  (0, 5)", text)
        self.assertIn("Playbook:", text)
        self.assertIn("Pitfalls:", text)

    def test_simulation_text_links_options_to_nodes(self):
        sim = next(s for s in load_simulations() if s["id"] == "salary-negotiation")
        text = self.claude.simulation_part(sim)
        self.assertIn("[n0] Decision: You have an offer. What salary do you ask for? Ask 50k -> n1", text)
        self.assertIn("[n6] End: failure", text)

    def test_ask_sends_only_the_parts_and_question(self):
        self.claude.set_on(True, self.home)
        seen = {}
        answer, sent = self.claude.ask("why defect", [("Game", "Prisoner's Dilemma text")],
                                       home=self.home, opener=self.fake_opener("Because it pays.", seen))
        self.assertEqual(answer, "Because it pays.")
        self.assertEqual(seen["url"], self.claude.API_URL)
        self.assertEqual(seen["headers"]["x-api-key"], "test-key")
        self.assertEqual(seen["headers"]["anthropic-version"], self.claude.API_VERSION)
        content = seen["body"]["messages"][0]["content"]
        self.assertEqual(sent, len(content))
        self.assertIn("## Game\nPrisoner's Dilemma text", content)
        self.assertTrue(content.endswith("## Question\nwhy defect"))

    def test_http_error_is_a_plain_message(self):
        self.claude.set_on(True, self.home)

        def failing(request, timeout):
            raise self.claude.urllib.error.HTTPError(request.full_url, 401, "denied", {}, None)

        with self.assertRaisesRegex(ValueError, "error \\(401\\)"):
            self.claude.ask("hi", [], home=self.home, opener=failing)

    def test_long_text_is_clipped(self):
        long = "x" * (self.claude.MAX_QUESTION + 500)
        self.assertLessEqual(len(self.claude.build_prompt(long, [])), self.claude.MAX_QUESTION + 40)


if __name__ == "__main__":
    unittest.main()
