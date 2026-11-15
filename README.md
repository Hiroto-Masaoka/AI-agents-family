# AI-agents-family

天文学研究、特に**自前の電波望遠鏡の観測運用**を支援する AI-Agent(AI エージェント)を、小さく作って試し、評価しながら段階的に育てていくためのリポジトリです。
将来は X 線衛星など他の観測システムにも応用できる、汎用的な設計思想とノウハウの蓄積を目指します。

> **AI エージェントとは?** 大規模言語モデル(LLM)が、与えられた目的に向かって「考える → ツールを使う → 結果を見る」を繰り返しながら作業を進める仕組みです。詳しくは [用語集](docs/GLOSSARY.md) を参照してください。

## 現在の開発状況(2026-11-16 時点)

| 項目 | 状態 | 信頼性ラベル |
|------|------|-------------|
| リポジトリ作成(Initial commit `c325ddb`) | 完了 | Confirmed |
| 管理方針・ドキュメント基盤の整備 | 本コミット候補で作成(ユーザー確認待ち) | Proposed |
| AI-Agent 本体の実装 | **未着手** | — |
| 試験・評価 | **未実施** | — |

現在は **Phase 0(基盤整備)** です。詳細は [ROADMAP](docs/ROADMAP.md) と [開発ログ](docs/DEVELOPMENT_LOG.md) を参照してください。

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
│   ├── references/           ← 外部情報から集めた参考資料
│   └── templates/            ← 各種記録のテンプレート
└── src/                      ← ソースコード(現時点では未実装)
```

## 機密情報について

API キー・パスワード・アクセストークンは **絶対にコミットしない** でください。`.env` などはすでに `.gitignore` で除外しています。ルールは [DEVELOPMENT_GUIDELINES §8](docs/DEVELOPMENT_GUIDELINES.md#8-機密情報の扱い) を参照してください。
