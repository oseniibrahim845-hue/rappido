"""Order management: validation, ID assignment, submission and status tracking."""

from __future__ import annotations

import uuid
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterable, Optional

from .exchange_base import ExchangeAdapter, ExchangeError
from .models import (
    ExchangeOrder,
    ExecutionResult,
    ManagedOrder,
    OrderInstruction,
    OrderSide,
    OrderStatus,
)


class OrderValidationError(ValueError):
    """An order instruction failed pre-trade validation."""


class PlanAlreadyExecutedError(Exception):
    """A rebalance plan was submitted twice."""


class OrderManager:
    def __init__(
        self,
        exchange: ExchangeAdapter,
        *,
        min_order_value: Decimal = Decimal("10"),
        max_order_value: Decimal = Decimal("1000000"),
        max_price_deviation: Decimal = Decimal("0.05"),
    ) -> None:
        self.exchange = exchange
        self.min_order_value = min_order_value
        self.max_order_value = max_order_value
        self.max_price_deviation = max_price_deviation
        self._orders: dict[str, ManagedOrder] = {}
        self._executed_plans: set[str] = set()

    # -------------------------------------------------------------- validation

    def validate(self, instruction: OrderInstruction) -> None:
        """Basic pre-trade checks. Raises OrderValidationError on failure."""
        if instruction.side not in (OrderSide.BUY, OrderSide.SELL):
            raise OrderValidationError(f"Invalid side {instruction.side}")
        if instruction.quantity <= 0:
            raise OrderValidationError("Quantity must be positive")
        if instruction.reference_price <= 0:
            raise OrderValidationError("Reference price must be positive")
        if not (self.min_order_value <= instruction.estimated_value <= self.max_order_value):
            raise OrderValidationError(
                f"Order value {instruction.estimated_value} outside allowed range "
                f"[{self.min_order_value}, {self.max_order_value}]"
            )
        try:
            market_price = self.exchange.get_price(instruction.symbol)
        except ExchangeError as exc:
            raise OrderValidationError(str(exc)) from exc
        deviation = abs(market_price - instruction.reference_price) / instruction.reference_price
        if deviation > self.max_price_deviation:
            raise OrderValidationError(
                f"Market price moved {deviation:.1%} since the plan was calculated; recalculate"
            )

    # -------------------------------------------------------------- submission

    def submit_orders(self, plan_id: str, instructions: Iterable[OrderInstruction]) -> ExecutionResult:
        """Validate and submit each instruction. Invalid ones are recorded as REJECTED."""
        if plan_id in self._executed_plans:
            raise PlanAlreadyExecutedError(f"Plan {plan_id} has already been executed")
        self._executed_plans.add(plan_id)

        submitted: list[ManagedOrder] = []
        for instruction in instructions:
            now = datetime.now(timezone.utc)
            order = ManagedOrder(
                order_id=f"ORD-{uuid.uuid4().hex[:10].upper()}",
                plan_id=plan_id,
                asset=instruction.asset,
                symbol=instruction.symbol,
                side=instruction.side,
                quantity=instruction.quantity,
                estimated_value=instruction.estimated_value,
                status=OrderStatus.PENDING,
                created_at=now,
                updated_at=now,
            )
            try:
                self.validate(instruction)
                exchange_order = self.exchange.create_order(
                    client_order_id=order.order_id,
                    symbol=instruction.symbol,
                    side=instruction.side,
                    quantity=instruction.quantity,
                )
                order.exchange_order_id = exchange_order.exchange_order_id
                self._apply(order, exchange_order)
            except (OrderValidationError, ExchangeError) as exc:
                order.status = OrderStatus.REJECTED
                order.reject_reason = str(exc)
            self._orders[order.order_id] = order
            submitted.append(order)

        return ExecutionResult(plan_id=plan_id, orders=[o.model_copy() for o in submitted],
                               summary=self.summarize(submitted))

    # ---------------------------------------------------------------- tracking

    def refresh(self) -> None:
        """Poll the exchange for every order that is still PENDING."""
        for order in self._orders.values():
            if order.status is OrderStatus.PENDING and order.exchange_order_id:
                self._apply(order, self.exchange.get_order(order.exchange_order_id))

    def list_orders(self, plan_id: Optional[str] = None) -> list[ManagedOrder]:
        self.refresh()
        return [o.model_copy() for o in self._orders.values()
                if plan_id is None or o.plan_id == plan_id]

    def get_order(self, order_id: str) -> ManagedOrder:
        order = self._orders.get(order_id)
        if order is None:
            raise KeyError(order_id)
        if order.status is OrderStatus.PENDING and order.exchange_order_id:
            self._apply(order, self.exchange.get_order(order.exchange_order_id))
        return order.model_copy()

    @staticmethod
    def summarize(orders: Iterable[ManagedOrder]) -> dict[str, int]:
        counts = Counter(o.status.value for o in orders)
        return {status.value: counts.get(status.value, 0) for status in OrderStatus}

    @staticmethod
    def _apply(order: ManagedOrder, exchange_order: ExchangeOrder) -> None:
        order.status = exchange_order.status
        order.filled_quantity = exchange_order.filled_quantity
        order.average_price = exchange_order.average_price
        order.fee = exchange_order.fee
        order.reject_reason = exchange_order.reject_reason
        order.updated_at = exchange_order.updated_at
