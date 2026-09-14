# Codex £100 Challenge

Repository: `ijyates1992/Codex-100GBP-challenge`

## Objective

Design, implement, test and optimise an automated trading system for MetaTrader 5 that achieves the **maximum possible growth from a starting balance of only £100 over a three-year backtest**, while keeping maximum equity drawdown at or below **30%**.

There is no specific profit target.

The objective is simply:

> **Finish the three-year test with the highest possible equity while never exceeding 30% maximum equity drawdown.**

You are responsible for researching, designing, implementing, testing and improving the strategy.

Do not ask the user to provide a trading strategy.

## Starting Conditions

* Starting balance: **£100**
* Account currency: **GBP**
* Maximum permitted equity drawdown: **30%**
* Test duration: **3 years**
* Test period: the most recent continuous three-year period for which reliable broker history is available, ending on the latest fully completed trading day
* Platform: **MetaTrader 5**
* Broker environment: **IG**
* Use realistic IG contract specifications, spreads, margin requirements, minimum trade sizes and symbol properties wherever available.

The system must remain tradable from the original £100 balance. Strategies which require capital unavailable to the account are invalid.

## Leverage and Margin

IG MT5 leverage is commonly **up to 200:1**, but this must **not** be assumed universally.

You must inspect and confirm the actual leverage, margin rate, contract specification and margin requirements applicable to each symbol used by the strategy.

Different symbols or asset classes may have different effective leverage or margin requirements.

Use the correct IG settings wherever the MT5 Strategy Tester permits this.

### Strategy Tester Leverage Limitations

MetaTrader 5's Strategy Tester may occasionally fail to reproduce the broker's true leverage or margin configuration correctly.

If the tester cannot be made to use the correct IG leverage despite reasonable attempts to configure it:

* use the **closest practical simulation available**;
* do not abandon an otherwise valid strategy solely because of a Strategy Tester leverage limitation;
* account for the real IG margin requirement separately where practical;
* ensure that the strategy would still have been executable on the real IG account with the equity available at the time;
* clearly document the discrepancy between the real IG leverage/margin requirement and the leverage or margin behaviour used by the tester.

The purpose is to reproduce real IG trading conditions as closely as reasonably possible, not to fail the challenge because of an MT5 tester limitation.

A test must not deliberately use favourable leverage assumptions that would make trades possible when they would not have been possible on the real IG account.

## Markets

You may trade **any symbol or combination of symbols available through IG**.

You are not restricted to symbols currently visible or configured in the MT5 terminal.

You may:

* discover additional IG symbols;
* add or enable symbols in MT5;
* download missing historical data;
* use multiple asset classes;
* trade multiple symbols simultaneously;
* decide dynamically which markets should be traded.

Potential markets include, but are not limited to:

* forex;
* equity indices;
* commodities;
* precious metals;
* energies;
* cryptocurrencies, where supported;
* other instruments available in the IG MT5 environment.

Symbol selection is part of the challenge.

## Strategy Freedom

There is deliberately **no prescribed trading strategy**.

You may research and test any legitimate systematic approach, including combinations of approaches.

You may modify or replace an unsuccessful strategy entirely.

You may create supporting scripts, research tools, data-analysis programs or optimisation infrastructure where useful.

Do not stop merely because an early strategy performs poorly.

Explore alternatives.

## Optimisation Goal

The primary ranking metric is:

**Final equity after the complete three-year test.**

Subject to:

**Maximum equity drawdown ≤ 30%.**

A system producing £10,000 with 29% maximum drawdown therefore beats one producing £5,000 with 10% maximum drawdown.

Risk efficiency may be considered during development, but the challenge is intentionally focused on achieving the greatest sustainable compounding possible within the drawdown ceiling.

## Backtesting Requirements

Prefer the highest-quality historical data available.

Where practical:

* use real tick data;
* obtain missing history automatically;
* validate symbol specifications;
* account for realistic spreads and trading costs;
* verify leverage and margin requirements for every traded symbol;
* ensure trades could actually have been executed with the available equity and margin;
* avoid assumptions which artificially improve the result.

The final result must cover the **entire three-year period**, not merely favourable portions of it.

## Drawdown

The hard limit is:

**30% maximum equity drawdown.**

Equity drawdown is used rather than balance drawdown because open-position risk matters.

Any candidate exceeding 30% maximum equity drawdown fails the challenge regardless of its final profit.

Design sufficient safety controls to prevent catastrophic account loss.

## Capital Constraints

The £100 starting balance is intentionally restrictive.

The system must respect:

* broker minimum position sizes;
* available margin;
* actual symbol-specific leverage or margin rates;
* margin call / stop-out constraints;
* commissions and spreads;
* the ability to place the proposed trade with the equity actually available at that point in the test.

Do not simulate fractional positions that IG/MT5 could not actually execute.

Position sizing should adapt as the account grows.

If Strategy Tester limitations require an imperfect leverage simulation, independently verify that the resulting trades would still have been possible under the real IG margin conditions.

## Invalid Results

Do not count results which rely on:

* future information or look-ahead bias;
* corrupted or misaligned historical data;
* impossible fills;
* trades below the broker's permitted minimum size;
* margin that would not actually have been available;
* deliberately favourable or unrealistic leverage assumptions;
* tester or platform exploits;
* deliberately selecting only profitable fragments of the required test period;
* changing historical decisions using information that would only have become available later.

Normal strategy optimisation and historical research are permitted.

A documented Strategy Tester leverage mismatch is **not** by itself grounds for invalidating a result, provided the closest practical simulation was used and real-world IG margin feasibility was independently checked.

## Development Approach

Work autonomously.

You are expected to:

1. inspect the repository and MT5 environment;
2. inspect available IG instruments, leverage, margin and trading specifications;
3. obtain whatever historical market data is required;
4. research candidate strategies;
5. implement promising approaches;
6. backtest them;
7. analyse weaknesses;
8. improve, combine or replace strategies;
9. repeat the process while meaningful improvements remain;
10. retain the strongest valid system discovered.

Do not assume that the first profitable strategy is the best one.

The challenge rewards exploration.

## Deliverables

The repository should contain everything required to understand and reproduce the final result, including:

* EA source code;
* compiled EA where appropriate;
* supporting scripts/tools;
* configuration or parameter files;
* strategy documentation;
* backtest reports;
* relevant optimisation results;
* instructions for reproducing the final test.

Document the final result clearly, including:

* starting balance;
* final balance/equity;
* total return;
* compound growth;
* maximum equity drawdown;
* profit factor;
* number of trades;
* symbols traded;
* test dates;
* modelling/data quality;
* actual IG leverage/margin requirements for traded symbols;
* Strategy Tester leverage used;
* any leverage or margin simulation discrepancies;
* important risk controls;
* strategy overview.

Also record important unsuccessful approaches where they provide useful evidence about why the final design was selected.

## Final Instruction

Starting with only **£100**, find the fastest-growing automated trading approach you can discover that survives the complete three-year test while remaining within **30% maximum equity drawdown**.

You have complete freedom over strategy and market selection.

Research broadly, test aggressively, reject weak ideas and continue improving the system.

Where MT5 prevents an exact recreation of IG leverage, use the closest defensible approximation and verify real-world margin feasibility separately.

**Maximise the final equity.**
