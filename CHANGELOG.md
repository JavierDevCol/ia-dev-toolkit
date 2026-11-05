# Changelog

## [Unreleased]

## [4.0.0] - 2026-11-05

### Breaking
- feat(config): unified sac.json + memctl, single documentacion_sac_path root (#10)

### Added
- feat(estado-ambientes): add environment promotion status skill
- feat(entrega-ambiente-banco): add configurable output_documentacion path
- feat(vault-manager): diagnose auth failures and add REST fallback
- feat(ado-pipeline-analyzer): verify run integrity and stage coverage
- feat(bitacora-tecnica): estimate duration and split work sessions
- feat(ado-wi-query): add read-only WI query skill aligned with sac.json (memctl block, profile guard, MCP catalog tools)
- feat(planear-agenda-siguiente-dia): add the skill aligned with sac.json (memctl table, configuration phase, outputs under documentacion_sac_path)
- feat(iniciar-dia-laboral): add the skill aligned with sac.json (memctl block, configuration phase, calendar id as argument)
- feat(chat-equipo): add the skill aligned with sac.json (memctl block, configuration phase, tz/aliases from config)
- feat(config): add chat-dm and agenda-laboral sections to the sac.json template (no defaults, no personal data)
- feat: run SAC workflows in Claude Code via exc-workflow-sac skill and per-harness installer (#6)

### Changed
- test: guard the chat and agenda skills against personal data and unknown memctl keys; drop empty memory from the new sections
- chore: start sac.json alignment of chat-equipo and the agenda skills
- docs(changelog): note the sac- prefix rename of SAC skills (#13)
- refactor(skills): ado- prefix, project_map resolution and profile guard (#8)

### Fixed
- fix(ado-wi-query): inline the MCP tool names in the skill instead of referencing the _docs catalog at runtime
- fix(exc-workflow-sac): resolve .SAC only at project root (#9)
- fix(ci): configure git identity before moving -TEST tag (#7)

**Full Changelog**: https://github.com/JavierDevCol/ia-dev-toolkit/compare/v3.0.0...v4.0.0

## [3.0.0] - 2026-10-30

### Breaking
- feat(skills): sac.json alignment, ado-wi-query and diagnostic hardening (#17)

**Full Changelog**: https://github.com/JavierDevCol/ia-dev-toolkit/compare/v2.0.0...v3.0.0

## [2.0.0] - 2026-10-27

### Breaking
- release: sac.json unificado, prefijo sac- en skills y mejoras del instalador (#16)

**Full Changelog**: https://github.com/JavierDevCol/ia-dev-toolkit/compare/v1.1.1...v2.0.0

### Changed
- **BREAKING** refactor(skills): the 14 SAC skills now carry the `sac-` prefix, like `ado-*`: `sac-tomar-contexto`, `sac-iniciar-sprint`, `sac-refinar-hu`, `sac-validar-hu`, `sac-planificar-hu`, `sac-ejecutar-plan`, `sac-validar-ca`, `sac-priorizar-backlog`, `sac-sincronizar-backlog`, `sac-registrar-hallazgo`, `sac-init-reglas-arquitectonicas`, `sac-crear-adr`, `sac-analizar-calidad-codigo`, `sac-analizar-seguridad`. `git-branch-commit`, `bitacora-tecnica` and `exc-workflow-sac` keep their names.
- **BREAKING** triggers follow the new names: `>validar_ca` is now `>sac_validar_ca`, `>tomar_contexto` is `>sac_tomar_contexto`, and so on.
- Migration: `diat --update` converts the registered names and removes the old skill folders; skills you wrote yourself are left untouched.

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
