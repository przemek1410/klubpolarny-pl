"""Homepage and local asset smoke checks; no external requests or deployment."""
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.parse import unquote, urlsplit, quote
from urllib.request import urlopen
import sys
import unittest

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = set()
        self.in_title = False
        self.title = ""
        self.assets = set()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.add(tag)
        if tag == "title":
            self.in_title = True
        url = a.get("src") if tag in ("script", "img") else None
        if tag == "link" and set(a.get("rel", "").split()) & {"stylesheet", "icon", "apple-touch-icon"}:
            url = a.get("href")
        if url and not urlsplit(url).scheme and not url.startswith(("//", "#")):
            self.assets.add(unquote(urlsplit(url).path))
    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
    def handle_data(self, data):
        if self.in_title:
            self.title += data

def validate(root):
    root = Path(root).resolve()
    source = (root / "index.html").read_text(encoding="utf-8-sig")
    if any(line.startswith(("<<<<<<< ", "=======", ">>>>>>> ")) for line in source.splitlines()):
        raise ValueError("Unresolved merge conflict in homepage")
    page = Page()
    page.feed(source)
    if not {"html", "head", "body", "title"} <= page.tags or not page.title.strip():
        raise ValueError("Homepage must have html/head/body and a non-empty title")
    local_files = {"index.html"}
    for asset in page.assets:
        candidate = (root / asset.lstrip("/")).resolve()
        if not candidate.is_relative_to(root) or not candidate.is_file() or candidate.stat().st_size == 0:
            raise ValueError(f"Missing, empty or unsafe homepage asset: {asset}")
        local_files.add(candidate.relative_to(root).as_posix())
    return local_files

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def smoke(root):
    files = validate(root)
    handler = partial(QuietHandler, directory=str(Path(root).resolve()))
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for file in sorted(files):
                with urlopen(f"http://127.0.0.1:{server.server_port}/" + quote(file), timeout=10) as response:
                    if response.status != 200 or not response.read(1):
                        raise ValueError(f"Asset is not served: {file}")
        finally:
            server.shutdown()
            thread.join(timeout=5)
    print(f"PASS: homepage and {len(files)-1} unique local assets served over HTTP")

class CheckerTests(unittest.TestCase):
    def test_valid_page(self):
        with TemporaryDirectory() as d:
            Path(d, "index.html").write_text('<html><head><title>Test</title></head><body><img src="a.png"></body></html>', encoding="utf8")
            Path(d, "a.png").write_bytes(b"fixture")
            self.assertEqual(validate(d), {"index.html", "a.png"})
    def test_missing_asset_fails(self):
        with TemporaryDirectory() as d:
            Path(d, "index.html").write_text('<html><head><title>Test</title></head><body><script src="missing.js"></script></body></html>', encoding="utf8")
            with self.assertRaisesRegex(ValueError, "asset"):
                validate(d)
    def test_missing_title_fails(self):
        with TemporaryDirectory() as d:
            Path(d, "index.html").write_text("<html><head></head><body>Broken</body></html>", encoding="utf8")
            with self.assertRaisesRegex(ValueError, "title"):
                validate(d)
    def test_path_escape_fails(self):
        with TemporaryDirectory() as d:
            Path(d, "index.html").write_text('<html><head><title>Test</title></head><body><img src="../outside.png"></body></html>', encoding="utf8")
            with self.assertRaisesRegex(ValueError, "asset"):
                validate(d)

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        unittest.main(argv=[sys.argv[0]], verbosity=2)
    else:
        smoke(Path(__file__).resolve().parents[1])
