"""Client-facing text regressions without a database or production data."""
import unittest
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


class ClientPresentationTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.env = Environment(loader=FileSystemLoader(self.root / 'app/templates'),
                               autoescape=select_autoescape(['html']))

    def test_client_labels_are_readable(self):
        html = self.env.get_template('client_cabinet.html').render(
            lead={'id': 1, 'name': 'Тест', 'lead_status': 'in_work', 'city': 'spb',
                  'service_type': 'consultation', 'style_preference': 'graphics',
                  'body_place': 'arm', 'approximate_size': '10_20'}, files=[])
        for value in ('В работе', 'Санкт-Петербург', 'Консультация', 'Графика', 'Рука', '10–20 см'):
            self.assertIn(value, html)
        for code in ('>in_work<', '>spb<', '>consultation<'):
            self.assertNotIn(code, html)

    def test_unknown_and_empty_labels_remain_safe(self):
        label = self.env.get_template('partials/client_labels.html').module.label
        self.assertEqual(label('city', 'Казань'), 'Казань')
        self.assertEqual(label('city', None), '—')
        self.assertEqual(label('city', '<script>alert(1)</script>'),
                         '&lt;script&gt;alert(1)&lt;/script&gt;')

    def test_confirmation_has_no_dangling_sentence(self):
        html = self.env.get_template('thanks.html').render()
        self.assertNotIn('в выбранный способ связи.', html)

    @unittest.skipUnless((Path(__file__).resolve().parents[1] / 'docs/screenshots').is_dir(),
                         'Documentation assets are not shipped in the application image')
    def test_portfolio_screenshot_extensions_match_content(self):
        for stem in ('home-desktop', 'home-mobile', 'project', 'request', 'admin-crm'):
            with self.subTest(stem=stem):
                path = self.root / 'docs/screenshots' / (stem + '.jpg')
                with path.open('rb') as handle:
                    self.assertEqual(handle.read(3), b'\xff\xd8\xff')


if __name__ == '__main__':
    unittest.main()
