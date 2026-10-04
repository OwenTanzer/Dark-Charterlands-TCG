"""Synthetic, offline tests. No card text, artwork, or live HTTP requests."""
import copy
import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import analyze_cards as analyze
import scrape_cards as scrape

URL = scrape.BASE + "/card/MZ1/1"
HTML = '''<article><header><p>Test Set · MZ1 #1</p><h1>Éclair <span>— Test</span></h1>
<div><span style="background-color: blue">Air</span><span>Rare</span>
<span>Equipment</span><span>Creature</span></div></header>
<dl><dt>Cost</dt><dd>3</dd><dt>Influence</dt><dd>2</dd><dt>New Stat</dt><dd>4</dd></dl>
<div><span>Traits</span><span>Invented</span></div>
<div><span>New List</span><span>Example</span></div>
<section><h3>Test ability</h3><p>While testing, do nothing.</p></section>
<blockquote>Original synthetic fixture.</blockquote></article>'''


def response(body=HTML, status=200):
    r = requests.Response()
    r.status_code = status
    r._content = body.encode("utf-8")
    r.encoding = "ISO-8859-1"  # Reproduce requests' missing-charset fallback.
    r.url = URL
    return r


class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.here = Path(self.tmp.name)
        for name, value in (("HERE", self.here), ("CACHE", self.here / "cache")):
            p = patch.object(scrape, name, value)
            p.start()
            self.addCleanup(p.stop)
        p = patch.object(analyze, "HERE", self.here)
        p.start()
        self.addCleanup(p.stop)
        self.addCleanup(self.tmp.cleanup)
        self.card = scrape.parse_card(HTML, URL)

    def scrape_run(self, argv, urls=None, side_effect=None):
        policy = Mock()
        policy.can_fetch.return_value = True
        with patch.object(scrape, "robots_policy", return_value=(policy, 1)), \
             patch.object(scrape, "card_urls", return_value=urls or [URL]), \
             patch.object(scrape, "fetch", side_effect=side_effect, return_value=HTML), \
             redirect_stderr(io.StringIO()):
            return scrape.main(argv)

    def test_parse_unicode_and_generic_fields(self):
        self.assertEqual(self.card["name"], "Éclair")
        self.assertEqual(self.card["subtitle"], "Test")
        self.assertEqual(self.card["card_types"], ["Equipment", "Creature"])
        self.assertEqual(self.card["rarity"], "Rare")
        self.assertEqual(self.card["stats"]["New Stat"], "4")
        self.assertEqual(self.card["lists"]["New List"], ["Example"])

    def test_missing_header_is_parse_failure(self):
        with self.assertRaises(ValueError):
            scrape.parse_card("<article><h1>Not a card</h1></article>", URL)

    def test_mismatched_card_header_is_rejected(self):
        with self.assertRaises(ValueError):
            scrape.parse_card(HTML, scrape.BASE + "/card/MZ1/2")

    def test_rate_limit_aborts_remaining_pages(self):
        error = requests.HTTPError(response=response("Busy", 429))
        with patch.object(scrape, "fetch", side_effect=error) as fetch:
            policy = Mock()
            policy.can_fetch.return_value = True
            with patch.object(scrape, "robots_policy", return_value=(policy, 1)), \
                 patch.object(scrape, "card_urls", return_value=[URL, scrape.BASE + "/card/MZ1/2"]), \
                 redirect_stderr(io.StringIO()):
                self.assertEqual(scrape.main([]), 1)
            self.assertEqual(fetch.call_count, 1)

    @patch.object(scrape.time, "sleep")
    def test_transport_failure_is_paced_and_stops_run(self, sleep):
        session = Mock()
        session.get.side_effect = requests.ConnectionError("connection reset")
        policy = Mock()
        policy.can_fetch.return_value = True
        with patch.object(scrape.requests, "Session", return_value=session), \
             patch.object(scrape, "robots_policy", return_value=(policy, 3)), \
             patch.object(scrape, "card_urls", return_value=[URL, scrape.BASE + "/card/MZ1/2"]), \
             redirect_stderr(io.StringIO()):
            self.assertEqual(scrape.main([]), 1)
        self.assertEqual(session.get.call_count, 1)
        sleep.assert_called_once_with(3)
        self.assertFalse((self.here / "cards.json").exists())

    def test_url_allowlist_prevents_foreign_hosts_and_cache_traversal(self):
        for url in ("https://evil.test/card/MZ1/1", scrape.BASE + "/card/../1", URL + "?query=1"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                scrape.fetch(Mock(), url, 1)

    @patch.object(scrape.time, "sleep")
    def test_sitemap_http_error_cannot_become_empty_dataset(self, sleep):
        session = Mock()
        session.get.return_value = response("<error/>", 404)
        with self.assertRaises(requests.HTTPError):
            scrape.card_urls(session)

    @patch.object(scrape.time, "sleep")
    def test_sitemap_uses_xml_and_same_origin_only(self, sleep):
        session = Mock()
        session.get.return_value = response(f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{URL}</loc></url><url><loc>https://evil.test/card/MZ1/2</loc></url></urlset>')
        self.assertEqual(scrape.card_urls(session), [URL])

    @patch.object(scrape.time, "sleep")
    def test_empty_sitemap_rejected(self, sleep):
        session = Mock()
        session.get.return_value = response("<urlset/>")
        with self.assertRaises(ValueError):
            scrape.card_urls(session)

    @patch.object(scrape.time, "sleep")
    def test_utf8_ignores_latin1_fallback(self, sleep):
        session = Mock()
        session.get.return_value = response()
        self.assertEqual(scrape.request_text(session, URL, 1), HTML)
        self.assertFalse(session.get.call_args.kwargs["allow_redirects"])

    @patch.object(scrape.time, "sleep")
    def test_bad_encoding_not_cached(self, sleep):
        session = Mock()
        r = response()
        r._content = b"\xff"
        session.get.return_value = r
        with self.assertRaises(UnicodeDecodeError):
            scrape.fetch(session, URL, 1)
        self.assertFalse(scrape.CACHE.exists())

    @patch.object(scrape.time, "sleep")
    def test_interstitial_not_cached(self, sleep):
        session = Mock()
        session.get.return_value = response("<h1>Please sign in</h1>")
        with self.assertRaises(ValueError):
            scrape.fetch(session, URL, 1)
        self.assertFalse(scrape.CACHE.exists())

    @patch.object(scrape.time, "sleep")
    def test_retries_are_bounded(self, sleep):
        session = Mock()
        session.get.return_value = response("Busy", 503)
        with self.assertRaises(requests.HTTPError):
            scrape.request_text(session, URL, 1)
        self.assertEqual(session.get.call_count, 3)

    @patch.object(scrape.time, "sleep")
    def test_long_retry_after_stops_without_early_retry(self, sleep):
        session = Mock()
        r = response("Busy", 429)
        r.headers["Retry-After"] = "120"
        session.get.return_value = r
        with self.assertRaises(requests.HTTPError):
            scrape.request_text(session, URL, 1)
        self.assertEqual(session.get.call_count, 1)

    @patch.object(scrape.time, "sleep")
    def test_redirect_not_followed_or_cached(self, sleep):
        session = Mock()
        r = response("", 302)
        r.headers["Location"] = "https://evil.test/"
        session.get.return_value = r
        with self.assertRaises(ValueError):
            scrape.fetch(session, URL, 1)
        self.assertFalse(scrape.CACHE.exists())

    def test_cached_page_does_not_request_network(self):
        path = scrape.CACHE / "MZ1" / "0001.html"
        path.parent.mkdir(parents=True)
        path.write_text(HTML)
        session = Mock()
        self.assertEqual(scrape.fetch(session, URL, 1), HTML)
        session.get.assert_not_called()

    def test_invalid_cli_values_stop_before_network(self):
        for args in (["--limit", "0"], ["--limit", "-1"], ["--delay", "-1"], ["--delay", "nan"], ["--delay", "inf"]):
            with self.subTest(args=args), patch.object(scrape, "robots_policy") as policy, redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                scrape.main(args)
            policy.assert_not_called()

    def test_unknown_set_rejected_without_export(self):
        self.assertEqual(self.scrape_run(["--sets", "BAD"]), 1)
        self.assertFalse((self.here / "cards.partial.json").exists())

    def test_robots_denial_stops_before_card_fetch(self):
        policy = Mock()
        policy.can_fetch.return_value = False
        with patch.object(scrape, "robots_policy", return_value=(policy, 1)), \
             patch.object(scrape, "card_urls") as urls, redirect_stderr(io.StringIO()):
            self.assertEqual(scrape.main([]), 1)
        urls.assert_not_called()

    def test_failure_preserves_existing_exports(self):
        for suffix in ("json", "csv", "manifest.json"):
            (self.here / f"cards.{suffix}").write_text("old")
        self.assertEqual(self.scrape_run([], side_effect=ValueError("bad page")), 1)
        for suffix in ("json", "csv", "manifest.json"):
            self.assertEqual((self.here / f"cards.{suffix}").read_text(), "old")
        self.assertTrue((self.here / "failed.json").exists())

    def test_partial_run_never_overwrites_full_exports_or_report(self):
        (self.here / "cards.json").write_text("old full")
        (self.here / "FEATURES.md").write_text("old full report")
        self.assertEqual(self.scrape_run(["--limit", "1"]), 0)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(analyze.main(["--partial"]), 0)
        self.assertEqual((self.here / "cards.json").read_text(), "old full")
        self.assertEqual((self.here / "FEATURES.md").read_text(), "old full report")
        self.assertIn("filtered", (self.here / "FEATURES.partial.md").read_text())

    def test_success_manifest_and_full_analysis(self):
        (self.here / "failed.json").write_text("stale")
        self.assertEqual(self.scrape_run([]), 0)
        self.assertFalse((self.here / "failed.json").exists())
        cards, manifest = analyze.load_cards("cards")
        self.assertEqual(cards, [self.card])
        self.assertEqual(manifest["set_counts"], {"MZ1": 1})
        with redirect_stdout(io.StringIO()):
            self.assertEqual(analyze.main([]), 0)
        report = (self.here / "FEATURES.md").read_text()
        self.assertIn("full_sitemap", report)
        self.assertIn("heuristic", report)

    def test_bad_checksum_or_counts_cannot_overwrite_report(self):
        self.scrape_run([])
        (self.here / "FEATURES.md").write_text("keep")
        (self.here / "cards.json").write_text("[]")
        with redirect_stderr(io.StringIO()):
            self.assertEqual(analyze.main([]), 1)
        self.assertEqual((self.here / "FEATURES.md").read_text(), "keep")
        self.scrape_run([])
        path = self.here / "cards.manifest.json"
        manifest = json.loads(path.read_text())
        manifest["sitemap_count"] = 2
        path.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            analyze.load_cards("cards")

    def test_missing_manifest_does_not_silently_analyze_legacy_data(self):
        (self.here / "cards.json").write_text(json.dumps([self.card]))
        with redirect_stderr(io.StringIO()):
            self.assertEqual(analyze.main([]), 1)
        self.assertFalse((self.here / "FEATURES.md").exists())

    def test_csv_formula_safety_and_field_collision(self):
        card = copy.deepcopy(self.card)
        card["name"] = "=1+1"
        card["stats"]["name"] = "untrusted"
        card["lists"]["name"] = ["another"]
        path = self.here / "test.csv"
        scrape.write_csv([card], path)
        row = next(csv.DictReader(io.StringIO(path.read_text())))
        self.assertEqual(row["name"], "'=1+1")
        self.assertEqual(row["stat:name"], "untrusted")
        self.assertEqual(row["list:name"], "another")
        self.assertEqual(scrape.csv_safe(" \t@SUM(1)"), "' \t@SUM(1)")

    def test_nonfinite_stats_and_markdown_table_escape(self):
        self.assertIsNone(analyze.num("NaN"))
        self.assertIsNone(analyze.num("inf"))
        self.assertIn(r"a\|b", analyze.table(["Test"], [["a|b"]])[2])


if __name__ == "__main__":
    unittest.main()
