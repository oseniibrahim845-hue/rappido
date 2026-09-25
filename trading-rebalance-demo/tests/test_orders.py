from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.exchange_base import ExchangeAdapter, ExchangeError
from app.main import SAMPLE_CURRENT, SAMPLE_PORTFOLIO_VALUE, SAMPLE_PRICES, SAMPLE_TARGET, create_app
from app.mock_exchange import MockExchange, make_sample_exchange
from app.models import OrderInstruction, OrderSide, OrderStatus
from app.order_manager import OrderManager, PlanAlreadyExecutedError
from app.rebalance_engine import calculate_rebalance


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def exchange(clock):
    return make_sample_exchange(SAMPLE_CURRENT, SAMPLE_PORTFOLIO_VALUE, SAMPLE_PRICES,
                                fill_delay_seconds=1.0, clock=clock)


@pytest.fixture
def plan():
    return calculate_rebalance(SAMPLE_CURRENT, SAMPLE_TARGET, SAMPLE_PORTFOLIO_VALUE, SAMPLE_PRICES)


def instruction(**overrides):
    base = dict(asset="BTC", symbol="BTC/USDC", side=OrderSide.BUY, quantity=Decimal("0.1"),
                reference_price=Decimal("65000"), estimated_value=Decimal("6500"),
                current_pct=Decimal("30"), target_pct=Decimal("40"))
    return OrderInstruction(**{**base, **overrides})


# ------------------------------------------------------------------ mock exchange


def test_mock_exchange_implements_interface(exchange):
    assert isinstance(exchange, ExchangeAdapter)
    assert exchange.get_price("BTC/USDC") == Decimal("65000")
    assert exchange.get_balance()["USDC"] == Decimal("20000")


def test_mock_order_goes_pending_then_filled(exchange, clock):
    order = exchange.create_order(client_order_id="c1", symbol="BTC/USDC",
                                  side=OrderSide.BUY, quantity=Decimal("0.1"))
    assert order.status is OrderStatus.PENDING
    assert exchange.get_order(order.exchange_order_id).status is OrderStatus.PENDING

    clock.now = 1.0
    filled = exchange.get_order(order.exchange_order_id)
    assert filled.status is OrderStatus.FILLED
    assert filled.filled_quantity == Decimal("0.1")
    assert filled.average_price == Decimal("65000")
    assert filled.fee == Decimal("6.5")  # 0.1% of 6,500

    balances = exchange.get_balance()
    assert balances["USDC"] == Decimal("20000") - Decimal("6506.5")
    assert balances["BTC"] == Decimal("0.46153846") + Decimal("0.1")


def test_mock_sell_credits_quote(exchange, clock):
    order = exchange.create_order(client_order_id="c1", symbol="ETH/USDC",
                                  side=OrderSide.SELL, quantity=Decimal("1"))
    clock.now = 5
    assert exchange.get_order(order.exchange_order_id).status is OrderStatus.FILLED
    assert exchange.get_balance()["USDC"] == Decimal("20000") + Decimal("3200") - Decimal("3.2")


def test_mock_rejection_rule(exchange, clock):
    exchange.set_rejection_rule("SOL/USDC", "market halted")
    order = exchange.create_order(client_order_id="c1", symbol="SOL/USDC",
                                  side=OrderSide.BUY, quantity=Decimal("10"))
    assert order.status is OrderStatus.PENDING
    clock.now = 5
    rejected = exchange.get_order(order.exchange_order_id)
    assert rejected.status is OrderStatus.REJECTED
    assert rejected.reject_reason == "market halted"
    assert exchange.get_balance()["SOL"] == Decimal("66.66666667")  # unchanged


def test_mock_rejects_insufficient_balance(exchange, clock):
    order = exchange.create_order(client_order_id="c1", symbol="BTC/USDC",
                                  side=OrderSide.BUY, quantity=Decimal("1"))  # needs ~65k USDC
    clock.now = 5
    rejected = exchange.get_order(order.exchange_order_id)
    assert rejected.status is OrderStatus.REJECTED
    assert "Insufficient USDC" in rejected.reject_reason


def test_mock_refuses_invalid_requests(exchange):
    with pytest.raises(ExchangeError, match="Unsupported symbol"):
        exchange.create_order(client_order_id="c1", symbol="DOGE/USDC",
                              side=OrderSide.BUY, quantity=Decimal("1"))
    with pytest.raises(ExchangeError, match="positive"):
        exchange.create_order(client_order_id="c2", symbol="BTC/USDC",
                              side=OrderSide.BUY, quantity=Decimal("0"))
    with pytest.raises(ExchangeError, match="Unknown order"):
        exchange.get_order("MOCK-999999")


# ------------------------------------------------------------------ order manager


