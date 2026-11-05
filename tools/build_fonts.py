"""The game's PAGAN HD fonts (gallows_font: axe-cut display capitals; gallows_body: the plain text face) for the site,
rendered sharper than the game's own sheets.

The game's sheets (54 px / 34 px caps) are drawn for the game's sizes; on the site they were upscaled (HiDPI screens,
big headings) and blurred. So this re-renders both fonts at 4x in a throwaway copy of the game's PAGAN project
(../loose/art/tools/gen_hd_font.py with the cells, caps and baselines scaled: the same stroke skeletons, seeds, chips
and bevel, so the same letters) and builds from that:

- public/fonts/gallows_font.webp + src/lib/gallows_font.json: the display font at 2x (every glyph), for headings
  (PaganText: the real bevelled, chipped glyphs).
- public/fonts/gallows_title.webp + src/lib/gallows_title.json: the title's glyphs at 4x (PaganText `hd`).
- public/fonts/gallows_font.woff2, gallows_body.woff2: each glyph's face traced into outlines from the 4x render and
  simplified (straight edges, not pixel steps), for body copy and small UI text (CSS colours them).

The soot outline is added here (PAGAN's outline caps at 8 px). Advances are the game sheets', scaled, so the spacing
is the game's (the traced fonts, which drop the outline, lose its width from each advance).

    .venv/bin/python tools/build_fonts.py [--game ../loose]      (needs the game repo's .venv with PAGAN)
"""

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
RENDER = 4  # the PAGAN render scale
SHEET = 2  # the headings' sheet scale
TITLE_GLYPHS = " LOSE!"
UNIT = 10  # font units per game-sheet pixel
INK = (0x14, 0x11, 0x10)  # palettes/gallows.pal.yaml "0" (ink)
# name -> (Pen line prefix in gen_hd_font.py, cap, cell, baseline, the game's outline px)
PENS = {
    "gallows_font": ('DISPLAY = Pen("gallows_font", cap_px=54, cell=(92, 92), baseline=68,', 54, 92, 68, 3),
    "gallows_body": ('BODY = Pen("gallows_body", cap_px=34, cell=(60, 60), baseline=44,', 34, 60, 44, 2),
}


def parse_fnt(path: Path) -> tuple[dict, dict[int, dict]]:
    common: dict = {}
    chars: dict[int, dict] = {}
    for line in path.read_text().splitlines():
        kv = {k: v.strip('"') for k, v in re.findall(r'(\w+)=("[^"]*"|\S+)', line)}
        if line.startswith("common") or line.startswith("info"):
            common.update(kv)
        elif line.startswith("char "):
            chars[int(kv["id"])] = {k: int(v) for k, v in kv.items() if k in
                                    ("x", "y", "width", "height", "xoffset", "yoffset", "xadvance")}
    return common, chars


# --- rendering ----------------------------------------------------------------------------------------------------

def render(game: Path, work: Path) -> Path:
    """Both fonts at RENDER x through PAGAN; returns the output fonts dir (<name>.fnt/.png)."""
    art = work / "art"
    (art / "sprites").mkdir(parents=True)
    (art / "tools").mkdir()
    shutil.copytree(game / "art" / "palettes", art / "palettes")
    (art / "pagan.toml").write_text('palette_mode = "strict"\ndefault_palette = "siege"\noutput_dir = "../out"\n'
                                    'preview_dir = "previews"\nexport = ["png"]\n')
    src = (game / "art" / "tools" / "gen_hd_font.py").read_text()
    for name, (prefix, cap, cell, base, _o) in PENS.items():
        if prefix not in src:
            raise SystemExit(f"gen_hd_font.py changed: can't find {prefix!r}")
        s = RENDER
        src = src.replace(prefix, f'{prefix.split("=", 1)[0]}= Pen("{name}", cap_px={cap * s}, cell=({cell * s}, {cell * s}), '
                                  f'baseline={base * s},')
    # Thinnest PAGAN outline: the real one is drawn here.
    src = src.replace("bevel=0.85, outline=3,", "bevel=0.85, outline=1,").replace("outline=2, spacing=0.03", "outline=1, spacing=0.03")
    (art / "tools" / "gen_hd_font.py").write_text(src)
    subprocess.run([str(game / ".venv" / "bin" / "python"), "tools/gen_hd_font.py"], cwd=art, check=True)
    subprocess.run([str(game / ".venv" / "bin" / "pagan"), "--quiet", "build"], cwd=art, check=True)
    return work / "out" / "fonts"


def shift_for(outline_px: int) -> int:
    """PAGAN's outline=1 leaves a 2 px left bearing at RENDER x; the game's (outline + 1 px) scaled is more."""
    return (outline_px + 1) * RENDER - 2


