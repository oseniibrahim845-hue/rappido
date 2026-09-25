"""In-memory exchange used for the demo. No network, no keys, no real funds.

Orders are accepted as PENDING and settle after a configurable delay, the
next time the exchange is queried. Settlement either FILLS the order at the
current mock price (moving balances and charging a fee) or REJECTS it, for
example on insufficient balance or a configured rejection rule.
"""

from __future__ import annotations

import itertools
import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import Callable, Mapping

from .exchange_base import ExchangeAdapter, ExchangeError
from .models import ExchangeOrder, OrderSide, OrderStatus

BALANCE_PRECISION = Decimal("0.00000001")


def _now() -> datetime:
    return datetime.now(timezone.utc)


class MockExchange(ExchangeAdapter):
    name = "mock"

    def __init__(
        self,
        balances: Mapping[str, Decimal],
        prices: Mapping[str, Decimal],
        *,
        quote_asset: str = "USDC",
        fee_rate: Decimal = Decimal("0.001"),
        fill_delay_seconds: float = 0.0,
        fill_stagger_seconds: float = 0.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.quote_asset = quote_asset
        self.fee_rate = Decimal(str(fee_rate))
        self.fill_delay_seconds = fill_delay_seconds
        self.fill_stagger_seconds = fill_stagger_seconds
        self._clock = clock
        self._balances = {a: Decimal(str(q)) for a, q in balances.items()}
        self._prices = {a: Decimal(str(p)) for a, p in prices.items()}
        self._orders: dict[str, ExchangeOrder] = {}
        self._settle_at: dict[str, float] = {}
        self._rejection_rules: dict[str, str] = {}
        self._ids = itertools.count(1)

    # ------------------------------------------------------------------ config

    def set_rejection_rule(self, symbol: str, reason: str) -> None:
        """Force every order for ``symbol`` to be rejected on settlement."""
        self._rejection_rules[symbol] = reason

    def clear_rejection_rules(self) -> None:
        self._rejection_rules.clear()

    def set_price(self, asset: str, price: Decimal) -> None:
        self._prices[asset] = Decimal(str(price))

    # --------------------------------------------------------------- interface

    def get_balance(self) -> dict[str, Decimal]:
        self._settle_due_orders()
        return dict(self._balances)

    def get_price(self, symbol: str) -> Decimal:
        base, _ = self._parse_symbol(symbol)
        return self._prices[base]

    def create_order(
        self,
        *,
        client_order_id: str,
        symbol: str,
        side: OrderSide,
        quantity: Decimal,
    ) -> ExchangeOrder:
        self._parse_symbol(symbol)
        quantity = Decimal(str(quantity))
        if quantity <= 0:
            raise ExchangeError("Quantity must be positive")
        if any(o.client_order_id == client_order_id for o in self._orders.values()):
            raise ExchangeError(f"Duplicate client order id {client_order_id}")

        now = _now()
        order = ExchangeOrder(
            exchange_order_id=f"MOCK-{next(self._ids):06d}",
            client_order_id=client_order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            status=OrderStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        pending = sum(1 for o in self._orders.values() if o.status is OrderStatus.PENDING)
        self._orders[order.exchange_order_id] = order
        self._settle_at[order.exchange_order_id] = (
            self._clock() + self.fill_delay_seconds + pending * self.fill_stagger_seconds
        )
        return order.model_copy()

    def get_order(self, exchange_order_id: str) -> ExchangeOrder:
        self._settle_due_orders()
        try:
            return self._orders[exchange_order_id].model_copy()
        except KeyError:
            raise ExchangeError(f"Unknown order {exchange_order_id}") from None

    # --------------------------------------------------------------- internals

    def _parse_symbol(self, symbol: str) -> tuple[str, str]:
        base, sep, quote = symbol.partition("/")
        if not sep or quote != self.quote_asset or base not in self._prices or base == quote:
            raise ExchangeError(f"Unsupported symbol {symbol}")
        return base, quote

    def _settle_due_orders(self) -> None:
        now = self._clock()
        # Dicts keep insertion order, so orders settle in submission order.
        for order_id, order in self._orders.items():
            if order.status is OrderStatus.PENDING and self._settle_at[order_id] <= now:
                self._settle(order)

    def _settle(self, order: ExchangeOrder) -> None:
        order.updated_at = _now()
        if order.symbol in self._rejection_rules:
            self._reject(order, self._rejection_rules[order.symbol])
            return

        base, quote = self._parse_symbol(order.symbol)
        price = self._prices[base]
        notional = order.quantity * price
        fee = (notional * self.fee_rate).quantize(BALANCE_PRECISION)

        if order.side is OrderSide.BUY:
            cost = notional + fee
            available = self._balances.get(quote, Decimal("0"))
            if available < cost:
                self._reject(order, f"Insufficient {quote} balance "
                                    f"(required {cost:.2f}, available {available:.2f})")
                return
            self._balances[quote] = available - cost
            self._balances[base] = self._balances.get(base, Decimal("0")) + order.quantity
        else:
            available = self._balances.get(base, Decimal("0"))
            if available < order.quantity:
                self._reject(order, f"Insufficient {base} balance "
                                    f"(required {order.quantity}, available {available})")
                return
            self._balances[base] = available - order.quantity
            self._balances[quote] = self._balances.get(quote, Decimal("0")) + notional - fee

        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.average_price = price
        order.fee = fee

    @staticmethod
    def _reject(order: ExchangeOrder, reason: str) -> None:
        order.status = OrderStatus.REJECTED
        order.reject_reason = reason


def make_sample_exchange(
    allocation: Mapping[str, Decimal],
    portfolio_value: Decimal,
    prices: Mapping[str, Decimal],
    **kwargs,
) -> MockExchange:
    """Build a MockExchange whose balances match a percentage allocation."""
    balances = {
        asset: (Decimal(str(portfolio_value)) * Decimal(str(pct)) / 100
                / Decimal(str(prices[asset]))).quantize(BALANCE_PRECISION)
        for asset, pct in allocation.items()
    }
    return MockExchange(balances, prices, **kwargs)


__all__ = ["MockExchange", "make_sample_exchange", "ExchangeError"]
