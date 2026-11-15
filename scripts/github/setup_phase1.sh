#!/usr/bin/env bash
# Phase 1 の GitHub ラベル・Milestone・Issue を作成する(2回実行しても重複しない)
# 必要: GitHub CLI (gh) にログイン済み  →  gh auth login
# 使い方: リポジトリのルートで  bash scripts/github/setup_phase1.sh
set -euo pipefail
REPO="Hiroto-Masaoka/AI-agents-family"
MS="Phase 1 - Read-Only Monitoring"
DIR="$(cd "$(dirname "$0")" && pwd)/issues"

echo "== ラベル(DEVELOPMENT_GUIDELINES §4)"
label() { gh label create "$1" --repo "$REPO" --color "$2" --description "$3" --force >/dev/null && echo "  $1"; }
label "type:task"       1D76DB "作業"
label "type:bug"        D73A4A "不具合"
label "type:experiment" 5319E7 "実験・試験"
label "type:question"   FBCA04 "未確認事項・調査"
label "type:idea"       C5DEF5 "改善案・将来構想"
for p in 0 1 2 3 4 5 6 7; do label "phase:$p" 0E8A16 "ROADMAP Phase $p"; done
label "priority:high"   B60205 "優先度: 高"
label "priority:medium" FF9F1C "優先度: 中"
label "priority:low"    BFD4F2 "優先度: 低"
label "safety"          000000 "装置操作・安全性に関わる"
label "read-only"       006B75 "読み取り専用で実施(ADR-0009)"

echo "== Milestone"
if gh api "repos/$REPO/milestones?state=all" --jq '.[].title' | grep -qxF "$MS"; then
  echo "  既存: $MS"
else
  gh api "repos/$REPO/milestones" -f title="$MS" \
    -f description="汎用エージェントの基本を読み取り専用で学ぶ 5 タスク。計画: docs/EXPERIMENTS/PHASE1_TEST_PLAN.md" >/dev/null
  echo "  作成: $MS"
fi

echo "== Issues"
create() { # $1=file $2=title $3=labels(comma)
  if gh issue list --repo "$REPO" --state all --search "\"$2\" in:title" --json title --jq '.[].title' | grep -qxF "$2"; then
    echo "  既存: $2"
  else
    gh issue create --repo "$REPO" --title "$2" --body-file "$DIR/$1" --label "$3" --milestone "$MS"
  fi
}
create 01-p1-1.md "[P1-1] 最小エージェント:リポジトリの文書に答える"            "type:experiment,phase:1,read-only,priority:high"
create 02-p1-2.md "[P1-2] 文献調査エージェント(arXiv API・引用検証)"            "type:experiment,phase:1,read-only,priority:high"
create 03-p1-3.md "[P1-3] データ分析・コード読解エージェント"                    "type:experiment,phase:1,read-only,priority:medium"
create 04-p1-4.md "[P1-4] MCP 連携による定型モニタリング(日次ダイジェスト)"     "type:experiment,phase:1,read-only,priority:medium"
create 05-p1-5.md "[P1-5] マルチエージェント調査+独立検証:研究資金の公募調査"  "type:experiment,phase:1,read-only,priority:medium"

echo "== 結果"
gh issue list --repo "$REPO" --milestone "$MS" --state all
