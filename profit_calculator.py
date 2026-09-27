"""
利润计算器 —— 纯 Python 数学计算模块。

原则：
1. 所有利润 / 利润率 / 盈亏平衡 ACOS 等计算必须在本模块完成，
   严禁交给 LLM 计算（LLM 只负责文字解读）。
2. 公式全部显式写明，便于核对。
3. 示例对照（与产品需求一致的用例）：
   售价 29.99 / 采购 8.00 / 头程 2.50 / 佣金 15%(=4.50) / FBA 3.50 / 其他 0 / 广告 0
   → 广告前总成本 18.50 → 单件利润 11.49 → 利润率 38.3% → 盈亏平衡 ACOS 38.3%
"""

from dataclasses import dataclass, field


@dataclass
class ProfitInput:
    price: float = 0.0              # 产品售价 (USD)
    cost: float = 0.0               # 采购成本 (USD / 件)
    shipping: float = 0.0           # 头程物流 (USD / 件)
    commission_rate: float = 15.0   # 平台佣金比例 (%)
    fulfillment: float = 0.0        # FBA / 履约费用 (USD / 件)
    ad_cost: float = 0.0            # 广告成本 (USD / 件，按单件均摊)
    other: float = 0.0             # 其他费用 (USD / 件：包装 / 退换货 / 仓储等)


@dataclass
class ProfitResult:
    commission: float            # 平台佣金金额 (USD)
    total_cost_before_ad: float   # 广告前总成本 (USD)
    profit_before_ad: float      # 广告前单件利润 (USD)
    profit: float                # 广告后单件利润 (USD)
    profit_margin: float         # 广告后利润率 (%)
    margin_before_ad: float     # 广告前利润率 (%)
    break_even_acos: float      # 盈亏平衡 ACOS (%)
    is_profitable: bool
    warnings: list = field(default_factory=list)


def calculate(inp: ProfitInput) -> ProfitResult:
    """按固定公式计算利润指标。输入不合法时抛出 ValueError。"""
    # ---- 输入校验 ----
    errors = []
    if inp.price <= 0:
        errors.append("产品售价必须大于 0")
    for label, v in [("采购成本", inp.cost), ("头程物流", inp.shipping),
                     ("FBA/履约费用", inp.fulfillment), ("广告成本", inp.ad_cost),
                     ("其他费用", inp.other)]:
        if v < 0:
            errors.append(f"{label}不能为负数")
    if not 0 <= inp.commission_rate <= 100:
        errors.append("平台佣金比例必须在 0% ~ 100% 之间")
    if errors:
        raise ValueError("；".join(errors))

    # ---- 公式区（全部显式，禁止改动口径）----
    # 1) 平台佣金 = 售价 × 佣金比例
    commission = inp.price * inp.commission_rate / 100.0
    # 2) 广告前总成本 = 采购成本 + 头程物流 + 平台佣金 + FBA/履约 + 其他费用
    total_cost_before_ad = (inp.cost + inp.shipping + commission
                            + inp.fulfillment + inp.other)
    # 3) 广告前单件利润 = 售价 − 广告前总成本
    profit_before_ad = inp.price - total_cost_before_ad
    # 4) 广告后单件利润 = 广告前单件利润 − 单件广告成本
    profit = profit_before_ad - inp.ad_cost
    # 5) 利润率（广告后）= 广告后单件利润 ÷ 售价 × 100%
    profit_margin = profit / inp.price * 100.0
    # 6) 广告前利润率 = 广告前单件利润 ÷ 售价 × 100%
    margin_before_ad = profit_before_ad / inp.price * 100.0
    # 7) 盈亏平衡 ACOS = 广告前单件利润 ÷ 售价 × 100%
    #    （广告花费占销售额的比例一旦超过该值，即开始亏损）
    break_even_acos = margin_before_ad

    # ---- 风险提示 ----
    warnings = []
    if profit_before_ad <= 0:
        warnings.append(
            "广告前已亏损：固定成本（采购+头程+佣金+FBA+其他）已高于售价，"
            "任何广告投入都会扩大亏损。请先优化成本结构或提高售价。")
    elif profit <= 0:
        warnings.append(
            f"广告后亏损：单件广告成本（${inp.ad_cost:.2f}）已越过盈亏平衡线"
            f"（盈亏平衡 ACOS = {break_even_acos:.1f}%），当前广告投入不经济。")
    if inp.commission_rate == 0:
        warnings.append("平台佣金比例设为 0%，实际运营中 Amazon 通常收取 8%~15% 佣金，请注意核对。")

    return ProfitResult(
        commission=commission,
        total_cost_before_ad=total_cost_before_ad,
        profit_before_ad=profit_before_ad,
        profit=profit,
        profit_margin=profit_margin,
        margin_before_ad=margin_before_ad,
        break_even_acos=break_even_acos,
        is_profitable=profit > 0,
        warnings=warnings,
    )
