# TECH_STACK — 技術選定

最終更新: 2026-11-16

> 採用済みの技術と候補技術を明確に分けて記載します。候補技術は **「名前を挙げただけ」で、適合性は未調査** です。採用時は ADR を作成し、この表を更新してください。

## 1. 採用済み(Confirmed / Decided)

| 分野 | 技術 | ラベル | 理由・備考 |
|------|------|--------|-----------|
| バージョン管理 | Git + GitHub(`Hiroto-Masaoka/AI-agents-family`) | Confirmed | リポジトリ作成済み。[ADR-0001](DECISIONS/ADR-0001-github-as-knowledge-base.md) |
| ドキュメント | Markdown + Mermaid(図) | Decided | GitHub 上でそのまま表示でき、どの AI も読める |
| 開発支援 AI | Claude(claude.ai、Claude Code) | Confirmed(ドキュメント作成で使用) | 他の AI の利用も可。記録ルールは共通 |
| LLM 実行環境の方針 | 商用 API とローカル(自前計算機)の併用 | Decided(方針のみ) | [ADR-0004](DECISIONS/ADR-0004-hybrid-llm-environment.md) |

## 2. 導入候補(Proposed、未調査)

### 2.1 LLM

| 区分 | 候補 | 比較の観点 |
|------|------|-----------|
| 商用 API | Anthropic(Claude)、OpenAI(GPT)、Google(Gemini) | 推論性能、Tool Calling の安定性、料金、データ取り扱い規約 |
| ローカル LLM の実行ソフト | Ollama、llama.cpp、vLLM | 導入の容易さ、速度、対応 GPU / Apple Silicon |
| ローカル LLM のモデル | Llama 系、Qwen 系、Gemma 系など公開モデル | 日本語能力、Tool Calling 対応、必要メモリ |

**未確認:** 自前計算機の仕様(CPU / GPU / メモリ)。これがローカル LLM の選択肢を決めます。

### 2.2 エージェントの作り方

| 候補 | 特徴 | 初心者にとって |
|------|------|---------------|
| フレームワークを使わず API を直接呼ぶ | 仕組みが全部見える、依存が少ない | **学習目的では最も理解しやすい**(推奨候補) |
| Claude Agent SDK | Claude Code と同じ仕組みでエージェントを作れる | Claude 前提になる |
| OpenAI Agents SDK | OpenAI 系の公式 SDK | OpenAI 前提になる |
| LangGraph | 状態遷移グラフでワークフローを組める、モデル非依存 | 概念が多く学習コスト高め |

### 2.3 ツール接続

| 候補 | 特徴 |
|------|------|
| MCP(Model Context Protocol) | ツールを共通規格で公開し、複数の AI クライアントから再利用できる。汎用化方針と相性が良い |
| 各 SDK の独自 Tool Calling | 実装は簡単だが特定ベンダーに依存しやすい |

### 2.4 ワークフロー・状態・ログ

| 分野 | 候補 | 備考 |
|------|------|------|
| 定時実行 | cron / launchd / systemd timer | 最も単純。最初はこれで十分な可能性 |
| ワークフロー管理 | Prefect、Airflow | 処理が増えてから検討 |
| 状態・メモリ | Markdown/JSON ファイル、SQLite | 最初はファイル、構造化が必要になったら SQLite |
| 時系列データ | PostgreSQL(+TimescaleDB)、InfluxDB | 装置状態の長期保存が必要になったら |
| 監視・可視化 | Prometheus + Grafana | 長期運用フェーズで検討 |

### 2.5 天文・観測関連

| 分野 | 候補 | 備考 |
|------|------|------|
| 突発天体探索 | Heimdall、PRESTO、your、FETCH など既存ツール | 自前の観測データ形式との適合は未確認 |
| 突発現象通知の受信 | VOEvent、GCN など | 追観測フェーズで検討 |
| 天体計算 | Astropy(Python)、AstroLib.jl など(Julia) | 可視判定・座標計算 |
| 装置制御 | **望遠鏡側の制御方式が未確認のため未定** | 最優先の確認事項 |

## 3. 比較検討事項(未決定)

### 3.1 開発言語:Julia か Python か(Proposed)

| | Julia | Python |
|---|---|---|
| 開発者の慣れ | 普段使用している | 未確認 |
| LLM SDK・エージェント関連の公式ライブラリ | 少ない(HTTP で API を直接呼ぶことは可能) | 豊富(各社公式 SDK、MCP SDK) |
| 天文データ処理 | 高速。既存資産があれば活用可 | Astropy など既存ツールが豊富 |

**提案:** エージェント部分(LLM 呼び出し・ツール接続)は SDK が揃う Python、重いデータ処理は Julia で書き、ツールとして呼び出す分担を検討する。→ 決定は保留([OPEN_ISSUES](OPEN_ISSUES.md))。

### 3.2 商用 API とローカル LLM の役割分担(Proposed)

| 処理 | 想定 | 理由 |
|------|------|------|
| 計画立案、原因推定などの難しい判断 | 商用 API | 性能が必要 |
| 定型ログの要約・分類 | ローカル | 量が多くコストを抑えたい |
| 通信断時の最低限の判断 | ローカル | 外部依存を避ける |
| 公開できないデータの処理 | ローカル | データを外部に送らない |

試験で検証してから決定します。
