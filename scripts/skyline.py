# Renders data/github.json as an animated skyline SVG for a GitHub profile README.
# README images can't run JavaScript, so the animation is plain CSS inside the SVG.
import json
import math
import sys
from datetime import date, timedelta

src, out, theme = sys.argv[1], sys.argv[2], sys.argv[3]  # theme: light | dark
D = json.load(open(src))

W, H = 900, 300
LIGHT = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
DARK = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
# GitHub picks the file per theme via <picture>, so each SVG has fixed colors
PAL, FG, MUTED = (DARK, "#e6edf3", "#8b949e") if theme == "dark" else (LIGHT, "#1f2328", "#656d76")


def mix(c, target, t):
    a = [int(c[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(target[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def palette_css(p):
    rules = []
    for i, c in enumerate(p):
        rules.append(f".f{i}{{fill:{c}}}.t{i}{{fill:{mix(c, '#ffffff', 0.22)}}}.s{i}{{fill:{mix(c, '#000000', 0.18)}}}")
    return "".join(rules)


start = date.fromisoformat(D["start"])
off = (start.weekday() + 1) % 7  # Sunday = 0, like GitHub's grid
days = []
for i, count in enumerate(D["counts"]):
    days.append({"i": i, "date": start + timedelta(days=i), "count": count,
                 "level": int(D["levels"][i]), "col": (i + off) // 7, "row": (i + off) % 7})
ncols = days[-1]["col"] + 1
grid = {(d["col"], d["row"]): d for d in days}
mx = max(1, max(D["counts"]))
best = max(days, key=lambda d: d["count"])

cw = (W - 24) / (ncols + 4.2)
dx, dy = cw * 0.6, cw * 0.45
base_y, x0, max_h, bw = H - 12, 12, H * 0.62, cw * 0.86
f = lambda v: f"{v:.1f}".rstrip("0").rstrip(".")
pts = lambda *p: " ".join(f"{f(x)},{f(y)}" for x, y in p)

shapes, best_top = [], None
# Far rows first so nearer rows paint over them
for r in range(6, -1, -1):
    for c in range(ncols):
        d = grid.get((c, r))
        if not d:
            continue
        bx, by, lv = x0 + c * cw + r * dx, base_y - r * dy, d["level"]
        h = max(2, max_h * math.sqrt(d["count"] / mx)) if d["count"] else 0
        top = pts((bx, by - h), (bx + bw, by - h), (bx + bw + dx, by - h - dy), (bx + dx, by - h - dy))
        if not h:
            shapes.append(f'<polygon class="f0" points="{top}"/>')
            continue
        delay = (c * 24 + (6 - r) * 30) / 1000
        shapes.append(
            f'<g class="b" style="animation-delay:{delay:.2f}s">'
            f'<polygon class="s{lv}" points="{pts((bx + bw, by), (bx + bw + dx, by - dy), (bx + bw + dx, by - dy - h), (bx + bw, by - h))}"/>'
            f'<rect class="f{lv}" x="{f(bx)}" y="{f(by - h)}" width="{f(bw)}" height="{f(h)}"/>'
            f'<polygon class="t{lv}" points="{top}"/></g>')
        if d is best:
            best_top = (bx + (bw + dx) / 2, by - h - dy / 2)

label = ""
if best_top:
    px, py = best_top
    right = px > W / 2
    ly, tx = 22, px + (-14 if right else 14)
    when = best["date"].strftime("%b %-d, %Y")
    label = (f'<g class="lbl"><path d="M{f(px)} {f(py - 3)}V{ly}h{-10 if right else 10}" fill="none" class="ln"/>'
             f'<text x="{f(tx)}" y="{ly}" text-anchor="{"end" if right else "start"}" dominant-baseline="middle">'
             f'Best day · {when} · {best["count"]} contributions</text></g>')

total = f'<text x="12" y="22" class="ttl" dominant-baseline="middle">{D["total"]:,} contributions in the last year</text>'

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{D["total"]} GitHub contributions in the last year, as a skyline">
<style>
{palette_css(PAL)}
text{{font:15px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:{FG}}}.ttl{{font-weight:600;font-size:16px}}.ln{{stroke:{MUTED}}}
.b{{transform-box:fill-box;transform-origin:50% 100%;animation:grow .7s cubic-bezier(.22,1,.36,1) both}}
.lbl,.ttl{{opacity:0;animation:fade .5s ease 2.4s forwards}}.ttl{{animation-delay:.2s}}
@keyframes grow{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
@keyframes fade{{to{{opacity:1}}}}
@media (prefers-reduced-motion:reduce){{.b,.lbl,.ttl{{animation:none;opacity:1}}}}
</style>
{"".join(shapes)}
{label}{total}
</svg>
'''
open(out, "w").write(svg)
