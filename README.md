# AI-agents-family

日々の研究・業務を支援する AI-Agent(AI エージェント)を、小さく作って試し、評価しながら段階的に育てていくためのリポジトリです。
当面はコーディング、文献調査、データ分析、定型作業、研究資金の公募調査などの汎用エージェントで経験を積み([ADR-0008](docs/DECISIONS/ADR-0008-general-purpose-agents-first.md))、将来は自前の電波望遠鏡の観測運用や X 線衛星などにも応用できる設計思想とノウハウの蓄積を目指します。

> **AI エージェントとは?** 大規模言語モデル(LLM)が、与えられた目的に向かって「考える → ツールを使う → 結果を見る」を繰り返しながら作業を進める仕組みです。詳しくは [用語集](docs/GLOSSARY.md) を参照してください。

## 現在の開発状況(2026-11-16 時点)

| 項目 | 状態 | 信頼性ラベル |
|------|------|-------------|
| リポジトリ作成(Initial commit `c325ddb`) | 完了 | Confirmed |
| 管理方針・ドキュメント基盤の整備 | 完了(開発者承認済み) | Confirmed |
| Phase 1 試験計画(5 タスク) | 作成済み([計画](docs/EXPERIMENTS/PHASE1_TEST_PLAN.md))、[Milestone](https://github.com/Hiroto-Masaoka/AI-agents-family/milestone/1) と Issue #1〜#5 を作成 | Confirmed |
| P1-0 共通基盤と 2 方式(Track A / B)の雛形 | 実装済み(LLM なしの試験 16 件に合格)。実機での動作確認は未実施 | Confirmed(単体試験)/ Unverified(実機) |
| 試験・評価 | **未実施** | — |

現在は **Phase 1(Read-Only Monitoring)** の準備段階です。詳細は [ROADMAP](docs/ROADMAP.md) と [開発ログ](docs/DEVELOPMENT_LOG.md) を参照してください。

## 信頼性ラベル

すべてのドキュメントで、情報に次のラベルを付けます。

| ラベル | 意味 |
|--------|------|
| **Confirmed** | 実装・試験などで確認済み |
| **Decided** | 方針として決定済み |
| **Proposed** | 提案・検討中 |
| **Planned** | 今後実施予定 |
| **Unverified** | 未検証・未確認 |

## はじめて読む人へ(推奨する読む順番)

1. [PROJECT_OVERVIEW](docs/PROJECT_OVERVIEW.md):なぜ、何を作るのか
2. [GLOSSARY](docs/GLOSSARY.md):用語集(AI-Agent の基礎用語)
3. [BASICS](docs/BASICS.md):AI-Agent の基礎知識
4. [ARCHITECTURE](docs/ARCHITECTURE.md):システム構成(構想段階)
5. [ROADMAP](docs/ROADMAP.md):開発の段階と完了条件
6. [DEVELOPMENT_LOG](docs/DEVELOPMENT_LOG.md):これまでの経緯
7. [OPEN_ISSUES](docs/OPEN_ISSUES.md):未確認事項・未解決課題

**GitHub の初期設定や、AI が作った変更の取り込み方** は [手順書](docs/guides/GITHUB_SETUP_AND_SYNC.md) を参照してください。

**AI(Claude、ChatGPT など)で開発を続ける場合**は、最初に [AGENTS.md](AGENTS.md) を読ませてください。

## ディレクトリ構成

```
AI-agents-family/
├── README.md                 ← 入口(このファイル)
├── AGENTS.md                 ← AI に最初に読ませる作業ルール(ベンダー非依存)
├── CLAUDE.md                 ← Claude Code 用。AGENTS.md を参照するだけ
├── CHANGELOG.md              ← リリース(バージョン)単位の変更履歴
├── .gitignore                ← 機密情報をコミットしないための設定
├── .github/                  ← Issue / Pull Request のテンプレート
├── docs/
│   ├── PROJECT_OVERVIEW.md   ← 背景・最終目標・開発方針・対象システム
│   ├── BASICS.md             ← AI-Agent の基礎知識・技術解説
│   ├── GLOSSARY.md           ← 用語集
│   ├── ARCHITECTURE.md       ← システム構成(現状と将来構想を区別)
│   ├── TECH_STACK.md         ← 採用済み技術 / 候補技術 / 比較
│   ├── ROADMAP.md            ← 開発フェーズ・完了条件・優先順位
│   ├── DEVELOPMENT_GUIDELINES.md ← Git・Commit・Issue・ドキュメント・ログの規則
│   ├── DEVELOPMENT_LOG.md    ← 開発・議論・意思決定・試験の時系列記録(追記のみ)
│   ├── KNOWLEDGE.md          ← 開発で得られた知見(教訓)集
│   ├── TROUBLESHOOTING.md    ← 問題と解決方法の記録
│   ├── OPEN_ISSUES.md        ← 未確認事項・未解決課題・改善案
│   ├── DECISIONS/            ← 技術的意思決定の記録(ADR)
│   ├── EXPERIMENTS/          ← 個別の実験・試験記録
│   ├── PROMPTS/              ← AI に与えた重要な指示文の保存
│   ├── guides/               ← 手順書(Wiki)
│   ├── references/           ← 外部情報から集めた参考資料
│   └── templates/            ← 各種記録のテンプレート
├── evals/                    ← 試験課題(JSON)
├── pyproject.toml            ← Python パッケージ定義(pip install -e ".[all]")
├── scripts/github/           ← GitHub の Milestone・Issue 作成スクリプト
└── src/                      ← ソースコード(現時点では未実装)
```

## 機密情報について

API キー・パスワード・アクセストークンは **絶対にコミットしない** でください。`.env` などはすでに `.gitignore` で除外しています。ルールは [DEVELOPMENT_GUIDELINES §8](docs/DEVELOPMENT_GUIDELINES.md#8-機密情報の扱い) を参照してください。
