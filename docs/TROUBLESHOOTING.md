# TROUBLESHOOTING — トラブルシューティング

発生した問題と解決方法を記録します。同じ問題に再び遭遇したときに検索できるよう、**症状(エラーメッセージ)をそのまま** 書いてください。

- ID:`T-xx`。追記のみ。
- 未解決の問題は OPEN_ISSUES に書き、解決したらここへ記録する。

## テンプレート

```markdown
### T-xx: <症状の短い説明>
- 日付 / 関連: YYYY-MM-DD / LOG-..., #Issue
- 症状: <エラーメッセージ・現象>
- 環境: <OS、ツール、モデル、バージョン>
- 原因: <確認できた原因(推定の場合は Unverified と明記)>
- 解決方法: <手順>
- 再発防止: <あれば>
```

## 記録

### T-01: AI のリモート操作で `.github/` に書き込めない
- 日付 / 関連: 2026-11-16 / LOG-20261116-02
- 症状: `... .github/ISSUE_TEMPLATE/bug.md is a protected file and cannot be written via remote tools.`
- 環境: claude.ai(クラウド)から Claude デスクトップアプリ経由で Mac のフォルダへ書き込み
- 原因: リモートのファイル書き込み機能が `.github/` を保護対象として扱う(Confirmed:エラーメッセージ)
- 解決方法: GitHub から複製したクラウド側の作業コピーで `.github/` に配置してコミットした
- 再発防止: `.github/` の変更は git 経由(commit / push)で行う

### T-02: AI セッションからの push・Issue 作成が拒否される
- 日付 / 関連: 2026-11-16 / LOG-20261116-03
- 症状: `gh label create` で `HTTP 403: Resource not accessible by integration`。push も権限不足で拒否。Mac 側シェルからは `Could not resolve hostname github.com`
- 環境: claude.ai の Claude Code 環境(クラウド)、Claude デスクトップアプリ経由の Mac 側シェル
- 原因: セッションの GitHub 連携に書き込み権限がない(読み取りは可能)。Mac 側シェルはネットワーク制限で GitHub に届かない(Confirmed:エラーメッセージ)
- 解決方法: 開発者の Mac のターミナルから push とスクリプト実行を行う。恒久対策として Claude GitHub App を対象リポジトリにインストールする(https://github.com/apps/claude/installations/select_target)
- 再発防止: K-02
