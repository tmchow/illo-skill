import importlib.util
import sys
import unittest
from pathlib import Path
from typing import Any, cast


REPO = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO / "skills" / "illo" / "scripts" / "diagram_route.py"
COMPOSITION_PATH = REPO / "skills" / "illo" / "references" / "composition.md"
QUALITY_BAR_PATH = REPO / "skills" / "illo" / "references" / "quality-bar.md"
PROMPT_RECIPE_PATH = REPO / "skills" / "illo" / "references" / "prompt-recipe.md"


def load_router():
    spec = importlib.util.spec_from_file_location("diagram_route_arrow_notes", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load diagram_route from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return cast(Any, module)


class ArrowNoteAlignmentTests(unittest.TestCase):
    """If composition.md / quality-bar drift off the arrow-note budget, fail."""

    @classmethod
    def setUpClass(cls):
        cls.route = load_router()
        cls.policy = cls.route.parse_arrow_note_policy(
            COMPOSITION_PATH.read_text(encoding="utf-8")
        )

    def test_composition_suggests_three_stations_and_two_arrow_notes(self):
        self.assertEqual(self.policy.suggested_station_names, 3)
        self.assertEqual(self.policy.max_arrow_notes, 2)
        self.assertEqual(self.policy.max_callouts, 6)
        self.assertEqual(self.policy.max_words, 4)

    def test_quality_bar_fails_mute_arrows_and_paragraph_arrows(self):
        body = QUALITY_BAR_PATH.read_text(encoding="utf-8")
        self.assertIn("mute", body.lower())
        self.assertIn("plaques", body)
        self.assertIn("paragraph", body)

    def test_prompt_recipe_names_both_text_jobs(self):
        body = PROMPT_RECIPE_PATH.read_text(encoding="utf-8")
        self.assertIn("station names", body)
        self.assertIn("arrow notes", body)
        self.assertIn("on or along the arrow", body)


class ArrowNoteBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = load_router()

    def _plan(self, stations, notes):
        return self.route.CalloutPlan(
            station_names=tuple(stations),
            arrow_notes=tuple(notes),
        )

    def test_suggested_split_three_stations_and_two_notes_passes(self):
        plan = self._plan(
            ("intent", "bounded", "audited"),
            ("senses", "if slop"),
        )
        self.assertEqual(self.route.evaluate_callouts(plan), [])
        self.assertTrue(self.route.suggested_callout_split(plan))

    def test_main_flow_verb_only_is_within_budget(self):
        plan = self._plan(("intent", "bounded", "verified"), ("bounds",))
        self.assertEqual(self.route.evaluate_callouts(plan), [])
        self.assertTrue(self.route.suggested_callout_split(plan))

    def test_mute_arrows_fail_when_all_text_is_station_plaques(self):
        plan = self._plan(("intent", "bounded", "audited"), ())
        errors = self.route.evaluate_callouts(plan)
        self.assertIn(self.route.MUTE_ARROWS, errors)

    def test_arrow_paragraph_fails(self):
        plan = self._plan(
            ("intent", "bounded", "audited"),
            ("then the sample is checked twice and poured back",),
        )
        errors = self.route.evaluate_callouts(plan)
        self.assertIn(self.route.ARROW_PARAGRAPH, errors)

    def test_punctuated_arrow_sentence_fails(self):
        plan = self._plan(
            ("intent", "bounded"),
            ("check it. send it back",),
        )
        errors = self.route.evaluate_callouts(plan)
        self.assertIn(self.route.ARROW_PARAGRAPH, errors)

    def test_over_budget_seven_callouts_fails(self):
        plan = self._plan(
            ("intent", "bounded", "sensored", "audited", "verified"),
            ("senses", "if slop"),
        )
        errors = self.route.evaluate_callouts(plan)
        self.assertIn(self.route.OVER_BUDGET, errors)

    def test_four_stations_and_two_notes_is_within_hard_budget(self):
        plan = self._plan(
            ("intent", "bounded", "audited", "verified"),
            ("senses", "if slop"),
        )
        self.assertEqual(self.route.evaluate_callouts(plan), [])
        self.assertFalse(self.route.suggested_callout_split(plan))

    def test_station_name_over_four_words_fails(self):
        plan = self._plan(
            ("the intent hopper station here", "bounded"),
            ("senses",),
        )
        errors = self.route.evaluate_callouts(plan)
        self.assertIn(self.route.WORD_LIMIT, errors)

    def test_three_arrow_notes_fail(self):
        plan = self._plan(
            ("intent", "bounded"),
            ("senses", "if slop", "then ships"),
        )
        errors = self.route.evaluate_callouts(plan)
        self.assertIn(self.route.TOO_MANY_ARROW_NOTES, errors)


if __name__ == "__main__":
    unittest.main()
