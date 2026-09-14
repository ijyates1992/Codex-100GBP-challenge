# Results and selection

The frozen baseline is `final_verified`: £492.59 final equity from £100, 26.7025% maximum tick-observed equity drawdown, 853 trades and 1.2032 net profit factor. All 30 acceptance checks pass. It exactly reproduces `complete_01` using the final 1.10 source with every input specified. The £100 starting balance is the only positive cash transfer.

## Comparable complete-data native runs

All rows below use the full three-year period, the completed hybrid gap day, conversion fees deducted from cash, real lot increments and buffered IG margin. The baseline has 100 ms execution delay.

| Evidence directory | Change from baseline | Final GBP | Maximum equity DD |
|---|---|---:|---:|
| complete_01 / final_verified | Selected 1.25 ATR stop, 2% risk | 492.59 | 26.70% |
| complete_02 | Risk 2.1% | 110.23 | 28.94% |
| complete_03 | Risk 2.2% | 328.84 | 28.58% |
| complete_04 | Risk 1.9% | 440.30 | 27.21% |
| complete_05 | Stop 1.125 ATR | 94.05 | 28.84% |
| complete_06 | Stop 1.375 ATR | 383.19 | 27.05% |
| complete_07 | Stop 2 ATR, risk 2.5%, margin cap 80% | 478.40 | 24.68% |
| complete_08 | Stop 2 ATR, risk 2.75%, margin cap 80% | 112.96 | 28.66% |
| stress_final | Every ask widened by half a pip | 100.69 | 28.74% |

Risk changes affect which trades meet the minimum lot and drawdown-headroom tests, so outcomes are discontinuous. The spread stress retained only 234 trades and a 1.003 net profit factor. It remained inside the drawdown cap but lost almost all baseline growth. Both parameter sensitivity and cost sensitivity are material weaknesses. No parameters were retuned after the frozen stress result.

## Execution and capital evidence

The baseline has 1,706 fills. Of these, 1,705 match preserved quotes within the documented report timestamp tolerance; one lies within the declared gap-day M1 price bounds. All 468 stress fills match the original quotes with the specified ask shift. This bounds-check is weaker evidence than an exact recorded quote for the one baseline fallback fill.

The native tester reports a 99% margin-call threshold and 50% stop-out, consistent with the observed IG demo account. Every executed entry satisfies the independent buffered margin formula and the minimum-volume rule. The separate GBPJPY valuation and capital ledger use recorded conversion quotes where available, with adverse M1 bounds for missing quotes. They audit the fixed executed fills, not a new counterfactual strategy simulation.

The completed reference ledger closes at **£492.48849**, only £0.10151 below the native net result. All 853 entries have sufficient independently valued cash; maximum reference margin/cash is 52.18%. Two gap-day entry/exit quotes require adverse M1 bounds. The largest individual matched-trade valuation difference is £0.02217.

## Rejected and superseded evidence

The initial H1 search tested 106,920 configurations across 66 markets with sufficient history and affordable minimum sizes. It covered breakout, mean-reversion and momentum families. Those approximate rankings selected hypotheses for native testing, rather than establishing accepted results. The strongest native development path was long USDJPY momentum.

`tick_usdjpy_01` advertised 100% real ticks but logged 462 discard warnings. This motivated independent raw-quote replay. Early `replay_*` runs also preceded repair of a small-value conversion probe that rounded to pennies and inflated the inferred margin. `corrected_*` are pre-conversion-fee experiments. `costed_*` introduced actual cash fee deductions. `refined_*` preceded correction of the importer's missing interior bars, and `complete_*` repeat the relevant selections with all 1,426 gap-day minute bars present. These stages must not be ranked as though their assumptions were identical.

The directory named `final` is **rejected**, despite its name. MT5 used saved settings (including Lookback 4 and StopATR 2) when an empty inputs section was supplied. It produced £170.56. Its updated acceptance file correctly fails the effective-inputs check. The runner now explicitly writes every input, and `final_verified` is the final baseline.

## Conclusion

The selected system meets the numerical challenge within the disclosed historical simulation: 392.59% net return and less than 30% equity drawdown. The recorded-data gap, historical margin-rate assumption, extensive in-sample selection, sharp parameter sensitivity and failed growth under modest spread stress prevent a claim of robust future performance. No untouched holdout, forward demo, live result or provable global optimum is claimed.
