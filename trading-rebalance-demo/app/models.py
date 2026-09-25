"""Shared domain and API models.

Monetary values and quantities are held as ``Decimal`` internally to avoid
floating-point drift, and serialised as plain JSON numbers for the frontend.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, Field, PlainSerializer

Num = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class RebalanceAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    QUOTE = "QUOTE"  # settlement asset: changes as a result of the other trades


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    REJECTED = "REJECTED"


# --------------------------------------------------------------------------
# Rebalance engine output
# --------------------------------------------------------------------------


class AllocationRow(BaseModel):
    asset: str
    price: Num
    current_pct: Num
    target_pct: Num
    diff_pct: Num
    current_value: Num
    target_value: Num
    diff_value: Num
    action: RebalanceAction
    quantity: Num
    estimated_value: Num


class OrderInstruction(BaseModel):
    asset: str
    symbol: str
    side: OrderSide
    quantity: Num
    reference_price: Num
    estimated_value: Num
    current_pct: Num
    target_pct: Num


class RebalancePlan(BaseModel):
    plan_id: str
    created_at: datetime
    portfolio_value: Num
    quote_asset: str
    rows: list[AllocationRow]
    orders: list[OrderInstruction]
    net_quote_change: Num
    warnings: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------
# Exchange / order lifecycle
# --------------------------------------------------------------------------


class ExchangeOrder(BaseModel):
    """An order as seen by an exchange adapter."""

    exchange_order_id: str
    client_order_id: str
    symbol: str
    side: OrderSide
    quantity: Num
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    filled_quantity: Num = Decimal("0")
    average_price: Optional[Num] = None
    fee: Num = Decimal("0")
    reject_reason: Optional[str] = None


class ManagedOrder(BaseModel):
    """An order as tracked by the OrderManager (our side of the lifecycle)."""

    order_id: str
    plan_id: str
    asset: str
    symbol: str
    side: OrderSide
    quantity: Num
    estimated_value: Num
    status: OrderStatus
    exchange_order_id: Optional[str] = None
    filled_quantity: Num = Decimal("0")
    average_price: Optional[Num] = None
    fee: Num = Decimal("0")
    reject_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ExecutionResult(BaseModel):
    plan_id: str
    orders: list[ManagedOrder]
    summary: dict[str, int]


# --------------------------------------------------------------------------
# API request bodies
# --------------------------------------------------------------------------


class RebalanceRequest(BaseModel):
    """All fields optional: omitted values fall back to the live demo portfolio."""

    current_allocation: Optional[dict[str, Decimal]] = None
    target_allocation: Optional[dict[str, Decimal]] = None
    portfolio_value: Optional[Decimal] = None
    prices: Optional[dict[str, Decimal]] = None


class ExecuteRequest(BaseModel):
    plan_id: str
    # Asset whose order the mock exchange will reject, to demonstrate the
    # REJECTED path. Set to null to let every valid order fill.
    simulate_rejection_asset: Optional[str] = "SOL"
