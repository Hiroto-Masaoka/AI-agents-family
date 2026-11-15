# AGENTS.md — このリポジトリで作業する AI への指示

このファイルは、Claude・ChatGPT・Codex など **どの AI がこのリポジトリで作業しても** 同じ前提・同じルールで開発を継続できるようにするためのものです。人間の開発者も同じルールに従います。

## 1. 最初に読むもの(この順番で)

1. `README.md`:現在の状態
2. `docs/PROJECT_OVERVIEW.md`:目的と方針
3. `docs/ROADMAP.md`:今どのフェーズか
4. `docs/DEVELOPMENT_LOG.md` の **最新 3 件**:直近の経緯
5. `docs/OPEN_ISSUES.md`:未確認事項(ここにあることを事実として扱わない)
6. 作業に関係する `docs/DECISIONS/ADR-*.md`

## 2. 絶対に守ること

- **推測を事実として書かない。** 情報には必ず信頼性ラベル(Confirmed / Decided / Proposed / Planned / Unverified)を付ける。分からないことは「未確認」と書き、`docs/OPEN_ISSUES.md` に追加する。
- **構想と実装済みを混同しない。** 実装・試験で確認していない機能を「できる」と書かない。
- **過去の記録を書き換えない。** `DEVELOPMENT_LOG.md`・ADR・実験記録は追記のみ。誤りは新しいエントリで訂正し、元の記述には「→ LOG-xxxx で訂正」と注記する。
- **機密情報(API キー、パスワード、トークン、個人情報)をファイルに書かない。**
- **履歴の書き換え(rebase / reset --hard / force push)とファイル削除は、ユーザーの明示的な許可なしに行わない。** commit・push・Issue / Milestone の作成は許可済み(2026-11-16、DEVELOPMENT_GUIDELINES §1)。
- **Phase 1 のエージェントには書き込み能力を与えない**(ADR-0009)。
- **観測装置を実際に動かすコードを、ユーザーの承認なしに実行しない。**(将来の実装時の原則)
- 既存のソースコード・設定ファイルを、依頼範囲を超えて変更しない。

## 3. 作業の進め方

1. 作業前に、対応する GitHub Issue(なければ作業目的)を確認する。
2. 小さく変更し、試験し、結果を記録する。
3. 作業の終わりに、`docs/templates/DEV_LOG_ENTRY.md` の形式で `docs/DEVELOPMENT_LOG.md` に 1 エントリ追記する。必ず **AI 利用の記録** 欄を埋める。
4. 実験・試験をしたら `docs/EXPERIMENTS/` に記録を作る。
5. 重要な技術判断をしたら `docs/DECISIONS/` に ADR を作る(提案段階なら Status: Proposed)。
6. コミットメッセージは `docs/DEVELOPMENT_GUIDELINES.md` §2 に従い、AI が関与した場合はトレーラーを付ける。

## 4. 書き方

- 日本語で書く。コード・コマンド・識別子は英語のまま。
- 専門用語は初出時に一言説明するか、`docs/GLOSSARY.md` にリンクする。新しい用語は GLOSSARY に追加する。
- 結論だけでなく「なぜそうしたか」「他に何を検討したか」を残す。
- 日付は `YYYY-MM-DD`(JST)。
