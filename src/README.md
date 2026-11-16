# src — ソースコード

**現時点では実装はありません**。Phase 1 の P1-1(最小エージェント)から実装を始め、構成を ADR に記録します。現時点の構成案(Proposed、2 つの実行方式の比較に対応、ADR-0012):

```
src/
├── agent_family/
│   ├── tools/        ツール関数(読み取り専用、両方式で共通)
│   ├── guard/        許可リスト・ガードレール(共通)
│   ├── trace/        トレース形式(共通)
│   ├── runtimes/
│   │   ├── sdk_runtime.py   Track A:Claude Agent SDK(Pro 枠)
│   │   └── api_runtime.py   Track B:Messages API を直接呼ぶ自作ループ
│   └── eval/         評価ハーネス(同じ試験課題・同じ合否判定)
├── julia/            重い計算(ツールとして呼び出す)
├── adapters/         装置インターフェース(Phase 5 以降)
└── tests/            試験
```

開発言語:エージェント部分は Python、重い計算は Julia(`src/julia/` に置き、ツールとして呼び出す予定)。[ADR-0010](../docs/DECISIONS/ADR-0010-python-agents-julia-compute.md)
