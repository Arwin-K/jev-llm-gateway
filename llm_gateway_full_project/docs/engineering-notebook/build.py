"""Build the engineering notebook: figures -> notebook.html -> PDF with a page-numbered contents.

Usage:  python3 build.py            (needs Google Chrome and poppler's pdftotext)
"""

import html
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARTS = sorted((ROOT / "source" / "parts").glob("*.html"))
HTML_OUT = ROOT / "notebook.html"
PDF_OUT = ROOT / "Jev-LLM-Gateway-Engineering-Notebook.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def assemble():
    body = "\n".join(p.read_text() for p in PARTS)
    body = body.replace('src="../figures/', 'src="figures/')

    # Number figures in document order and inline their images.
    numbers = {}

    def figure(m):
        attrs, inner = m.group(1), m.group(2)
        src = re.search(r'data-src="([^"]+)"', attrs).group(1)
        fid = re.search(r'id="([^"]+)"', attrs).group(1)
        assert (ROOT / "figures" / f"{src}.svg").exists(), src
        numbers[fid] = len(numbers) + 1
        inner = inner.replace("<figcaption>", f'<figcaption><span class="fig-no">Figure {numbers[fid]}.</span> ', 1)
        return f'<figure{attrs}><img src="figures/{src}.svg" alt="Figure {numbers[fid]}">{inner}</figure>'

    body = re.sub(r"<figure([^>]*data-src[^>]*)>(.*?)</figure>", figure, body, flags=re.S)

    # Checkpoint cards: each dt/dd pair becomes an unbreakable row; the card heading stays with row one.
    def card(m):
        head, dl = m.group(1), m.group(2)
        rows = re.findall(r"<dt([^>]*)>(.*?)</dt>\s*<dd>(.*?)</dd>", dl, flags=re.S)
        html_rows = [f'<div class="row"><div class="dt"{a}>{k}</div><div class="dd">{v}</div></div>' for a, k, v in rows]
        return (f'<div class="cp"><div class="cp-keep">{head}{html_rows[0]}</div>' + "".join(html_rows[1:]) + "</div>")

    body = re.sub(r'<div class="cp">(<div class="cp-head">.*?</div>)<dl>(.*?)</dl></div>', card, body, flags=re.S)
    body = body.replace('<div class="dt" class="', '<div class="dt ')

    def xref(m):
        target = m.group(1)
        assert target in numbers, f"unresolved figure reference #{target}"
        return f'<a class="xref" href="#{target}">Figure {numbers[target]}</a>'

    body = re.sub(r'<a class="xref" href="#([^"]+)"></a>', xref, body)

    # Contents entries: every h1 with an id, and h2s under numbered parts.
    entries = []
    for m in re.finditer(r'<h([12]) id="([^"]+)"([^>]*)>(.*?)</h\1>', body, flags=re.S):
        level, hid, attrs, inner = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        part = re.search(r'<span class="part-no">(.*?)</span>', inner)
        title = re.sub(r"<[^>]+>", "", re.sub(r'<span class="part-no">.*?</span>', "", inner)).strip()
        entries.append({"level": level, "id": hid, "title": html.unescape(title),
                        "num": part.group(1).replace("Part ", "") if part else ""})
    return body, entries, numbers


def toc_html(entries, pages):
    rows = []
    for e in entries:
        pg = pages.get(e["id"], "")
        cls = "t1" if e["level"] == 1 else "t2"
        num = f'<span class="num">{e["num"]}</span>' if e["level"] == 1 else ""
        rows.append(f'<li class="{cls}">{num}<a href="#{e["id"]}">{html.escape(e["title"])}</a>'
                    f'<span class="dots"></span><span class="pg">{pg}</span></li>')
    return ('<section class="toc"><h1 id="contents" class="unnumbered">Contents</h1><ol>'
            + "".join(rows) + "</ol></section>")


def write_html(body, entries, pages):
    doc = body.replace("<!--TOC-->", toc_html(entries, pages))
    HTML_OUT.write_text(
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        "<title>Jev LLM Gateway — Engineering Notebook</title>"
        '<link rel="stylesheet" href="source/notebook.css"></head>\n<body>\n' + doc + "\n</body></html>\n")


def render():
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--generate-pdf-document-outline", "--allow-file-access-from-files",
                    f"--print-to-pdf={PDF_OUT}", HTML_OUT.as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def norm(s):
    s = unicodedata.normalize("NFKC", s).replace("­", "")
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def page_texts():
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(PDF_OUT)], capture_output=True, text=True).stdout).group(1))
    out = subprocess.run(["pdftotext", "-layout", str(PDF_OUT), "-"], capture_output=True, text=True).stdout
    pages = out.split("\f")[:n]
    return [norm(p) for p in pages]


def locate(entries):
    texts = page_texts()
    toc_end = next(i for i, t in enumerate(texts) if "contents" in t[:40]) + 1
    while toc_end < len(texts) and "howtoreadthisnotebook" not in texts[toc_end][:80]:
        toc_end += 1
    pages, cursor = {}, toc_end
    for e in entries:
        key = norm(e["title"])[:48]
        for i in range(cursor, len(texts)):
            if key in texts[i]:
                pages[e["id"]] = i + 1
                cursor = i
                break
        else:
            raise SystemExit(f"could not locate heading: {e['title']}")
    return pages, len(texts)


def main():
    subprocess.run([sys.executable, str(ROOT / "source" / "figures.py")], check=True, stdout=subprocess.DEVNULL)
    body, entries, figs = assemble()
    pages = {}
    for attempt in range(4):
        write_html(body, entries, pages)
        render()
        found, total = locate(entries)
        if found == pages:
            break
        pages = found
    else:
        raise SystemExit("contents page numbers did not converge")
    print(f"{PDF_OUT.name}: {total} pages, {len(figs)} figures, {len(entries)} contents entries")


if __name__ == "__main__":
    main()
