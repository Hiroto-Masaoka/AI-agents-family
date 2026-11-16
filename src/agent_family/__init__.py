"""AI-agents-family: Phase 1 の読み取り専用エージェント。

構成(ADR-0012):
- 共通部分: tools(ツール関数), guard(許可リスト), trace(記録形式), eval(評価の入口)
- 実行方式: runtimes.api_runtime(Track B: Messages API 直接)/ runtimes.sdk_runtime(Track A: Claude Agent SDK)
"""

__version__ = "0.0.1"
