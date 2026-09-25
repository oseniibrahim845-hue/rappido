"""Portfolio rebalance calculation.

Given current and target allocations (in percent), a portfolio value and
asset prices, compute per-asset drift and the BUY / SELL orders required to
move the portfolio to its target.

The quote asset (USDC by default) is the settlement currency: every order is
priced against it, so it is not traded directly. Its balance changes as the
net result of the other orders (sells add to it, buys draw from it).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal
from typing import Mapping, Optional, Union

from .models import (
    AllocationRow,
    OrderInstruction,
    OrderSide,
    RebalanceAction,
    RebalancePlan,
)

Number = Union[Decimal, int, float, str]

QUOTE_ASSET = "USDC"
DEFAULT_MIN_TRADE_VALUE = Decimal("10")
ALLOCATION_TOLERANCE = Decimal("0.01")  # percentage points

# Exchange lot sizes: quantities are rounded DOWN to these increments so we
# never try to trade more than the calculated amount.
DEFAULT_STEP_SIZES: dict[str, Decimal] = {
    "BTC": Decimal("0.00001"),
    "ETH": Decimal("0.0001"),
    "SOL": Decimal("0.01"),
    "USDC": Decimal("0.01"),
}
FALLBACK_STEP_SIZE = Decimal("0.00000001")

CENT = Decimal("0.01")


class RebalanceError(ValueError):
    """Raised when rebalance inputs are invalid."""


def _dec(value: Number) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def round_down(quantity: Decimal, step: Decimal) -> Decimal:
    """Round a quantity down to the nearest exchange lot size."""
    return (quantity / step).to_integral_value(rounding=ROUND_DOWN) * step


def _normalise_allocation(name: str, allocation: Mapping[str, Number]) -> dict[str, Decimal]:
    if not allocation:
        raise RebalanceError(f"{name} allocation is empty")
    result: dict[str, Decimal] = {}
    for asset, pct in allocation.items():
        pct = _dec(pct)
        if pct < 0:
            raise RebalanceError(f"{name} allocation for {asset} is negative")
        result[asset.upper()] = pct
    total = sum(result.values(), Decimal("0"))
    if abs(total - Decimal("100")) > ALLOCATION_TOLERANCE:
        raise RebalanceError(f"{name} allocation must sum to 100% (got {total}%)")
    return result


def calculate_rebalance(
    current_allocation: Mapping[str, Number],
    target_allocation: Mapping[str, Number],
    portfolio_value: Number,
    prices: Mapping[str, Number],
    *,
    quote_asset: str = QUOTE_ASSET,
    step_sizes: Optional[Mapping[str, Decimal]] = None,
    min_trade_value: Number = DEFAULT_MIN_TRADE_VALUE,
) -> RebalancePlan:
    """Calculate the rebalance plan.

    Allocations are percentages (``30`` means 30%). Prices are per unit in the
    quote asset. Returns a :class:`RebalancePlan` with one row per asset and
    the order instructions, SELLs first so their proceeds can fund the BUYs.
    """
    current = _normalise_allocation("Current", current_allocation)
    target = _normalise_allocation("Target", target_allocation)
    value = _dec(portfolio_value)
    if value <= 0:
        raise RebalanceError("Portfolio value must be positive")
    min_trade = _dec(min_trade_value)
    steps = {**DEFAULT_STEP_SIZES, **(step_sizes or {})}
    quote_asset = quote_asset.upper()
    price_map = {asset.upper(): _dec(p) for asset, p in prices.items()}

    assets = list(dict.fromkeys([*current, *target]))
    for asset in assets:
        if asset not in price_map:
            raise RebalanceError(f"Missing price for {asset}")
        if price_map[asset] <= 0:
            raise RebalanceError(f"Price for {asset} must be positive")

    rows: list[AllocationRow] = []
    orders: list[OrderInstruction] = []
    quote_row: Optional[dict] = None
    net_quote_change = Decimal("0")

    for asset in assets:
        price = price_map[asset]
        cur_pct = current.get(asset, Decimal("0"))
        tgt_pct = target.get(asset, Decimal("0"))
        cur_value = value * cur_pct / 100
        tgt_value = value * tgt_pct / 100
        diff_value = tgt_value - cur_value

        base = dict(
            asset=asset,
            price=price,
            current_pct=cur_pct,
            target_pct=tgt_pct,
            diff_pct=tgt_pct - cur_pct,
            current_value=_money(cur_value),
            target_value=_money(tgt_value),
            diff_value=_money(diff_value),
        )

        if asset == quote_asset:
            quote_row = base
            continue

        quantity = round_down(abs(diff_value) / price, steps.get(asset, FALLBACK_STEP_SIZE))
        estimated = _money(quantity * price)

        if quantity == 0 or estimated < min_trade:
            rows.append(AllocationRow(**base, action=RebalanceAction.HOLD,
                                      quantity=Decimal("0"), estimated_value=Decimal("0")))
            continue

        side = OrderSide.BUY if diff_value > 0 else OrderSide.SELL
        net_quote_change += estimated if side is OrderSide.SELL else -estimated
        rows.append(AllocationRow(**base, action=RebalanceAction(side.value),
                                  quantity=quantity, estimated_value=estimated))
        orders.append(OrderInstruction(
            asset=asset,
            symbol=f"{asset}/{quote_asset}",
            side=side,
            quantity=quantity,
            reference_price=price,
            estimated_value=estimated,
            current_pct=cur_pct,
            target_pct=tgt_pct,
        ))

    warnings: list[str] = []
    quote_price = price_map.get(quote_asset, Decimal("1"))
    if quote_row is None:
        quote_row = dict(asset=quote_asset, price=quote_price, current_pct=Decimal("0"),
                         target_pct=Decimal("0"), diff_pct=Decimal("0"),
                         current_value=Decimal("0"), target_value=Decimal("0"),
                         diff_value=Decimal("0"))
    rows.append(AllocationRow(
        **quote_row,
        action=RebalanceAction.QUOTE,
        quantity=round_down(abs(net_quote_change) / quote_price, steps.get(quote_asset, CENT)),
        estimated_value=net_quote_change,
    ))
    if quote_row["current_value"] + net_quote_change < 0:
        warnings.append(
            f"Buys exceed available {quote_asset} plus sell proceeds; "
            "some BUY orders may be rejected."
        )

    # Sells first (they free up quote currency), largest first within a side.
    orders.sort(key=lambda o: (o.side is OrderSide.BUY, -o.estimated_value))

    return RebalancePlan(
        plan_id=f"PLAN-{uuid.uuid4().hex[:8].upper()}",
        created_at=datetime.now(timezone.utc),
        portfolio_value=_money(value),
        quote_asset=quote_asset,
        rows=rows,
        orders=orders,
        net_quote_change=net_quote_change,
        warnings=warnings,
    )
