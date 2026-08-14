from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

from engine import run_pipeline


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.output = run_pipeline.build_output()

    def test_expected_scenario_shape(self) -> None:
        self.assertTrue(self.output["meta"]["synthetic"])
        self.assertEqual(len(self.output["people"]), 9)
        self.assertEqual(len(self.output["events"]), 4)
        self.assertEqual(len(self.output["zones"]), 10)
        self.assertEqual(self.output["metrics"]["evaluated_pairs"], 36)

    def test_probability_distributions_are_valid(self) -> None:
        for person in self.output["people"]:
            self.assertGreaterEqual(person["involvement"], 0)
            self.assertLessEqual(person["involvement"], 1)
            self.assertTrue(math.isclose(sum(person["roles"].values()), 1, abs_tol=1e-3))
            self.assertTrue(math.isclose(sum(person["crime_types"].values()), 1, abs_tol=1e-3))
        for event in self.output["events"]:
            self.assertGreaterEqual(event["risk"], 0)
            self.assertLessEqual(event["risk"], 1)
            self.assertTrue(math.isclose(sum(event["crime_types"].values()), 1, abs_tol=1e-3))

    def test_machine_view_threshold_selects_both_roles(self) -> None:
        threshold = self.output["meta"]["threshold"]
        relevant = [person for person in self.output["people"] if person["involvement"] >= threshold]
        winning_roles = {max(person["roles"], key=person["roles"].get) for person in relevant}
        self.assertEqual(len(relevant), 7)
        self.assertIn("victim", winning_roles)
        self.assertIn("perpetrator", winning_roles)

    def test_output_is_deterministic_and_json_serializable(self) -> None:
        second = run_pipeline.build_output()
        self.assertEqual(self.output, second)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "output.json"
            run_pipeline.write_json(path, self.output)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), self.output)

    def test_explanations_reference_existing_evidence(self) -> None:
        for person in self.output["people"]:
            evidence_ids = {item["id"] for item in person["evidence"]}
            for explanation in person["explanations"]:
                self.assertTrue(set(explanation["record_ids"]).issubset(evidence_ids))


if __name__ == "__main__":
    unittest.main()
