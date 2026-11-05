# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
