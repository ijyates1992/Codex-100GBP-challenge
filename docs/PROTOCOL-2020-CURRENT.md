# Frozen continuous test: January 2020 to current date

The user requested a backtest from January 2020 to the current date. The current task date is 14 September 2026, a Monday. To avoid incorporating an incomplete trading session, this test is defined as **2020-01-01 00:00 inclusive through 2026-09-14 00:00 exclusive**. That includes the latest completed FX session, Friday 11 September 2026, and only the following weekend before Monday's session begins.

The EA source, binary and inputs are frozen at commit `07d51bca04a22e6fe36313d19c3972f078bc3a72`; this is the same strategy and configuration used by all prior results. Starting capital is £100 once. Capital, cash conversion-fee deductions, the equity peak, drawdown controls and risk state continue over the entire interval. There are no annual resets, optimisation runs, parameter changes or retuning.

The test uses Model 4, 100 ms delay, USDJPY H1, 0.01-lot minimum/step, 3.53% notional margin, the frozen conversion-fee assumption and existing entry/exit logic. It will preserve broker quote provenance, read back imported prices and minute bars, identify all missing-tick days, and retain a losing result if one occurs. Independent fill, currency-conversion and margin/capital audits are required after the native report.

This protocol was written before acquiring the missing 2023 history or running the selected interval.
