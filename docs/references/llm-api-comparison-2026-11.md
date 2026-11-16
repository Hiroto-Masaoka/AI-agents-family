# 商用 LLM API の比較(Phase 1 向け、2026-11-16 調査)

- **目的:** OPEN_ISSUES Q-05(Phase 1 で使う商用 LLM API の選定)の判断材料
- **状態:** 料金は 2026-11-16 時点の Web 上の公開情報(公式ページと価格比較サイト)。**契約前に各社の公式料金ページで必ず確認すること**(Unverified 扱い)。「評価」列は AI による整理で、本プロジェクトでの試験結果ではない(Proposed)
- **単位:** 米ドル / 100 万トークン(入力 / 出力)。1 トークンは英語で約 0.75 単語、日本語では 1 文字前後
- **関連:** [ADR-0011](../DECISIONS/ADR-0011-phase1-llm-api.md)(提案)、[TECH_STACK](../TECH_STACK.md)

## 1. 料金の比較(標準料金・短いプロンプト)

| 価格帯 | Anthropic(Claude) | OpenAI(GPT) | Google(Gemini) |
|-------|-------------------|-------------|----------------|
| 最上位 | Opus 5.5:$4 / $20 | GPT-6 Astra:$10 / $50 | Gemini 4 Argon:$2 / $10(**11/30 までの導入価格**。12/1 から $4 / $20) |
| 中位(主力) | Sonnet 5.5:$2 / $10 | GPT-6.1 Sol:$2 / $10 / GPT-6.1 Terra:$1 / $5 | Gemini 3.1 Pro:$2 / $12 |
| 小型・安価 | Haiku 5.5:$0.10 / $0.50(10 万トークン以下のプロンプト。超えると $0.50 / $2.50) | GPT-6 Luna:$0.10 / $0.50 | Gemini 3.8 Flash:$0.75 / $3.75(12/31 までの導入価格)、Flash-Lite 系:$0.10〜0.30 / $0.40〜2.50 |
| 無料枠 | なし | なし(前払いクレジット制、最低 $5) | **あり**(Flash 系のみ、回数制限つき。Argon は対象外) |
| 割引 | Batch(非同期)で半額、キャッシュ読み取りが大幅割引 | Batch で半額、キャッシュ割引 | Batch / Flex で半額、キャッシュ割引 |
| 注意点 | 長いプロンプトで Haiku の単価が上がる | 長いコンテキスト(約 27 万トークン超)で単価が上がる。内蔵 Web 検索は別料金 | 導入価格の期限がある。Google 検索連携は月 5,000 回まで無料、以降は別料金 |

> 「キャッシュ」:同じ長い前置き(システムプロンプト、文書など)を繰り返し送るとき、2 回目以降を安く処理する仕組み。エージェントは同じ指示を何度も送るため、実際の費用への影響が大きい。

## 2. 主要な観点の比較

評価は ◎ 優れている / ○ 十分 / △ 注意が必要。**AI による整理であり、本プロジェクトでの検証前の暫定評価** です。

| 観点 | 意味 | Anthropic | OpenAI | Google |
|------|------|-----------|--------|--------|
| **コスト** | 同じ作業をしたときの費用 | ○ 中位 $2/$10。Haiku が非常に安い | ○ 中位 $2/$10。Luna が非常に安い | ◎ 無料枠あり。Flash 系が安い。ただし導入価格の終了に注意 |
| **正確性** | 推論・指示への従い方・ツール呼び出しの正しさ | ◎ 第三者の総合指標で Opus 5.5 / Sonnet 5.5 が上位 | ○〜◎ 同価格帯で同程度 | ○〜◎ 同価格帯で同程度 |
| **拡張性** | 機能・規模を広げやすいか(長いコンテキスト、Batch、上位モデルへの切り替え) | ◎ 全モデル 100 万トークン級、3 段階のモデル | ◎ 4 段階のモデル、内蔵ツールが豊富 | ◎ 100 万トークン級、マルチモーダルが強い |
| **柔軟性** | 他の道具と組み合わせやすいか、ベンダーに縛られないか | ◎ MCP の提唱元。Claude Code / Agent SDK と同じ仕組み | ○ 独自の Responses API・Agents SDK が中心(MCP 対応状況は要確認) | ○ ADK・Vertex AI など Google 系と統合(MCP 対応状況は要確認) |
| **学習のしやすさ** | 初心者がつまずきにくいか | ◎ 現在の開発(Claude Code)と同じ会社で、用語・挙動が共通 | ○ 情報量が最も多い | ○ 無料で試し始められる |
| **データの扱い** | 送ったデータが学習に使われないか | 有料 API は既定で学習に使わない方針(要確認) | 同左(要確認) | **無料枠では製品改善に使われる場合がある**(要確認)。有料枠は既定で使わない方針 |

