"""Offline regression tests; run with python3 -B -m unittest discover -s tests."""

import contextlib
import io
import json
import runpy
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

CLI = Path(__file__).resolve().parents[1] / "reddit"
POST = {
    "id": "abc",
    "subreddit": "UMBC",
    "author": "tester",
    "title": "Campus",
    "selftext": "Full body\n" + "x" * 2100,
    "created_utc": 1704067201,
    "score": 5,
    "num_comments": 2,
}
COMMENT = {
    "id": "def",
    "subreddit": "UMBC",
    "author": "tester",
    "body": "Comment\n" + "y" * 700,
    "created_utc": 1704067202,
    "score": 3,
    "link_id": "t3_abc",
}
FIELDS = {
    "id",
    "kind",
    "subreddit",
    "author",
    "title",
    "body",
    "created_utc",
    "permalink",
    "score",
    "num_comments",
}


class CliTests(unittest.TestCase):
    def setUp(self):
        self.module = runpy.run_path(str(CLI))
        self.ns = self.module["main"].__globals__

    def invoke(self, args, records=True):
        calls = []

        def fake_api(path, params):
            calls.append((path, params))
            return (
                [dict(COMMENT if path.startswith("/comments") else POST)]
                if records
                else []
            )

        out = io.StringIO()
        with (
            patch.dict(self.ns, api=fake_api),
            patch("time.sleep"),
            patch.object(sys, "argv", ["reddit", *args]),
            contextlib.redirect_stdout(out),
        ):
            self.module["main"]()
        return out.getvalue(), calls

    def test_json_every_command_and_flag_position(self):
        commands = [
            ("search", "campus", "-s", "UMBC"),
            ("browse", "-s", "UMBC"),
            ("thread", "abc"),
            ("comments", "campus", "-s", "UMBC"),
            ("user", "tester"),
        ]
        for command in commands:
            for args in (["--json", *command], [*command, "--json"]):
                with self.subTest(args=args):
                    out, _ = self.invoke(args)
                    items = [json.loads(line) for line in out.splitlines()]
                    self.assertTrue(items)
                    for item in items:
                        self.assertEqual(set(item), FIELDS)
                        source = POST if item["kind"] == "post" else COMMENT
                        self.assertEqual(
                            item["id"],
                            ("t3_" if item["kind"] == "post" else "t1_")
                            + str(source["id"]),
                        )
                        self.assertEqual(
                            item["body"], source.get("selftext", source.get("body"))
                        )
                        self.assertTrue(
                            item["permalink"].startswith(
                                "https://www.reddit.com/r/UMBC/comments/abc/"
                            )
                        )
                        if item["kind"] == "comment":
                            self.assertIsNone(item["title"])
                            self.assertIsNone(item["num_comments"])

    def test_empty_json_is_empty_stdout(self):
        for args in (["browse", "-s", "UMBC"], ["user", "tester"], ["thread", "abc"]):
            out, _ = self.invoke([*args, "--json"], records=False)
            self.assertEqual(out, "")

    def test_date_and_timestamp_bounds_on_search_browse_user(self):
        for args in (
            ["search", "campus", "-s", "UMBC"],
            ["browse", "-s", "UMBC"],
            ["user", "tester"],
        ):
            for after in ("2024-01-01", "1704067200", "0"):
                with self.subTest(args=args, after=after):
                    _, calls = self.invoke(
                        [*args, "--after", after, "--before", "2024-01-02", "--json"]
                    )
                    for _, params in calls:
                        self.assertEqual(
                            params["after"], 0 if after == "0" else 1704067200
                        )
                        self.assertEqual(params["before"], 1704153600)

    def test_invalid_date_and_missing_bounds(self):
        for args in (
            ["browse", "-s", "UMBC", "--after", "yesterday"],
            ["user", "tester", "--before"],
        ):
            out, err = io.StringIO(), io.StringIO()
            with (
                contextlib.redirect_stdout(out),
                contextlib.redirect_stderr(err),
                self.assertRaises(SystemExit) as raised,
            ):
                self.invoke(args)
            self.assertEqual(raised.exception.code, 1)
            self.assertEqual(out.getvalue(), "")
            self.assertIn("reddit: error:", err.getvalue())

    def test_default_text_output(self):
        cases = [
            (["search", "campus", "-s", "UMBC"], "2024-01-01  r/UMBC"),
            (["browse", "-s", "UMBC"], "### r/UMBC\n"),
            (["thread", "abc"], "Campus\nr/UMBC"),
            (["comments", "campus", "-s", "UMBC"], "2024-01-01  r/UMBC"),
            (["user", "tester"], "--- posts by u/tester ---\n"),
        ]
        for args, heading in cases:
            with self.subTest(args=args):
                actual, _ = self.invoke(args)
                self.assertTrue(actual.startswith(heading))
                self.assertNotIn('"kind":', actual)
                self.assertNotIn("x" * 2100, actual)
                if args[0] != "comments":
                    self.assertIn("Campus", actual)
                    self.assertIn("https://reddit.com/r/UMBC/comments/abc/", actual)

    def test_comment_search_uses_body_parameter(self):
        _, calls = self.invoke(["comments", "campus", "-s", "UMBC", "--json"])
        self.assertEqual(calls[0][1]["body"], "campus")

    def test_http_and_network_failures_exit_nonzero_stderr_only(self):
        for error in (
            'urllib.error.HTTPError("https://example.invalid", 503, "Unavailable", {}, None)',
            'urllib.error.URLError("offline")',
            'TimeoutError("timed out")',
        ):
            # Exercise the actual entry point in a separate process, including retries.
            script = f"""import runpy, sys, urllib.error
from unittest.mock import patch
sys.argv = ['reddit', '--json', 'browse', '-s', 'UMBC']
with patch('urllib.request.urlopen', side_effect={error}), patch('time.sleep'):
    runpy.run_path({str(CLI)!r}, run_name='__main__')
"""
            result = subprocess.run(
                [sys.executable, "-B", "-c", script],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("reddit: error: request failed:", result.stderr)


if __name__ == "__main__":
    unittest.main()
