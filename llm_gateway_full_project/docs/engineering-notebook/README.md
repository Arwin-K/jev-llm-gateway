# Engineering notebook

`Jev-LLM-Gateway-Engineering-Notebook.pdf` is the finished notebook: foundations, Jev research, architecture, and Day 1–2 checkpoints. Everything else here is its editable source.

| Path | What it is |
| --- | --- |
| `source/parts/*.html` | The text, one file per part, assembled in filename order. Edit these. |
| `source/notebook.css` | Print stylesheet (page size, fonts, callouts, checkpoint cards). |
| `source/figures.py`, `source/svg.py` | Generate every diagram in `figures/` as vector SVG. |
| `figures/*.svg` | Generated diagrams (do not edit by hand; edit `figures.py`). |
| `notebook.html` | Assembled single HTML document produced by the build (opens in any browser). |
| `build.py` | Regenerates figures, assembles `notebook.html`, numbers figures, and prints the PDF with a page-numbered contents. |

Rebuild on macOS (needs Google Chrome and poppler's `pdftotext`/`pdfinfo`, e.g. `brew install poppler`):

```bash
python3 build.py
```

Without the build script, open `notebook.html` in Chrome, choose Print → Save as PDF, Letter size, margins "Default", and enable "Background graphics". Contents page numbers come only from `build.py`.

In the source, figures are written as `<figure data-src="f01-architecture" id="...">` and cross-references as `<a class="xref" href="#id"></a>`; the build fills in numbers. Checkpoint cards use `<div class="cp">` with a `<dl>` of Understand / Change / Why here / Evidence / Common mistake / Recorded rows.
