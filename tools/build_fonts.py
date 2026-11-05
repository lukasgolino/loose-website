"""The game's PAGAN HD fonts (../loose/assets/generated/fonts/gallows_font|gallows_body: BMFont .fnt + .png sheets) for
the site:

- public/fonts/<name>.woff2: each glyph's face traced into outlines (the baked soot outline and bevel shading are
  dropped; CSS colours the text), for body copy and small UI text.
- public/fonts/gallows_font.png + src/lib/gallows_font.json: the display sheet itself and its glyph metrics, for the
  PaganText component (headings drawn with the real bevelled, chipped glyphs).

    .venv/bin/python tools/build_fonts.py [--game ../loose]
"""

import argparse
import json
import re
import shutil
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
UNIT = 10  # font units per sheet pixel


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


def face_mask(cell: Image.Image) -> list[list[bool]]:
    """Pixels of the glyph's face: opaque and not the near-black soot outline."""
    w, h = cell.size
    px = cell.load()
    out = []
    for y in range(h):
        row = []
        for x in range(w):
            r, g, b, a = px[x, y]
            row.append(a >= 128 and (0.299 * r + 0.587 * g + 0.114 * b) >= 40)
        out.append(row)
    return out


def trace(mask: list[list[bool]]) -> list[list[tuple[int, int]]]:
    """Closed pixel-edge contours around the filled pixels (image coordinates, y down), clockwise on screen for
    filled regions, so clockwise in font space after flipping y... TrueType wants outer contours clockwise in y-up
    space: emit edges with the filled pixel on the right when walking in y-up coordinates."""
    h = len(mask)
    w = len(mask[0]) if h else 0

    def filled(x: int, y: int) -> bool:
        return 0 <= x < w and 0 <= y < h and mask[y][x]

    # Directed edges in image space with the filled pixel on the LEFT (y down) == on the RIGHT in y-up space.
    nxt: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for y in range(h):
        for x in range(w):
            if not mask[y][x]:
                continue
            if not filled(x, y - 1):
                nxt.setdefault((x + 1, y), []).append((x, y))  # top edge, right -> left
            if not filled(x, y + 1):
                nxt.setdefault((x, y + 1), []).append((x + 1, y + 1))  # bottom edge, left -> right
            if not filled(x - 1, y):
                nxt.setdefault((x, y), []).append((x, y + 1))  # left edge, down
            if not filled(x + 1, y):
                nxt.setdefault((x + 1, y + 1), []).append((x + 1, y))  # right edge, up
    contours = []
    while nxt:
        start = next(iter(nxt))
        pts = [start]
        prev = start
        cur = nxt[start].pop()
        if not nxt[start]:
            del nxt[start]
        d_prev = (cur[0] - prev[0], cur[1] - prev[1])
        while cur != start:
            outs = nxt[cur]
            if len(outs) == 1:
                n = outs.pop()
            else:
                # A pinch vertex: keep turning the same way (left in y-down image space) so diagonal pixels stay apart.
                def turn(o: tuple[int, int]) -> int:
                    d = (o[0] - cur[0], o[1] - cur[1])
                    return d_prev[0] * d[1] - d_prev[1] * d[0]
                outs.sort(key=turn)
                n = outs.pop(0)
            if not outs:
                del nxt[cur]
            pts.append(cur)
            d_prev = (n[0] - cur[0], n[1] - cur[1])
            prev, cur = cur, n
        # Drop collinear points.
        simple = []
        m = len(pts)
        for i in range(m):
            a, b, c = pts[i - 1], pts[i], pts[(i + 1) % m]
            if (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]) != 0:
                simple.append(b)
        contours.append(simple)
    return contours


def build_woff2(fnt: Path, out: Path, family: str) -> None:
    common, chars = parse_fnt(fnt)
    sheet = Image.open(fnt.with_suffix(".png")).convert("RGBA")
    line, base = int(common["lineHeight"]), int(common["base"])
    upm = line * UNIT
    order = [".notdef"]
    cmap: dict[int, str] = {}
    glyphs = {}
    metrics = {}
    empty = TTGlyphPen(None)
    glyphs[".notdef"] = empty.glyph()
    metrics[".notdef"] = (line * UNIT // 2, 0)
    for cid, c in sorted(chars.items()):
        name = f"uni{cid:04X}"
        cell = sheet.crop((c["x"], c["y"], c["x"] + c["width"], c["y"] + c["height"]))
        pen = TTGlyphPen(None)
        for contour in trace(face_mask(cell)):
            if len(contour) < 3:
                continue
            for i, (x, y) in enumerate(contour):
                p = ((x + c["xoffset"]) * UNIT, (base - (y + c["yoffset"])) * UNIT)
                if i == 0:
                    pen.moveTo(p)
                else:
                    pen.lineTo(p)
            pen.closePath()
        glyphs[name] = pen.glyph()
        metrics[name] = (c["xadvance"] * UNIT, 0)
        order.append(name)
        cmap[cid] = name
    fb = FontBuilder(upm, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    for n, g in glyphs.items():
        g.recalcBounds(fb.font["glyf"])
        metrics[n] = (metrics[n][0], getattr(g, "xMin", 0))
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=base * UNIT, descent=-(line - base) * UNIT)
    fb.setupNameTable({"familyName": family, "styleName": "Regular"})
    fb.setupOS2(sTypoAscender=base * UNIT, sTypoDescender=-(line - base) * UNIT, usWinAscent=base * UNIT,
                usWinDescent=(line - base) * UNIT)
    fb.setupPost()
    fb.font.flavor = "woff2"
    out.parent.mkdir(parents=True, exist_ok=True)
    fb.save(str(out))
    print(f"{out.relative_to(ROOT)}: {len(chars)} glyphs, {out.stat().st_size / 1e3:.0f} kB")


def build_sprite(fnt: Path, name: str) -> None:
    common, chars = parse_fnt(fnt)
    dst = ROOT / "public" / "fonts" / f"{name}.png"
    shutil.copyfile(fnt.with_suffix(".png"), dst)
    data = {"line": int(common["lineHeight"]), "base": int(common["base"]), "w": int(common["scaleW"]),
            "h": int(common["scaleH"]), "chars": {chr(k): [v["x"], v["y"], v["width"], v["height"], v["xadvance"]]
                                                  for k, v in chars.items()}}
    (ROOT / "src" / "lib" / f"{name}.json").write_text(json.dumps(data, separators=(",", ":")))
    print(f"public/fonts/{name}.png + src/lib/{name}.json: {len(chars)} glyphs")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", type=Path, default=ROOT.parent / "loose")
    a = ap.parse_args()
    fonts = a.game / "assets" / "generated" / "fonts"
    build_woff2(fonts / "gallows_font.fnt", ROOT / "public" / "fonts" / "gallows_font.woff2", "Gallows")
    build_woff2(fonts / "gallows_body.fnt", ROOT / "public" / "fonts" / "gallows_body.woff2", "Gallows Body")
    build_sprite(fonts / "gallows_font.fnt", "gallows_font")


if __name__ == "__main__":
    main()
