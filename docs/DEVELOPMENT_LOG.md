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
| [LOG-20261116-04](#log-20261116-04) | 2026-11-16 | push・Milestone / Issue 作成の完了、同期スクリプトの不具合修正、手順書の作成 | 作業・障害 |
| [LOG-20261116-05](#log-20261116-05) | 2026-11-16 | 開発言語の決定(Python + Julia)、商用 LLM API の比較と提案 | 意思決定・調査 |
| [LOG-20261116-06](#log-20261116-06) | 2026-11-16 | Pro 枠(Agent SDK)と API 直接の 2 方式で比較する構成に決定、P1-0 追加 | 意思決定・設計 |
| [LOG-20261116-07](#log-20261116-07) | 2026-11-16 | Track B の月の予算上限を 30 USD に決定 | 意思決定 |
| [LOG-20261117-01](#log-20261117-01) | 2026-11-17 | P1-0:共通部分と Track A / B の雛形を実装 | 実装 |
| [LOG-20261124-01](#log-20261124-01) | 2026-11-24 | Claude Code セッション用の読み取り専用 hook を追加(有効化はせず例として配置) | 実装 |

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

---

## LOG-20261116-04

**日付:** 2026-11-16 / **種別:** 作業・障害 / **関連:** [手順書](guides/GITHUB_SETUP_AND_SYNC.md)、[T-03](TROUBLESHOOTING.md)、[T-04](TROUBLESHOOTING.md)、[Milestone #1](https://github.com/Hiroto-Masaoka/AI-agents-family/milestone/1)、Issue #1〜#5

### 1. 何を実現しようとしたか
LOG-20261116-03 でローカルにコミットした内容を GitHub に公開し、Phase 1 の Milestone・Issue を作成すること。あわせて、その手順を初めての人向けの手順書にすること。

### 2. なぜ必要だったか
AI の作業環境に GitHub の書き込み権限がなく(T-02)、開発者の Mac から実行する必要があった。同じ作業を今後も繰り返す可能性があるため、手順を残す。

### 3. 採用した技術・手法
git bundle によるコミットの受け渡し、`git stash` による未コミット変更の退避、`git pull --ff-only`(履歴を書き換えない取り込み)、GitHub CLI(`gh`)。

### 4. 実装・変更内容
- 開発者が `gh auth login` を実行(ブラウザ方式を途中で中断し、トークン方式でログイン。SSH 鍵は登録済み)。
- `apply_and_push.sh` の 1 回目は失敗(T-03)。AI が Mac 上のスクリプトを修正し、一時コピーで退避・取り込みの部分を試験。
- 2 回目で成功:stash 退避 → fast-forward(`c325ddb..c2dc48e`、46 files)→ push → ラベル 18 種・Milestone・Issue #1〜#5 作成。
- 本エントリのコミットで追加・更新:`docs/guides/`(手順書と索引)、README、ROADMAP(Issue 番号)、OPEN_ISSUES(I-02/03/05 を解消済みへ)、TROUBLESHOOTING(T-03、T-04)、CHANGELOG。

### 5. 試験内容
GitHub API(読み取り)で、コミット・Milestone・Issue の状態を確認。

### 6. 試験結果
- `origin/main` = `c2dc48e`(Confirmed)
- Milestone `Phase 1 - Read-Only Monitoring`(#1)に Issue 5 件、すべて `type:experiment, phase:1, read-only` と優先度ラベル付き(Confirmed)
- スクリプト最後の一覧が 4 件だったのは検索反映の遅延(T-04)
- 本エントリのコミット(`c06ea16`)は **AI セッションから直接 push できた**。ラベルの更新(API 書き込み)も成功。T-02 の状況が変わったため Q-10 を解消済みへ移動(Confirmed)

### 7. 問題と原因
T-03(スクリプトの除外指定の書き方とエラー検知漏れ)。AI がスクリプトを渡す前に、最後まで通しで試験していなかったことが根本原因。

### 8. 得られた知見
- 人に実行してもらうスクリプトは、一時コピーのリポジトリで最後まで通して試験してから渡す(→ KNOWLEDGE K-03)。

### 9. 次に実施すること
1. 開発者による後片付け(`git stash drop`、`_from_claude/` の削除)
2. Q-05(LLM API)と Q-06(開発言語)の決定
3. P1-1(#1)に着手

### AI 利用の記録
- ツール:Claude(claude-opus-5-5)
- 依頼内容:エラーログを確認しての修正、出力ログを参考にした初心者向け手順書の作成
- 生成物:修正版スクリプト、手順書、本エントリと関連文書の更新(すべて AI 生成)
- 人間の確認:スクリプトの実行結果は開発者のログで確認済み。手順書の文面は **未確認**

---

## LOG-20261116-05

**日付:** 2026-11-16 / **種別:** 意思決定・調査 / **関連:** [ADR-0010](DECISIONS/ADR-0010-python-agents-julia-compute.md)、[ADR-0011](DECISIONS/ADR-0011-phase1-llm-api.md)、[比較資料](references/llm-api-comparison-2026-11.md)、Issue [#1](https://github.com/Hiroto-Masaoka/AI-agents-family/issues/1)

### 1. 何を実現しようとしたか
P1-1 に着手するための 2 つの前提(開発言語 Q-06、LLM API Q-05)を決める。

### 2. なぜ必要だったか
どちらも P1-1 の実装に必須(Issue #1 の受け入れ基準に開発言語の ADR を含む)。

### 3. 採用した技術・手法
- Q-06:開発者が決定(エージェントは Python、重い計算は高速処理とメモリ効率のために Julia)。
- Q-05:Web 上の公開情報(公式料金ページと価格比較サイト)を調べ、コスト・正確性・拡張性・柔軟性・学習のしやすさ・データの扱いで 3 社を比較。

### 4. 実装・変更内容
新規:ADR-0010(Decided)、ADR-0011(Proposed)、`docs/references/llm-api-comparison-2026-11.md`。更新:OPEN_ISSUES(Q-06 を解消済みへ、Q-05 に資料をリンク)、TECH_STACK、DECISIONS/README、ROADMAP、src/README。Issue #1 の「開発言語を決めて ADR を作成」にチェック。

### 5〜6. 試験内容と結果
なし(調査のみ)。料金は 2026-11-16 時点の公開情報で、**公式ページでの最終確認は未実施(Unverified)**。Gemini 4 Argon は 11/30 まで、Gemini 3.8 Flash は 12/31 までの導入価格である点に注意。

### 7. 問題と原因
なし。

### 8. 得られた知見
- 3 社とも、中位モデルは同価格帯($2 / $10 前後)に並んでおり、価格だけでは差がつきにくい。差が出るのは、無料枠の有無、キャッシュ割引、内蔵ツールの料金、他の道具との相性(MCP など)。(調査結果。本プロジェクトでは未検証)

### 9. 次に実施すること
1. 開発者が ADR-0011 を判断(採用 API、予算上限)
2. API キーを取得して `.env` に保存し、予算アラートを設定
3. P1-1(#1)の実装開始

### AI 利用の記録
- ツール:Claude(claude-opus-5-5)、Web 検索
- 依頼内容:Q-06 の決定の記録、Q-05 の候補の整理と比較表の作成
- 生成物:§4 のファイル(すべて AI 生成)。比較表の評価(◎○△)は AI による整理で、試験に基づくものではない
- 人間の確認:Q-06 は開発者の決定。比較資料の内容は **未確認**

---

## LOG-20261116-06

**日付:** 2026-11-16 / **種別:** 意思決定・設計 / **関連:** [ADR-0011](DECISIONS/ADR-0011-phase1-llm-api.md)、[ADR-0012](DECISIONS/ADR-0012-dual-track-comparison.md)、[PHASE1_TEST_PLAN §2](EXPERIMENTS/PHASE1_TEST_PLAN.md#2-2-つの実行方式の比較track-a--track-b)、Issue #1〜#6

### 1. 何を実現しようとしたか
Claude Pro の枠内で実装する方式と、API を直接呼ぶ方式の両方で Phase 1 を実装し、比較できる構成にする。

### 2. なぜ必要だったか
開発者の質問「Claude Pro の枠内では実装できないのか」への調査で、Agent SDK と `claude -p` は Pro の利用枠内で使えるが、Messages API の直接呼び出しは従量課金の別契約が必要と分かった(2026-11-16 時点の公式ヘルプ、support.claude.com/en/articles/15036540。2026-06-15 に予定されていた SDK 利用の別枠化は見送られている)。開発者は「両方の実装を比較する構成」を選んだ。

### 3. 採用した技術・手法
- Track A:Claude Agent SDK(Pro アカウントでログイン)
- Track B:Messages API を API キーで直接呼ぶ自作ループ
- 公平な比較のため、変えるのは実行方式だけ(ツール・許可リスト・試験課題・合否判定・トレース・指示文・モデルは共通)

### 4. 実装・変更内容
- 新規:ADR-0012、P1-0(共通基盤と 2 方式の雛形)と Issue #6、`scripts/github/issues/00-p1-0.md`
- 更新:ADR-0011(Status を Decided にし、決定を追記)、PHASE1_TEST_PLAN(§2 比較の設計と指標、各タスクに両方式での実施と比較の合格基準)、ARCHITECTURE、ROADMAP、OPEN_ISSUES(Q-05 を解消、Q-12・Q-13 を追加)、TECH_STACK、比較資料、GLOSSARY、src/README、CHANGELOG
- GitHub:Issue #1〜#5 に比較の受け入れ基準を追加、#6 を作成して Milestone に追加

### 5〜6. 試験内容と結果
なし(設計のみ)。

### 7. 問題と原因
なし。

### 8. 得られた知見
- Claude の「サブスクリプション(Pro)」と「API(従量課金)」は別の契約で、使える経路が違う。プラン内で使えるのは Claude Code・Agent SDK・`claude -p` で、API キーでの直接呼び出しは含まれない(2026-11-16 時点。料金体系は変更されることがあるため、実装時に公式ヘルプを再確認する)

### 9. 次に実施すること
1. Q-12(Track B の予算上限)を開発者が決める
2. P1-0(#6)に着手

### AI 利用の記録
- ツール:Claude(claude-opus-5-5)、Web 検索・公式ヘルプの取得
- 生成物:§4 のファイルと Issue の更新(すべて AI 生成)
- 人間の確認:方針(2 方式の比較)は開発者が決定。文面は未確認

---

## LOG-20261116-07

**日付:** 2026-11-16 / **種別:** 意思決定 / **関連:** [ADR-0012](DECISIONS/ADR-0012-dual-track-comparison.md)、OPEN_ISSUES Q-12、Issue #6

### 1〜2. 何を・なぜ
Track B(API 直接・従量課金)の費用の上限を決める(OPEN_ISSUES Q-12)。

### 3〜4. 決定内容
- 月の予算上限:**30 USD**(開発者決定)。
- 運用:Claude Console 側で上限を設定する(開発者が実施)。上限に近づいたら Track B の実行を止め、その時点までの結果で比較する。
- 参考:Phase 1 全体の費用見込みは Sonnet 5.5 中心で約 60 USD(比較資料 §3、キャッシュなしの試算)。2 か月に分けるか、繰り返し試験に Haiku 5.5 を使えば上限内に収まる見込み(未検証)。

### 5〜8.
試験なし。

### 9. 次に実施すること
P1-0(#6):Console での API キー取得と上限設定(開発者)、共通部分と 2 方式の雛形の実装(AI)。

### AI 利用の記録
- ツール:Claude(claude-opus-5-5)。記録の更新のみ。

---

## LOG-20261117-01

**日付:** 2026-11-17 / **種別:** 実装 / **関連:** Issue [#6](https://github.com/Hiroto-Masaoka/AI-agents-family/issues/6)、ブランチ `feat/p1-0-scaffold`、[src/README](../src/README.md)、[手順書 P1-0_SETUP](guides/P1-0_SETUP.md)

### 1. 何を実現しようとしたか
2 方式で共通に使う部分(ツール、許可リスト、記録形式、評価の入口)と、Track A(Agent SDK・Pro 枠)・Track B(API 直接)の雛形を実装する。

### 2. なぜ必要だったか
P1-1 以降を、実行方式だけを変えて公平に比較するため(ADR-0012)。

### 3. 採用した技術・手法
- 1 つのツール定義(ToolSpec)から、Track B 用の `tools` 定義と Track A 用の SDK ツール(プロセス内 MCP)の両方を生成する。
- 読み取り専用の強制:書き込み系ツールは登録自体を拒否(ToolRegistry)。Track A は組み込みツールを全無効(`tools=[]`)+許可ツールの限定+書き込み系の明示的禁止+利用者設定の非読み込み(`setting_sources=[]`)。
- 許可リスト:`..`・シンボリックリンクによる脱出、`.env`・鍵・`.git` などを拒否。
- トレース:JSON Lines の共通形式(run_start / llm_call / tool_call / run_end)。Track A でもツール呼び出しは同じ関数で記録。
- 費用の安全装置(Track B):1 回の上限と、月 30 USD のローカル記録による上限(Console の上限と二重)。
- Track A では実行中だけ `ANTHROPIC_API_KEY` を環境変数から外し、従量課金ではなく Pro の枠が使われるようにした。
- 外部ライブラリの依存を最小化(Track A / B のライブラリは必要な方式でだけ読み込む)。

### 4. 実装・変更内容
新規:`pyproject.toml`、`.env.example`、`src/agent_family/`(tools / guard / trace / runtimes / eval / cli)、`src/tests/test_scaffold.py`、`evals/p1-0_smoke.json`(3 問:フェーズの確認、ADR の読み取り、`.env` の拒否)、`docs/guides/P1-0_SETUP.md`。更新:src/README、README、OPEN_ISSUES(P-04)、.gitignore、guides/README、CHANGELOG。

### 5. 試験内容
LLM に接続しない単体試験 16 件:許可リスト(脱出・機密・シンボリックリンク)、ツール、Track B のループ(偽の LLM で tool_use → tool_result → 最終回答、ステップ上限、予算超過時に LLM を呼ばないこと、拒否されたツールが失敗として LLM に返ること)、Track A の設定(組み込みツール無効、許可ツール、指示文が共通)と SDK ツールの動作・トレース形式、評価ハーネス(比較表、SHA-256 前後比較)。

### 6. 試験結果
- 16 件すべて合格(Confirmed、AI の作業環境:Python 3.13、claude-agent-sdk 0.2.172)。
- **実際の LLM での動作確認は未実施(Unverified)**:AI の作業環境には開発者の Pro ログインと API キーがないため。開発者の Mac で手順書 §6 を実行して確認する。

### 7. 問題と原因
なし(Track B の `anthropic` パッケージは AI の作業環境に入っておらず導入もできないため、偽の LLM で試験した)。

### 8. 得られた知見
- Claude Agent SDK は、組み込みツールの無効化(`tools=[]`)、自作ツールのプロセス内 MCP 登録、費用上限(`max_budget_usd`)、利用量・費用の報告(ResultMessage)を備えており、Track B と同じ条件・同じ記録形式に揃えられる(SDK 0.2.172 のコードで確認)。

### 9. 次に実施すること
1. 開発者が手順書 P1-0_SETUP に従って環境構築し、`agent-family eval --tracks a,b evals/p1-0_smoke.json` を実行
2. 結果を EXP 記録にし、#6 を完了 → P1-1(#1)へ

### AI 利用の記録
- ツール:Claude(claude-opus-5-5)
- 生成物:§4 のファイル(すべて AI 生成)
- 人間の確認:**未確認**(PR でのレビュー待ち)

---

## LOG-20261124-01

**日付:** 2026-11-24 / **種別:** 実装 / **関連:** ADR-0009、ブランチ `feat/claude-code-readonly-hook`、[evals/scorecard.md](../evals/scorecard.md)

### 1. 何を実現しようとしたか
Claude Code のセッションを「読み取り専用」で動かしたいときに使える PreToolUse hook(ツール実行前に呼ばれ、実行を許可・拒否するスクリプト)を用意する。

### 2. なぜ必要だったか
別の場で整理した AI-agent family の設計メモ(Claude Project の PLAYBOOK v0.2)で、「守らせたい規則は指示文ではなく hook で強制する」方針を採った。ADR-0009 の「読み取り専用」を、Claude Code を調査役として使う場面にも適用できるようにするため。

### 3. 採用した技術・手法
- Claude Code の hook:標準入力でツール呼び出しの JSON を受け取り、終了コード 2 で拒否する。
- 書き込みは許可ディレクトリ(`logs/`、`evals/`、`scratch/`、`wiki/`、`PLAN.md`)のみ。`.claude/` と `CLAUDE.md` は常に書き込み不可(エージェントが自分の防御を弱められないようにする)。
- Bash は正規表現で、削除・外部送信・パッケージ導入・履歴書き換え・許可外へのリダイレクトを拒否。入力を解釈できないときは拒否(fail closed)。
- 比較した選択肢:`permissions.deny` のみ(記述が単純だが、リダイレクトや pipe 先を見られない)。両方の併用を例の設定に入れた。

### 4. 実装・変更内容
新規:`.claude/hooks/block_write.py`、`.claude/settings.readonly.example.json`、`src/tests/test_block_write_hook.py`、`evals/scorecard.md`。更新:CHANGELOG、OPEN_ISSUES(Q-14)、本ログ。
**設定は `.claude/settings.json` ではなく例(`settings.readonly.example.json`)として置いた。** 有効化すると `docs/` や `src/` への通常の開発編集も拒否され、AGENTS.md §3 の作業(開発ログの追記など)ができなくなるため。読み取り専用セッションを作るときだけ `.claude/settings.local.json` にコピーする。
ADR-0009 の対象(エージェントの実行時の行動。ツールを与えないことで強制)とは別の仕組みで、置き換えるものではない。

### 5. 試験内容
LLM に接続しない単体試験 31 件:許可 9 件、拒否 20 件(rm、sudo、git push、パッケージ導入、curl での送信、許可外へのリダイレクト、`.claude/` や CLAUDE.md の編集、パス脱出など)、不正入力で拒否、拒否の記録。

### 6. 試験結果
- 31 件すべて合格、既存の 16 件と合わせて 47 件合格(Confirmed、AI の作業環境:Python 3.13)。
- **実際の Claude Code セッション上での動作確認は未実施(Unverified)**:Q-14 に記録。
- 限界(Confirmed、設計上):正規表現による防御であり、`python -c` や `julia -e` 経由のファイル書き込みは検知できない。無人運転の前には OS レベルの隔離が必要。

### 7. 問題と原因
なし。

### 8. 得られた知見
- 「規則を守らせる仕組み」を開発用のリポジトリに入れるときは、開発作業そのものを止めないよう、既定では無効の例として置く必要がある(当初案は有効化する構成で、リポジトリの既存ルールと衝突していた)。

### 9. 次に実施すること
1. 開発者の環境で `settings.local.json` にコピーし、`rm` が拒否されること、通常の調査(読み取りと `logs/` への追記)が拒否されないことを確認 → Q-14 を解消、`evals/scorecard.md` を更新
2. 無人運転(Phase 4 以降)の前に、コンテナなどの隔離を検討

### AI 利用の記録
- ツール・モデル:Claude Code(claude-sonnet-5-5)
- 依頼内容(要約):読み取り専用 hook の実装、記録、push
- AI が生成・変更したもの:§4 のファイルすべて
- 人間が確認した範囲 / 確認していない範囲:**未確認**(PR または push 後のレビュー待ち)
- 採用しなかった AI の提案と理由:`.claude/settings.json` での有効化(開発編集を止めるため)
