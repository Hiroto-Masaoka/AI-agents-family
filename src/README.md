# src — ソースコード

**現時点では実装はありません**。Phase 1 の P1-1(最小エージェント)から実装を始め、構成を ADR に記録します。現時点の構成案(Proposed):

```
src/
├── agent/        エージェント本体(LLM 呼び出し、エージェントループ)
├── tools/        ツール(読み取り用と操作用を分ける)
├── adapters/     装置インターフェース(望遠鏡ごとに差し替え)
├── workflows/    定時処理など決まった手順
└── tests/        試験
```

開発言語:エージェント部分は Python、重い計算は Julia(`src/julia/` に置き、ツールとして呼び出す予定)。[ADR-0010](../docs/DECISIONS/ADR-0010-python-agents-julia-compute.md)
