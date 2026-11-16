# CHANGELOG

リリース(バージョン)単位の変更をまとめます。日々の詳細な経緯は [docs/DEVELOPMENT_LOG.md](docs/DEVELOPMENT_LOG.md) を参照してください。
形式は [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に、バージョン番号は [Semantic Versioning](https://semver.org/lang/ja/) に従います(詳細は [DEVELOPMENT_GUIDELINES §7](docs/DEVELOPMENT_GUIDELINES.md#7-バージョン管理))。

## [Unreleased]

### Added
- P1-0:共通部分(ツール・許可リスト・トレース・評価ハーネス)と Track A / B の雛形、CLI、単体試験 16 件、手順書 P1-0_SETUP(LOG-20261117-01)
- ADR-0012(2 方式の比較)、P1-0(共通基盤)と Issue #6、Phase 1 計画に Track A / B の比較設計(LOG-20261116-06)
- ADR-0010(Python + Julia)、ADR-0011(LLM API、提案)、LLM API 比較資料(LOG-20261116-05)
- 手順書 `docs/guides/GITHUB_SETUP_AND_SYNC.md`(GitHub CLI 初期設定と変更の取り込み・公開)(LOG-20261116-04)
- Phase 1 試験計画(5 タスク)、ADR-0008(汎用エージェント優先)、ADR-0009(Phase 1 読み取り専用)、GitHub の Milestone / Issue 作成スクリプト(LOG-20261116-03)

### Changed
- 当面の目標を汎用 AI-Agent に変更し、PROJECT_OVERVIEW・ARCHITECTURE・ROADMAP・OPEN_ISSUES を更新。DEVELOPMENT_GUIDELINES を Decided に(LOG-20261116-03)

### Added(初回)
- リポジトリ管理基盤(README、AGENTS.md、docs 一式、ADR、テンプレート、Issue / PR テンプレート、.gitignore)を追加(LOG-20261116-02)

## [0.0.0] - 2026-11-16
- Initial commit(`c325ddb`):README.md のみ
