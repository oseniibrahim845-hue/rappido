# Slave: resolve master symbols on the follower broker (symbol mapping)

## What and why

`ImentoreSlave` uses the symbol name sent by the server exactly as the master reported it (`orderdataparse[12]` in `UpdateSlavePositionOrders()`). When the follower broker names the instrument differently, for example `EURUSD.m`, `EURUSDpro`, `GOLD` for `XAUUSD` or `DJ30` for `US30`:

- every `OrderSend` for that symbol fails, and the slave retries it on every tick/timer cycle
- `GetSymbolDigits()` falls back to 2 digits and `NormalizeNumber()` rounds SL/TP with 0 digits, because the symbol does not exist locally

This PR adds a small symbol resolution step on the slave side, so one master can be copied to brokers that use suffixes, prefixes or different names.

## How it works

`UpdateSlavePositionOrders()` now calls `ResolveSlaveSymbol(orderdataparse[12])`. Then it uses the resolved name for `symbol`, `symbolDigits` and the SL/TP normalization. Resolution order:

1. **Explicit mapping** from `InputSymbolMapping` (the master name is matched case-insensitively)
2. **Prefix/suffix**: `InputSymbolPrefix + master + InputSymbolSuffix`, then the same with the master's base name (so `EURUSD.a` with suffix `.m` becomes `EURUSD.m`)
3. **Exact name**: the master symbol itself
4. **Auto detect** (if `InputSymbolAutoDetect = true`): it scans `SymbolsTotal(false)` for a tradeable symbol with the same base name. The base name is the alphanumeric core in upper case: `EURUSD.m` gives `EURUSD`, and `#US30` gives `US30`. It also accepts a short letter-only tail on either side (`EURUSDpro`, `EURUSDm`). A tail with digits is rejected, so `US30` never matches `US300`. Exact base matches are preferred. If there are several candidates, the choice is logged.

Other behavior:

- **Cache**: one entry per master symbol, so the lookup runs once and not on every tick. The cache is cleared in `OnInit` (`SlaveSymbolInit()`), so changing the inputs takes effect right away.
- **Market Watch**: the resolved symbol is added with `SymbolSelect(..., true)`. On a cache hit it is selected again if it was removed. `MakeOrderPreCheck()` calls `SymbolSelect(order.symbol, false)` when the connection drops, so without this a reconnect could leave the symbol without quotes.
- **Logging** (through `AddCommentOnChart`, so it goes to the chart, the Experts tab and the log file):
  - each mapping that changes the name is logged once, e.g. `SymbolMapping - XAUUSD -> GOLD (mapping)`
  - an unresolved symbol is logged once with a hint: `Symbol XAUUSD not found on this broker. Set InputSymbolMapping (ex: XAUUSD=BROKER_SYMBOL) ...`
  - invalid mapping entries are logged and skipped
  - the active configuration is logged at startup
- **Fallback**: if nothing matches, the master name is returned unchanged, so the result is the same as before this PR. Unresolved symbols are retried after 60 seconds (`SlaveSymbolRetrySeconds`), so a symbol the broker adds later is picked up without a restart.

## Inputs added (ImentoreSlave)

| Input | Default | Example |
|---|---|---|
| `InputSymbolMapping` | `""` | `XAUUSD=GOLD;US30=DJ30;NAS100=USTEC` |
| `InputSymbolPrefix` | `""` | `m.` |
| `InputSymbolSuffix` | `""` | `.m`, `pro`, `.ecn` |
| `InputSymbolAutoDetect` | `false` | set `true` to auto-find suffixed names (EURUSD -> EURUSD.m) |

Mapping targets must be the exact symbol name on the follower broker, as shown in Market Watch.

## Files

- `MQL/Imentore/MT5/Lib/ImentoreLib-13.mqh`: new globals (`SlaveSymbol*`) and functions (`SlaveSymbolInit`, `ResolveSlaveSymbol`, `SlaveSymbolFind`, `SlaveSymbolAutoFind`, plus small helpers). `UpdateSlavePositionOrders()` changes in 3 lines.
- `MQL/Imentore/MT5/ImentoreSlave-3.00-04.mq5`: 4 inputs, and 5 lines in `OnInit` to pass them to the lib.

I edited the latest files in place so the diff is easy to review. I did not bump `VERSION_UPDATE`/`LIB_UPDATE` and did not create new versioned files (`ImentoreSlave-3.00-05`, `ImentoreLib-14`). If you prefer that convention, I can rename them, or you can do it when you merge. `ImentoreCopy` and the MT4 code are not changed. The Copy EA includes the same lib but never calls `UpdateSlavePositionOrders()`, so its behavior does not change.

## Backward compatibility

- With the default inputs, a symbol that exists on the follower broker resolves to itself (step 3), so existing setups behave exactly as before.
- Auto detect only runs when the exact name does **not** exist. Today that case always fails.
- No server/API or message format change. Note: the slave reports `PositionOrders` back to the server with the **resolved** (local) symbol name. History orders already report the local deal symbol, so this is consistent. Please confirm the backend does not match slave positions by symbol name.

## How to test (demo, two brokers)

1. Open a demo on broker A (master, e.g. plain `EURUSD`, `XAUUSD`) and a demo on broker B (follower) that uses a suffix or other names (many brokers have `EURUSD.m`/`EURUSDm`, `GOLD`, `DJ30`/`US30.cash`).
2. Copy `Lib/ImentoreLib-13.mqh` to `MQL5/Include/ImentoreLib.mqh` on terminal B (and the matching Common/Settings includes as usual). Compile `ImentoreSlave-3.00-04.mq5`.
3. **Auto detect**: set `InputSymbolAutoDetect = true`, open `EURUSD` on the master. On the slave, the log should show `SymbolMapping - EURUSD -> EURUSD.m (auto detect)` and the order should open on `EURUSD.m` with the correct SL/TP digits.
4. **Explicit mapping**: set `InputSymbolMapping = XAUUSD=GOLD` and open `XAUUSD` on the master. Expect `XAUUSD -> GOLD (mapping)`.
5. **Suffix**: set `InputSymbolAutoDetect = false`, `InputSymbolSuffix = .m`, and open `EURUSD`. Expect `(prefix/suffix)`.
6. **Unresolved**: set auto detect to false, leave the mapping empty, and trade a symbol broker B does not have. Expect one `not found on this broker` message, not a message on every tick.
7. **Regression**: run the slave on a broker with identical names. There should be no `SymbolMapping ->` lines and trading should be unchanged.
8. **Modify/close**: change SL/TP on the master and close the position. Check that the slave modifies and closes the mapped position.

## Limitations / notes

- **Not compiled.** I wrote this without a MetaEditor build in this environment, so please compile before merging. I kept to standard MQL5 calls (`SymbolExist`, `SymbolSelect`, `SymbolsTotal`, `SymbolName`, `SymbolInfoInteger`, `StringSplit`, `StringTrimLeft/Right`, `StringGetCharacter`). `SymbolExist` needs build 2085 or later.
- Auto detect is a heuristic. If a broker has several variants (`EURUSD.m`, `EURUSD.ecn`), it picks the first exact-base match and logs the alternatives. Set `InputSymbolMapping` or the suffix to make the choice explicit. It can also match crypto-style names like `BTCUSD` to `BTCUSDT`. It is off by default so nothing changes unless you opt in.
- No lot scaling or contract size conversion between brokers (e.g. GOLD 100 oz vs 10 oz). That is a separate open area and would make a good follow-up PR.
- MT4 (`MQL/Imentore/MT4`) is not covered by this PR.
