"""Exchange adapter interface.

Every venue integration (the in-memory MockExchange here; Binance, Kraken,
etc. in a production build) implements this interface, so the OrderManager
never depends on a specific exchange.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal

from .models import ExchangeOrder, OrderSide


class ExchangeError(Exception):
    """Raised when an exchange refuses a request (bad symbol, bad quantity, ...)."""


class ExchangeAdapter(ABC):
    name: str = "base"

    @abstractmethod
    def get_balance(self) -> dict[str, Decimal]:
        """Return available balances keyed by asset."""

    @abstractmethod
    def get_price(self, symbol: str) -> Decimal:
        """Return the current price for a symbol such as ``BTC/USDC``."""

    @abstractmethod
    def create_order(
        self,
        *,
        client_order_id: str,
        symbol: str,
        side: OrderSide,
        quantity: Decimal,
    ) -> ExchangeOrder:
        """Submit a market order. Returns the accepted order (normally PENDING)."""

    @abstractmethod
    def get_order(self, exchange_order_id: str) -> ExchangeOrder:
        """Return the latest state of a previously submitted order."""
