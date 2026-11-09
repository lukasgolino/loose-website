# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.1] - 2026-11-09

### Added

- Footer link to the privacy notice at lukasgolino.com/privacy.html, which covers the analytics and hosting of all our
  sites ([lukasgolino.github.io#16](https://github.com/lukasgolino/lukasgolino.github.io/issues/16)).

## [0.5.0] - 2026-11-09

### Added

- Umami analytics alongside Cloudflare Web Analytics: cookieless, so still no consent banner, and it adds
  per-visit page journeys (entry page, pages in order, exit), which Cloudflare's aggregate counts can't show.
  All our sites share one Umami website; the Host filter separates them.

## [0.4.0] - 2026-11-06

### Added

- A standard icon set: `favicon.ico` (16/32/48 px), a 96 px icon, a 180 px apple-touch icon and `site.webmanifest`
  with 192/512 px and maskable icons, so search results, tabs, bookmarks and home-screen shortcuts all show the
  icon ([#9](https://github.com/lukasgolino/loose-website/issues/9)).
- schema.org structured data (JSON-LD) on the home page, an `llms.txt` summary for AI assistants, and robots.txt
  content signals allowing search and AI use; the home page title names what the site is for
  ([#10](https://github.com/lukasgolino/loose-website/issues/10)).

### Changed

- Tool dependency updates (`tools/requirements.txt`).

## [0.3.0] - 2026-11-06

### Changed

- The site moves to its own domain, https://loosegame.com/ (it was https://lukasgolino.com/loose-website/, which now
  redirects), with an `og:url` tag. The KILN link points at https://kiln3d.dev/
  ([#2](https://github.com/lukasgolino/loose-website/issues/2)).

### Added

- `sitemap.xml` and `robots.txt`, generated from the pages and the site URL
  ([#1](https://github.com/lukasgolino/loose-website/issues/1)).
- Cloudflare Web Analytics beacon, production builds only
  ([#3](https://github.com/lukasgolino/loose-website/issues/3)).
- A check on every push (`astro check`, build, and `tools/check-dist.mjs`: the sitemap lists exactly the built pages,
  robots.txt points to it, every page loads the beacon), run by deploys too, and a notes-only GitHub release per
  `vX.Y.Z` tag ([#4](https://github.com/lukasgolino/loose-website/issues/4)).

## [0.2.2] - 2026-11-05

### Fixed

- All text is sharp on HiDPI screens: `tools/build_fonts.py` re-renders both PAGAN fonts at 4x through PAGAN and
  builds the headings' glyph sheet at 2x (WebP), the hero title at 4x, and the text fonts traced from the 4x render
  with simplified outlines (straight edges instead of pixel steps). The text fonts' spacing no longer counts the
  dropped outline (it read letter-spaced). `tools/build_hd_title.py` is folded into it.

## [0.2.1] - 2026-11-05

### Fixed

- The hero title is sharp: it uses a 4x render of the PAGAN display font (`tools/build_hd_title.py`, same letterforms
  and spacing as the game) instead of upscaling the game's 54 px glyphs.

## [0.2.0] - 2026-11-05

### Changed

- The game's own PAGAN fonts replace Cinzel and Alegreya Sans: headings are drawn with the real bevelled `gallows_font`
  glyphs from its sheet (`PaganText`), body and UI text use `gallows_font` / `gallows_body` traced to web fonts
  (`tools/build_fonts.py`, `npm run fonts`).
- The hero loop is cropped clear of the game's HUD.

## [0.1.0] - 2026-11-05

### Added

- One-page site: hero flight loop, six gameplay moments (kill cam, keg, bowling, drawbridge, fire, trebuchet), the
  five arrows, the eight levels, stills, "Coming soon to Steam". Deployed to GitHub Pages on push.
