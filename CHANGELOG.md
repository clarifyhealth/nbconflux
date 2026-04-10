# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.12] - 2026-04-10

### Added
- CircleCI deployment pipeline with jobs for sensitive-information checks, build-and-test, and artifact publishing
- `git-secrets` integration via `install-git-secrets-circleci` Makefile target and `git-secrets-runner.sh`
- `radon` added to test requirements for cyclomatic complexity and maintainability checks in CI

### Changed
- Requirements pinned: `requirements-test.txt` uses exact versions; `requirements.txt` and `setup.py` use minimum-version bounds reflecting the tested baseline
- `mistune>=3.0` added as an explicit runtime dependency (was previously an implicit transitive dep)

### Fixed
- Upgraded to `nbconvert>=7.0` Jinja2 template system: replaced legacy `.tpl` template with `nbconflux/templates/confluence/index.html.j2` and `conf.json`
- `ConfluenceMarkdownRenderer.image()` updated for `mistune>=3.0` API (argument order changed from `src, title, alt` to `alt, url, title`)
- `filter.py` updated for `bleach>=6.0` API: replaced deprecated `styles=` kwarg with `css_sanitizer=CSSSanitizer(...)`
- Test assertions updated to match current `bleach`/`html5lib` serialization (`<ri:url ...></ri:url>` instead of `<ri:url ... />`) and Pygments quote encoding
- Papermill `injected-parameters` cells are now filtered from output (added to `TagRemovePreprocessor.remove_cell_tags`)
- Minified Plotly JS bundle no longer appears as visible text: `script` added to `ALLOWED_TAGS` and `REMOVED_TAGS` so `RemovalFilter` strips tag and content
- Table cell alignment preserved: `style` attribute allowed on `td` and `th` in `ALLOWED_ATTRS`
- END OF REPORT heading removal now applies to all notebooks, not just those with Plotly charts

## [1.0.11] - 2025-11-25

### Fixed
- Reworked Plotly static preprocessing to resolve duplicate graph rendering in exported pages

## [1.0.10] - 2025-11-25

### Changed
- Moved Plotly preprocessing logic from `PlotlyStaticPreprocessor` into `ConfluenceExporter.from_notebook_node`

## [1.0.9] - 2025-11-25

### Fixed
- Corrected output file path construction in `PlotlyStaticPreprocessor`

## [1.0.8] - 2025-11-25

### Changed
- Configured Kaleido engine settings in `PlotlyStaticPreprocessor` for reliable PNG export

## [1.0.7] - 2025-11-24

### Fixed
- Patched `versioneer.py` for compatibility with current Python/Git environment

## [1.0.6] - 2025-11-24

### Changed
- Updated `versioneer.py` to latest release

## [1.0.5] - 2025-11-24

### Changed
- Updated `requirements.txt` runtime dependencies

## [1.0.4] - 2025-11-24

### Fixed
- Minor release tagging correction

## [1.0.3] - 2025-11-24

### Added
- Plotly chart conversion to static PNG via Kaleido (`PlotlyStaticPreprocessor`)
- `plotly` and `kaleido` added as runtime dependencies

## [1.0.1] - 2025-11-24

### Added
- Bundled nbconvert 7.x-compatible Jinja2 templates (`nbconflux/templates/`) so the package is self-contained and does not rely on system-installed nbconvert templates

## [0.6.0] - 2019

### Added
- Pagination support for attachment lookups (follows `_links.next`)
- Table cell `rowspan`/`colspan` attribute support

## [0.5.1] - 2019

### Fixed
- Anchor link CSS rule fix
- Paragraph glyph regression

## [0.5.0] - 2019

Initial open source release by Valassis Digital.

### Added
- `ConfluenceExporter` — converts notebooks to Confluence XHTML storage format via nbconvert
- `ConfluencePreprocessor` — resolves attachment versions and builds versioned download/upload URLs
- `ConfluenceMarkdownRenderer` — renders Markdown images as `<ac:image>` tags
- `sanitize_html` filter — strips tags/attributes not valid in Confluence storage format via bleach
- Table of contents macro, optional MathJax, optional stylesheet injection
- `attach_ipynb` option to attach the source notebook to the Confluence page
- CLI (`nbconflux`) with credential support via env vars, `~/.nbconflux` file, or interactive prompt
- `extra_labels` support for tagging published pages

[Unreleased]: https://github.com/clarifyhealth/nbconflux/compare/1.0.11...HEAD
[1.0.11]: https://github.com/clarifyhealth/nbconflux/compare/1.0.10...1.0.11
[1.0.10]: https://github.com/clarifyhealth/nbconflux/compare/1.0.9...1.0.10
[1.0.9]: https://github.com/clarifyhealth/nbconflux/compare/1.0.8...1.0.9
[1.0.8]: https://github.com/clarifyhealth/nbconflux/compare/1.0.7...1.0.8
[1.0.7]: https://github.com/clarifyhealth/nbconflux/compare/1.0.6...1.0.7
[1.0.6]: https://github.com/clarifyhealth/nbconflux/compare/1.0.5...1.0.6
[1.0.5]: https://github.com/clarifyhealth/nbconflux/compare/1.0.4...1.0.5
[1.0.4]: https://github.com/clarifyhealth/nbconflux/compare/1.0.3...1.0.4
[1.0.3]: https://github.com/clarifyhealth/nbconflux/compare/1.0.1...1.0.3
[1.0.1]: https://github.com/clarifyhealth/nbconflux/compare/0.6.0...1.0.1
[0.6.0]: https://github.com/clarifyhealth/nbconflux/compare/0.5.1...0.6.0
[0.5.1]: https://github.com/clarifyhealth/nbconflux/compare/0.5.0...0.5.1
[0.5.0]: https://github.com/clarifyhealth/nbconflux/releases/tag/0.5.0
