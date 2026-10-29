"""Generate every notebook figure as a vector SVG. Run: python3 source/figures.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from svg import ACCENT, INK, LINE, MUTED, Svg  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "figures"
OUT.mkdir(exist_ok=True)
FIGS = {}


def fig(name):
    def wrap(fn):
        FIGS[name] = fn
        return fn
    return wrap


def legend(s, x, y, items, gap=150):
    for i, (kind, label) in enumerate(items):
        xx = x + i * gap
        s.rect(xx, y - 10, 22, 13, kind, rx=3)
        s.text(xx + 30, y + 1, label, 10.5, color=MUTED)


# ---------------------------------------------------------------- Part 1
@fig("f01-architecture")
def architecture():
    s = Svg(720, 470)
    s.frame(16, 30, 478, 392, "M3 MacBook · application machine", "mac")
    s.box(36, 88, 120, 64, ["Client", "curl · jev smoke", "your app"], "plain")
    s.box(200, 64, 274, 112, ["Gateway", "FastAPI on 127.0.0.1:8080", "validate · resolve tier", "forward · stream · trace"], "mac")
    s.arrow(156, 120, 198, 120)
    s.box(200, 236, 274, 72, ["Native Ollama · :11434", "small  qwen2.5:1.5b", "medium qwen2.5:7b"], "mac")
    s.arrow(337, 176, 337, 234)
    s.label(337, 210, "explicit tier (Day 1)")
    s.box(36, 236, 132, 72, ["Request records", "trace log · usage", "timings · status"], "plain")
    s.line([(230, 176), (230, 196), (102, 196), (102, 234)])
    s.box(36, 342, 208, 54, ["DistilBERT fallback", "trained router · Day 3"], "muted")
    s.box(266, 342, 208, 54, ["Embeddings + FAISS cache", "Day 4"], "muted")

    s.frame(516, 30, 188, 250, "External APIs", "ext")
    s.box(532, 66, 156, 74, ["Jev · TypeSafe", "decision API", "routing from Day 3"], "jev")
    s.box(532, 176, 156, 74, ["Frontier model API", "paid · budget-gated", "key from env only"], "ext")
    s.line([(474, 92), (530, 92)], dash="5 4", color=ACCENT)
    s.label(502, 84, "Day 3+", size=9.5)
    s.line([(474, 150), (500, 150), (500, 212), (530, 212)], color="#55697d")

    s.frame(516, 304, 188, 118, "Google Colab · experiments", "colab")
    s.box(532, 336, 156, 70, ["vLLM on NVIDIA GPU", "same repo source", "loopback only"], "colab")
    s.line([(494, 372), (530, 372)], dash="3 3", color="#5c7a5c")
    s.label(512, 392, "source zip", size=9.5)

    legend(s, 24, 452, [("mac", "runs on the Mac"), ("ext", "external service"),
                        ("colab", "separate experiment env"), ("muted", "later build day")], gap=172)
    return s


@fig("f02-runtime-options")
def runtime_options():
    s = Svg(720, 330)
    cols = [
        ("1 · Local only", False),
        ("2 · Notebook-dependent app", False),
        ("3 · Mac app + separate GPU lab", True),
    ]
    for i, (title, chosen) in enumerate(cols):
        x = 12 + i * 236
        s.rect(x, 12, 224, 306, "plain", rx=10, sw=2.2 if chosen else 1.2,
               stroke=ACCENT if chosen else None)
        s.text(x + 112, 36, title, 13, "middle", 600, ACCENT if chosen else INK)
        if chosen:
            s.label(x + 112, 54, "proposed direction", 10, color=ACCENT, bg=False, italic=True)
    # option 1
    x = 12
    s.frame(x + 14, 66, 196, 104, "Mac", "mac", size=10.5)
    s.box(x + 26, 92, 80, 60, ["Gateway"], "mac", size=11.5)
    s.box(x + 120, 92, 80, 60, ["Ollama", "small/medium"], "mac", size=11.5)
    s.arrow(x + 106, 122, x + 118, 122)
    s.text(x + 16, 196, ["+ private, works offline", "+ one machine to reason about",
                         "– no NVIDIA/vLLM evidence", "– bounded by unified memory",
                         "– frontier still external"], 11, color=INK)
    # option 2
    x = 248
    s.box(x + 16, 92, 72, 60, ["Gateway", "on Mac"], "mac", size=11.5)
    s.box(x + 136, 80, 76, 84, ["vLLM", "in Colab", "notebook"], "colab", size=11.5)
    s.line([(x + 88, 122), (x + 134, 122)], dash="4 3", color="#a24b36")
    s.label(x + 111, 112, "tunnel", 9.5, color="#a24b36")
    s.text(x + 16, 196, ["+ real NVIDIA GPU behind app", "– session ends → app breaks",
                         "– public tunnel exposes a port", "– latency includes internet hop",
                         "– results mix two machines"], 11, color=INK)
    # option 3
    x = 484
    s.frame(x + 12, 66, 98, 104, "Mac", "mac", size=10.5)
    s.box(x + 22, 88, 78, 34, ["Gateway"], "mac", size=11.5)
    s.box(x + 22, 128, 78, 34, ["Ollama"], "mac", size=11.5)
    s.frame(x + 118, 66, 96, 104, "Colab", "colab", size=10.5)
    s.box(x + 126, 88, 80, 74, ["vLLM", "same source", "own results"], "colab", size=11.5)
    s.text(x + 16, 196, ["+ app never needs a notebook", "+ NVIDIA runs from same commit",
                         "+ each result labelled by env", "– two setups to maintain",
                         "– GPU access not guaranteed"], 11, color=INK)
    return s


@fig("f03-routing-value")
def routing_value():
    s = Svg(720, 262)
    s.text(16, 22, "Where a request's time and cost go (illustrative proportions, not measurements)", 12, weight=600)
    rows = [
        ("Always frontier", [("frontier generation", 330, "ext")]),
        ("Routed · easy request", [("decision", 56, "jev"), ("small generation", 100, "mac")]),
        ("Routed · misjudged", [("decision", 56, "jev"), ("small gen.", 84, "mac"),
                                ("check", 46, "jev"), ("frontier generation", 330, "ext")]),
    ]
    for i, (name, parts) in enumerate(rows):
        y = 48 + i * 58
        s.text(170, y + 23, name, 12, "end", 600)
        x = 182
        for label, w, kind in parts:
            s.box(x, y, w, 36, [label], kind, size=10.5)
            x += w + 2
    s.line([(514, 40), (514, 214)], dash="3 3", color=MUTED, arrow=False)
    s.note(520, 52, "frontier-only total", 10)
    s.text(182, 228, ["Routing helps only if savings on correctly routed requests exceed",
                      "decision cost + escalation cost + quality lost on misroutes."], 11, color=INK, italic=True)
    return s


@fig("f04-roadmap")
def roadmap():
    s = Svg(720, 150)
    days = [("Day 1", "Serving", ["gateway · 3 tiers", "streaming · traces"]),
            ("Day 2", "Evaluation", ["datasets · scoring", "baselines · cost"]),
            ("Day 3", "Routers", ["Jev · DistilBERT", "calibration"]),
            ("Day 4", "Verify + cache", ["cascades · FAISS", "Jev checks"]),
            ("Day 5", "Operate", ["Docker · kind", "load · CI"]),
            ("Day 6", "GPU + report", ["vLLM profiling", "held-out test"])]
    for i, (d, t, sub) in enumerate(days):
        x = 10 + i * 117
        kind = "jev" if i < 2 else "muted"
        pts = f"{x},20 {x + 104},20 {x + 116},62 {x + 104},104 {x},104 {x + 12},62"
        f = "#f6e2d4" if i < 2 else "#f7f4ef"
        st = ACCENT if i < 2 else "#b9ae9f"
        s.add(f'<polygon points="{pts}" fill="{f}" stroke="{st}" stroke-width="1.3"/>')
        s.text(x + 60, 42, d, 12, "middle", 700, ACCENT if i < 2 else MUTED)
        s.text(x + 60, 58, t, 11, "middle", 600, INK)
        s.text(x + 60, 74, sub, 9, "middle", 400, MUTED)
        _ = kind
    s.line([(10, 122), (244, 122)], color=ACCENT, arrow=False, sw=2)
    s.text(127, 140, "covered in depth by this notebook", 10.5, "middle", 600, ACCENT)
    s.text(480, 140, "explained only enough to understand the architecture", 10.5, "middle", 400, MUTED, italic=True)
    return s


# ---------------------------------------------------------------- Part 2: Jev
@fig("f05-jev-anatomy")
def jev_anatomy():
    s = Svg(720, 320)
    s.text(16, 20, "One System One request: a state, several typed questions, one typed answer per question", 12, weight=600)
    s.box(16, 40, 196, 110, ["state", '{"prompt": "...",', ' "task_hint": "math",', ' "tiers": {...}}'],
          "plain", mono_sub=True, align="start")
    s.box(16, 166, 196, 136, ["questions", 'tier:   Choice', 'diff:   Score (4 levels)', 'small_ok: Noul'],
          "plain", mono_sub=True, align="start")
    s.box(268, 120, 150, 84, ["Jev", "POST /v1/systemone", "model: jev-1.14.0"], "jev")
    s.line([(212, 95), (240, 95), (240, 150), (266, 150)])
    s.line([(212, 234), (240, 234), (240, 176), (266, 176)])
    s.arrow(418, 162, 452, 162)
    s.rect(454, 40, 252, 262, "plain")
    s.text(466, 62, "answers (illustrative values)", 11, weight=600, color=MUTED)
    rows = [
        ("tier", "Choice", ['choice: "medium"', "probabilities: {small .15,", "  medium .70, frontier .15}",
                            "confidence: 0.55"]),
        ("diff", "Score", ["score: 1.6   (0 … 3)", "probabilities, confidence, legend"]),
        ("small_ok", "Noul", ["noul: 0.34   (probability of yes)"]),
    ]
    y = 84
    for key, typ, body in rows:
        s.text(466, y, f"{key}", 11.5, weight=700, mono=True)
        s.text(694, y, typ, 10.5, "end", 600, ACCENT)
        s.text(476, y + 16, body, 10.5, mono=True, color=INK, lh=1.3)
        y += 18 + 13.7 * len(body) + 12
    s.text(466, 292, "+ usage {input_tokens, output_tokens}", 10, color=MUTED, mono=True)
    return s


@fig("f06-decision-to-action")
def decision_to_action():
    s = Svg(720, 330)
    s.rect(236, 18, 150, 24, "jev", rx=4)
    s.text(311, 35, "documented product behavior", 10, "middle", 600, ACCENT)
    s.text(16, 35, "our proposed application design", 10, weight=600, color=MUTED)
    s.text(704, 35, "our proposed application design", 10, "end", 600, MUTED)
    s.box(16, 60, 118, 86, ["Request context", "messages", "task metadata", "available tiers"], "plain")
    s.box(152, 60, 72, 86, ["Build", "state +", "question", "v3"], "plain", size=11.5)
    s.box(242, 60, 138, 86, ["Jev", "evaluates typed", "question vs state"], "jev")
    s.box(398, 60, 126, 86, ["Typed result", "choice", "probabilities", "confidence"], "plain")
    s.arrow(134, 103, 150, 103)
    s.arrow(224, 103, 240, 103)
    s.arrow(380, 103, 396, 103)
    # policy diamond
    cx, cy = 618, 103
    s.add(f'<polygon points="{cx},{cy - 50} {cx + 84},{cy} {cx},{cy + 50} {cx - 84},{cy}" '
          f'fill="#f4ecdf" stroke="#8a6a48" stroke-width="1.3"/>')
    s.text(cx, cy - 8, "Application policy", 11.5, "middle", 600)
    s.text(cx, cy + 8, ["confidence ≥ t?", "tier on? budget ok?"], 10, "middle", color=MUTED)
    s.arrow(524, 103, 532, 103)
    s.box(548, 196, 140, 62, ["Call selected tier", "small · medium · frontier"], "mac")
    s.arrow(618, 153, 618, 194)
    s.label(650, 178, "accept", 10)
    s.box(318, 196, 192, 62, ["Fallback rule", "DistilBERT or fixed tier", "on low confidence / error"], "warn")
    s.line([(576, 132), (576, 174), (414, 174), (414, 194)], color="#b08532")
    s.label(490, 168, "reject / error / timeout", 10)
    s.line([(414, 258), (414, 276), (618, 276), (618, 260)], color="#b08532")
    s.box(16, 196, 280, 62, ["Trace record", "question version · raw probabilities", "policy decision · decision latency"], "plain")
    s.line([(311, 146), (311, 170), (156, 170), (156, 194)], dash="3 3", color=MUTED)
    s.note(16, 304, "Jev returns numbers; it never calls a model. The gateway's own code turns the answer into an action.", 11)
    return s


@fig("f07-four-roles")
def four_roles():
    s = Svg(720, 300)
    steps = [("Request", 16, "plain"), ("Cache lookup", 126, "muted"), ("Route", 252, "mac"),
             ("Generate", 378, "mac"), ("Verify", 504, "muted"), ("Return", 616, "plain")]
    for name, x, kind in steps:
        s.box(x, 130, 96 if name != "Return" else 88, 46, [name], kind, size=12)
    xs = [x for _, x, _ in steps]
    for a, b in zip(xs, xs[1:]):
        s.arrow(a + 96, 153, b - 2, 153)
    roles = [
        (4, 174, "Does this cached answer", "apply to the new request?", "Noul"),
        (1, 300, "Which tier should answer?", "small / medium / frontier", "Choice"),
        (2, 336, "Will the small tier", "answer this correctly?", "Noul"),
        (3, 552, "Is this generated answer", "correct and complete?", "Noul"),
    ]
    for n, x, l1, l2, prim in roles:
        up = n in (1, 3)
        y = 26 if up else 220
        bx = x - 78
        s.rect(bx, y, 156, 64, "jev", rx=6)
        s.badge(bx + 14, y + 14, n)
        s.text(bx + 30, y + 19, prim, 11, weight=700, color=ACCENT)
        s.text(bx + 10, y + 38, [l1, l2], 10.5, color=INK)
        if up:
            s.line([(x, y + 64), (x, 128)], dash="3 3", color=ACCENT)
        else:
            s.line([(x, y), (x, 178)], dash="3 3", color=ACCENT)
    s.note(470, 250, ["Roles 1–2: before generation (Day 3)", "Roles 3–4: after an answer exists (Day 4)"], 10.5)
    return s


@fig("f08-two-probabilities")
def two_probabilities():
    s = Svg(720, 300)
    for x, title in ((12, "Tier-choice confidence (Choice)"), (372, "Probability of a defined event (Noul)")):
        s.rect(x, 12, 336, 244, "plain", rx=10)
        s.text(x + 168, 36, title, 12.5, "middle", 600)
    # left bars
    vals = [("small", .15), ("medium", .70), ("frontier", .15)]
    base = 190
    for i, (n, v) in enumerate(vals):
        x = 52 + i * 90
        h = v * 170
        s.rect(x, base - h, 52, h, "jev" if n == "medium" else "plain", rx=3)
        s.text(x + 26, base + 16, n, 10.5, "middle", color=INK)
        s.text(x + 26, base - h - 6, f"{v:.2f}", 10.5, "middle", 600)
    s.text(30, 228, "confidence = (0.70 − 1/3) / (1 − 1/3) = 0.55", 10.5, mono=True)
    s.text(30, 246, "Event: none defined — a preference spread", 10.5, color=MUTED, italic=True)
    # right
    s.rect(412, 70, 256, 26, "plain", rx=4)
    s.rect(412, 70, 256 * 0.62, 26, "jev", rx=4)
    s.text(420, 88, "noul = 0.62", 11, weight=600)
    s.text(392, 124, ["Event: “the small tier's answer to this", "prompt passes the Day 2 scorer”",
                      "", "Checked against observed outcomes:", "of all prompts given ≈0.6, about 60%",
                      "should pass — if calibrated."], 11, color=INK)
    s.text(392, 246, "Needs labels from real evaluation runs", 10.5, color=MUTED, italic=True)
    s.note(12, 286, "A confident tier choice is not a probability that the chosen tier's answer will be correct. "
                    "Only the right panel names an event that can be scored.", 10.5)
    return s


@fig("f09-reliability")
def reliability():
    s = Svg(720, 300)
    x0, y0, W, H = 70, 250, 260, 220
    s.add(f'<rect x="{x0}" y="{y0 - H}" width="{W}" height="{H}" fill="#fffdf9" stroke="#b3a491"/>')
    for i in range(0, 11, 2):
        gx = x0 + W * i / 10
        gy = y0 - H * i / 10
        s.add(f'<line x1="{gx}" y1="{y0}" x2="{gx}" y2="{y0 - H}" stroke="#ece4d8"/>')
        s.add(f'<line x1="{x0}" y1="{gy}" x2="{x0 + W}" y2="{gy}" stroke="#ece4d8"/>')
        s.text(gx, y0 + 15, f"{i / 10:.1f}", 9.5, "middle", color=MUTED)
        s.text(x0 - 6, gy + 3, f"{i / 10:.1f}", 9.5, "end", color=MUTED)
    s.add(f'<line x1="{x0}" y1="{y0}" x2="{x0 + W}" y2="{y0 - H}" stroke="{MUTED}" stroke-dasharray="4 3"/>')
    pts = [(.05, .02, 40), (.15, .09, 55), (.25, .18, 60), (.35, .27, 70), (.45, .40, 80),
           (.55, .46, 90), (.65, .55, 85), (.75, .63, 70), (.85, .74, 60), (.95, .86, 50)]
    for c, a, n in pts:
        s.circle(x0 + W * c, y0 - H * a, 3 + n / 30, ACCENT, "#ffffff")
    s.text(x0 + W / 2, y0 + 34, "mean predicted probability in bin", 10.5, "middle", color=INK)
    s.add(f'<text x="22" y="{y0 - H / 2}" transform="rotate(-90 22 {y0 - H / 2})" font-family="Avenir Next" '
          f'font-size="10.5" text-anchor="middle" fill="{INK}">observed frequency of the event</text>')
    s.text(380, 54, "Synthetic points — no project data", 12, weight=600, color=ACCENT)
    s.text(380, 80, ["Each dot is one probability bin; dot size is", "the number of predictions in it.",
                     "", "Points below the dashed diagonal mean", "the predictions were overconfident.",
                     "", "ECE = Σ (n_b / N) · |acc(b) − conf(b)|", "",
                     "Requires: a defined event, many scored", "predictions, and a split not used for tuning."],
           11, color=INK)
    return s


# ---------------------------------------------------------------- Part 3: models and programs
@fig("f10-layers")
def layers():
    s = Svg(720, 350)
    bands = [("Application code (this repository)", "mac", 16),
             ("Serving software / hosted services", "ext", 122),
             ("Models (weights)", "plain", 228)]
    for title, kind, y in bands:
        s.rect(10, y, 700, 92, kind, rx=10, sw=1)
        s.text(700, y + 14, title.upper(), 9, "end", 700, MUTED)
    app = ["Client / smoke", "Gateway", "Eval runner (D2)", "Colab notebook", "Router code (D3)"]
    for i, n in enumerate(app):
        s.box(24 + i * 138, 34, 126, 52, [n], "mac", size=11.5)
    srv = ["Ollama (Mac)", "vLLM (Colab)", "TypeSafe API", "Frontier API", "PyTorch / ST"]
    for i, n in enumerate(srv):
        s.box(24 + i * 138, 140, 126, 52, [n], "ext", size=11.5)
    s.box(24, 252, 264, 52, ["small qwen2.5:1.5b · medium qwen2.5:7b", "same weights family, two serving paths"], "plain", size=11.5)
    mdl = [["Jev", "decision model"], ["frontier", "provider model"], ["DistilBERT +", "embedding model"]]
    for i, n in enumerate(mdl):
        s.box(300 + i * 138, 252, 126, 52, n, "plain", size=11.5)
    for cx in (87, 225, 363, 501, 639):
        s.arrow(cx, 192, cx, 250, color=MUTED)
    s.label(360, 116, "application code calls these over HTTP or Python APIs", 10, color=INK)
    s.note(14, 340, "Serving software loads weights and produces tokens or decisions; application code decides what to ask and records what happened.", 10.5)
    return s


@fig("f11-prefill-decode")
def prefill_decode():
    s = Svg(720, 290)
    s.text(16, 22, "One generation request inside a model server", 12, weight=600)
    s.box(16, 42, 210, 58, ["Prefill", "all prompt tokens processed together", "builds KV cache"], "ext", size=12)
    for i in range(6):
        x = 238 + i * 72
        s.box(x, 42, 62, 58, [f"step {i + 1}", "1 token"], "mac", size=11)
    s.text(682, 76, "…", 16, "middle", color=MUTED)
    s.line([(16, 116), (226, 116)], color=ACCENT, arrow=False, sw=2)
    s.text(121, 132, "≈ time to first token", 10.5, "middle", 600, ACCENT)
    s.line([(238, 116), (692, 116)], color="#8a6a48", arrow=False, sw=2)
    s.text(465, 132, "decode: one forward pass per new token, sequential", 10.5, "middle", 600, "#8a6a48")
    s.text(16, 168, "KV cache (keys and values kept for every token seen so far)", 11, weight=600)
    widths = [210, 222, 234, 246, 258, 270, 282]
    for i, w in enumerate(widths):
        y = 180 + i * 12
        s.rect(16, y, w, 9, "jev" if i == 0 else "plain", rx=2, sw=0.8)
        s.text(w + 24, y + 8, "after prefill" if i == 0 else f"+{i} token{'s' if i > 1 else ''}", 9, color=MUTED)
    s.text(380, 188, ["Prefill is mostly compute-bound: many tokens", "share each weight read.",
                      "Decode is often memory-bandwidth-bound: every", "step re-reads weights and the growing cache",
                      "to produce a single token."], 11, color=INK)
    return s


@fig("f12-memory")
def memory():
    s = Svg(720, 300)
    s.text(16, 22, "Approximate weight memory = parameters × bits ÷ 8 (illustrative arithmetic, not measured residency)", 11.5, weight=600)
    x0, scale = 150, 30   # px per GB
    rows = [("1.54B · 16-bit", 3.09), ("1.54B · 4-bit", 0.77), ("7.62B · 16-bit", 15.2),
            ("7.62B · 8-bit", 7.6), ("7.62B · 4-bit", 3.8)]
    for i, (n, gb) in enumerate(rows):
        y = 44 + i * 34
        s.text(x0 - 10, y + 16, n, 11, "end")
        s.rect(x0, y, gb * scale, 22, "mac" if "4-bit" in n else "plain", rx=3)
        s.text(x0 + gb * scale + 6, y + 16, f"{gb:.2f} GB", 10.5, weight=600)
    for g in range(0, 17, 2):
        gx = x0 + g * scale
        s.text(gx, 228, str(g), 9.5, "middle", color=MUTED)
    s.text(x0 + 9 * scale, 244, "gigabytes", 10, "middle", color=MUTED)
    lim = x0 + 18 * scale
    s.add(f'<line x1="{lim}" y1="36" x2="{lim}" y2="216" stroke="{ACCENT}" stroke-width="1.6" stroke-dasharray="5 3"/>')
    s.text(lim - 6, 46, ["18 GB unified memory", "shared by macOS, apps,", "CPU and GPU"], 9.5, "end", 600, ACCENT)
    s.note(16, 270, ["Not included: KV cache (grows with context × parallel requests), runtime buffers, other loaded models,",
                     "Docker and the gateway itself. Ollama lists qwen2.5:7b at 4.7 GB because its quantization mixes precisions."], 10.5)
    return s


@fig("f13-cold-warm")
def cold_warm():
    s = Svg(720, 262)
    lanes = [("Cold start", [("load weights from disk", 230, "warn"), ("prefill", 70, "ext"), ("decode", 150, "mac")]),
             ("Warm", [("prefill", 70, "ext"), ("decode", 150, "mac")]),
             ("Switch tier", [("unload small", 110, "bad"), ("load medium", 230, "warn"),
                              ("prefill", 70, "ext"), ("decode", 150, "mac")])]
    for i, (n, parts) in enumerate(lanes):
        y = 22 + i * 56
        s.text(104, y + 24, n, 12, "end", 600)
        x = 114
        for label, w, kind in parts:
            s.box(x, y, w - 2, 36, [label], kind, size=10.5)
            x += w
    s.line([(114, 196), (704, 196)], color=MUTED)
    s.text(704, 212, "time →", 10, "end", color=MUTED)
    s.note(16, 230, ["Block widths are illustrative. Ollama keeps a model loaded for 5 minutes by default (keep_alive);",
                     "when memory is short, new requests queue until idle models unload."], 10.5)
    return s


@fig("f14-localhost")
def localhost():
    s = Svg(720, 300)
    s.frame(10, 14, 300, 160, "Mac host", "mac")
    s.box(26, 44, 120, 56, ["Gateway", "127.0.0.1:8080"], "mac", size=11.5)
    s.box(174, 44, 120, 56, ["Ollama", "127.0.0.1:11434"], "mac", size=11.5)
    s.arrow(146, 72, 172, 72, color="#5c7a5c")
    s.text(160, 126, "✓ same host: localhost works", 11, "middle", 600, "#5c7a5c")
    s.frame(26, 190, 270, 98, "Docker container on the Mac (Day 5)", "muted")
    s.box(40, 222, 112, 52, ["Gateway", "in container"], "plain", size=11.5)
    s.text(164, 236, ["localhost = the container", "use host.docker.internal", "to reach Mac services"], 10.5, color=INK)
    s.line([(96, 222), (96, 192), (268, 192), (268, 102)], dash="4 3", color="#a24b36")
    s.frame(330, 14, 380, 160, "Google Colab VM (remote)", "colab")
    s.box(346, 44, 150, 56, ["Notebook client", "127.0.0.1 (VM)"], "colab", size=11.5)
    s.box(540, 44, 150, 56, ["vLLM", "127.0.0.1:8000 (VM)"], "colab", size=11.5)
    s.arrow(496, 72, 538, 72, color="#5c7a5c")
    s.text(520, 126, ["✓ inside the VM: works", "✗ from the Mac: a different machine"], 11, "middle", 600, INK)
    s.text(330, 220, ["“localhost” always means the machine or container", "the code is currently running in.",
                      "The project keeps Colab servers notebook-local", "and never exposes them through a tunnel."],
           11, color=INK)
    return s


# ---------------------------------------------------------------- Part 5: repository
@fig("f15-modules")
def modules():
    s = Svg(720, 360)
    s.box(16, 34, 150, 58, ["cli.py", "jev serve | doctor | smoke"], "mac", size=12)
    s.box(230, 34, 160, 58, ["api.py", "FastAPI app · routes"], "mac", size=12)
    s.box(470, 34, 234, 58, ["diagnostics.py", "doctor report · smoke request"], "mac", size=12)
    s.arrow(166, 63, 228, 63)
    s.label(197, 57, "serve", 9.5)
    s.line([(91, 34), (91, 14), (587, 14), (587, 32)])
    s.label(340, 18, "doctor / smoke", 9.5)
    mods = [("config.py", "Settings · Backend", 16), ("transport.py", "pooled httpx client", 182),
            ("budget.py", "frontier admission", 348)]
    for n, d, x in mods:
        s.box(x, 150, 150, 56, [n, d], "plain", size=12)
    s.box(514, 150, 120, 56, ["tracing.py", "secret-free log"], "plain", size=12)
    for x in (91, 257, 423, 574):
        s.line([(310, 92), (310, 124), (x, 124), (x, 148)], color=MUTED)
    s.box(560, 236, 144, 52, ["ollama.py", "/api/tags · /api/ps"], "plain", size=12)
    s.line([(680, 92), (680, 234)], color=MUTED)
    s.line([(500, 92), (500, 112), (120, 112), (120, 148)], color=MUTED, dash="3 3")
    s.label(470, 108, "reads config", 9)
    s.box(182, 236, 150, 52, ["Backends", "Ollama · vLLM · API"], "ext", size=11.5)
    s.arrow(257, 206, 257, 234, color="#55697d")
    s.text(16, 318, "Tests (15, offline):", 11, weight=700)
    s.text(16, 336, ["test_config · test_api_contract · test_transport · test_ollama · test_budget · test_dispatch",
                     "test_streaming · test_errors · test_tracing · test_diagnostics · test_profile_integration"],
           10.5, color=MUTED)
    return s


# ---------------------------------------------------------------- Part 6: Day 1
@fig("f16-day1-sequence")
def day1_sequence():
    s = Svg(720, 530)
    lanes = [("Client", 58), ("Gateway API", 184), ("Config + budget", 312), ("Transport", 436),
             ("Backend", 556), ("Trace log", 664)]
    kinds = {"Client": "plain", "Backend": "ext"}
    for n, x in lanes:
        s.box(x - 52, 14, 104, 38, [n], kinds.get(n, "mac"), size=11)
        s.add(f'<line x1="{x}" y1="52" x2="{x}" y2="420" stroke="#c9bcaa" stroke-dasharray="3 4"/>')
    X = dict(lanes)

    def msg(a, b, y, text, n=None, dash=None, color=LINE):
        xa, xb = X[a], X[b]
        s.arrow(xa, y, xb + (-2 if xb > xa else 2), y, dash=dash, color=color)
        left = min(xa, xb)
        if n:
            s.badge(left + 12, y - 11, n, r=8, size=9.5)
        s.label(left + (26 if n else 10), y - 6, text, 10, anchor="start")

    msg("Client", "Gateway API", 82, "POST /v1/chat/completions", 1)
    s.rect(X["Gateway API"] - 7, 96, 14, 36, "jev", rx=2)
    s.badge(X["Gateway API"] + 22, 104, 2, r=8, size=9.5)
    s.label(X["Gateway API"] + 36, 108, "validate with Pydantic; invalid → 422", 10, anchor="start")
    msg("Gateway API", "Config + budget", 162, "resolve tier → Backend", 3)
    msg("Gateway API", "Config + budget", 198, "frontier only: reserve budget", 4, dash="4 3", color=MUTED)
    msg("Gateway API", "Transport", 236, "OpenAI-style payload", 5)
    msg("Transport", "Backend", 262, "POST …/chat/completions")
    msg("Backend", "Transport", 296, "JSON or SSE bytes", 6, dash="5 3")
    msg("Transport", "Gateway API", 326, "result or open stream", dash="5 3")
    msg("Gateway API", "Client", 360, "body + headers", 7, dash="5 3")
    msg("Gateway API", "Trace log", 400, "finish(status, usage, duration_ms, cost_status)", 8)
    s.rect(16, 438, 688, 78, "warn", rx=8)
    s.text(30, 460, "Day 1 boundary", 11.5, weight=700)
    s.text(30, 478, ["The client names the tier (small, medium, frontier). There is no automatic routing:",
                     "model=\"auto\" is rejected with 422. In Day 3 a router supplies the tier at step 3; the rest of the path is unchanged."],
           10.5, color=INK)
    return s


@fig("f17-streaming")
def streaming():
    s = Svg(720, 300)
    s.text(16, 22, "Streaming: the gateway forwards SSE bytes as they arrive", 12, weight=600)
    for n, y in (("Backend", 70), ("Gateway", 140), ("Client", 210)):
        s.text(86, y + 4, n, 11.5, "end", 600)
        s.add(f'<line x1="96" y1="{y}" x2="704" y2="{y}" stroke="#c9bcaa"/>')
    s.add(f'<line x1="250" y1="44" x2="250" y2="240" stroke="{ACCENT}" stroke-width="1.6" stroke-dasharray="5 3"/>')
    s.text(250, 258, "response headers sent (HTTP 200)", 10.5, "middle", 600, ACCENT)
    s.rect(100, 120, 146, 40, "bad", rx=4)
    s.text(173, 136, ["failure here →", "JSON 502 / 504"], 10, "middle", 600)
    xs = [300, 370, 440, 510]
    for i, x in enumerate(xs):
        s.rect(x, 60, 44, 20, "mac", rx=3)
        s.text(x + 22, 74, f"ev{i + 1}", 9.5, "middle")
        s.arrow(x + 22, 80, x + 30, 132, color=MUTED)
        s.arrow(x + 30, 148, x + 38, 200, color=MUTED)
        s.rect(x + 16, 200, 44, 20, "mac", rx=3)
        s.text(x + 38, 214, f"ev{i + 1}", 9.5, "middle")
    s.rect(580, 120, 124, 40, "warn", rx=4)
    s.text(642, 136, ["failure here →", "stream cut, traced"], 10, "middle", 600)
    s.text(16, 286, "After the first byte the status code is already 200, so a mid-stream failure can only end the stream "
                    "and be recorded as stream_interrupted.", 10.5, color=MUTED, italic=True)
    return s


@fig("f18-error-map")
def error_map():
    s = Svg(720, 432)
    steps = [("Request arrives", None),
             ("Schema valid?", "422  model=auto, images, unknown fields, empty messages"),
             ("Frontier enabled?", "503  key, model, rates or caps missing"),
             ("max_tokens ≤ policy?", "422  exceeds JEV_MAX_OUTPUT_TOKENS"),
             ("Budget admits?", "429  process request/token/USD cap reached"),
             ("Backend responds in time?", "504  httpx timeout"),
             ("Backend OK?", "502  connect error, HTTP error, bad JSON (sanitized)")]
    y = 14
    for i, (q, err) in enumerate(steps):
        kind = "plain" if i == 0 else "mac"
        s.box(16, y, 196, 38, [q], kind, size=11.5)
        if err:
            s.arrow(212, y + 19, 262, y + 19, color="#a24b36")
            code, rest = err.split("  ", 1)
            s.rect(264, y + 4, 52, 30, "bad", rx=4)
            s.text(290, y + 24, code, 11.5, "middle", 700)
            s.text(326, y + 24, rest, 10.5, color=INK)
            if i in (2, 4):
                s.text(690, y + 24, "frontier only", 9.5, "end", 400, MUTED, italic=True)
        if i < len(steps) - 1:
            s.arrow(114, y + 38, 114, y + 50, color="#5c7a5c")
        y += 52
    s.box(16, y, 196, 38, ["200 + headers"], "ok", size=12)
    s.note(240, y + 24, "Provider error text never reaches the client; tests assert this.", 10.5)
    return s


@fig("f19-budget")
def budget():
    s = Svg(720, 270)
    s.box(16, 30, 170, 70, ["Message text", "4 units per character", "+ 32 per message"], "plain", size=11.5)
    s.box(16, 120, 170, 56, ["max_tokens", "requested output"], "plain", size=11.5)
    s.box(226, 60, 196, 86, ["Conservative estimate", "tokens = input + output", "usd = in×rate_in + out×rate_out", "÷ 1,000,000"], "jev", size=11.5)
    s.arrow(186, 65, 224, 90)
    s.arrow(186, 148, 224, 124)
    s.box(462, 30, 242, 116, ["Under one asyncio.Lock", "requests + 1 ≤ MAX_REQUESTS", "tokens ≤ MAX_TOKENS",
                              "usd ≤ MAX_USD"], "mac", size=11.5)
    s.arrow(422, 103, 460, 92)
    s.box(462, 170, 112, 46, ["Admit", "counters grow"], "ok", size=11.5)
    s.box(592, 170, 112, 46, ["Reject", "HTTP 429"], "bad", size=11.5)
    s.arrow(540, 146, 520, 168, color="#5c7a5c")
    s.arrow(626, 146, 646, 168, color="#a24b36")
    s.note(16, 232, ["Reservations are never released, so counts only rise within a process. The guard is per-process and",
                     "approximate; it complements, and does not replace, spending limits in the provider's account."], 10.5)
    return s


@fig("f20-evidence-ladder")
def evidence_ladder():
    s = Svg(720, 290)
    steps = [("Unit test", "one function, no I/O", "ok", "done"),
             ("Mocked transport test", "httpx.MockTransport as backend", "ok", "done"),
             ("Contract check", "accepted / rejected API shapes", "ok", "done"),
             ("Real integration", "live Ollama, vLLM, provider API", "warn", "pending"),
             ("Benchmark", "controlled, repeated workload", "muted", "Day 2 / Day 6")]
    for i, (n, d, kind, st) in enumerate(steps):
        x = 16 + i * 64
        y = 222 - i * 46
        s.box(x, y, 300, 40, [n, d], kind, size=11.5)
        s.text(x + 312, y + 25, st, 10.5, weight=600,
               color={"done": "#5c7a5c", "pending": "#b08532"}.get(st, MUTED))
    s.text(704, 30, "stronger evidence ↑", 10.5, "end", 600, ACCENT)
    s.text(704, 262, ["Day 1 offline suite: 15 passed", "(evidence/day1/mac-offline-20261027-1314.txt)"], 10, "end", color=MUTED)
    return s


@fig("f21-colab-flow")
def colab_flow():
    s = Svg(720, 300)
    s.frame(10, 14, 180, 270, "Mac", "mac")
    s.box(24, 46, 152, 50, ["git archive HEAD", "committed source only"], "mac", size=11)
    s.box(24, 116, 152, 50, ["shasum -a 256", "record the digest"], "mac", size=11)
    s.box(24, 186, 152, 50, ["Upload zip", "+ paste SHA-256"], "mac", size=11)
    s.arrow(100, 96, 100, 114)
    s.arrow(100, 166, 100, 184)
    s.frame(206, 14, 504, 270, "Colab GPU runtime · cells in order", "colab")
    cells = [("1", "Preflight", "nvidia-smi"), ("2", "Verify + extract", "hash, safe paths"),
             ("3", "pip install", "source + vllm pin"), ("4", "vllm serve", "127.0.0.1:8000"),
             ("5", "Readiness", "poll /v1/models"), ("6", "2 requests", "max_tokens 16"),
             ("7", "Export JSON", "download result"), ("8", "Cleanup", "terminate server")]
    for i, (n, a, b) in enumerate(cells):
        col, row = i % 4, i // 4
        x = 222 + col * 120
        y = 50 + row * 110
        s.box(x, y, 106, 62, [a, b], "colab", size=11)
        s.badge(x + 8, y + 8, n, color="#5c7a5c", r=8, size=9)
        if col < 3:
            s.arrow(x + 106, y + 31, x + 118, y + 31, color="#5c7a5c")
    s.line([(642, 112), (642, 136), (270, 136), (270, 158)], color="#5c7a5c")
    s.line([(176, 211), (200, 211), (200, 81), (220, 81)], color=LINE)
    s.text(458, 262, "Status recorded in repo: notebook JSON and cell syntax validated; no cell executed yet.", 10.5,
           "middle", 400, MUTED, italic=True)
    return s


def checkpoint_grid(day, items, statuses, legend_items):
    s = Svg(720, 400)
    for b in range(6):
        y = 12 + b * 62
        s.text(14, y + 30, f"Block {b + 1}", 11, weight=700, color=MUTED)
        for j in range(3):
            k = b * 3 + j
            x = 84 + j * 210
            kind = statuses[k]
            s.rect(x, y, 200, 52, kind, rx=7)
            s.text(x + 10, y + 20, f"{day}-{k + 1:02d}", 11, weight=700, color=ACCENT)
            s.text(x + 10, y + 38, items[k], 10.5, color=INK)
    legend(s, 84, 392, legend_items, gap=230)
    return s


DAY1_SHORT = ["Scope + runtime profiles", "Mac + Colab preflights", "Package + CLI (uv)",
              "Config + resource limits", "API, health, models", "Async transport",
              "Small Ollama model", "Medium model + memory", "Frontier + spend caps",
              "Explicit-tier responses", "Streaming forwarding", "Deadlines + errors",
              "Traces, usage, timings", "doctor + smoke", "Colab serving notebook",
              "Mac / Colab profiles", "Offline + real checks", "Docs + evidence handoff"]
DAY2_SHORT = ["Immutable eval records", "GSM8K loader", "MMLU loader", "MBPP tasks + tests",
              "Code sandbox", "Manifest + 60/20/20", "Math scoring", "Multiple-choice scoring",
              "Code scoring", "Manual audit export", "3-tier eval runner", "Checkpoint + resume",
              "Hindsight oracle labels", "Complete cost model", "Per-tier reports",
              "Serving workloads", "Latency + throughput", "Train/val measurements"]


@fig("f22-day1-blocks")
def day1_blocks():
    pending = {2, 7, 8, 9, 10, 11, 15, 17, 18}
    st = ["warn" if i + 1 in pending else "ok" for i in range(18)]
    return checkpoint_grid("D1", DAY1_SHORT, st, [("ok", "committed · offline checks recorded"),
                                                  ("warn", "committed · live check still pending")])


@fig("f23-day2-pipeline")
def day2_pipeline():
    s = Svg(720, 470)
    srcs = [("GSM8K", "math · MIT"), ("MMLU", "multiple choice · MIT"), ("MBPP", "code · CC BY 4.0")]
    for i, (n, d) in enumerate(srcs):
        s.box(16, 16 + i * 62, 140, 50, [n, d], "ext", size=11.5)
        s.arrow(156, 41 + i * 62, 182, 41 + i * 62, color="#55697d")
    s.box(184, 16, 130, 174, ["Loaders", "pinned dataset", "revision", "→ prompt records", "+ answer", "provenance"], "mac", size=11.5)
    s.box(340, 16, 150, 76, ["Deduplicate + group", "near-duplicates and", "related variants"], "mac", size=11.5)
    s.box(340, 114, 150, 76, ["Frozen manifest", "2,000–3,000 prompts", "content hash"], "mac", size=11.5)
    s.arrow(314, 54, 338, 54)
    s.arrow(415, 92, 415, 112)
    s.box(516, 16, 92, 52, ["train", "60%"], "ok", size=11.5)
    s.box(516, 76, 92, 52, ["validation", "20%"], "warn", size=11.5)
    s.box(516, 136, 92, 54, ["test", "20%"], "lock", size=11.5)
    s.text(618, 158, ["held out ·", "sealed until", "Day 6"], 10, color="#6d5a7a", weight=600)
    s.line([(490, 150), (502, 150), (502, 42), (514, 42)])
    s.arrow(502, 102, 514, 102)
    s.arrow(502, 162, 514, 162, color="#6d5a7a", dash="4 3")
    s.box(184, 230, 186, 80, ["Bounded runner", "small · medium · frontier", "budgets · retries · resume"], "mac", size=11.5)
    s.line([(608, 42), (700, 42), (700, 212), (277, 212), (277, 228)])
    s.line([(608, 102), (700, 102)], arrow=False)
    s.box(400, 230, 148, 80, ["Task scorers", "math extractor", "letter parser", "code sandbox"], "mac", size=11.5)
    s.arrow(370, 270, 398, 270)
    s.box(576, 230, 128, 80, ["Immutable", "records", "append-only", "JSONL + run id"], "plain", size=11.5)
    s.arrow(548, 270, 574, 270)
    outs = [("Per-tier reports", "accuracy · completion · errors"), ("Oracle labels", "cheapest observed success"),
            ("Cost tables", "API vs capacity"), ("Audit samples", "30–50 per task")]
    for i, (a, b) in enumerate(outs):
        x = 16 + i * 174
        s.box(x, 364, 164, 56, [a, b], "plain", size=11.5)
    s.line([(640, 310), (640, 340), (98, 340), (98, 362)])
    for i in range(1, 4):
        s.arrow(98 + i * 174, 340, 98 + i * 174, 362)
    s.note(16, 452, "Every report is regenerated from stored records. The test split is not read by the runner, the scorers' tuning, or training.", 10.5)
    return s


@fig("f24-grouped-splits")
def grouped_splits():
    s = Svg(720, 222)
    groups = [("#a8512a", 3), ("#55697d", 2), ("#5c7a5c", 2), ("#b08532", 3), ("#6d5a7a", 2)]
    s.text(16, 22, "Rows split independently", 12, weight=700, color="#a24b36")
    s.text(372, 22, "Whole groups assigned to one split", 12, weight=700, color="#5c7a5c")
    bad = {"train": [], "val": [], "test": []}
    good = {"train": [], "val": [], "test": []}
    order = ["train", "val", "test"]
    k = 0
    for gi, (c, n) in enumerate(groups):
        for j in range(n):
            bad[order[(k + j) % 3]].append(c)
            k += 1
        good[["train", "train", "val", "test", "train"][gi]].extend([c] * n)
    for x0, data in ((16, bad), (372, good)):
        for i, name in enumerate(order):
            x = x0 + i * 112
            s.rect(x, 40, 102, 124, "plain", rx=8)
            s.text(x + 51, 58, name, 11, "middle", 600, MUTED)
            for j, c in enumerate(data[name]):
                s.circle(x + 26 + (j % 3) * 25, 82 + (j // 3) * 26, 9, c)
    s.text(16, 190, ["Same colour = paraphrases or variants of one problem.", "Seeing one in training leaks the test answer."], 10.5, color=INK)
    s.text(372, 190, ["Split by group id, then check proportions", "(60/20/20 by prompt count, approximately)."], 10.5, color=INK)
    return s


@fig("f25-outcomes")
def outcomes():
    s = Svg(720, 320)
    s.box(280, 14, 160, 42, ["Evaluation attempt"], "plain", size=12)
    s.box(60, 96, 230, 52, ["No usable response", "infrastructure or serving failure"], "bad", size=11.5)
    s.box(430, 96, 230, 52, ["Response received", "now parse and score"], "mac", size=11.5)
    s.line([(330, 56), (330, 76), (175, 76), (175, 94)])
    s.line([(390, 56), (390, 76), (545, 76), (545, 94)])
    leaves1 = [("backend_error", 20), ("timeout", 110), ("sandbox_error", 196)]
    for n, x in leaves1:
        s.box(x, 188, 82, 34, [n], "bad", size=10)
        s.line([(175, 148), (175, 168), (x + 41, 168), (x + 41, 186)], color="#a24b36")
    leaves2 = [("unparseable", 330, "warn"), ("truncated", 418, "warn"), ("incorrect", 506, "plain"), ("correct", 594, "ok")]
    for n, x, kind in leaves2:
        s.box(x, 188, 82, 34, [n], kind, size=10)
        s.line([(545, 148), (545, 168), (x + 41, 168), (x + 41, 186)])
    s.add(f'<path d="M20,236 L300,236" stroke="#a24b36" stroke-width="2"/>')
    s.text(160, 254, "counted in error / completion rate", 10.5, "middle", 600, "#a24b36")
    s.add(f'<path d="M330,236 L498,236" stroke="#b08532" stroke-width="2"/>')
    s.text(414, 254, ["model or format problem —", "audit before blaming the model"], 10.5, "middle", 600, "#b08532")
    s.add(f'<path d="M506,236 L676,236" stroke="#5c7a5c" stroke-width="2"/>')
    s.text(591, 254, "enter accuracy", 10.5, "middle", 600, "#5c7a5c")
    s.note(16, 306, "Each outcome is stored as its own value. Accuracy, completion rate, and error rate state their denominators.", 10.5)
    return s


@fig("f26-sandbox")
def sandbox():
    s = Svg(720, 270)
    s.frame(10, 14, 700, 244, "Mac host (planned design)", "mac")
    s.box(28, 60, 150, 70, ["Scorer process", "writes code + tests", "to a temp directory"], "mac", size=11.5)
    s.frame(214, 44, 300, 190, "Disposable container", "bad")
    rules = ["--network none", "memory + CPU limits", "process count limit", "read-only base, tmp workdir",
             "non-root user", "wall-clock timeout, then kill"]
    s.text(230, 82, rules, 10.5, mono=True, color=INK, lh=1.45)
    s.box(372, 168, 128, 52, ["python -m pytest", "on given tests"], "plain", size=11)
    s.arrow(178, 95, 228, 95)
    s.label(203, 86, "mount", 9.5)
    s.box(550, 60, 146, 140, ["Structured result", "passed", "failed", "timeout", "crashed", "sandbox_error"], "plain", size=11.5)
    s.arrow(514, 130, 548, 130)
    s.note(28, 160, ["Model-written code never", "runs directly on the host.", "Exact flags are chosen and", "tested in D2-05."], 10.5)
    return s


@fig("f27-oracle")
def oracle():
    s = Svg(720, 280)
    heads = ["prompt", "small", "medium", "frontier", "oracle label"]
    xs = [20, 190, 300, 410, 540]
    for h, x in zip(heads, xs):
        s.text(x, 26, h, 11.5, weight=700, color=MUTED)
    rows = [("gsm8k-0412", "✓", "✓", "✓", "small"), ("mmlu-1185", "✗", "✓", "✓", "medium"),
            ("mbpp-0077", "✗", "✗", "✓", "frontier"), ("gsm8k-0903", "✗", "✗", "✗", "none"),
            ("mmlu-0261", "✓", "✗", "✓", "small")]
    for i, r in enumerate(rows):
        y = 40 + i * 38
        s.rect(14, y, 692, 32, "plain" if i % 2 else "mac", rx=4, sw=0.6)
        s.text(xs[0], y + 21, r[0], 11, mono=True)
        for j in range(1, 4):
            ok = r[j] == "✓"
            s.text(xs[j] + 18, y + 22, r[j], 14, "middle", 700, "#5c7a5c" if ok else "#a24b36")
        s.text(xs[4], y + 21, r[4], 11.5, weight=700, color=ACCENT if r[4] != "none" else MUTED)
    s.text(20, 250, ["Illustrative rows. The label is the cheapest tier that was observed to succeed, so it uses",
                     "outcomes that a live router cannot see before generating. Note the last row: correctness is not monotonic in size."],
           10.5, color=INK)
    return s


@fig("f28-resume")
def resume():
    s = Svg(720, 226)
    s.box(16, 24, 220, 108, ["Fingerprint", "prompt id + text hash", "tier + model revision", "generation settings",
                             "template version"], "plain", size=11.5)
    s.box(272, 40, 140, 76, ["Seen in", "completed", "records?"], "mac", size=11.5)
    s.arrow(236, 78, 270, 78)
    s.box(452, 14, 252, 52, ["Yes → skip", "reuse; keep original run id + time"], "ok", size=11.5)
    s.box(452, 90, 252, 52, ["No → call backend", "append one record, then flush"], "warn", size=11.5)
    s.arrow(412, 66, 450, 42, color="#5c7a5c")
    s.arrow(412, 90, 450, 114, color="#b08532")
    s.note(16, 176, ["An interrupted run leaves complete lines plus at most one partial line. On resume, the partial line",
                     "is discarded, completed fingerprints are skipped, and only missing work is sent.",
                     "Changing any fingerprint field (e.g. a new model revision) makes a new experiment, not a resume."], 10.5)
    return s


@fig("f29-day2-blocks")
def day2_blocks():
    return checkpoint_grid("D2", DAY2_SHORT, ["muted"] * 18, [("muted", "planned · not started in repository")])


# ---------------------------------------------------------------- Part 8: measurement
@fig("f30-latency-anatomy")
def latency_anatomy():
    s = Svg(720, 250)
    s.text(16, 22, "Client-side timeline of one streamed request (illustrative)", 12, weight=600)
    s.add(f'<line x1="40" y1="110" x2="700" y2="110" stroke="{LINE}" stroke-width="1.4"/>')
    marks = [(40, "t0 send"), (250, "first event"), (330, ""), (380, ""), (470, ""), (530, ""), (660, "[DONE]")]
    for x, lab in marks:
        s.add(f'<line x1="{x}" y1="102" x2="{x}" y2="118" stroke="{LINE}" stroke-width="1.4"/>')
        if lab:
            s.text(x, 136, lab, 10.5, "middle", 600)
    for x in (250, 330, 380, 470, 530):
        s.rect(x - 10, 78, 20, 18, "mac", rx=3)
    s.line([(40, 60), (250, 60)], color=ACCENT, start_arrow=True)
    s.text(145, 52, "time to first visible output", 10.5, "middle", 600, ACCENT)
    s.line([(40, 170), (660, 170)], color=INK, start_arrow=True)
    s.text(350, 188, "end-to-end latency", 10.5, "middle", 600)
    s.line([(330, 150), (380, 150)], color="#55697d", start_arrow=True)
    s.text(355, 145, "event gap", 9.5, "middle", 600, "#55697d")
    s.note(16, 222, ["An event may carry one token, several, or none (role, usage, [DONE]). Event gaps are only token timings",
                     "when the interface guarantees one token per event — otherwise use token counts from usage."], 10.5)
    return s


@fig("f31-percentiles")
def percentiles():
    s = Svg(720, 230)
    vals = [410, 430, 445, 450, 470, 480, 490, 500, 505, 520, 530, 540, 560, 575, 600, 640, 690, 760, 980, 1650]
    x0, scale = 40, 0.5
    s.text(16, 22, "Twenty request latencies (illustrative numbers in ms)", 12, weight=600)
    s.add(f'<line x1="{x0}" y1="130" x2="{x0 + 1300 * scale}" y2="130" stroke="{LINE}"/>')
    for v in range(400, 1701, 100):
        x = x0 + (v - 400) * scale
        s.add(f'<line x1="{x}" y1="126" x2="{x}" y2="134" stroke="{LINE}"/>')
        if v % 200 == 0:
            s.text(x, 150, str(v), 9.5, "middle", color=MUTED)
    for i, v in enumerate(vals):
        hi = i in (9, 10, 18)
        s.circle(x0 + (v - 400) * scale, 116 - (i % 4) * 11, 4.5, ACCENT if hi else "#b3a491")
    p50 = x0 + (525 - 400) * scale
    p95 = x0 + (980 - 400) * scale
    mean = x0 + (611.25 - 400) * scale
    for x, lab, y in ((p50, "p50 = 525 ms (mean of 10th and 11th)", 50), (p95, "p95 = 980 ms (nearest rank: 19th)", 50)):
        s.add(f'<line x1="{x}" y1="{y + 6}" x2="{x}" y2="134" stroke="{ACCENT}" stroke-dasharray="4 3"/>')
        s.text(x + 4, y, lab, 10.5, weight=700, color=ACCENT)
    s.add(f'<line x1="{mean}" y1="72" x2="{mean}" y2="134" stroke="#55697d" stroke-dasharray="2 3"/>')
    s.text(mean + 4, 76, "mean = 611 ms", 10, weight=600, color="#55697d")
    s.text(16, 182, ["One 1,650 ms outlier pulls the mean up; the median ignores it. With 20 samples, p95 rests on one",
                     "request, so report the sample count and the percentile method with every tail number."], 10.5, color=INK)
    return s


if __name__ == "__main__":
    only = set(sys.argv[1:])
    for name, fn in FIGS.items():
        if only and name not in only:
            continue
        fn().save(OUT / f"{name}.svg")
    print(f"wrote {len(FIGS) if not only else len(only)} figures to {OUT}")
