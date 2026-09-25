# Demo Notes

**This is a technical proof of concept using simulated exchange execution. It is not connected to live trading accounts.**

## What is demonstrated

- An automatic rebalance calculation from current and target allocations, portfolio value
  and prices, using Decimal arithmetic, lot-size rounding and a minimum trade threshold.
- Structured BUY/SELL order generation. SELLs are sequenced first so they fund the BUYs.
  The stablecoin is treated as the settlement (quote) asset.
- An `OrderManager` that validates orders, generates order IDs, submits them through an
  adapter, tracks their status and guards against duplicate plan execution.
- An `ExchangeAdapter` interface (`get_balance`, `get_price`, `create_order`, `get_order`)
  with a `MockExchange` implementation.
- The order lifecycle: `PENDING` → `FILLED`, a simulated `REJECTED` order, and
  insufficient-balance rejection.
- A FastAPI backend, a small HTML/CSS/JS dashboard, and 25 automated tests.

## Intentionally not included

- AQMath or any other proprietary allocation model integration
- Real exchange integrations (Binance, Kraken, etc.) and real API credentials
- The non-custodial architecture and client-side signing
- Production authentication, database, deployment and monitoring
- Real money execution
- WebSocket streaming infrastructure
- Complete risk management, portfolio management and security systems

## Paid production phase

- Integration with the client's allocation engine (AQMath) as the target-allocation source
- Production exchange adapters on the existing `ExchangeAdapter` interface
- The agreed non-custodial / client-side signing architecture
- Limit orders, partial fills, order slicing, cancel/replace and retry handling
- Real-time order and balance updates over exchange WebSocket streams
- Persistent storage for plans, orders and fills, with an audit trail
- Risk limits, pre-trade checks and kill switches
- Authentication, secrets management, deployment, monitoring and alerting
