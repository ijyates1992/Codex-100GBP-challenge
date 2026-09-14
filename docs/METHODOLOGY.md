# Research protocol and limitations

The challenge is £100 GBP initial capital, maximum 30% peak-to-trough **equity** drawdown, and the greatest final equity discovered in a continuous three-year test. The research window is 2023-09-12 00:00 through 2026-09-12 00:00 exclusive, including the latest completed FX trading day, Friday 2026-09-11. This is 1,096 calendar days. Warm-up history starts 2023-09-01.

The GitHub repository was empty when cloned. There was no base commit. All work is local; publishing was not requested.

## Broker and capital

`evidence/broker.json` records the IG-DEMO symbol inventory and account properties without account credentials. The account is GBP, reports leverage 1:200, margin call 99%, and stop-out 50%. That account leverage is not the effective leverage of every instrument. At discovery, minimum USDJPY volume 0.01 required approximately £26.02 margin. Gold, Nasdaq and several other markets were unaffordable from £100 at their minimum sizes.

For USDJPY the contract is 100,000 USD per lot, with minimum and step 0.01 lot. Measured margin divided by GBP notional is approximately 3.52%. The reconstructed research symbol uses a **3.53% notional CFD margin rate**, approximately 1:28.33 effective leverage, and JPY margin currency. This is an explicit simulation of the measured margin, independent of the tester's nominal 1:200 account setting. No increased leverage is used to enable otherwise unaffordable positions.

The EA additionally applies a 15% margin buffer and a £2,602-per-lot floor. It uses the greater of native calculated margin and this independent requirement. Position size is rounded down to 0.01, and skipped when minimum size exceeds risk or margin budgets. The drawdown headroom further reduces the per-trade risk budget. One position is allowed at a time.

## Data integrity

The first native USDJPY Model=4 report advertised 100% real ticks but its journal contained 462 tick-discard warnings. This is rejected as clean quote evidence. MetaQuotes documents that inconsistent or missing real ticks may be replaced with generated ticks: [testing documentation](https://www.mql5.com/en/docs/runtime/testing).

IG's recorded quotes were exported independently using `CopyTicksRange`. All timestamps and bid/ask values were retained; no interpolation was used. Prices are stored in native 0.001 JPY units. Minute bars were reconstructed from the **same** quotes. The importer creates a separate research symbol and verifies every imported quote by reading it back. The original broker symbols are untouched. The export contains 70,421,527 quotes including warm-up, with daily hashes in `evidence/USDJPY-raw-manifest.json`. `evidence/import-result.txt` records complete quote comparisons.

IG returned no quotes for 2025-01-14, including four independent six-hour retries. It did supply 1,426 observed minute bars; their hourly aggregation exactly matched the original H1 history. The patch uses 113,465 independent Dukascopy quotes for 14 hours, downloaded over HTTPS, with one pip added to each ask. The remaining **586 minutes** use IG's observed M1 bars and a minimum one-pip spread. Native generated-tick paths in those minutes are an explicit approximation, not clean recorded-tick evidence. Provenance, hashes, requested URLs and hour coverage are in `evidence/gap-provenance.json`. The independent provider rate-limited the remaining requests after partial download. The patched test does not skip that day.

Currency conversion uses the tester's GBPJPY history. Its journal contains generated-tick fallback for this conversion symbol even though the trading symbol's quotes are reconstructed. The completed independent audit matches 852 of 853 closed trades to recorded GBPJPY quotes; the missing day's entry and exit use adverse IG M1 conversion bounds. The full independent cash ledger closes at £492.48849, £0.10151 below native net cash. All 853 entries remain margin-feasible, with maximum reference margin/cash 52.18%. This values the same executed fills; it does not independently resimulate decisions using alternative conversion quotes. See `final_verified/reference-capital-validation.json` and its ledger.

The full-gap importer replaces ticks first, then bars, and verifies every minute OHLC. Reversing that order can cause MT5 to remove interior minutes without recorded ticks. The hourly price cross-check found median OHLC difference zero and 99th percentile 0.009 JPY across 18,784 matched hours; six hours differed by more than 0.1 JPY, and none by more than 1%. These checks support plausibility without proving perfect data.

## Trading costs and drawdown accounting

Actual variable bid/ask spreads are retained for IG quotes. The independent day has the additional spread allowances above. The EA closes at 20:00 quote time, with no intended overnight holdings. Report deals are checked for overnight exposure and broker lot-grid compliance.

IG publishes conversion charges when instrument and account currencies differ. The [UK charges page](https://www.ig.com/uk/charges) states 0.8%, while its [conversion help article](https://www.ig.com/uk/help-and-support/articles/681702-what-are-ig-s-currency-conversion-fees-for-spread-bet-or-cfd-accounts) states 0.7%. We use the more conservative **0.8% of absolute realised P/L**, rounded to pennies, on gains and losses. The demo tester's zero commission setting alone is insufficient proof that conversion is free.

These costs are deducted from simulated cash using [TesterWithdrawal](https://www.mql5.com/en/docs/common/testerwithdrawal). They therefore reduce subsequent sizing and available margin. No deposits or capital injections are made. Every deduction is in `fees.csv` and the report deal ledger. Native report trading profit excludes these cash deductions: **use `stats.csv` and the reconciled closing balance for net results**.

Native withdrawal-adjusted drawdown statistics can understate the equity decline relevant to this challenge. The EA records peak equity and maximum relative decline independently on every `OnTick`, and the reported drawdown is the greater of that value and native tester drawdown. Hourly snapshots are in `equity.csv`. Profit factor in `stats.csv` is calculated from individual trades after the fee deduction.

## Search and interpretation

The first H1 screen evaluated 106,920 configurations across 66 affordable markets with sufficient bars, testing breakout, mean-reversion and momentum families. It was a hypothesis screen, not accepted execution evidence. The reconstructed USDJPY minute screen compared long, short and combined directions, stop/target distances, horizons and risk. Subsequent searches refined promising settings. Native reports, including unsuccessful runs, are retained.

This is extensive **in-sample optimisation**. The whole period influenced selection. No untouched holdout, forward demo or live performance is claimed. The strongest discovered historical configuration is not proof of a global maximum or future profitability. Circuit breakers cannot guarantee a drawdown ceiling through unobserved gaps or live slippage; the measured three-year result, rather than the existence of the control, determines acceptance.

The source currently deliberately runs in Strategy Tester only. The deliverable is a reproducible research system, not a validated live deployment.

After freezing that baseline, the user requested an untouched-year test. Calendar 2022 was selected before acquiring its prices, using the exact frozen source, binary and inputs. Its separate protocol, results and data limitations are documented in `UNTESTED-YEAR-PROTOCOL.md` and `RESULTS-2022.md`. The initial search discussion above describes the three-year development result; the later 2022 experiment provides a distinct historical holdout.

The user's subsequent request tested the preceding three calendar years, 2019–2021, continuously from £100 without annual resets. It lost 22.97%, remaining within 28.76% drawdown but taking no trades after June 2019. `RESULTS-2019-2021.md` preserves this negative result, its independent audits and the 1,375-minute price-data fallback. No strategy retuning followed either historical holdout.
