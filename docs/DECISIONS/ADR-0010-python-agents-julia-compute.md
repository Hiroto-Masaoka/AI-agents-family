# ADR-0010: エージェント部分は Python、重い計算は Julia で書く

- **Status:** Decided(言語の分担)/ Python と Julia の連携方式は Proposed
- **日付:** 2026-11-16
- **決定者:** 開発者
- **関連:** OPEN_ISSUES Q-06(解消)、[TECH_STACK §3.1](../TECH_STACK.md)、Issue [#1](https://github.com/Hiroto-Masaoka/AI-agents-family/issues/1)、LOG-20261116-05

## 背景
開発者は普段 Julia を使っているが、LLM の公式 SDK、MCP SDK、エージェント関連のライブラリは Python で最も充実している。

## 選択肢
| 案 | 長所 | 短所 |
|----|------|------|
| Julia のみ | 慣れている、高速 | LLM・MCP の公式ライブラリが乏しく、HTTP を直接扱う手間が大きい |
| Python のみ | ライブラリが最も豊富、情報が多い | 重い数値計算の速度・メモリ効率で Julia に劣る場合がある。既存の Julia 資産を使えない |
| **Python(エージェント)+ Julia(重い計算)** ← 採用 | 両方の長所を使える | 2 言語の環境管理と、連携部分の設計が必要 |

## 決定
- **Python:** エージェントループ、LLM API 呼び出し、ツール定義、MCP サーバー、ワークフロー、評価ハーネス。
- **Julia:** 高速処理とメモリ効率が重要な計算(大きなデータの解析、数値シミュレーションなど)。エージェントからは **ツールとして呼び出す**。

## Python と Julia の連携方式(Proposed、P1-3 で試して決める)
| 方式 | 内容 | 向いている場面 |
|------|------|---------------|
| A. コマンド実行 | Python から `julia script.jl 入力 出力` を実行し、結果を JSON で受け取る | 最も単純で壊れにくい。Phase 1 の第一候補 |
| B. 同一プロセス連携 | Python から JuliaCall(PythonCall.jl)で Julia 関数を直接呼ぶ | 大きな配列をコピーせずに渡したいとき |
| C. 常駐サービス | Julia を MCP サーバーや HTTP サーバーとして常駐させる | 起動時間(JIT コンパイル)を毎回払いたくないとき |

> 補足:Julia は初回実行時にコンパイル時間がかかる。方式 A で遅さが問題になれば、B または C を検討する。

## トレードオフ
- 2 言語の環境(Python の仮想環境と Julia の Project.toml)を両方管理する必要がある。
- Phase 1 は読み取り専用のため、Julia 側も「入力を読み、結果を返すだけ」の関数に限定する(ADR-0009)。

## 未決定事項
- Python 環境の管理ツール(uv / conda / venv)
- Python と Julia のバージョン

## 追記(2026-11-17)
- Python パッケージは `pyproject.toml` で定義し、`pip install -e ".[all]"` で導入する形にした(環境管理ツールに依存しない)。開発者は anaconda を使っているため、手順書では conda の例を示した。正式な選択は開発者の実行後に記録する(Proposed)。
