# Reproduce the continuous 2020 to current-date test

This test is fixed at 1 January 2020 inclusive through 14 September 2026 exclusive, which ends after Friday 11 September's completed session. It is not an intraday test of Monday 14 September. The EA and settings were frozen before new 2023 data acquisition; see `PROTOCOL-2020-CURRENT.md`.

The large linked data directories under `data/replay/` are excluded from Git. Preserve those raw inputs and their manifests. `USDJPY2020_current` is composed using NTFS hard links from the preexisting dated sources, so do not remove source datasets while reproducing the combined test.

```powershell
python tools/assemble_continuous.py --dataset USDJPY2020_current --start 2019-12-20 --end 2026-09-14 --sources config/sources-2020-current.json
python tools/audit_continuous_data.py USDJPY2020_current --fallbacks '{"2021.10.01":1375,"2022.03.01":1440,"2025.01.14":586}'
python tools/prepare_holdout.py --dataset USDJPY2020_current --symbol GBP100_USDJPY_2020_CURRENT --expert ImportHoldout2020Current
pwsh -File tools/import.ps1 -Expert ImportHoldout2020Current
python tools/tester.py holdout_2020_current_repeat GBP100_USDJPY_2020_CURRENT --start 2020.01.01 --end 2026.09.14
python tools/verify.py evidence/holdout_2020_current_repeat --start 2020.01.01 --end 2026.09.14 --fallbacks '{"2021.10.01":1375,"2022.03.01":1440,"2025.01.14":586}'
python tools/annual_results.py evidence/holdout_2020_current_repeat
python tools/audit_fills.py evidence/holdout_2020_current_repeat
python tools/audit_fx.py evidence/holdout_2020_current_repeat
python tools/audit_margin_reference.py evidence/holdout_2020_current_repeat
python tools/plot_result.py evidence/holdout_2020_current_repeat --modeled-minutes 3401
```

Use a fresh dataset name if the existing combined directory is present; the assembler refuses to overwrite data. It also uses its explicit source-list order for overlapping warm-up days. Keep the 2025 gap patch ahead of the raw USDJPY source so that 14 January 2025 retains the independent ticks and declared M1 fallback. MT5 must be closed before import or tester operations.

The frozen strategy takes two Christmas positions over a weekend. This is expected from the recorded result and makes the strict acceptance check fail; do not alter the EA simply to reproduce a passing test.
