# Changelog

## [Unreleased]

## [1.1.1] - 2026-10-21

### Changed
- refactor(entrega-ambiente-banco): phase-based flow, unified outputs (#5)

**Full Changelog**: https://github.com/JavierDevCol/ia-dev-toolkit/compare/v1.1.0...v1.1.1

## [1.1.0] - 2026-10-21

### Added
- feat(release): resume half-finished stable releases on rerun
- feat(release): add changelog updater and release notes renderer
- feat(release): plan per-channel version with -TEST adoption and CLI
- feat(release): add commit classification and semver bump logic

### Changed
- docs: scope auto-versioning skill to manual recovery
- test(release): cross-check tag regexes against installer pattern
- docs: clarify version adoption rule and scope skill to manual use
- docs: document automated release channels and reserve skill
- ci: publish stable release on main pushes with changelog and merge-back
- ci: move vX.Y.Z-TEST tag on develop pushes
- docs(release): add release automation spec and implementation plan

### Fixed
- fix(ci): skip runs triggered by release bot bookkeeping commits
- fix(ci): tolerate an empty changelog diff when committing
- fix(release): anchor changelog insertion to line starts
- fix(ci): gate changelog step on a computed release tag
- fix(release): make changelog insertion idempotent per version
- fix(release): never adopt a -TEST below the last stable version
- fix(release): normalize next_version output without v prefix

**Full Changelog**: https://github.com/JavierDevCol/ia-dev-toolkit/compare/v1.0.1...v1.1.0
