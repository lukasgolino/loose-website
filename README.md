# LOOSE! website

One-page static Astro site for LOOSE! (game repo: `../loose`). No backend. Live at https://loosegame.com/
(GitHub Pages, deployed by `.github/workflows/deploy.yml` on every push to `main`).

```sh
npm ci
npm run dev        # http://localhost:4321/
npm run build      # -> dist/
npm run check      # astro check (types)
```

- Copy and game facts: `src/lib/data.ts` (Steam URL, clips, arrows, levels).
- Clips: `public/video/<id>.mp4|.webm|.jpg` (muted loops, a couple of MB each). A clip shows only once its mp4 exists.
  Record in the game repo offscreen (`tools/capture.sh <dir> <frames> -- <demo args>`, e.g. `--ragdoll-demo=bowl`,
  `--ragdoll-demo=bridge --level=0`, `--level=4 --autopilot`), then encode:
  `.venv/bin/python tools/encode_clip.py <dir> <id> --from N --to N [--crop 1280:500:0:112]`
  (`python3 -m venv .venv && .venv/bin/pip install -r tools/requirements.txt`).
- Fonts: the game's PAGAN `gallows` fonts. `npm run fonts` rebuilds `public/fonts/` and `src/lib/gallows_font.json`
  from `../loose/assets/generated/fonts` (re-rendered at 4x through PAGAN, so it needs the game repo's `.venv`: headings = a 2x glyph sheet via `PaganText`,
  the hero title = 4x, text = traced, simplified woff2). Commit the output.
- Stills: JPGs in `public/img/shots/` appear under the level list; `public/img/og.jpg` is the share image.
