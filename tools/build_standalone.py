"""Build the dependency-free, single-file HTML version of The Machine.

Newcomer summary
----------------
1. The Python engine writes ``app/data/machine-output.json``.
2. ``standalone/template.html`` contains the page, CSS and JavaScript.
3. This script puts the JSON into the template.
4. The result can be opened by double-clicking it. No web server is needed.

Run from the repository root:

    python tools/build_standalone.py
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "app" / "data" / "machine-output.json"
TEMPLATE_PATH = ROOT / "standalone" / "template.html"
OUTPUT_PATH = ROOT / "standalone" / "the-machine-manhattan.html"
PLACEHOLDER = "/*__MACHINE_DATA__*/"


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    if PLACEHOLDER not in template:
        raise ValueError(f"Template is missing placeholder: {PLACEHOLDER}")

    # Compact JSON keeps the final HTML reasonably small. Replacing </ avoids
    # accidentally ending the <script> tag if future demo text contains it.
    embedded_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    embedded_json = embedded_json.replace("</", "<\\/")
    result = template.replace(PLACEHOLDER, embedded_json, 1)

    # These checks enforce the promise that the generated page is truly local.
    forbidden = (
        "fetch(",
        'src="http://',
        'src="https://',
        'href="http://',
        'href="https://',
        'type="module"',
    )
    found = [token for token in forbidden if token in result]
    if found:
        raise ValueError(f"Standalone output contains network-dependent code: {found}")

    OUTPUT_PATH.write_text(result, encoding="utf-8")
    print(f"Built {OUTPUT_PATH.relative_to(ROOT)} ({OUTPUT_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
