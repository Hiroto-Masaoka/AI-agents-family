# ADR-0011: Phase 1 で使う商用 LLM API

- **Status:** Proposed(開発者の判断待ち)
- **日付:** 2026-11-16
- **関連:** OPEN_ISSUES Q-05、[比較資料](../references/llm-api-comparison-2026-11.md)、ADR-0004、LOG-20261116-05

## 背景
Phase 1 の 5 タスクを実装するために、Tool Calling に対応した商用 LLM API が必要。

## 選択肢
1. **Anthropic(Claude)を主に使い、Gemini の無料枠を比較用に使う** ← 提案
2. OpenAI(GPT)を主に使う
3. Google(Gemini)を主に使う(無料枠から開始)

比較は [llm-api-comparison-2026-11.md](../references/llm-api-comparison-2026-11.md) を参照。

## 提案理由
- 正確性と費用のバランス(Sonnet 5.5 を主力、Haiku 5.5 を繰り返し試験、Opus 5.5 を P1-5 の計画・検証役)。
- 開発に使っている Claude Code と仕組みが共通で、初心者が学びやすい。MCP(P1-4)と相性が良い。
- 別ベンダー(Gemini)でも動かして比較することで、特定ベンダーへの依存を避ける。

## トレードオフ
- 無料枠がないため、最初から少額の費用がかかる(Phase 1 全体で数ドル〜数十ドルの見込み、比較資料 §3)。

## 決定時に記録すること
採用した API、予算上限の設定値(金額は記録してよいが API キーは書かない)、キーの保管場所(`.env`)。
