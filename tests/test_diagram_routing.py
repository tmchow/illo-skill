import importlib.util
import re
import sys
import unittest
from pathlib import Path
from typing import Any, cast


REPO = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO / "skills" / "illo" / "scripts" / "diagram_route.py"
COMPOSITION_PATH = REPO / "skills" / "illo" / "references" / "composition.md"


def load_router():
    spec = importlib.util.spec_from_file_location("diagram_route_under_test", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load diagram_route from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return cast(Any, module)


class CompositionAlignmentTests(unittest.TestCase):
    """If the function and composition.md drift, these fail."""

    @classmethod
    def setUpClass(cls):
        cls.route = load_router()
        cls.policy = cls.route.parse_composition_policy(
            COMPOSITION_PATH.read_text(encoding="utf-8")
        )

    def test_picker_section_names_match_current_policy(self):
        self.assertEqual(
            self.policy.named_phrases,
            (
                "as labeled stages",
                "label the steps",
                "walk the stages",
                "timeline",
                "loop",
                "fan-out",
                "stack",
                "mini-comic",
                "just the scene",
            ),
        )
        self.assertEqual(self.policy.register_only_phrases, ("as an explainer",))
        self.assertEqual(
            self.policy.description_examples,
            (
                "swim the stages",
                "one machine with windows",
                "as a flowchart",
                "labeled workflow",
            ),
        )
        self.assertEqual(
            self.policy.allusion_examples, ("like that factory diagram",)
        )
        self.assertTrue(self.policy.locks_register_only)
        self.assertNotIn("flowchart", self.policy.named_phrases)
        self.assertNotIn("as a flowchart", self.policy.named_phrases)
        self.assertNotIn("labeled workflow", self.policy.named_phrases)

    def test_default_map_labels_follow_composition_order(self):
        self.assertEqual(
            self.policy.default_map_labels[:8],
            (
                self.route.TYPE_LABELED_STAGES,
                self.route.TYPE_FAN_OUT,
                self.route.TYPE_TIMELINE,
                self.route.TYPE_LOOP,
                self.route.TYPE_STACK,
                self.route.TYPE_SLICE,
                self.route.TYPE_COMIC,
                self.route.TYPE_EDITORIAL,
            ),
        )

    def test_precedence_headings_are_still_name_then_description_then_allusion(self):
        body = COMPOSITION_PATH.read_text(encoding="utf-8")
        names_at = body.index("1. The user **names** a type")
        describes_at = body.index("2. The user **describes** a type")
        alludes_at = body.index("3. The user **alludes** to a type")
        default_at = body.index("4. The agent default")
        self.assertLess(names_at, describes_at)
        self.assertLess(describes_at, alludes_at)
        self.assertLess(alludes_at, default_at)

    def test_flowchart_formality_ban_is_a_look_constraint(self):
        body = COMPOSITION_PATH.read_text(encoding="utf-8")
        picker = re.sub(
            r"\s+",
            " ",
            body[
                body.index("## Pick the diagram type") : body.index(
                    "## The explainer register"
                )
            ],
        )
        self.assertIn("boxes-and-diamonds", picker)
        self.assertIn("do not refuse the word flowchart", picker)
        self.assertIn("examples, not a closed list", picker)
        self.assertIn("not a keyword scan", picker)


class DiagramRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = load_router()

    def _decide(self, text, thesis=None):
        return self.route.route_diagram(text, thesis=thesis)

    def test_pipeline_intent_bounded_audited_is_labeled_stages(self):
        decision = self._decide("pipeline intent→bounded→audited")
        self.assertEqual(decision.diagram_type, self.route.TYPE_LABELED_STAGES)
        self.assertEqual(decision.register, self.route.REGISTER_EXPLAINER)
        self.assertIsNone(decision.override)

    def test_one_source_into_traffic_trust_conversion_is_fan_out(self):
        decision = self._decide("one source into traffic/trust/conversion")
        self.assertEqual(decision.diagram_type, self.route.TYPE_FAN_OUT)
        self.assertEqual(decision.register, self.route.REGISTER_EXPLAINER)

    def test_feedback_cycle_as_the_point_is_loop(self):
        decision = self._decide("the point is the feedback cycle")
        self.assertEqual(decision.diagram_type, self.route.TYPE_LOOP)
        self.assertEqual(decision.register, self.route.REGISTER_EXPLAINER)

    def test_failed_then_fixed_is_mini_comic(self):
        decision = self._decide("we failed then we fixed it")
        self.assertEqual(decision.diagram_type, self.route.TYPE_COMIC)
        self.assertEqual(decision.register, self.route.REGISTER_EDITORIAL)

    def test_youre_the_bottleneck_is_editorial(self):
        decision = self._decide("you're the bottleneck")
        self.assertEqual(decision.diagram_type, self.route.TYPE_EDITORIAL)
        self.assertEqual(decision.register, self.route.REGISTER_EDITORIAL)

    def test_bottleneck_as_labeled_stages_is_name_override(self):
        decision = self._decide("bottleneck as labeled stages")
        self.assertEqual(decision.diagram_type, self.route.TYPE_LABELED_STAGES)
        self.assertEqual(decision.register, self.route.REGISTER_EXPLAINER)
        self.assertEqual(decision.override, self.route.OVERRIDE_NAME)

    def test_label_the_steps_is_name_override(self):
        decision = self._decide("you're the bottleneck, label the steps")
        self.assertEqual(decision.diagram_type, self.route.TYPE_LABELED_STAGES)
        self.assertEqual(decision.override, self.route.OVERRIDE_NAME)

    def test_walk_the_stages_is_name_override(self):
        decision = self._decide("walk the stages of the bottleneck")
        self.assertEqual(decision.diagram_type, self.route.TYPE_LABELED_STAGES)
        self.assertEqual(decision.override, self.route.OVERRIDE_NAME)

    def test_as_a_factory_is_not_a_type_name(self):
        decision = self._decide("bottleneck as a factory")
        self.assertNotEqual(decision.diagram_type, self.route.TYPE_LABELED_STAGES)
        self.assertNotEqual(decision.override, self.route.OVERRIDE_NAME)

    def test_one_machine_with_windows_is_description_override(self):
        decision = self._decide("one machine with windows")
        self.assertEqual(decision.diagram_type, self.route.TYPE_LABELED_STAGES)
        self.assertEqual(decision.override, self.route.OVERRIDE_DESCRIPTION)

    def test_like_that_factory_diagram_is_allusion_override(self):
        decision = self._decide("like that factory diagram")
        self.assertEqual(decision.diagram_type, self.route.TYPE_LABELED_STAGES)
        self.assertEqual(decision.override, self.route.OVERRIDE_ALLUSION)

    def test_just_the_scene_of_the_pipeline_stays_editorial(self):
        decision = self._decide("just the scene of the pipeline")
        self.assertEqual(decision.diagram_type, self.route.TYPE_EDITORIAL)
        self.assertEqual(decision.register, self.route.REGISTER_EDITORIAL)
        self.assertEqual(decision.override, self.route.OVERRIDE_NAME)

    def test_make_the_pipeline_a_mini_comic(self):
        decision = self._decide("make the pipeline a mini-comic")
        self.assertEqual(decision.diagram_type, self.route.TYPE_COMIC)
        self.assertEqual(decision.register, self.route.REGISTER_EDITORIAL)
        self.assertEqual(decision.override, self.route.OVERRIDE_NAME)

    def test_as_an_explainer_bottleneck_locks_register_not_labeled_stages(self):
        decision = self._decide("as an explainer, you're the bottleneck")
        self.assertEqual(decision.register, self.route.REGISTER_EXPLAINER)
        self.assertNotEqual(decision.diagram_type, self.route.TYPE_LABELED_STAGES)
        self.assertEqual(decision.diagram_type, self.route.TYPE_EDITORIAL)
        self.assertEqual(decision.override, self.route.OVERRIDE_NAME)

    def test_bottleneck_as_a_flowchart_is_specified_labeled_stages(self):
        decision = self._decide("draw the bottleneck as a flowchart")
        self.assertEqual(decision.diagram_type, self.route.TYPE_LABELED_STAGES)
        self.assertEqual(decision.register, self.route.REGISTER_EXPLAINER)
        self.assertEqual(decision.override, self.route.OVERRIDE_DESCRIPTION)

    def test_labeled_workflow_of_onboarding_is_specified_labeled_stages(self):
        decision = self._decide("labeled workflow of onboarding")
        self.assertEqual(decision.diagram_type, self.route.TYPE_LABELED_STAGES)
        self.assertEqual(decision.register, self.route.REGISTER_EXPLAINER)
        self.assertEqual(decision.override, self.route.OVERRIDE_DESCRIPTION)

    def test_flowchart_style_of_shipping_steps_is_specified_labeled_stages(self):
        decision = self._decide("flowchart style of the shipping steps")
        self.assertEqual(decision.diagram_type, self.route.TYPE_LABELED_STAGES)
        self.assertEqual(decision.register, self.route.REGISTER_EXPLAINER)
        self.assertEqual(decision.override, self.route.OVERRIDE_DESCRIPTION)

    def test_process_diagram_of_the_steps_is_specified_labeled_stages(self):
        decision = self._decide("process diagram of the steps")
        self.assertEqual(decision.diagram_type, self.route.TYPE_LABELED_STAGES)
        self.assertEqual(decision.register, self.route.REGISTER_EXPLAINER)
        self.assertEqual(decision.override, self.route.OVERRIDE_DESCRIPTION)

    def test_better_flow_in_the_org_is_editorial_not_specified(self):
        decision = self._decide("we need better flow in the org")
        self.assertEqual(decision.diagram_type, self.route.TYPE_EDITORIAL)
        self.assertEqual(decision.register, self.route.REGISTER_EDITORIAL)
        self.assertIsNone(decision.override)

    def test_better_workflow_in_the_org_is_editorial_not_specified(self):
        decision = self._decide("we need a better workflow in the org")
        self.assertEqual(decision.diagram_type, self.route.TYPE_EDITORIAL)
        self.assertEqual(decision.register, self.route.REGISTER_EDITORIAL)
        self.assertIsNone(decision.override)

    def test_just_the_scene_as_a_flowchart_keeps_name_over_description(self):
        decision = self._decide("just the scene as a flowchart")
        self.assertEqual(decision.diagram_type, self.route.TYPE_EDITORIAL)
        self.assertEqual(decision.register, self.route.REGISTER_EDITORIAL)
        self.assertEqual(decision.override, self.route.OVERRIDE_NAME)


def _model(route, **fields):
    return route.InteractionModel(**fields)


class PackSolveTests(unittest.TestCase):
    """Same labeled-stages skeleton; fixtures encode pack interaction models."""

    @classmethod
    def setUpClass(cls):
        cls.route = load_router()
        cls.skeleton = cls.route.AUDIT_LABELED_STAGES
        cls.blip = _model(
            cls.route,
            name="blip",
            contact_surfaces=frozenset({"arm_tips", "feet"}),
            reach="stubby",
            grip="pressure/contact",
            support=frozenset({"feet"}),
            special_operators=frozenset(),
            undeclared=frozenset({"antenna"}),
            forbidden_verbs=frozenset(),
            style="pixel",
        )
        cls.forge = _model(
            cls.route,
            name="forge",
            contact_surfaces=frozenset({"arm_tips", "feet"}),
            reach="stubby",
            grip="pressure/contact",
            support=frozenset({"feet"}),
            special_operators=frozenset(),
            undeclared=frozenset({"hammer"}),
            forbidden_verbs=frozenset({"grasp"}),
            style="woodcut",
        )
        cls.spritz = _model(
            cls.route,
            name="spritz",
            contact_surfaces=frozenset({"vessel", "arm_tips"}),
            reach="short",
            grip="pressure/contact",
            support=frozenset({"base"}),
            special_operators=frozenset({"pour"}),
            undeclared=frozenset(),
            forbidden_verbs=frozenset({"crank", "wheel"}),
            style="riso",
        )
        cls.fathom = _model(
            cls.route,
            name="fathom",
            contact_surfaces=frozenset({"hook_mitts"}),
            reach="short",
            grip="hook",
            support=frozenset({"feet"}),
            special_operators=frozenset({"hook_mitts"}),
            undeclared=frozenset({"helmet"}),
            forbidden_verbs=frozenset(),
            style="blueprint",
        )
        cls.sulk = _model(
            cls.route,
            name="sulk",
            contact_surfaces=frozenset({"body"}),
            reach="body-contact only",
            grip="none",
            support=frozenset({"body"}),
            special_operators=frozenset(),
            undeclared=frozenset({"wings"}),
            forbidden_verbs=frozenset({"crank", "pedal", "grasp"}),
            style="felt",
        )

    def _solve(self, model):
        return self.route.pack_solve(model, self.skeleton)

    def _assert_system(self, solve):
        self.assertEqual(solve.stages, self.route.AUDIT_STAGES)
        self.assertEqual(solve.reject, "slop")
        self.assertEqual(solve.return_leg, "re-audit")
        self.assertEqual(solve.bind, "one flow line")
        self.assertNotEqual(solve.style, "whiteboard")
        factory_world = ("factory building", "hopper", "conveyor belt")
        used = " ".join(
            (
                solve.bind,
                *(line.object_part for line in solve.contact_map),
            )
        ).lower()
        for token in factory_world:
            self.assertNotIn(token, used)

    def test_blip_operates_bounded_pedal_or_press_not_antenna(self):
        solve = self._solve(self.blip)
        self._assert_system(solve)
        self.assertEqual(solve.operator_stage, "bounded")
        self.assertIn(solve.verb, {"pedal", "press"})
        self.assertNotEqual(solve.contact_part, "antenna")
        parts = {line.character_part for line in solve.contact_map}
        self.assertNotIn("antenna", parts)
        self.assertEqual(solve.style, "pixel")

    def test_blip_fails_if_antenna_is_used_as_a_limb(self):
        illegal = self.route.ContactLine(
            "antenna", "press", "above body", "taps the bound plate"
        )
        errors = self.route.feasibility_errors(self.blip, [illegal], verb="press")
        self.assertTrue(errors)
        self.assertTrue(any("antenna" in error for error in errors))

    def test_forge_operates_pedal_or_press_not_hammer(self):
        solve = self._solve(self.forge)
        self._assert_system(solve)
        self.assertEqual(solve.operator_stage, "bounded")
        self.assertIn(solve.verb, {"pedal", "press"})
        used = {
            token
            for line in solve.contact_map
            for token in (line.character_part, line.object_part)
        }
        self.assertNotIn("hammer", used)

    def test_forge_fails_if_hammer_is_the_workflow_tool(self):
        illegal = self.route.ContactLine(
            "arm_tips", "hammer", "beside body", "hammers the line"
        )
        errors = self.route.feasibility_errors(self.forge, [illegal], verb="press")
        self.assertTrue(any("hammer" in error for error in errors))

    def test_spritz_operates_sensored_pour_not_crank(self):
        solve = self._solve(self.spritz)
        self._assert_system(solve)
        self.assertEqual(solve.operator_stage, "sensored")
        self.assertIn(solve.verb, {"pour", "sprinkle"})
        self.assertNotIn(solve.verb, {"crank", "wheel"})

    def test_spritz_fails_if_asked_to_crank_a_wheel(self):
        illegal = self.route.ContactLine(
            "arm_tips", "wheel", "beside body", "cranks the wheel"
        )
        errors = self.route.feasibility_errors(
            self.spritz, [illegal], verb="crank"
        )
        self.assertTrue(errors)
        self.assertTrue(any("crank" in error for error in errors))

    def test_fathom_operates_audited_handle_or_reject_hose(self):
        solve = self._solve(self.fathom)
        self._assert_system(solve)
        self.assertIn(solve.operator_stage, {"audited", "slop"})
        self.assertIn(solve.verb, {"handle", "hose"})
        self.assertEqual(solve.contact_part, "hook_mitts")
        used = {
            token
            for line in solve.contact_map
            for token in (line.character_part, line.object_part)
        }
        self.assertNotIn("helmet", used)

    def test_fathom_fails_if_helmet_is_used_as_a_tool(self):
        illegal = self.route.ContactLine(
            "helmet", "audit handle", "on the bar", "butts the gate"
        )
        errors = self.route.feasibility_errors(self.fathom, [illegal], verb="handle")
        self.assertTrue(any("helmet" in error for error in errors))

    def test_sulk_is_jam_or_vessel_on_bound_plate(self):
        solve = self._solve(self.sulk)
        self._assert_system(solve)
        self.assertEqual(solve.operator_stage, "bounded")
        self.assertIn(solve.verb, {"jam", "vessel"})
        self.assertEqual(solve.contact_part, "body")
        self.assertNotIn(solve.verb, {"crank", "pedal", "grasp"})

    def test_sulk_fails_crank_pedal_or_grasp(self):
        for verb, part, obj in (
            ("crank", "wings", "wheel"),
            ("pedal", "feet", "pedal"),
            ("grasp", "wings", "handle"),
        ):
            with self.subTest(verb=verb):
                illegal = self.route.ContactLine(part, obj, "on the system", verb)
                errors = self.route.feasibility_errors(
                    self.sulk, [illegal], verb=verb
                )
                self.assertTrue(errors)

    def test_pack_solve_keeps_the_pack_look(self):
        for model in (self.blip, self.forge, self.spritz, self.fathom, self.sulk):
            with self.subTest(pack=model.name):
                solve = self._solve(model)
                self.assertEqual(solve.style, model.style)
                self.assertNotEqual(solve.style, "whiteboard")

    def test_pack_solve_does_not_require_a_factory_building(self):
        for model in (self.blip, self.forge, self.spritz, self.fathom, self.sulk):
            with self.subTest(pack=model.name):
                solve = self._solve(model)
                self._assert_system(solve)
                self.assertEqual(solve.bind, "one flow line")
                self.assertNotIn("factory", solve.bind.lower())
                self.assertNotIn("plant", solve.bind.lower())


if __name__ == "__main__":
    unittest.main()
