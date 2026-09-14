# Reproduce the untouched 2022 test

The strategy was frozen at `b29d9586c58929c358b9741dd957e10175d0a767` before acquiring 2022 prices. The year predates every native test and the screening history in this project. See `UNTESTED-YEAR-PROTOCOL.md` for the pre-test selection. No parameter search was run on 2022.

The preserved data are under `data/replay/USDJPY2022`, separate from the baseline. IG supplied 41,155,534 quotes including warm-up from 20 December 2021. All quotes and reconstructed bars were hashed. The sole empty weekday, 1 March 2022, remained empty after four six-hour retries. Its 1,440 observed IG minute bars were retained with at least a one-pip spread and explicitly generated intraminute paths. The importer reads back all imported quotes and OHLC bars. It imports the missing-tick day last so later tick replacement cannot remove those minute bars.

From the repository root, with the preserved inputs present and MT5 closed:

```powershell
python tools/prepare_holdout.py
pwsh -File tools/import.ps1 -Expert ImportHoldout2022
Copy-Item data/replay/USDJPY2022/import-result.txt evidence/holdout2022-import-result.txt
python tools/tester.py holdout_2022_repeat GBP100_USDJPY_2022 --start 2022.01.01 --end 2023.01.01
python tools/verify.py evidence/holdout_2022_repeat --start 2022.01.01 --end 2023.01.01 --fallback-minutes 1440 --fallback-day 2022.03.01
python tools/audit_fills.py evidence/holdout_2022_repeat
python tools/audit_fx.py evidence/holdout_2022_repeat
python tools/audit_margin_reference.py evidence/holdout_2022_repeat
python tools/plot_result.py evidence/holdout_2022_repeat --modeled-minutes 1440
```

The runner checks that the installed EX5 matches `src/Challenge.ex5`; use the frozen binary or compile the unchanged source with the documented compiler. Its manifest records every effective input and the year's own data provenance. Use a new name for each run. A losing test may return a nonzero acceptance exit code because profitability is an explicit outcome check; still run and retain the independent execution and accounting audits.

For reacquisition on the IG demo terminal, use `export_ticks.py --start 2021-12-20 --end 2023-01-01 --dataset USDJPY2022` followed by `complete_holdout_data.py`. Reacquired broker history may differ. Compare all hashes to the frozen manifest before treating a new dataset as equivalent. Preserve the original manifests rather than overwriting them during a new experiment.
