import sys
import time
import pathlib
import urllib.parse
import urllib.request
from html.parser import HTMLParser

PAGE = "https://redziny.pl/dla-mieszkancow/gminny-zaklad-komunikacji/rozklad-jazdy-caloroczny/"
USER_AGENT = "rozklady-osobiste/1.0 (uzytek osobisty)"
PAUSE_SECONDS = 2


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


class PdfLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for key, value in attrs:
                if key == "href" and value and value.lower().endswith(".pdf"):
                    self.links.append(value)


def main():
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "rozklady")
    out.mkdir(exist_ok=True)

    parser = PdfLinks()
    parser.feed(get(PAGE).decode("utf-8", errors="replace"))
    urls = sorted({urllib.parse.urljoin(PAGE, link) for link in parser.links})
    print(f"Znaleziono PDF-ów: {len(urls)}")

    for url in urls:
        name = urllib.parse.unquote(url.rsplit("/", 1)[-1])
        target = out / name
        if target.exists():
            continue
        target.write_bytes(get(url))
        print("zapisano:", name)
        time.sleep(PAUSE_SECONDS)


if __name__ == "__main__":
    main()