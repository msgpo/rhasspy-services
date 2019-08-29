import io
from glob import glob
import unittest
import logging
import tempfile
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

from jsgf2fst import (
    get_grammar_dependencies,
    grammar_to_fsts,
    slots_to_fsts,
    make_intent_fst,
    fstprintall,
    fstaccept,
)


class Jsgf2FstTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # -------------------------------------------------------------------------

    def test_dependencies(self):
        # ChangeLight
        grammar = Path("test/ChangeLight.gram").read_text()
        deps = get_grammar_dependencies(grammar)
        g = deps.graph

        # Verify grammar
        self.assertTrue(g.has_node("ChangeLight"))
        self.assertEqual(g.nodes["ChangeLight"]["type"], "local grammar")

        # Verify local rule
        self.assertTrue(g.has_node("ChangeLight.ChangeLight"))
        self.assertEqual(g.nodes["ChangeLight.ChangeLight"]["type"], "local rule")
        self.assertTrue(g.has_edge("ChangeLight", "ChangeLight.ChangeLight"))

        # Verify remote rule
        self.assertTrue(g.has_node("ChangeLightColor.ChangeLightColor"))
        self.assertEqual(
            g.nodes["ChangeLightColor.ChangeLightColor"]["type"], "remote rule"
        )
        self.assertTrue(
            g.has_edge("ChangeLight.ChangeLight", "ChangeLightColor.ChangeLightColor")
        )

        # ChangeLightColor
        grammar = Path("test/ChangeLightColor.gram").read_text()
        deps = get_grammar_dependencies(grammar)
        g = deps.graph

        # Verify slot
        self.assertTrue(g.has_node("$colors"))
        self.assertEqual(g.nodes["$colors"]["type"], "slot")
        self.assertTrue(g.has_edge("ChangeLightColor.color", "$colors"))

    # -------------------------------------------------------------------------

    def test_end_disjunction(self):
        # GetGarageState
        grammar = Path("test/GetGarageState.gram").read_text()
        result = grammar_to_fsts(grammar)
        grammar_fst = result.grammar_fst

        self.assertGreater(len(list(grammar_fst.states())), 0)
        self.assertIsNotNone(grammar_fst.input_symbols())
        self.assertIsNotNone(grammar_fst.output_symbols())

        sentences = fstprintall(grammar_fst, exclude_meta=False)
        self.assertEqual(len(sentences), 2)

        # Join strings
        sentences = [" ".join(s) for s in sentences]

        self.assertIn("is the garage door open", sentences)
        self.assertIn("is the garage door closed", sentences)

    # -------------------------------------------------------------------------

    def test_slots(self):
        slot_fsts = slots_to_fsts(Path("test/slots"))
        self.assertIn("$colors", slot_fsts)

        # Verify slot values
        values = set(v[0] for v in fstprintall(slot_fsts["$colors"]))
        self.assertSetEqual(
            values, {"yellow", "purple", "orange", "blue", "red", "green"}
        )

        # Fold into a grammar
        grammar = Path("test/ChangeLightColor.gram").read_text()
        grammar_fst = grammar_to_fsts(grammar, replace_fsts=slot_fsts).grammar_fst
        self.assertGreater(len(list(grammar_fst.states())), 0)

        intents = fstaccept(
            grammar_fst, "set color to orange", intent_name="ChangeLightColor"
        )
        intent = intents[0]

        logging.debug(intent)
        self.assertEqual(intent["intent"]["name"], "ChangeLightColor")
        self.assertEqual(intent["intent"]["confidence"], 1)
        self.assertEqual(len(intent["entities"]), 1)

        ev = intent["entities"][0]
        self.assertEqual(ev["entity"], "color")
        self.assertEqual(ev["value"], "orange")

    # -------------------------------------------------------------------------

    def test_printall(self):
        slot_fsts = slots_to_fsts(Path("test/slots"))
        grammar = Path("test/ChangeLightColor.gram").read_text()
        grammar_fst = grammar_to_fsts(grammar, replace_fsts=slot_fsts).grammar_fst
        self.assertGreater(len(list(grammar_fst.states())), 0)
        sentences = fstprintall(grammar_fst, exclude_meta=False)
        self.assertEqual(len(sentences), 12)

        # Verify all sentences have intent/entity meta tokens
        for sentence in sentences:
            self.assertIn("__begin__color", sentence)
            self.assertIn("__end__color", sentence)

    # -------------------------------------------------------------------------

    def test_timer(self):
        grammar = Path("test/SetTimer.gram").read_text()
        timer_fst = grammar_to_fsts(grammar).grammar_fst
        self.assertGreater(len(list(timer_fst.states())), 0)
        timer_fst.write("timer.fst")

        intents = fstaccept(
            timer_fst,
            "set a timer for ten minutes and forty two seconds",
            intent_name="SetTimer",
        )

        intent = intents[0]

        logging.debug(intent)
        self.assertEqual(intent["intent"]["name"], "SetTimer")
        self.assertEqual(intent["intent"]["confidence"], 1)
        self.assertEqual(len(intent["entities"]), 2)

        # Verify text with replacements
        text = intent["text"]
        self.assertEqual(text, "set a timer for 10 minutes and 40 2 seconds")

        # Verify "raw" text (no replacements)
        raw_text = intent["raw_text"]
        self.assertEqual(raw_text, "set a timer for ten minutes and forty two seconds")

        # Verify individual entities
        expected = {"minutes": "10", "seconds": "40 2"}
        raw_expected = {"minutes": "ten", "seconds": "forty two"}

        for ev in intent["entities"]:
            entity = ev["entity"]
            if (entity in expected) and (ev["value"] == expected[entity]):
                # Check start/end inside text
                start, end = ev["start"], ev["end"]
                self.assertEqual(text[start:end], ev["value"])
                expected.pop(entity)

            if (entity in raw_expected) and (ev["raw_value"] == raw_expected[entity]):
                raw_expected.pop(entity)

        self.assertDictEqual(expected, {})
        self.assertDictEqual(raw_expected, {})

        # Verify number of sentences (takes a long time)
        logging.debug("Counting all possible test sentences...")
        sentences = fstprintall(timer_fst, exclude_meta=False)
        self.assertEqual(len(sentences), 2 * (59 * (1 + (2 * 59))))

    # -------------------------------------------------------------------------

    def test_reference(self):
        slot_fsts = slots_to_fsts(Path("test/slots"))
        light_color_fsts = grammar_to_fsts(
            Path("test/ChangeLightColor.gram").read_text(), replace_fsts=slot_fsts
        ).fsts

        replace_fsts = {**slot_fsts, **light_color_fsts}
        light_fst = grammar_to_fsts(
            Path("test/ChangeLight.gram").read_text(), replace_fsts=replace_fsts
        ).grammar_fst
        self.assertGreater(len(list(light_fst.states())), 0)

        # Change state
        intents = fstaccept(light_fst, "turn off", intent_name="ChangeLight")
        intent = intents[0]

        logging.debug(intent)
        self.assertEqual(intent["intent"]["name"], "ChangeLight")
        self.assertEqual(intent["intent"]["confidence"], 1)
        self.assertEqual(len(intent["entities"]), 1)

        ev = intent["entities"][0]
        self.assertEqual(ev["entity"], "state")
        self.assertEqual(ev["value"], "off")

        # Change color
        intents = fstaccept(light_fst, "set color to orange", intent_name="ChangeLight")
        intent = intents[0]

        logging.debug(intent)
        self.assertEqual(intent["intent"]["name"], "ChangeLight")
        self.assertEqual(intent["intent"]["confidence"], 1)
        self.assertEqual(len(intent["entities"]), 1)

        ev = intent["entities"][0]
        self.assertEqual(ev["entity"], "color")
        self.assertEqual(ev["value"], "orange")

    # -------------------------------------------------------------------------

    def test_intent_fst(self):
        slot_fsts = slots_to_fsts(Path("test/slots"))

        change_light_color = grammar_to_fsts(
            Path("test/ChangeLightColor.gram").read_text(), replace_fsts=slot_fsts
        )

        replace_fsts = {**slot_fsts, **change_light_color.fsts}
        change_light = grammar_to_fsts(
            Path("test/ChangeLight.gram").read_text(), replace_fsts=replace_fsts
        )

        set_timer = grammar_to_fsts(Path("test/SetTimer.gram").read_text())
        garage_state = grammar_to_fsts(Path("test/GetGarageState.gram").read_text())

        grammar_fsts = {
            "ChangeLightColor": change_light_color.grammar_fst,
            "ChangeLight": change_light.grammar_fst,
            "SetTimer": set_timer.grammar_fst,
            "GetGarageState": garage_state.grammar_fst,
        }

        intent_fst = make_intent_fst(grammar_fsts)

        # Check timer input
        intents = fstaccept(
            intent_fst, "set a timer for ten minutes and forty two seconds"
        )

        intent = intents[0]

        logging.debug(intent)
        self.assertEqual(intent["intent"]["name"], "SetTimer")
        self.assertEqual(intent["intent"]["confidence"], 1)
        self.assertEqual(len(intent["entities"]), 2)

        expected = {"minutes": "10", "seconds": "40 2"}
        for ev in intent["entities"]:
            entity = ev["entity"]
            if (entity in expected) and (ev["value"] == expected[entity]):
                expected.pop(entity)

        self.assertDictEqual(expected, {})

        # Verify multiple interpretations
        intents = fstaccept(intent_fst, "set color to purple")

        logging.debug(intents)
        self.assertEqual(len(intents), 2)

        for intent in intents:
            self.assertIn(intent["intent"]["name"], ["ChangeLight", "ChangeLightColor"])
            self.assertEqual(intent["intent"]["confidence"], 0.5)
            self.assertEqual(len(intent["entities"]), 1)

            ev = intent["entities"][0]
            self.assertEqual(ev["entity"], "color")
            self.assertEqual(ev["value"], "purple")


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
