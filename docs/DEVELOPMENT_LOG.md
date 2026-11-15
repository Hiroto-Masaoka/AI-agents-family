# DEVELOPMENT_LOG — 開発ログ

開発・議論・意思決定・実装・試験の経緯を **時系列(古い順)** に記録します。

- **追記のみ。** 過去のエントリは書き換えない。訂正は新しいエントリで行い、元のエントリに「→ LOG-xxxx で訂正」と注記する。
- 新しいエントリは [templates/DEV_LOG_ENTRY.md](templates/DEV_LOG_ENTRY.md) をコピーしてファイル末尾に追加する。
- ID 形式:`LOG-YYYYMMDD-NN`(同日の通し番号)

## 目次

| ID | 日付 | 概要 | 種別 |
|----|------|------|------|
| [LOG-20261113-01](#log-20261113-01) | 2026-11-13 | AI-Agent family 構想の開始と公開情報の調査、Agent Family Kit v0.1 作成 | 議論・調査 |
| [LOG-20261116-01](#log-20261116-01) | 2026-11-16 | GitHub リポジトリ作成(Initial commit) | 作業 |
| [LOG-20261116-02](#log-20261116-02) | 2026-11-16 | リポジトリ管理基盤の設計とドキュメント整備 | 作業・設計 |
| [LOG-20261116-03](#log-20261116-03) | 2026-11-16 | 管理方針の承認、優先順位の変更(汎用エージェント優先)、Phase 1 試験計画 | 意思決定・設計 |

---

## LOG-20261113-01

**日付:** 2026-11-13 / **種別:** 議論・調査 / **関連:** [references/agent-family-playbook.md](references/agent-family-playbook.md)

### 1. 何を実現しようとしたか
複数の AI モデルで構成される「AI-Agent family」を作り、研究を効率化する構想の第一歩として、公開されているベストプラクティスを集め、誰でもエージェント家族を作って最適化できる環境・手引きを作ること。

### 2. なぜ必要だったか
研究の効率を上げて本来の関心に集中し、ブレークスルーにつなげるため(開発者の発言、Decided)。AI-Agent 開発が初めてのため、まず世界の試行錯誤の結果を学ぶ必要があった。

### 3. 採用した技術・手法
claude.ai(Claude)による Web 調査と文書作成。

### 4. 実装・変更内容
claude.ai 上で「Agent Family Kit v0.1」(zip)を作成し、開発者に提供:
- PLAYBOOK(12 の設計原則、役割、最適化ループ、成熟度段階、出典付き)
- Claude Code 用テンプレート(researcher / builder / verifier / scribe のサブエージェント定義、指示書テンプレート、設定例、評価表)
- family-architect エージェント定義
- 分野別プリセット(電波天文、Web、ゲーム、資産管理)

PLAYBOOK は claude.ai Project「AI-agent family」の資料にも保存。本リポジトリには参考資料として PLAYBOOK を収録した(LOG-20261116-02)。

### 5. 試験内容
なし。

### 6. 試験結果
なし。**Kit のテンプレート類は実際の開発で使用・検証していない(Unverified)。**

### 7. 問題と原因
なし。

- AI のリモート操作から `.github/` への書き込みが保護されており失敗した。Issue / PR テンプレートは `docs/templates/github/` に仮置きした。→ 同日、クラウド側の作業コピーで `.github/` へ移動して初回コミットに含めた(LOG-20261116-03)。

### 8. 得られた知見(公開情報からの知見。本プロジェクトでは未検証)
- エージェント数を増やすほど調整コストが非線形に増える。まず 1〜3 個から始めるのがよい。
- マルチエージェントが有効なのは、並列化・情報の分離・独立した検証が必要な場合。
- 守らせたいルールは指示文ではなくプログラム(権限設定・フック)で強制する。
- 科学分野のエージェントは「計画」より「実行と検証」が弱い。検証役と既知解のある試験が重要。

### 9. 次に実施すること
目的を具体化する(→ 2026-11-16 に「自前の電波望遠鏡の観測運用」を最初の対象とすることを提示)。

### AI 利用の記録
- ツール:claude.ai(Claude Opus 5.5)
- 依頼内容:公開情報の調査と、エージェント家族構築のための手引き・テンプレート作成
- 生成物:Agent Family Kit v0.1(本リポジトリには PLAYBOOK のみ収録)
- 人間の確認:**未確認**(開発者による内容レビューの有無は記録なし)

---

## LOG-20261116-01

**日付:** 2026-11-16(00:40 JST) / **種別:** 作業 / **関連:** commit `c325ddb`

### 1〜2. 何を・なぜ
開発の中心的なナレッジベースとして GitHub リポジトリ `Hiroto-Masaoka/AI-agents-family` を作成(Confirmed:Git 履歴で確認)。

### 4. 実装・変更内容
Initial commit(README.md にタイトル 1 行のみ)。

### 5〜8.
試験なし、問題なし。

### 9. 次に実施すること
管理方針とドキュメント基盤の整備(→ LOG-20261116-02)。

---

## LOG-20261116-02

**日付:** 2026-11-16 / **種別:** 作業・設計 / **関連:** [PROMPTS/2026-11-16_repository-setup-mission.md](PROMPTS/2026-11-16_repository-setup-mission.md)、ADR-0001〜0007

### 1. 何を実現しようとしたか
今後どの AI を使って開発しても、このリポジトリを読めばプロジェクトの背景・設計思想・実装・試験結果・課題を正確に理解して開発を続けられる状態にすること。

### 2. なぜ必要だったか
AI-Agent 開発は初めてで、AI との対話で議論や判断が散逸しやすいため。初心者が後から経緯を追える記録が必要(開発者の要望、Decided)。

### 3. 採用した技術・手法
- Markdown + Mermaid によるドキュメント
- 「現在の状態を表す文書(更新可)」と「記録(追記のみ)」の分離
- ADR(Architecture Decision Record)による意思決定の記録
- 5 段階の信頼性ラベル
- ベンダー非依存の AI 向け指示ファイル `AGENTS.md`(+ Claude Code 用 `CLAUDE.md` は参照のみ)

### 4. 実装・変更内容
- 現状調査:リポジトリは README.md(1 行)のみ、ブランチは `main`、作業ツリーはクリーン、remote は `origin`(GitHub)。既存のコード・設定ファイルなし。→ 既存情報との重複・矛盾なし。
- 作成:README.md(既存のタイトルを維持して拡充)、AGENTS.md、CLAUDE.md、CHANGELOG.md、.gitignore、docs/ 一式、ADR-0001〜0007、テンプレート、Issue / PR テンプレート、src/README.md。
- 既存ファイルの削除・コードの変更:なし。
- **コミット・push:未実施**(ユーザーの確認待ち)。

### 5. 試験内容
ドキュメントの検証:Markdown 内の相対リンクの存在確認(スクリプトで全リンクを検査)、実装済み/構想の表記の確認。

### 6. 試験結果
- 相対リンク検査:全ファイルでリンク切れ 0 件(Confirmed、2026-11-16 スクリプトで確認)。
- 実装済み機能を記載していないこと、構想に Planned / Proposed を付けていることを目視で確認(Confirmed)。
- GitHub 上での Mermaid 図の表示:未確認(push 前のため)。

### 7. 問題と原因
- ミッション文書が言及する「これまでの議論」(プロジェクト構想 A、ロードマップ B、技術アーキテクチャ C)の **元の会話は本作業の AI から参照できなかった**。そのため、ミッション文書に書かれた内容と 2026-11-13 の会話のみを情報源とし、それ以外は未確認として [OPEN_ISSUES](OPEN_ISSUES.md) に記載した。

### 8. 得られた知見
- 議論の結論は、会話の中だけでなく早い段階でリポジトリに書き出さないと、別の AI セッションから参照できない(→ [KNOWLEDGE K-01](KNOWLEDGE.md))。

### 9. 次に実施すること
1. ユーザーによる内容確認と DEVELOPMENT_GUIDELINES の承認
2. 初回コミット(許可後)
3. OPEN_ISSUES の Q-01〜Q-04 への回答
4. Phase 1 の Issue / Milestone 作成

### AI 利用の記録
- ツール:Claude(claude.ai から Claude Code 環境で作業、モデル claude-opus-5-5)
- 依頼内容:[PROMPTS/2026-11-16_repository-setup-mission.md](PROMPTS/2026-11-16_repository-setup-mission.md)
- 生成物:本エントリ §4 のファイル一式(すべて AI 生成)
- 人間の確認:**未確認**(ユーザーのレビュー待ち)
- 採用しなかった案:ディレクトリを細かく分ける案(知見・課題・トラブルを個別フォルダにする)は、初心者の分かりやすさと運用負荷を優先して単一ファイルにした。

---

## LOG-20261116-03

**日付:** 2026-11-16 / **種別:** 意思決定・設計 / **関連:** [ADR-0008](DECISIONS/ADR-0008-general-purpose-agents-first.md)、[ADR-0009](DECISIONS/ADR-0009-phase1-read-only-policy.md)、[PHASE1_TEST_PLAN](EXPERIMENTS/PHASE1_TEST_PLAN.md)、`scripts/github/`

### 1. 何を実現しようとしたか
(a) 管理方針の承認を反映する。(b) 当面の開発目標を、望遠鏡の運用自動化から「日常業務・研究を支援する汎用エージェント」に変更する。(c) Phase 1(Read-Only Monitoring)の 5 タスクを定義し、GitHub の Milestone・Issue として管理を始める。

### 2. なぜ必要だったか
開発者の指示(2026-11-16):
- 提案したリポジトリ構成・テンプレート・Git 管理規則を承認。AI による整理・文書更新・commit・push・Issue / Milestone 管理を許可。
- 当面は、実際の業務と研究に役立つエージェントを作りながら、エージェントの構成・ツール連携・メモリ・ワークフロー・マルチエージェント協調・評価の実践経験を積みたい。望遠鏡の仕様・制御方式の確認は、将来の観測所運用システムの開発まで不要。
- Phase 1 は厳密に読み取り専用(ファイル変更・システム変更・外部への書き込みなし)。

### 3. 採用した技術・手法
- 5 タスクを「新しく学ぶ要素を 1〜2 個ずつ増やす」順に配置(最小ループ → 外部 API → 構造化データ → MCP・ワークフロー → マルチエージェント+評価)。
- 各タスクに数値の合格基準を設定し、正解が独立に確認できる題材を選んだ(リポジトリ文書、実在確認できる論文 ID、独立に計算した数値、人手で作った正解一覧、公式ページ)。
- Read-Only はツールを与えないことで強制し、SHA-256 一覧の前後比較で検証する(ADR-0009)。

### 4. 実装・変更内容
- 初回のドキュメント基盤(LOG-20261116-02 の内容)をコミット(`.github/` テンプレートは正規の場所に配置)。
- 新規:ADR-0008、ADR-0009、`docs/EXPERIMENTS/PHASE1_TEST_PLAN.md`、`scripts/github/setup_phase1.sh`、`scripts/github/issues/*.md`(Issue 本文 5 件)。
- 更新:README、AGENTS.md、CLAUDE.md、PROJECT_OVERVIEW、ARCHITECTURE(当面の構成 §2 を追加、望遠鏡向けは将来構想へ)、ROADMAP(フェーズを再編)、DEVELOPMENT_GUIDELINES(Decided に変更、priority / read-only ラベル追加、push 許可を反映)、OPEN_ISSUES(望遠鏡関連を保留へ)、TECH_STACK、GLOSSARY、DECISIONS/README、ADR-0003(Status を Superseded に変更。本文は当時のまま)、EXPERIMENTS/README、KNOWLEDGE、TROUBLESHOOTING、CHANGELOG、src/README。

### 5. 試験内容
- Markdown の相対リンク検査、スクリプトの構文検査(`bash -n`)。
- GitHub への書き込み(ラベル作成、push)の試行。

### 6. 試験結果
- リンク切れ 0 件、スクリプト構文 OK(Confirmed)。
- **GitHub への書き込みは失敗**:クラウド側の AI セッションからの API 書き込み(ラベル作成)は `HTTP 403: Resource not accessible by integration`、push も権限不足で拒否。開発者の Mac 側シェルからは github.com に接続できなかった(T-02)。
- そのため Milestone・Issue は未作成。push と作成は開発者の Mac から実行する(OPEN_ISSUES I-02、I-03)。

### 7. 問題と原因
- 原因:このセッションの GitHub 連携に、対象リポジトリへの書き込み権限が付与されていない(Claude GitHub App が未インストール、または未リンク)。読み取りは可能。(Confirmed:エラーメッセージより)

### 8. 得られた知見
- AI に push や Issue 作成を任せるには、許可の意思表示とは別に、AI 側の GitHub 連携に書き込み権限が必要(→ KNOWLEDGE K-02)。

### 9. 次に実施すること
1. 開発者の Mac で push し、`scripts/github/setup_phase1.sh` を実行(I-02、I-03)
2. 作成された Issue 番号を ROADMAP・OPEN_ISSUES に追記(I-05)
3. Q-05(LLM API)と Q-06(開発言語)を決め、P1-1 に着手

### AI 利用の記録
- ツール:Claude(claude-opus-5-5、claude.ai から Claude Code 環境で作業)
- 依頼内容:開発者のメッセージ(2026-11-16 01:08 JST)の Next Actions 1〜4
- 生成物:§4 のファイル一式(すべて AI 生成)
- 人間の確認:管理方針は開発者が承認済み。本エントリで追加した Phase 1 計画・ADR-0008/0009 の文面は **未確認**(開発者のレビュー待ち)
- 採用しなかった案:定期実行(cron 等)を P1-4 に含める案は、OS 設定の変更にあたるため Phase 3 に回した。申請書作成支援は書き込みを伴うため Phase 2 に回した。
