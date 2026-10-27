# Renders the profile README header and stats cards from data/github.json,
# in the same look as skyline.py: GitHub greens, system font, no borders, CSS-only animation.
import json
import sys
from html import escape

src, out_dir, theme = sys.argv[1], sys.argv[2], sys.argv[3]  # theme: light | dark
D = json.load(open(src))

W = 900
LIGHT = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
DARK = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
PAL, FG, MUTED, ACCENT = (DARK, "#e6edf3", "#8b949e", "#3fb950") if theme == "dark" else (LIGHT, "#1f2328", "#656d76", "#1a7f37")
SANS = '-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif'
MONO = 'ui-monospace,SFMono-Regular,Menlo,Consolas,monospace'

BASE_CSS = f"""text{{font-family:{SANS};fill:{FG}}}.m{{fill:{MUTED}}}.a{{fill:{ACCENT}}}.mono{{font-family:{MONO}}}
.u{{opacity:0;animation:up .7s cubic-bezier(.22,1,.36,1) forwards}}
@keyframes up{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion:reduce){{.u,.g,.c{{animation:none;opacity:1;transform:none}}}}"""


def svg(h, label, css, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-label="{escape(label)}">\n'
            f'<style>\n{BASE_CSS}\n{css}\n</style>\n{body}\n</svg>\n')


def delay(s):
    return f' style="animation-delay:{s:.2f}s"'


# ---------- header ----------
weeks = 12
recent = D["levels"][-weeks * 7:]
cell, gap = 13, 3
gx = W - weeks * (cell + gap) + gap
cells = []
for i, lv in enumerate(recent):
    c, r = divmod(i, 7)
    cells.append(f'<rect class="c" x="{gx + c * (cell + gap)}" y="{40 + r * (cell + gap)}" width="{cell}" height="{cell}" rx="3" '
                 f'fill="{PAL[int(lv)]}"{delay(0.5 + (c + r) * 0.04)}/>')

header = svg(170, "Erkan Kolakan, Full Stack Developer",
             ".c{opacity:0;animation:pop .5s ease forwards}@keyframes pop{to{opacity:1}}",
             f'''<text class="a mono u" x="0" y="32" font-size="14"{delay(0)}>~/{escape(D["user"])}</text>
<text class="u" x="0" y="86" font-size="46" font-weight="700" letter-spacing="-1.2"{delay(0.1)}>Erkan Kolakan</text>
<text class="m u" x="0" y="122" font-size="18"{delay(0.2)}>Full Stack Developer — building web &amp; mobile apps with React Native.</text>
<text class="m u" x="0" y="156" font-size="14"{delay(0.3)}>Founder of <tspan fill="{FG}" font-weight="600">Flabex</tspan><tspan class="a">  ·  </tspan>Hackathon winner, 1st &amp; 2nd<tspan class="a">  ·  </tspan>Based in Turkey</text>
{"".join(cells)}''')

# ---------- stats ----------
counts = D["counts"]
last = len(counts) - 1
if counts[last] == 0:
    last -= 1  # today not done yet doesn't break the streak
s = last
while s >= 0 and counts[s] > 0:
    s -= 1
current = last - s
longest = run = 0
for c in counts:
    run = run + 1 if c else 0
    longest = max(longest, run)
stats = [(f"{max(counts)}", "best day"), (f"{longest}", "longest streak, days"),
         (f"{current}", "current streak, days"), (f"{sum(1 for c in counts if c)}", "active days this year")]

cols = []
for i, (num, label) in enumerate(stats):
    x = i * W / 4
    cols.append(f'<g class="u"{delay(0.1 * i)}><text x="{x:.0f}" y="38" font-size="34" font-weight="700" letter-spacing="-0.8">{num}</text>'
                f'<text class="m" x="{x:.0f}" y="62" font-size="13">{label}</text></g>')

langs = D.get("langs", [])
total = sum(l["size"] for l in langs) or 1
top = langs[:5]
other = total - sum(l["size"] for l in top)
parts = [(l["name"], l["color"], l["size"]) for l in top] + ([("Other", MUTED, other)] if other > 0 else [])
bar, legend, x, lx = [], [], 0.0, 0.0
for i, (name, color, size) in enumerate(parts):
    w = W * size / total
    bar.append(f'<rect class="g" x="{x:.1f}" y="92" width="{max(0, w - 2):.1f}" height="8" fill="{color}"{delay(0.4 + 0.08 * i)}/>')
    x += w
    label = f"{name} {100 * size / total:.1f}%"
    legend.append(f'<g class="u"{delay(0.6 + 0.06 * i)}><circle cx="{lx + 5:.0f}" cy="128" r="5" fill="{color}"/>'
                  f'<text class="m" x="{lx + 16:.0f}" y="133" font-size="13">{escape(label)}</text></g>')
    lx += 36 + len(label) * 7.2

stats_svg = svg(150, "GitHub stats and most used languages",
                ".g{transform-box:fill-box;transform-origin:0 50%;animation:grow .8s cubic-bezier(.22,1,.36,1) both}"
                "@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}",
                f'''{"".join(cols)}
<clipPath id="r"><rect x="0" y="92" width="{W}" height="8" rx="4"/></clipPath>
<g clip-path="url(#r)">{"".join(bar)}</g>
{"".join(legend)}''')

open(f"{out_dir}/header-{theme}.svg", "w").write(header)
open(f"{out_dir}/stats-{theme}.svg", "w").write(stats_svg)