## 3. Phase 1 の費用の目安(試算、Unverified)

Phase 1 の 5 タスクを、評価のための繰り返し実行も含めて **入力 2,000 万トークン・出力 200 万トークン** 使うと仮定(キャッシュ割引なし)。

| モデル | 入力 | 出力 | 合計 |
|--------|------|------|------|
| Claude Opus 5.5 | $80 | $40 | **$120** |
| Claude Sonnet 5.5 / GPT-6.1 Sol | $40 | $20 | **$60** |
| GPT-6.1 Terra | $20 | $10 | **$30** |
| Gemini 3.8 Flash(導入価格) | $15 | $7.5 | **$22.5** |
| Claude Haiku 5.5 / GPT-6 Luna | $2 | $1 | **$3** |

目安として、P1-1 の 10 問の試験 1 回(1 問あたり約 5 ステップ × 1 万トークン)は、Sonnet 5.5 でキャッシュなしでも約 $1.5 です。キャッシュを使えば入力費用はさらに下がります。**最初に API 側で月の利用上限(予算アラート)を設定することを推奨** します。

## 4. 提案(Proposed、開発者の判断待ち)

**主:Anthropic(Claude)**、**比較用:Google Gemini の無料枠**

| 用途 | モデル | 理由 |
|------|-------|------|
| P1-1〜P1-4 の主力 | Claude Sonnet 5.5 | 正確性と費用のバランス。開発に使っている Claude Code と仕組みが共通で学びやすい。P1-4 の MCP と相性が良い |
| 繰り返し試験・大量処理 | Claude Haiku 5.5 | 非常に安い。評価の繰り返しに向く |
| P1-5 のオーケストレーター・検証役 | Claude Opus 5.5 | 計画と検証には上位モデルを使う(PLAYBOOK P9) |
| P1-5 の比較評価 | Gemini 3.8 Flash(無料枠) | 別ベンダーでも同じハーネスが動くか確認し、特定ベンダーへの依存を避ける(ADR-0001 の考え方) |

**代替案:** 情報量の多さを重視するなら OpenAI(GPT-6.1 Sol)が同価格帯で同等の選択肢。費用を最優先するなら Gemini の無料枠から始める。

> 設計上の注意:どの API を選んでも、ハーネス側で「モデル名と呼び出し部分」を 1 か所にまとめ、後から差し替えられるようにする(P1-1 の実装方針)。

## 出典
- [Anthropic — Pricing(公式)](https://platform.claude.com/docs/en/about-claude/pricing)
- [OpenAI — API Pricing(公式)](https://developers.openai.com/api/docs/pricing)
- [Google — Gemini Developer API pricing(公式)](https://ai.google.dev/pricing)
- [benchlm.ai — Claude API Pricing (Oct 2026)](https://benchlm.ai/anthropic/api-pricing)
- [tech-insider — Claude Opus vs Sonnet vs Haiku 5.5](https://tech-insider.org/ie/claude-opus-vs-sonnet-vs-haiku-5-5-pricing-2026/)
- [benchlm.ai — OpenAI API Pricing (Oct 2026)](https://benchlm.ai/openai/api-pricing)
- [aibusinessweekly — OpenAI API pricing (Nov 1, 2026)](https://aibusinessweekly.net/p/openai-api-pricing)
- [benchlm.ai — Gemini API Pricing (Oct 2026)](https://benchlm.ai/google/api-pricing)
- [buildmvpfast — Gemini 4 Argon pricing](https://www.buildmvpfast.com/blog/gemini-4-argon-pricing-intro-rates-2026)
