"""Encode a game capture (a --write-movie PNG sequence, tools/capture.sh in the game repo) into a website loop.

    .venv/bin/python tools/encode_clip.py <frames dir> <id> [--from N] [--to N] [--speed X] [--poster N] [--width W]
        [--crop w:h:x:y]

Writes public/video/<id>.mp4 (H.264), <id>.webm (VP9) and <id>.jpg (poster): muted, 30 fps, a few MB at most.
"""

import argparse
import subprocess
import tempfile
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "public" / "video"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("frames", type=Path)
    ap.add_argument("id")
    ap.add_argument("--from", dest="first", type=int, default=0)
    ap.add_argument("--to", dest="last", type=int, default=-1)
    ap.add_argument("--speed", type=float, default=1.0, help="playback speed (2 = twice as fast)")
    ap.add_argument("--poster", type=int, default=-1, help="frame for the poster (default: a third in)")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--crop", default="", help="w:h:x:y of the source to keep (e.g. cut a HUD off)")
    a = ap.parse_args()

    files = sorted(a.frames.glob("f*.png"))
    last = len(files) if a.last < 0 else min(a.last, len(files))
    files = files[a.first:last]
    if not files:
        raise SystemExit("no frames")
    OUT.mkdir(parents=True, exist_ok=True)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    with tempfile.TemporaryDirectory() as tmp:
        lst = Path(tmp) / "frames.txt"
        lst.write_text("".join(f"file '{f.resolve()}'\nduration {1 / 30 / a.speed:.6f}\n" for f in files))
        common = [ff, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                  "-vf", (f"crop={a.crop}," if a.crop else "") + f"scale={a.width}:-2:flags=lanczos,fps=30", "-an"]
        subprocess.run(common + ["-c:v", "libx264", "-preset", "slow", "-crf", "24", "-pix_fmt", "yuv420p",
                                 "-movflags", "+faststart", str(OUT / f"{a.id}.mp4")], check=True)
        subprocess.run(common + ["-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "42", "-row-mt", "1",
                                 str(OUT / f"{a.id}.webm")], check=True)
    p = files[a.poster - a.first if a.poster >= 0 else len(files) // 3]
    im = Image.open(p).convert("RGB")
    if a.crop:
        w, h, x, y = (int(v) for v in a.crop.split(":"))
        im = im.crop((x, y, x + w, y + h))
    im = im.resize((a.width, round(im.height * a.width / im.width)), Image.LANCZOS)
    im.save(OUT / f"{a.id}.jpg", quality=82, optimize=True)
    for ext in ("mp4", "webm", "jpg"):
        print(f"{a.id}.{ext}: {(OUT / f'{a.id}.{ext}').stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
