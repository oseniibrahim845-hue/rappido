from decimal import Decimal

import pytest

from app.models import OrderSide, RebalanceAction
from app.rebalance_engine import RebalanceError, calculate_rebalance, round_down

PRICES = {"BTC": 65000, "ETH": 3200, "SOL": 150, "USDC": 1}
CURRENT = {"BTC": 30, "ETH": 40, "SOL": 10, "USDC": 20}
TARGET = {"BTC": 40, "ETH": 30, "SOL": 20, "USDC": 10}


def plan_for(current=CURRENT, target=TARGET, value=100_000, prices=PRICES, **kw):
    return calculate_rebalance(current, target, value, prices, **kw)


def rows(plan):
    return {r.asset: r for r in plan.rows}


def test_rebalance_values_and_differences():
    r = rows(plan_for())
    assert r["BTC"].current_value == Decimal("30000.00")
    assert r["BTC"].target_value == Decimal("40000.00")
    assert r["BTC"].diff_value == Decimal("10000.00")
    assert r["BTC"].diff_pct == Decimal("10")
    assert r["ETH"].diff_pct == Decimal("-10")
    assert r["SOL"].diff_pct == Decimal("10")
    assert r["USDC"].diff_pct == Decimal("-10")


def test_buy_calculation():
    r = rows(plan_for())
    assert r["BTC"].action is RebalanceAction.BUY
    # 10,000 / 65,000 = 0.153846..., rounded down to the 0.00001 lot size
    assert r["BTC"].quantity == Decimal("0.15384")
    assert r["BTC"].estimated_value == Decimal("9999.60")
    assert r["SOL"].action is RebalanceAction.BUY
    assert r["SOL"].quantity == Decimal("66.66")  # 10,000 / 150, lot 0.01


def test_sell_calculation():
    r = rows(plan_for())
    assert r["ETH"].action is RebalanceAction.SELL
    assert r["ETH"].quantity == Decimal("3.1250")  # 10,000 / 3,200
    assert r["ETH"].estimated_value == Decimal("10000.00")


def test_quote_asset_is_settlement_not_an_order():
    plan = plan_for()
    r = rows(plan)
    assert r["USDC"].action is RebalanceAction.QUOTE
    assert all(o.asset != "USDC" for o in plan.orders)
    # Net quote change = sells - buys = 10,000 - 9,999.60 - 9,999.00
    assert plan.net_quote_change == Decimal("-9998.60")


def test_order_generation_sells_first():
    plan = plan_for()
    assert [(o.symbol, o.side) for o in plan.orders] == [
        ("ETH/USDC", OrderSide.SELL),
        ("BTC/USDC", OrderSide.BUY),
        ("SOL/USDC", OrderSide.BUY),
    ]
    for o in plan.orders:
        assert o.estimated_value == (o.quantity * o.reference_price).quantize(Decimal("0.01"))
    assert plan.plan_id.startswith("PLAN-")


def test_small_drift_is_held():
    plan = plan_for(target={"BTC": 30.005, "ETH": 39.995, "SOL": 10, "USDC": 20})
    r = rows(plan)
    assert r["BTC"].action is RebalanceAction.HOLD
    assert r["ETH"].action is RebalanceAction.HOLD
    assert plan.orders == []


def test_new_asset_in_target_is_bought():
    plan = plan_for(target={"BTC": 30, "ETH": 30, "SOL": 10, "USDC": 20, "AVAX": 10},
                    prices={**PRICES, "AVAX": 25})
    r = rows(plan)
    assert r["AVAX"].current_pct == 0
    assert r["AVAX"].action is RebalanceAction.BUY


def test_full_exit_to_new_asset_is_funded_by_sells():
    plan = plan_for(current={"BTC": 100}, target={"SOL": 100}, prices={"BTC": 65000, "SOL": 150})
    assert [(o.asset, o.side) for o in plan.orders] == [("BTC", OrderSide.SELL), ("SOL", OrderSide.BUY)]
    assert plan.warnings == []
    assert plan.net_quote_change >= 0  # lot rounding never spends more than the sells raise


@pytest.mark.parametrize("kwargs, message", [
    ({"target": {"BTC": 50, "ETH": 30}}, "sum to 100"),
    ({"current": {"BTC": -10, "ETH": 110}}, "negative"),
    ({"value": 0}, "positive"),
    ({"prices": {"BTC": 65000, "ETH": 3200, "SOL": 150}}, "Missing price for USDC"),
    ({"prices": {**PRICES, "SOL": 0}}, "SOL must be positive"),
])
def test_invalid_inputs(kwargs, message):
    with pytest.raises(RebalanceError, match=message):
        plan_for(**kwargs)


def test_round_down():
    assert round_down(Decimal("1.23456789"), Decimal("0.001")) == Decimal("1.234")
