from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "standalone" / "the-machine-manhattan.html"


class StandaloneHtmlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = HTML_PATH.read_text(encoding="utf-8")

    def test_is_a_complete_html_document(self) -> None:
        parser = HTMLParser()
        parser.feed(self.html)
        self.assertIn("<!doctype html>", self.html.lower())
        for element_id in ("queue", "panel-head", "surface", "ticker", "dossier"):
            self.assertIn(f'id="{element_id}"', self.html)

    def test_data_is_embedded(self) -> None:
        self.assertNotIn("/*__MACHINE_DATA__*/", self.html)
        self.assertIn("const MACHINE_DATA = {", self.html)
        self.assertIn('"synthetic":true', self.html)

    def test_map_and_slider_interactions_are_embedded(self) -> None:
        self.assertIn('class="zone-selection"', self.html)
        self.assertIn("renderThresholdDependents(event.target)", self.html)
        self.assertIn('"scheme":"2020 Neighborhood Tabulation Areas"', self.html)

    def test_needs_no_network_or_module_loader(self) -> None:
        forbidden = (
            "fetch(",
            'src="http://',
            'src="https://',
            'href="http://',
            'href="https://',
            'type="module"',
        )
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, self.html)


if __name__ == "__main__":
    unittest.main()
