# DEVELOPMENT_GUIDELINES — 開発管理ルール

最終更新: 2026-11-16 / 状態: **Proposed(ユーザー承認待ち)** — 承認後に Decided へ変更し、DEVELOPMENT_LOG に記録する

方針:**個人開発でも続けられる最小限のルール。** 迷ったら「後から自分(または別の AI)が読んで経緯が分かるか」で判断する。

---

## 1. Git のブランチ運用

| ブランチ | 用途 | ルール |
|---------|------|-------|
| `main` | 常に「読める・動く」状態 | ドキュメントの小さな修正は直接コミットしてよい |
| `feat/<内容>` | 機能の実装 | 例:`feat/status-monitor-tool` |
| `exp/<内容>` | 実験・試行 | 失敗してもよい。結果は必ず `docs/EXPERIMENTS/` に残す |
| `fix/<内容>` | 不具合修正 | 例:`fix/log-timezone` |
| `docs/<内容>` | 大きなドキュメント変更 | 例:`docs/architecture-v2` |

- ブランチは短命に保つ(目安:1 週間以内に main へ取り込むか、記録を残して閉じる)。
- `git push`、`rebase`、`reset --hard`、force push は **ユーザーの明示的な許可なしに AI が実行しない**。
- 失敗した実験ブランチも消さずに残してよい(記録として価値がある)。

## 2. Commit message の規則

形式(Conventional Commits を簡略化):

```
<type>: <要約(日本語可、50 文字程度まで)>

<本文:何を・なぜ(任意、変更が大きいとき)>

Refs: #<Issue 番号> / LOG-YYYYMMDD-NN
AI-Assisted: <ツール名 (モデル名)>   ← AI が関与した場合
```

| type | 用途 |
|------|------|
| `feat` | 新機能 |
| `fix` | 不具合修正 |
| `docs` | ドキュメントのみ |
| `exp` | 実験コード・実験記録 |
| `test` | 試験の追加・修正 |
| `refactor` | 動作を変えない整理 |
| `chore` | 設定・雑務 |

例:

```
docs: リポジトリ管理基盤を整備

README、AGENTS.md、docs 一式、ADR、テンプレートを追加。

Refs: LOG-20261116-02
AI-Assisted: Claude (claude-opus-5-5)
```

## 3. Pull Request の運用

- 個人開発のため **必須ではない**。
- 次の場合は PR を作る:`feat/` ブランチの取り込み、装置操作に関わる変更、AI が大量に生成したコードの取り込み。PR 本文が「自己レビューの記録」になる。
- テンプレート:`.github/pull_request_template.md`

## 4. Issue によるタスク管理

| ラベル | 用途 |
|--------|------|
| `type:task` | 作業 |
| `type:bug` | 不具合 |
| `type:experiment` | 実験・試験 |
| `type:question` | 未確認事項・調査 |
| `type:idea` | 改善案・将来構想 |
| `phase:0` 〜 `phase:7` | ROADMAP のフェーズ |
| `safety` | 装置操作・安全性に関わる |

- 状態管理は GitHub 標準の Open / Closed のみ(ボードは任意)。
- Milestone = ROADMAP のフェーズ。
- Issue を閉じるときは、結果を 1〜2 行書き、関連する LOG / 実験記録 / ADR へリンクする。
- テンプレート:`.github/ISSUE_TEMPLATE/`
- **オフラインでも AI が読めるように**、未解決の重要事項は `docs/OPEN_ISSUES.md` にも要約を置く(Issue 番号を併記)。

## 5. ドキュメントの更新ルール

| こんなとき | 更新するドキュメント |
|-----------|---------------------|
| 作業をした(毎回) | `DEVELOPMENT_LOG.md` に 1 エントリ追記 |
| 実験・試験をした | `EXPERIMENTS/EXP-*.md` を作成 + LOG にリンク |
| 重要な技術判断をした | `DECISIONS/ADR-*.md` を作成 + LOG にリンク |
| 技術を採用・却下した | `TECH_STACK.md` + ADR |
| フェーズの状態・計画が変わった | `ROADMAP.md`、`README.md` の状況表 |
| 構成が変わった | `ARCHITECTURE.md` |
| 問題を解決した | `TROUBLESHOOTING.md` |
| 一般化できる教訓を得た | `KNOWLEDGE.md` |
| 未確認事項が出た / 解消した | `OPEN_ISSUES.md` |
| 新しい用語が出た | `GLOSSARY.md` |
| リリースした | `CHANGELOG.md` |

