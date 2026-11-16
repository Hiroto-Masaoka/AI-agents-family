# ADR-0011: Phase 1 で使う商用 LLM API

- **Status:** Decided(2026-11-16、末尾「決定」を参照。以下の提案本文は提案当時のまま)
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

## 決定(2026-11-16 追記)
- 主に使う LLM は **Anthropic(Claude)**。モデルの役割分担(Sonnet 5.5 主力、Haiku 5.5 繰り返し試験、Opus 5.5 計画・検証役)は提案どおり。
- ただし利用経路を 2 つに分け、比較する:**Track A = Claude Pro の枠で Agent SDK**、**Track B = API キーで Messages API を直接**([ADR-0012](ADR-0012-dual-track-comparison.md))。
- Gemini の無料枠は、P1-5 でのベンダー比較に任意で使う。
