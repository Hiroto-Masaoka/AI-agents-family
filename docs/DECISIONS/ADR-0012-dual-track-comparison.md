# ADR-0012: Phase 1 は 2 つの実行方式(Agent SDK・Pro 枠 / API 直接・従量課金)で実装して比較する

- **Status:** Decided
- **日付:** 2026-11-16
- **決定者:** 開発者
- **関連:** [ADR-0011](ADR-0011-phase1-llm-api.md)、[PHASE1_TEST_PLAN §2](../EXPERIMENTS/PHASE1_TEST_PLAN.md#2-2-つの実行方式の比較track-a--track-b)、LOG-20261116-06

## 背景
- Claude Pro プランでは、Claude Agent SDK と `claude -p` をサブスクリプションの利用枠内で使える(2026-11-16 時点の公式ヘルプ。[support.claude.com/en/articles/15036540](https://support.claude.com/en/articles/15036540))。
- 一方、Messages API を直接呼ぶには、Claude Console の API キーによる従量課金の契約が必要。
- 当初の P1-1 は「フレームワークを使わずに API を直接呼び、仕組みを理解する」計画だった。

## 選択肢
1. Pro 枠内(Agent SDK)だけで実装する:追加費用なし。ただし仕組みの多くは SDK に隠れる
2. API 直接(従量課金)だけで実装する:仕組みが全部見える。費用がかかる
3. **両方で実装し、同じ試験課題で比較する** ← 採用

## 決定
- **Track A:** Claude Agent SDK(Python)を Pro アカウントで使う。
- **Track B:** Anthropic の Messages API を API キーで直接呼び、エージェントループを自作する。
- 両方式で **ツール関数・許可リスト・試験課題・合否判定・トレース形式・指示文・モデル名を共通** にし、変えるのは実行方式だけにする。
- 比較の指標と手順は [PHASE1_TEST_PLAN §2](../EXPERIMENTS/PHASE1_TEST_PLAN.md#2-2-つの実行方式の比較track-a--track-b)。
- 共通基盤を作るタスク P1-0 を追加する。

## 理由
- 「実用的な道具(SDK)」と「仕組みそのもの(自作ループ)」の両方を学べる。
- 費用・正確性・作りやすさ・調べやすさの違いを、推測ではなく測定で判断できる。Phase 2 以降でどちらを使うかの根拠になる。
- ツールを共通にしておけば、2 つ目の方式の追加コストは小さい(登録部分と入口だけ)。

## トレードオフ
- 実装と試験の手間が増える(各タスク約 1.3〜1.5 倍の見込み、未検証)。
- Track B に費用がかかる(Phase 1 全体で数ドル〜数十ドルの見込み。[比較資料 §3](../references/llm-api-comparison-2026-11.md#3-phase-1-の費用の目安試算unverified))。
- Track A は Pro 枠をチャットや Claude Code と共有するため、評価の繰り返しで上限に達する可能性がある(上限到達も比較結果として記録する)。

## 未決定事項
- Track B の月の予算上限額(開発者が決める。OPEN_ISSUES Q-12)
- Pro プランで Agent SDK から使えるモデルの範囲(OPEN_ISSUES Q-13)

## 追記(2026-11-16)
- Track B の月の予算上限は **30 USD**(開発者決定、LOG-20261116-07)。上限に近づいた場合は Track B の実行を止め、その時点までの結果で比較する。
