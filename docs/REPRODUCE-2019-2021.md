# Reproduce the continuous 2019–2021 test

The strategy source, binary and final inputs remain frozen at commit `80296254c8105ac59b8b6bc4f140d7a49669c37e`. See `PROTOCOL-2019-2021.md`. This test starts from £100 once on 1 January 2019 and ends at 1 January 2022; capital and the equity peak do not reset at year boundaries.

Preserve `data/replay/USDJPY2019_2021` with its acquisition manifest and import evidence. The large raw dataset is excluded from Git. Do not silently replace frozen inputs with later broker downloads. Terminal locations are configured in the existing import and tester tools.

With the preserved data present and MT5 closed:

```powershell
python tools/prepare_holdout.py --dataset USDJPY2019_2021 --symbol GBP100_USDJPY_2019_2021 --expert ImportHoldout2019_2021
pwsh -File tools/import.ps1 -Expert ImportHoldout2019_2021
Copy-Item data/replay/USDJPY2019_2021/import-result.txt evidence/holdout2019_2021-import-result.txt
python tools/tester.py holdout_2019_2021_repeat GBP100_USDJPY_2019_2021 --start 2019.01.01 --end 2022.01.01
```

Use a new report name for each run. The runner writes every frozen input explicitly and checks the installed binary. Run the acceptance, fill, currency, margin and annual-result audits listed in the final results document. Profitability and drawdown are outcome checks; a failed outcome must remain recorded rather than being tuned away.

To acquire a separate new dataset, the acquisition commands are:

```powershell
python tools/export_ticks.py --start 2018-12-20 --end 2022-01-01 --dataset USDJPY2019_2021
# Close MT5 before changing its history capacity, then let the audit reopen it.
python tools/set_history_limit.py --max-bars 5000000
python tools/complete_holdout_data.py --dataset USDJPY2019_2021 --label holdout2019_2021
```

The increased history capacity permits date-checked M1 queries back to 2018, including independent conversion bounds if necessary. Empty weekdays receive four six-hour tick retries. Any unavailable normal trading day requires explicit recorded M1 fallback and disclosure; empty Christmas/New Year holidays are recorded separately. The importer processes fallback days last and verifies quote timestamps/prices and minute OHLC after import.
