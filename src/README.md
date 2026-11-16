# src — ソースコード

Phase 1 の読み取り専用エージェントを、2 つの実行方式で動かして比較するためのコードです([ADR-0012](../docs/DECISIONS/ADR-0012-dual-track-comparison.md))。
使い方は [手順書 P1-0_SETUP](../docs/guides/P1-0_SETUP.md) を参照してください。

## 構成(P1-0 で実装済み)

```
src/
├── agent_family/
│   ├── tools/        ツール関数(読み取り専用、両方式で共通)— list_dir, read_file
│   ├── guard/        許可リスト(許可ディレクトリ外・機密ファイル・大きすぎるファイルを拒否)
│   ├── trace/        トレース形式(JSON Lines、両方式で共通)
│   ├── runtimes/
│   │   ├── base.py          共通の設定(RunConfig)と結果(RunResult)、共通の指示文
│   │   ├── api_runtime.py   Track B:Messages API を直接呼ぶ自作ループ(仕組みがすべて見える)
│   │   ├── sdk_runtime.py   Track A:Claude Agent SDK(Pro 枠)
│   │   └── pricing.py       Track B の費用計算と月の予算上限(30 USD)の安全装置
│   ├── eval/         評価ハーネス(同じ試験課題・同じ合否判定)と読み取り専用の検証(SHA-256)
│   └── cli.py        コマンド:check / ask / eval
└── tests/            LLM に接続しない試験(偽の LLM と SDK の設定生成で確認)
```

試験課題は `evals/`(リポジトリ直下)に JSON で置きます。

## 共通部分と方式ごとの部分

| | 共通 | Track A のみ | Track B のみ |
|---|---|---|---|
| ツール関数・許可リスト | ✅ | | |
| 指示文・モデル名・上限(ステップ・費用) | ✅ | | |
| トレース形式・評価ハーネス・合否判定 | ✅ | | |
| ツールの登録 | | SDK のプロセス内 MCP | Messages API の `tools` |
| ループ | | SDK が担う | 自作(`api_runtime.py`) |
| 認証 | | Pro ログイン(API キーは実行中に外す) | `.env` の API キー |

## 開発言語
エージェント部分は Python、重い計算は Julia(`src/julia/` に置き、ツールとして呼び出す予定)。[ADR-0010](../docs/DECISIONS/ADR-0010-python-agents-julia-compute.md)

## 将来の追加予定
`src/julia/`(P1-3)、MCP サーバー(P1-4)、`adapters/`(装置インターフェース、Phase 5)
