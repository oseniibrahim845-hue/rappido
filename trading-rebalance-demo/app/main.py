"""FastAPI application for the Trading Rebalance Execution Demo.

SIMULATED EXECUTION ONLY: all orders go to an in-memory MockExchange.
"""

from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .mock_exchange import MockExchange, make_sample_exchange
from .models import ExecuteRequest, ExecutionResult, ManagedOrder, RebalancePlan, RebalanceRequest
from .order_manager import OrderManager, PlanAlreadyExecutedError
from .rebalance_engine import QUOTE_ASSET, RebalanceError, calculate_rebalance

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

SAMPLE_PORTFOLIO_VALUE = Decimal("100000")
SAMPLE_PRICES = {"BTC": Decimal("65000"), "ETH": Decimal("3200"),
                 "SOL": Decimal("150"), "USDC": Decimal("1")}
SAMPLE_CURRENT = {"BTC": Decimal("30"), "ETH": Decimal("40"),
                  "SOL": Decimal("10"), "USDC": Decimal("20")}
SAMPLE_TARGET = {"BTC": Decimal("40"), "ETH": Decimal("30"),
                 "SOL": Decimal("20"), "USDC": Decimal("10")}


class DemoState:
    """Holds the mock exchange, order manager and calculated plans."""

    def __init__(self, fill_delay_seconds: float, fill_stagger_seconds: float) -> None:
        self.fill_delay_seconds = fill_delay_seconds
        self.fill_stagger_seconds = fill_stagger_seconds
        self.reset()

    def reset(self) -> None:
        self.exchange: MockExchange = make_sample_exchange(
            SAMPLE_CURRENT, SAMPLE_PORTFOLIO_VALUE, SAMPLE_PRICES,
            quote_asset=QUOTE_ASSET,
            fill_delay_seconds=self.fill_delay_seconds,
            fill_stagger_seconds=self.fill_stagger_seconds,
        )
        self.manager = OrderManager(self.exchange)
        self.plans: dict[str, RebalancePlan] = {}
        self.target = dict(SAMPLE_TARGET)

    def live_portfolio(self) -> dict:
        balances = self.exchange.get_balance()
        values = {a: q * SAMPLE_PRICES[a] for a, q in balances.items()}
        total = sum(values.values(), Decimal("0"))
        holdings = [
            {
                "asset": asset,
                "quantity": balances[asset],
                "price": SAMPLE_PRICES[asset],
                "value": values[asset].quantize(Decimal("0.01")),
                "pct": (values[asset] / total * 100).quantize(Decimal("0.0001")),
            }
            for asset in balances
        ]
        return {"portfolio_value": total.quantize(Decimal("0.01")), "holdings": holdings}


def _jsonable(portfolio: dict) -> dict:
    """Convert Decimals to floats for JSON responses."""
    def conv(v):
        if isinstance(v, Decimal):
            return float(v)
        if isinstance(v, dict):
            return {k: conv(x) for k, x in v.items()}
        if isinstance(v, list):
            return [conv(x) for x in v]
        return v
    return conv(portfolio)


def create_app(fill_delay_seconds: float = 2.0, fill_stagger_seconds: float = 1.0) -> FastAPI:
    app = FastAPI(
        title="Trading Rebalance Execution Demo",
        description="Technical proof of concept using simulated exchange execution. "
                    "Not connected to live trading accounts.",
        version="0.1.0",
    )
    state = DemoState(fill_delay_seconds, fill_stagger_seconds)
    app.state.demo = state

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "exchange": state.exchange.name, "mode": "simulated"}

    @app.get("/portfolio")
    def portfolio() -> dict:
        live = state.live_portfolio()
        current = {h["asset"]: h["pct"] for h in live["holdings"]}
        return _jsonable({
            **live,
            "quote_asset": QUOTE_ASSET,
            "prices": SAMPLE_PRICES,
            "current_allocation": current,
            "target_allocation": state.target,
        })

    @app.post("/rebalance", response_model=RebalancePlan)
    def rebalance(request: Optional[RebalanceRequest] = None) -> RebalancePlan:
        request = request or RebalanceRequest()
        live = state.live_portfolio()
        try:
            plan = calculate_rebalance(
                current_allocation=request.current_allocation
                or {h["asset"]: h["pct"] for h in live["holdings"]},
                target_allocation=request.target_allocation or state.target,
                portfolio_value=request.portfolio_value or live["portfolio_value"],
                prices=request.prices or SAMPLE_PRICES,
                quote_asset=QUOTE_ASSET,
            )
        except RebalanceError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        state.plans[plan.plan_id] = plan
        return plan

    @app.post("/orders/execute", response_model=ExecutionResult)
    def execute(request: ExecuteRequest) -> ExecutionResult:
        plan = state.plans.get(request.plan_id)
        if plan is None:
            raise HTTPException(status_code=404, detail="Unknown plan_id; calculate a rebalance first")
        state.exchange.clear_rejection_rules()
        if request.simulate_rejection_asset:
            asset = request.simulate_rejection_asset.upper()
            state.exchange.set_rejection_rule(
                f"{asset}/{QUOTE_ASSET}",
                f"Simulated rejection: {asset}/{QUOTE_ASSET} market unavailable (demo scenario)",
            )
        try:
            return state.manager.submit_orders(plan.plan_id, plan.orders)
        except PlanAlreadyExecutedError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.get("/orders")
    def list_orders(plan_id: Optional[str] = None) -> dict:
        orders = state.manager.list_orders(plan_id)
        return {
            "orders": [o.model_dump(mode="json") for o in orders],
            "summary": state.manager.summarize(orders),
        }

    @app.get("/orders/{order_id}", response_model=ManagedOrder)
    def get_order(order_id: str) -> ManagedOrder:
        try:
            return state.manager.get_order(order_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Order not found") from None

    @app.post("/demo/reset")
    def reset() -> dict:
        state.reset()
        return {"status": "reset"}

    if FRONTEND_DIR.is_dir():
        @app.get("/", include_in_schema=False)
        def index() -> FileResponse:
            return FileResponse(FRONTEND_DIR / "index.html")

        app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    return app


app = create_app(
    fill_delay_seconds=float(os.getenv("MOCK_FILL_DELAY", "2.0")),
    fill_stagger_seconds=float(os.getenv("MOCK_FILL_STAGGER", "1.0")),
)
