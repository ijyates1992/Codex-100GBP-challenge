# Previously untested year: frozen protocol

Recorded before acquiring the new year's prices or running its strategy test.

- Select calendar **2022**, 2022-01-01 inclusive through 2023-01-01 exclusive. This predates the research history beginning September 2023 and is a full non-overlapping calendar year.
- Frozen EA and inputs: commit `b29d9586c58929c358b9741dd957e10175d0a767`, `src/Challenge.mq5`, `src/Challenge.ex5`, and `config/final.json`. Do not optimise or change strategy after seeing results.
- Starting balance £100 GBP; same 100 ms execution delay, Model 4, 0.01 lot minimum/step, 3.53% notional margin simulation, margin buffer and 0.8% cash conversion costs.
- Acquire IG USDJPY recorded bid/ask ticks, with warm-up from 2021-12-20. Create a separate research symbol and read back imported quotes. Retain daily hashes and disclose any gaps or generated-tick substitution.
- Report final balance/equity, net return, tick-observed maximum equity drawdown, net profit factor, trades, costs, margin feasibility and data quality. A negative result is retained without retuning.
- This is an untouched historical-year test of this project, not a prospective live or demo result. Historical IG margin rates remain approximated by the frozen observed rate.
