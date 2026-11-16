"""Track B の費用計算と、月の予算上限の確認。

料金(USD / 100 万トークン)は 2026-11-16 時点の公開情報
(docs/references/llm-api-comparison-2026-11.md)。変わることがあるので、公式ページで確認して更新すること。
請求の正となるのは Claude Console の表示です。ここでの計算は目安で、予算上限の手前で止めるために使います。
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

# model: (input, output, cache_read, cache_write_5m)
PRICES_PER_MTOK: dict[str, tuple[float, float, float, float]] = {
    "claude-opus-5-5": (4.00, 20.00, 0.20, 5.00),
    "claude-sonnet-5-5": (2.00, 10.00, 0.10, 2.50),
    # Haiku 5.5 はプロンプト 10 万トークン以下の料金(超えると 0.50 / 2.50)
    "claude-haiku-5-5": (0.10, 0.50, 0.01, 0.125),
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int,
                  cache_read: int = 0, cache_write: int = 0) -> float | None:
    p = PRICES_PER_MTOK.get(model)
    if p is None:
        return None
    return (input_tokens * p[0] + output_tokens * p[1] + cache_read * p[2] + cache_write * p[3]) / 1_000_000


class BudgetExceeded(RuntimeError):
    pass


class SpendLedger:
    """Track B の利用額をローカルに記録し、月の予算上限に近づいたら実行を止める。

    記録先: logs/runtime/spend.jsonl(Git 管理外)。Console の利用上限と二重の安全装置です。
    """

    def __init__(self, path: Path, monthly_budget_usd: float | None = None) -> None:
        self.path = path
        if monthly_budget_usd is None:
            monthly_budget_usd = float(os.environ.get("AGENT_FAMILY_MONTHLY_BUDGET_USD", "30"))
        self.monthly_budget_usd = monthly_budget_usd

    def month_total(self, month: str | None = None) -> float:
        month = month or datetime.now().strftime("%Y-%m")
        if not self.path.exists():
            return 0.0
        total = 0.0
        for line in self.path.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line)
            if rec.get("month") == month:
                total += rec.get("cost_usd") or 0.0
        return total

    def check(self, planned_max_usd: float) -> None:
        spent = self.month_total()
        if spent + planned_max_usd > self.monthly_budget_usd:
            raise BudgetExceeded(
                f"今月の Track B の利用額 ${spent:.2f} + 今回の上限 ${planned_max_usd:.2f} が "
                f"予算 ${self.monthly_budget_usd:.2f} を超えるため実行しません"
            )

    def add(self, cost_usd: float, run_id: str, model: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        rec = {"month": datetime.now().strftime("%Y-%m"), "run_id": run_id, "model": model, "cost_usd": cost_usd}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