def with_outline(cell: Image.Image, outline_px: int) -> Image.Image:
    """`cell` moved right by the bearing it lost, over a round soot outline of the game's width (at RENDER x)."""
    w, h = cell.size
    moved = Image.new("RGBA", (w, h))
    moved.paste(cell, (shift_for(outline_px), 0))
    grown = moved.getchannel("A")
    r = outline_px * RENDER
    for _ in range(3):
        grown = grown.filter(ImageFilter.MaxFilter(2 * (r // 3) + 1))
    grown = grown.filter(ImageFilter.GaussianBlur(0.8))
    ink = Image.new("RGBA", (w, h), INK + (0,))
    ink.putalpha(grown)
    return Image.alpha_composite(ink, moved)


def build_sheet(fonts: Path, game_fnt: Path, name: str, scale: int, only: str | None) -> None:
    """The display font as a PaganText sheet at `scale` (glyphs `only`, or all), with the game's spacing."""
    _, game_chars = parse_fnt(game_fnt)
    common, chars = parse_fnt(fonts / "gallows_font.fnt")
    src = Image.open(fonts / "gallows_font.png").convert("RGBA")
    keep = sorted(k for k in chars if only is None or chr(k) in only)
    cell = 92 * scale
    cols = 10
    out = Image.new("RGBA", (cell * min(cols, len(keep)), cell * ((len(keep) + cols - 1) // cols)))
    table = {}
    for i, k in enumerate(keep):
        c = chars[k]
        g = with_outline(src.crop((c["x"], c["y"], c["x"] + c["width"], c["y"] + c["height"])), PENS["gallows_font"][4])
        if scale != RENDER:
            g = g.resize((cell, cell), Image.LANCZOS)
        x, y = (i % cols) * cell, (i // cols) * cell
        out.paste(g, (x, y))
        table[chr(k)] = [x, y, cell, cell, game_chars[k]["xadvance"] * scale]
    dst = ROOT / "public" / "fonts" / f"{name}.webp"
    out.save(dst, quality=92, method=6, alpha_quality=100)
    data = {"line": 92 * scale, "base": 68 * scale, "w": out.size[0], "h": out.size[1], "chars": table}
    (ROOT / "src" / "lib" / f"{name}.json").write_text(json.dumps(data, separators=(",", ":")))
    print(f"public/fonts/{name}.webp: {len(keep)} glyphs, {out.size[0]}x{out.size[1]}, {dst.stat().st_size / 1e3:.0f} kB")


# --- tracing ------------------------------------------------------------------------------------------------------

def face_mask(cell: Image.Image) -> list[list[bool]]:
    """Pixels of the glyph's face: opaque and not the dark outline."""
    w, h = cell.size
    px = cell.load()
    return [[px[x, y][3] >= 128 and (0.299 * px[x, y][0] + 0.587 * px[x, y][1] + 0.114 * px[x, y][2]) >= 40
             for x in range(w)] for y in range(h)]


def trace(mask: list[list[bool]]) -> list[list[tuple[int, int]]]:
    """Closed pixel-edge contours around the filled pixels (image coordinates, y down), the filled side on the left
    walking in y-down space = on the right in y-up font space (TrueType outer contours run clockwise)."""
    h = len(mask)
    w = len(mask[0]) if h else 0

    def filled(x: int, y: int) -> bool:
        return 0 <= x < w and 0 <= y < h and mask[y][x]

    nxt: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for y in range(h):
        for x in range(w):
            if not mask[y][x]:
                continue
            if not filled(x, y - 1):
                nxt.setdefault((x + 1, y), []).append((x, y))
            if not filled(x, y + 1):
                nxt.setdefault((x, y + 1), []).append((x + 1, y + 1))
            if not filled(x - 1, y):
                nxt.setdefault((x, y), []).append((x, y + 1))
            if not filled(x + 1, y):
                nxt.setdefault((x + 1, y + 1), []).append((x + 1, y))
    contours = []
    while nxt:
        start = next(iter(nxt))
        pts = [start]
        cur = nxt[start].pop()
        if not nxt[start]:
            del nxt[start]
        d_prev = (cur[0] - start[0], cur[1] - start[1])
        while cur != start:
            outs = nxt[cur]
            if len(outs) > 1:
                # A pinch vertex: turn left (y down) so diagonal pixels stay apart.
                outs.sort(key=lambda o: d_prev[0] * (o[1] - cur[1]) - d_prev[1] * (o[0] - cur[0]))
                n = outs.pop(0)
            else:
                n = outs.pop()
            if not outs:
                del nxt[cur]
            pts.append(cur)
            d_prev = (n[0] - cur[0], n[1] - cur[1])
            cur = n
        contours.append(pts)
    return contours


def _rdp(pts: list[tuple[float, float]], eps: float) -> list[tuple[float, float]]:
    if len(pts) < 3:
        return pts
    (ax, ay), (bx, by) = pts[0], pts[-1]
    dx, dy = bx - ax, by - ay
    n = (dx * dx + dy * dy) ** 0.5
    best, bi = -1.0, 0
    for i in range(1, len(pts) - 1):
        px, py = pts[i]
        d = abs(dy * (px - ax) - dx * (py - ay)) / n if n > 0 else ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
        if d > best:
            best, bi = d, i
    if best <= eps:
        return [pts[0], pts[-1]]
    return _rdp(pts[:bi + 1], eps)[:-1] + _rdp(pts[bi:], eps)


def simplify(contour: list[tuple[int, int]], eps: float) -> list[tuple[float, float]]:
    """Pixel steps smoothed into straight edges: a closed contour split at its two farthest points, each half
    Douglas-Peucker'd within `eps` px."""
    if len(contour) < 4:
        return contour
    a = 0
    b = max(range(len(contour)), key=lambda i: (contour[i][0] - contour[0][0]) ** 2 + (contour[i][1] - contour[0][1]) ** 2)
    first = _rdp(contour[a:b + 1], eps)
    second = _rdp(contour[b:] + [contour[0]], eps)
    return first[:-1] + second[:-1]


def area(c: list[tuple[float, float]]) -> float:
    return 0.5 * sum(c[i - 1][0] * c[i][1] - c[i][0] * c[i - 1][1] for i in range(len(c)))


def build_woff2(fonts: Path, game_fnt: Path, name: str, family: str) -> None:
    _, game_chars = parse_fnt(game_fnt)
    _, chars = parse_fnt(fonts / f"{name}.fnt")
    sheet = Image.open(fonts / f"{name}.png").convert("RGBA")
    _prefix, _cap, line, base, _outline = PENS[name]
    k = UNIT / RENDER  # font units per render pixel
    # The game's glyphs carry a dark outline on both sides; the traced faces don't, so they sit one outline in from the
    # game's bearing and each advance loses two outlines (else the text reads letter-spaced).
    dx = shift_for(_outline) - _outline * RENDER
    order = [".notdef"]
    cmap: dict[int, str] = {}
    glyphs = {".notdef": TTGlyphPen(None).glyph()}
    advances = {".notdef": line * UNIT // 2}
    for cid, c in sorted(chars.items()):
        gname = f"uni{cid:04X}"
        cell = sheet.crop((c["x"], c["y"], c["x"] + c["width"], c["y"] + c["height"]))
        pen = TTGlyphPen(None)
        for contour in trace(face_mask(cell)):
            pts = simplify(contour, 0.9)
            if len(pts) < 3 or abs(area(pts)) < 4:
                continue
            for i, (x, y) in enumerate(pts):
                p = (round((x + dx) * k), round((base * RENDER - y) * k))
                pen.moveTo(p) if i == 0 else pen.lineTo(p)
            pen.closePath()
        glyphs[gname] = pen.glyph()
        adv = game_chars[cid]["xadvance"] if cid in game_chars else c["xadvance"] / RENDER
        advances[gname] = (adv if cid == 32 else max(adv - 2 * _outline, 1)) * UNIT  # a space has no outline
        order.append(gname)
        cmap[cid] = gname
    fb = FontBuilder(line * UNIT, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    metrics = {}
    for n, g in glyphs.items():
        g.recalcBounds(fb.font["glyf"])
        metrics[n] = (round(advances[n]), getattr(g, "xMin", 0))
    fb.setupHorizontalMetrics(metrics)
    asc, desc = base * UNIT, (line - base) * UNIT
    fb.setupHorizontalHeader(ascent=asc, descent=-desc)
    fb.setupNameTable({"familyName": family, "styleName": "Regular"})
    fb.setupOS2(sTypoAscender=asc, sTypoDescender=-desc, usWinAscent=asc, usWinDescent=desc)
    fb.setupPost()
    fb.font.flavor = "woff2"
    out = ROOT / "public" / "fonts" / f"{name}.woff2"
    fb.save(str(out))
    print(f"public/fonts/{name}.woff2: {len(chars)} glyphs, {out.stat().st_size / 1e3:.0f} kB")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", type=Path, default=ROOT.parent / "loose")
    a = ap.parse_args()
    game = a.game.resolve()
    game_fonts = game / "assets" / "generated" / "fonts"
    (ROOT / "public" / "fonts").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        fonts = render(game, Path(tmp))
        build_sheet(fonts, game_fonts / "gallows_font.fnt", "gallows_font", SHEET, None)
        build_sheet(fonts, game_fonts / "gallows_font.fnt", "gallows_title", RENDER, TITLE_GLYPHS)
        build_woff2(fonts, game_fonts / "gallows_font.fnt", "gallows_font", "Gallows")
        build_woff2(fonts, game_fonts / "gallows_body.fnt", "gallows_body", "Gallows Body")


if __name__ == "__main__":
    main()
