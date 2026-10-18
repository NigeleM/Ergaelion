import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from gtplaybook import advisor, solver  # noqa: E402
from gtplaybook.catalog import CatalogError, find_game, load_games  # noqa: E402
from gtplaybook.scenario import ScenarioError, describe, parse_scenario  # noqa: E402


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.games = load_games()

    def test_ids_are_unique_and_catalogue_is_substantial(self):
        ids = [g["id"] for g in self.games]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 15)

    def test_find_by_exact_name_and_prefix(self):
        self.assertEqual(find_game(self.games, "Prisoner's Dilemma")["id"], "prisoners-dilemma")
        self.assertEqual(find_game(self.games, "chick")["id"], "chicken")

    def test_ambiguous_query_is_rejected(self):
        with self.assertRaises(CatalogError):
            find_game(self.games, "game")


class SolverTests(unittest.TestCase):
    def analyse(self, text):
        return solver.analyse(solver.parse_matrix(text))

    def test_prisoners_dilemma_dominance_gives_defect_defect(self):
        result = self.analyse("3,3 0,5; 5,0 1,1")
        self.assertEqual(result["equilibria"], [(1, 1)])
        self.assertEqual(result["surviving_rows"], [1])
        self.assertEqual(result["surviving_cols"], [1])

    def test_matching_pennies_has_only_a_mixed_equilibrium(self):
        result = self.analyse("1,-1 -1,1; -1,1 1,-1")
        self.assertEqual(result["equilibria"], [])
        self.assertEqual(result["mixed"], (Fraction(1, 2), Fraction(1, 2)))
        self.assertEqual(result["constant_sum"], 0)

    def test_inspection_game_mixed_equilibrium(self):
        result = self.analyse("-1,0 2,-3; 0,0 -2,2")
        self.assertEqual(result["mixed"], (Fraction(2, 5), Fraction(4, 5)))

    def test_battle_of_sexes_has_two_pure_equilibria(self):
        result = self.analyse("2,1 0,0; 0,0 1,2")
        self.assertEqual(result["equilibria"], [(0, 0), (1, 1)])

    def test_bad_cell_is_rejected(self):
        with self.assertRaises(ValueError):
            solver.parse_matrix("3 0,5; 5,0 1,1")

    def test_ragged_matrix_is_rejected(self):
        with self.assertRaises(ValueError):
            solver.parse_matrix("1,1 2,2; 3,3")


class ScenarioTests(unittest.TestCase):
    def test_parse_file_normalises_values(self):
        scenario = parse_scenario("title: T\nplayers: 2\ntiming: Sequential\ndomain: work, business\n")
        self.assertEqual(scenario["traits"], {"players": "two", "timing": "sequential"})
        self.assertEqual(scenario["domains"], ["work", "business"])

    def test_bad_value_reports_line_number(self):
        with self.assertRaises(ScenarioError) as ctx:
            parse_scenario("title: x\ntiming: never\n")
        self.assertIn("line 2", str(ctx.exception))

    def test_unknown_key_is_rejected(self):
        with self.assertRaises(ScenarioError):
            parse_scenario("colour: blue\n")

    def test_unknown_domain_is_rejected(self):
        with self.assertRaises(ScenarioError):
            parse_scenario("domain: astrology\n")

    def test_describe_negotiation(self):
        result = describe("I'm negotiating my salary with a new employer, we will talk once")
        self.assertEqual(result["traits"]["bargaining"], "yes")
        self.assertEqual(result["traits"]["interaction"], "one-shot")
        self.assertIn("work", result["domains"])

    def test_describe_repeated(self):
        result = describe("Two suppliers keep dealing with each other every month, long-term")
        self.assertEqual(result["traits"]["interaction"], "repeated")

    def test_irreversible_is_commitment_yes_not_no(self):
        result = describe("The army makes an irreversible threat")
        self.assertEqual(result["traits"]["commitment"], "yes")

    def test_imperfect_information_is_not_read_as_perfect(self):
        result = describe("We have imperfect information about rival costs")
        self.assertEqual(result["traits"]["information"], "imperfect")


class AdvisorTests(unittest.TestCase):
    def test_one_shot_mixed_motive_ranks_prisoners_dilemma_in_top_three(self):
        games = load_games()
        traits = {
            "players": "two",
            "timing": "simultaneous",
            "interaction": "one-shot",
            "payoff": "mixed",
            "enforcement": "no",
        }
        # Several games share the same traits, so ties are broken by name. Check the score, not the position.
        ranked = advisor.rank_games(games, traits, [], top=3)
        scores = {hit["game"]["id"]: hit["score"] for hit in advisor.rank_games(games, traits, [], top=len(games))}
        self.assertEqual(scores["prisoners-dilemma"], max(scores.values()))
        self.assertTrue(ranked)

    def test_repeated_rules_mention_the_future(self):
        rules = advisor.general_rules({"interaction": "repeated"})
        self.assertTrue(any("future" in rule for rule in rules))


if __name__ == "__main__":
    unittest.main()
