# Reproduce the frozen continuous £500 test

Run from the repository root on the designated MT5 development VM. The linked datasets in `data/replay/` are intentionally excluded from Git; retain the dated source datasets and their evidence manifests.

```powershell
python tools/assemble_continuous.py --dataset USDJPY2019_2026_GBP500 --start 2018-12-20 --end 2026-09-14 --sources config/sources-2019-2026-gbp500.json
python tools/audit_continuous_data.py USDJPY2019_2026_GBP500 --fallbacks '{"2021.10.01":1375,"2022.03.01":1440,"2025.01.14":586}'
python tools/prepare_holdout.py --dataset USDJPY2019_2026_GBP500 --symbol GBP500_USDJPY_2019_2026 --expert ImportHoldout2019_2026_GBP500
pwsh -NoProfile -File tools/import.ps1 -Expert ImportHoldout2019_2026_GBP500
python tools/tester.py holdout_2019_2026_gbp500 GBP500_USDJPY_2019_2026 --start 2019.01.01 --end 2026.09.14 --deposit 500
python tools/verify.py evidence/holdout_2019_2026_gbp500 --start 2019.01.01 --end 2026.09.14 --deposit 500 --fallbacks '{"2021.10.01":1375,"2022.03.01":1440,"2025.01.14":586}'
python tools/annual_results.py evidence/holdout_2019_2026_gbp500
python tools/audit_fills.py evidence/holdout_2019_2026_gbp500
python tools/audit_fx.py evidence/holdout_2019_2026_gbp500
python tools/audit_margin_reference.py evidence/holdout_2019_2026_gbp500
python tools/plot_result.py evidence/holdout_2019_2026_gbp500 --modeled-minutes 3401
```

The verifier is expected to report the result as it is produced. It is not an optimisation loop: do not amend inputs after inspecting the output.