### 書き換えてよいもの・いけないもの

| 種類 | ファイル | ルール |
|------|---------|-------|
| **現在の状態を表す文書** | README、OVERVIEW、ARCHITECTURE、TECH_STACK、ROADMAP、GUIDELINES、OPEN_ISSUES | 最新状態に更新してよい。変更理由は LOG に書く(履歴は Git に残る) |
| **記録** | DEVELOPMENT_LOG、ADR、EXPERIMENTS、PROMPTS | **追記のみ。** 誤りは新エントリで訂正し、元の箇所に「→ LOG-xxxx で訂正」と注記。ADR を覆すときは新しい ADR を作り、旧 ADR の Status を `Superseded by ADR-xxxx` にする |

### 記述の原則

- 信頼性ラベル(Confirmed / Decided / Proposed / Planned / Unverified)を付ける。
- 専門用語は初出時に説明、または GLOSSARY にリンク。
- 結論だけでなく、背景・比較した選択肢・理由を残す。
- 図は Mermaid を使う(GitHub 上で表示される)。

## 6. 実験・試験結果の記録方法

- 1 実験 = 1 ファイル:`docs/EXPERIMENTS/EXP-YYYYMMDD-<短い名前>.md`
- テンプレート:`docs/templates/EXPERIMENT.md`
- **失敗した実験も必ず記録する**(何がうまくいかなかったかが最も価値のある知見)。
- 実験に使ったコード・設定のコミットハッシュ、LLM のモデル名とバージョン、プロンプトを記録する(再現性のため)。
- 大きな生データはリポジトリに入れず、保存場所を記載する。

## 7. バージョン管理

- Semantic Versioning(`MAJOR.MINOR.PATCH`)。開発初期は `0.x.y`。
- 目安:**ROADMAP のフェーズ完了ごとに MINOR を上げてタグを付ける**(Phase 1 完了 → `v0.1.0`)。修正は PATCH。
- `1.0.0` は「実観測の日常運用に使える」状態になったときに検討する。
- タグ付け・リリース時に `CHANGELOG.md` を更新する。

## 8. 機密情報の扱い

- API キー、パスワード、トークン、個人情報、非公開の観測装置アクセス情報はコミットしない。
- ローカルでは `.env` に置く(`.gitignore` 済み)。必要な変数名だけを `.env.example` に書く。
- 誤ってコミットした場合:**push 前なら** コミットを修正。**push 後なら、そのキーを直ちに無効化(再発行)** する(履歴から消すだけでは不十分)。

## 9. 未解決課題の管理

- 未確認事項・未解決課題・改善案は `docs/OPEN_ISSUES.md` に ID(`Q-xx` 未確認、`I-xx` 課題、`P-xx` 改善案)を付けて管理し、GitHub Issue と対応させる。
- 解消したら削除せず「解消済み」セクションへ移動し、解消した LOG へリンクする。

## 10. AI によるコード生成・修正の記録方法

AI(Claude Code、ChatGPT など)が関与した作業は、次の 3 か所で追跡できるようにする。

1. **コミット**:`AI-Assisted:` トレーラー(Claude Code は `Co-Authored-By:` も付く)。
2. **DEVELOPMENT_LOG のエントリ**:「AI 利用の記録」欄に以下を書く。
   - 使用ツール・モデル
   - AI に依頼した内容(要約。重要な指示文は `docs/PROMPTS/` に保存してリンク)
   - AI が生成・変更したファイル
   - **人間が確認した範囲 / 確認していない範囲**
   - AI の提案を採用しなかった点とその理由
3. **重要な指示文の保存**:`docs/PROMPTS/YYYY-MM-DD_<内容>.md`(機密情報は除く)。

> 原則:**AI が生成したものは、人間(またはテスト)が確認するまで Unverified。**
