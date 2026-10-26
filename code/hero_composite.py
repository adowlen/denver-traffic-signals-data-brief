"""Composite the headline figure over the generated hero illustration.
Run only when a generated illustration exists in hero_source/. Text
sits on a solid dark scrim band at the top for legibility. Headline
text is read from stats.json at run time so it cannot drift."""
import json, pathlib
from PIL import Image, ImageDraw, ImageFont

root = pathlib.Path(__file__).resolve().parent.parent
s = json.loads((root / "stats.json").read_text())
cands = sorted((root / "hero_source").glob("*.webp")) + \
        sorted((root / "hero_source").glob("*.png")) + \
        sorted((root / "hero_source").glob("*.jpg"))
if not cands:
    raise SystemExit("no hero illustration in hero_source/ - hero stays pending")
img = Image.open(cands[0]).convert("RGB")
W, H = img.size
band = int(H * 0.44)
scrim = Image.new("RGB", (W, band), (16, 20, 23))
img.paste(scrim, (0, 0))
d = ImageDraw.Draw(img)

def font(size, bold=True):
    p = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
         else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(p, size)

def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=f) <= maxw:
            cur = trial
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines

MAXW = W - 124
headline = "0 of 1,288 signals"
d.text((60, 40), headline, font=font(int(H * 0.095)), fill=(245, 168, 0))
sub_f = font(int(H * 0.036), bold=False)
y = 40 + int(H * 0.125)
sub = (f"Not one of Denver's {s['total_records']} traffic signals carries an installation, "
       f"rebuild, or retime date in the city register - so the fleet's age cannot be "
       f"read from the public record.")
for line in wrap(sub, sub_f, MAXW):
    d.text((62, y), line, font=sub_f, fill=(242, 242, 242))
    y += int(H * 0.052)
src_f = font(int(H * 0.026), bold=False)
srcline = ("Source: Denver Open Data, traffic signal register (1,288 signals; "
           "service data last edited May 24, 2024), pulled Oct 26, 2026")
for line in wrap(srcline, src_f, MAXW):
    d.text((62, y + 6), line, font=src_f, fill=(150, 210, 200))
    y += int(H * 0.040)
img.save(root / "hero.png")
print("hero", img.size, "from", cands[0].name)
