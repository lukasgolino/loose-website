"""A 4x copy of the game's PAGAN display font (gallows_font) for the hero title only: the game's sheet has 54 px caps
and blurred when the title showed it at ~150 css px (and twice that on HiDPI screens).

Renders the glyphs in a throwaway copy of the game's PAGAN project (art/tools/gen_hd_font.py with cap 216 px, same
skeletons, seeds, chips and bevel), then adds the soot outline here (PAGAN's outline caps at 8 px; the game's is 3 px
at 1x, so 12 px at 4x). Writes public/fonts/gallows_title.png + src/lib/gallows_title.json (PaganText's `hd`).

    .venv/bin/python tools/build_hd_title.py [--game ../loose] [--glyphs " LOSE!"]
"""

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageFilter

from build_fonts import parse_fnt

ROOT = Path(__file__).resolve().parent.parent
SCALE = 4
OUTLINE = 3 * SCALE  # the game's outline (output px) at this scale
INK = (0x14, 0x11, 0x10)  # palettes/gallows.pal.yaml "0" (ink)
# PAGAN's outline=1 leaves a 2 px left bearing; the game's (outline 3 + 1 px) at 4x is 16.
SHIFT = (3 + 1) * SCALE - 2


def render(game: Path, glyphs: str, work: Path) -> Path:
    art = work / "art"
    (art / "sprites").mkdir(parents=True)
    (art / "tools").mkdir()
    shutil.copytree(game / "art" / "palettes", art / "palettes")
    (art / "pagan.toml").write_text('palette_mode = "strict"\ndefault_palette = "siege"\noutput_dir = "../out"\n'
                                    'preview_dir = "previews"\nexport = ["png"]\n')
    src = (game / "art" / "tools" / "gen_hd_font.py").read_text()
    edits = [
        ('DISPLAY = Pen("gallows_font", cap_px=54, cell=(92, 92), baseline=68,',
         f'DISPLAY = Pen("gallows_font", cap_px={54 * SCALE}, cell=({92 * SCALE}, {92 * SCALE}), baseline={68 * SCALE},'),
        ("chips=3, bevel=0.85, outline=3,", "chips=3, bevel=0.85, outline=1,"),
        ("    for pen in (DISPLAY, BODY):", "    for pen in (DISPLAY,):"),
    ]
    for a, b in edits:
        if a not in src:
            raise SystemExit(f"gen_hd_font.py changed: can't find {a!r}")
        src = src.replace(a, b)
    start = src.index("ORDER = (")
    end = src.index('")\n', start) + 2
    src = src[:start] + f"ORDER = {glyphs!r}" + src[end:]
    (art / "tools" / "gen_hd_font.py").write_text(src)
    py = game / ".venv" / "bin" / "python"
    subprocess.run([str(py), "tools/gen_hd_font.py"], cwd=art, check=True)
    subprocess.run([str(game / ".venv" / "bin" / "pagan"), "--quiet", "build"], cwd=art, check=True)
    return work / "out" / "fonts" / "gallows_font.fnt"


def outline(cell: Image.Image) -> Image.Image:
    """`cell` moved right by SHIFT, with an OUTLINE px soot outline under it."""
    w, h = cell.size
    moved = Image.new("RGBA", (w, h))
    moved.paste(cell, (SHIFT, 0))
    a = moved.getchannel("A")
    # A round outline: dilate in steps (MaxFilter is square; three steps of a third look round enough).
    grown = a
    for _ in range(3):
        grown = grown.filter(ImageFilter.MaxFilter(2 * (OUTLINE // 3) + 1))
    grown = grown.filter(ImageFilter.GaussianBlur(0.8))
    ink = Image.new("RGBA", (w, h), INK + (0,))
    ink.putalpha(grown)
    return Image.alpha_composite(ink, moved)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", type=Path, default=ROOT.parent / "loose")
    ap.add_argument("--glyphs", default=" LOSE!")
    a = ap.parse_args()
    _, game_chars = parse_fnt(a.game / "assets" / "generated" / "fonts" / "gallows_font.fnt")
    game_adv = {k: v["xadvance"] for k, v in game_chars.items()}
    with tempfile.TemporaryDirectory() as tmp:
        fnt = render(a.game.resolve(), a.glyphs, Path(tmp))
        common, chars = parse_fnt(fnt)
        sheet = Image.open(fnt.with_suffix(".png")).convert("RGBA")
        out = Image.new("RGBA", sheet.size)
        for c in chars.values():
            cell = sheet.crop((c["x"], c["y"], c["x"] + c["width"], c["y"] + c["height"]))
            out.paste(outline(cell), (c["x"], c["y"]))
    dst = ROOT / "public" / "fonts" / "gallows_title.png"
    out.save(dst, optimize=True)
    data = {"line": int(common["lineHeight"]), "base": int(common["base"]), "w": int(common["scaleW"]),
            "h": int(common["scaleH"]),
            # Advances: the game sheet's x4, so the spacing is the game's.
            "chars": {chr(k): [v["x"], v["y"], v["width"], v["height"], game_adv[k] * SCALE] for k, v in chars.items()}}
    (ROOT / "src" / "lib" / "gallows_title.json").write_text(json.dumps(data, separators=(",", ":")))
    print(f"{dst.relative_to(ROOT)}: {len(chars)} glyphs, {out.size[0]}x{out.size[1]}, {dst.stat().st_size / 1e3:.0f} kB")


if __name__ == "__main__":
    main()
