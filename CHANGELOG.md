# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
