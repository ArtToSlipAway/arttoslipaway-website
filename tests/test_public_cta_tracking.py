import re
import unittest
from pathlib import Path


TEMPLATES = Path(__file__).resolve().parents[1] / "app" / "templates"
class PublicCtaTrackingTests(unittest.TestCase):
    def test_every_public_request_link_has_a_source(self):
        missing = []

        for path in TEMPLATES.rglob("*.html"):
            relative = path.relative_to(TEMPLATES)
            if "admin" in relative.parts or path.name.startswith("admin"):
                continue

            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r'href="(/request[^\"]*)"', text):
                if "source=" not in match.group(1):
                    line = text.count("\n", 0, match.start()) + 1
                    missing.append(f"{relative}:{line}: {match.group(1)}")

        self.assertEqual(missing, [], "Public request CTA without source:\n" + "\n".join(missing))


if __name__ == "__main__":
    unittest.main()