def test_order_manager_submits_plan_and_tracks_fills(exchange, clock, plan):
    manager = OrderManager(exchange)
    result = manager.submit_orders(plan.plan_id, plan.orders)

    assert result.summary == {"PENDING": 3, "FILLED": 0, "REJECTED": 0}
    ids = [o.order_id for o in result.orders]
    assert len(set(ids)) == 3 and all(i.startswith("ORD-") for i in ids)
    assert all(o.exchange_order_id.startswith("MOCK-") for o in result.orders)

    clock.now = 2
    orders = manager.list_orders(plan.plan_id)
    assert manager.summarize(orders) == {"PENDING": 0, "FILLED": 3, "REJECTED": 0}
    assert manager.get_order(ids[0]).status is OrderStatus.FILLED

    # Portfolio is now close to target (fees and lot rounding aside).
    balances = exchange.get_balance()
    values = {a: q * SAMPLE_PRICES[a] for a, q in balances.items()}
    total = sum(values.values())
    for asset, target in SAMPLE_TARGET.items():
        assert abs(values[asset] / total * 100 - target) < Decimal("0.05")


def test_order_manager_records_exchange_rejection(exchange, clock, plan):
    exchange.set_rejection_rule("SOL/USDC", "Simulated rejection")
    manager = OrderManager(exchange)
    manager.submit_orders(plan.plan_id, plan.orders)
    clock.now = 2
    by_asset = {o.asset: o for o in manager.list_orders()}
    assert by_asset["SOL"].status is OrderStatus.REJECTED
    assert by_asset["SOL"].reject_reason == "Simulated rejection"
    assert by_asset["BTC"].status is OrderStatus.FILLED
    assert by_asset["ETH"].status is OrderStatus.FILLED


def test_order_manager_validation_rejects_before_exchange(exchange):
    manager = OrderManager(exchange)
    result = manager.submit_orders("PLAN-1", [
        instruction(quantity=Decimal("0"), estimated_value=Decimal("0")),
        instruction(estimated_value=Decimal("5")),
        instruction(symbol="DOGE/USDC", asset="DOGE"),
        instruction(reference_price=Decimal("50000")),  # stale price, >5% away from market
    ])
    assert [o.status for o in result.orders] == [OrderStatus.REJECTED] * 4
    assert all(o.exchange_order_id is None for o in result.orders)
    reasons = [o.reject_reason for o in result.orders]
    assert "Quantity must be positive" in reasons[0]
    assert "outside allowed range" in reasons[1]
    assert "Unsupported symbol" in reasons[2]
    assert "recalculate" in reasons[3]


def test_plan_cannot_be_executed_twice(exchange, plan):
    manager = OrderManager(exchange)
    manager.submit_orders(plan.plan_id, plan.orders)
    with pytest.raises(PlanAlreadyExecutedError):
        manager.submit_orders(plan.plan_id, plan.orders)


# ------------------------------------------------------------------ API end-to-end


def test_api_full_flow():
    client = TestClient(create_app(fill_delay_seconds=0, fill_stagger_seconds=0))

    assert client.get("/health").json()["mode"] == "simulated"
    portfolio = client.get("/portfolio").json()
    assert portfolio["target_allocation"] == {"BTC": 40.0, "ETH": 30.0, "SOL": 20.0, "USDC": 10.0}
    assert round(portfolio["current_allocation"]["ETH"], 2) == 40.0

    plan = client.post("/rebalance").json()
    actions = {r["asset"]: r["action"] for r in plan["rows"]}
    assert actions == {"BTC": "BUY", "ETH": "SELL", "SOL": "BUY", "USDC": "QUOTE"}

    result = client.post("/orders/execute", json={"plan_id": plan["plan_id"],
                                                  "simulate_rejection_asset": "SOL"}).json()
    assert result["summary"]["PENDING"] == 3

    orders = client.get("/orders").json()
    assert orders["summary"] == {"PENDING": 0, "FILLED": 2, "REJECTED": 1}
    sol = next(o for o in orders["orders"] if o["asset"] == "SOL")
    assert client.get(f"/orders/{sol['order_id']}").json()["status"] == "REJECTED"

    assert client.post("/orders/execute", json={"plan_id": plan["plan_id"]}).status_code == 409
    assert client.post("/orders/execute", json={"plan_id": "nope"}).status_code == 404
    assert client.get("/orders/ORD-MISSING").status_code == 404

    # Recalculating after execution only re-proposes the rejected SOL order.
    follow_up = client.post("/rebalance").json()
    assert [o["asset"] for o in follow_up["orders"]] == ["SOL"]

    bad = client.post("/rebalance", json={"target_allocation": {"BTC": 50}})
    assert bad.status_code == 422

    client.post("/demo/reset")
    assert client.get("/orders").json()["orders"] == []
