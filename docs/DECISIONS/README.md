# DECISIONS — 技術的意思決定の記録(ADR)

ADR(Architecture Decision Record)は、重要な判断を「背景・選択肢・決定・理由・トレードオフ」の形で 1 件 1 ファイルで残す記録です。**後から「なぜこうなっているのか」を知るため** に書きます。

- ファイル名:`ADR-NNNN-<短い英語名>.md`(番号は通し)
- テンプレート:[../templates/ADR.md](../templates/ADR.md)
- Status:`Proposed`(提案)→ `Decided`(決定)→ 必要なら `Superseded by ADR-xxxx`(置き換え)/ `Rejected`(却下)
- **決定済みの ADR は書き換えない。** 判断を変えるときは新しい ADR を作る。

## 一覧

| ADR | タイトル | Status | 日付 |
|-----|---------|--------|------|
| [0001](ADR-0001-github-as-knowledge-base.md) | GitHub リポジトリを開発の中心的なナレッジベースにする | Decided | 2026-11-16 |
| [0002](ADR-0002-incremental-development.md) | 小さく実装・試験・評価を繰り返す段階的開発 | Decided | 2026-11-16 |
| [0003](ADR-0003-first-target-daily-operations.md) | 最初の目標を日常的な観測運用の自動化とする | Superseded by ADR-0008 | 2026-11-16 |
| [0004](ADR-0004-hybrid-llm-environment.md) | LLM 実行環境は商用 API と自前計算機を併用する | Decided(方針)/ 具体構成は未定 | 2026-11-16 |
| [0005](ADR-0005-reliability-labels.md) | 情報を 5 段階の信頼性ラベルで分類する | Decided | 2026-11-16 |
| [0006](ADR-0006-human-in-the-loop-safety.md) | 観測装置の操作は人間の承認を前提に段階的に自動化する | Proposed | 2026-11-16 |
| [0007](ADR-0007-start-with-single-agent.md) | 単一エージェントから始め、必要が示されてから分割する | Proposed | 2026-11-16 |
| [0008](ADR-0008-general-purpose-agents-first.md) | 当面は汎用 AI-Agent を優先し、望遠鏡固有の開発は延期する | Decided | 2026-11-16 |
| [0009](ADR-0009-phase1-read-only-policy.md) | Phase 1 のエージェントは厳密に読み取り専用とし、プログラム側で強制する | Decided(強制方法の詳細は Proposed) | 2026-11-16 |
| [0010](ADR-0010-python-agents-julia-compute.md) | エージェント部分は Python、重い計算は Julia で書く | Decided(連携方式は Proposed) | 2026-11-16 |
| [0011](ADR-0011-phase1-llm-api.md) | Phase 1 で使う商用 LLM API | Proposed | 2026-11-16 |
