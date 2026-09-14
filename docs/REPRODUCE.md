# Reproduce the frozen result

Run from the repository root in PowerShell 7. This research installation uses the IG MT5 terminal and data directory recorded in `tools/tester.py`, `tools/compile.ps1` and `tools/import.ps1`. Adjust those paths on another VM. Use an IG **demo** installation. The EA rejects non-tester execution.

## Preserved data on this VM

The exact source data remain in `data/` on D:, excluded from Git because of their size. Preserve this directory together with the repository for byte-identical reproduction. `evidence/USDJPY-raw-manifest.json` and `evidence/gap-provenance.json` identify the original inputs by SHA-256. A source-only checkout does not contain the raw dataset and cannot independently reproduce the result until those inputs are restored. Broker history downloaded later can change; never silently substitute it for the frozen data.

```powershell
python -m pip install -r requirements.txt
python tools/audit_data.py
pwsh -File tools/import.ps1 -Expert ImportIG
pwsh -File tools/import.ps1 -Expert ImportGap
pwsh -File tools/compile.ps1
python tools/tester.py reproduction_01 GBP100_USDJPY
python tools/verify.py evidence/reproduction_01
python tools/audit_fills.py evidence/reproduction_01
python tools/audit_fx.py evidence/reproduction_01
python tools/audit_margin_reference.py evidence/reproduction_01
python tools/plot_result.py evidence/reproduction_01
```

Close MT5 before imports and tester runs. The Python currency audit may start a terminal; close that demo terminal before another tester run. Names must be fresh; the runner refuses to overwrite an existing evidence directory. Use native MT5 build 6182 for closest reproduction. Recompilation with another compiler build may change the EX5 hash; each run snapshots the exact source and binary actually used.

The runner explicitly writes **all** source input defaults, including unchanged values, to its INI and manifest. Overrides are accepted with `--inputs '{"RiskPercent":1.9}'`. It also accepts `--delay 500`. `config/final.json` and `config/final.set` contain the frozen selection. Verify that `effective_report_inputs_match` is true; MT5 can reuse saved tester inputs when an INI leaves them unspecified. The earlier `evidence/final` run is preserved as a rejected example of that fault, and is not the final result.

The acceptance check reconciles net fees, initial capital, reported fills, minimum lots, risk and margin sizing, drawdown and the known data fallback. The independent currency and capital checks are separate files. A passing accounting check does not remove the 586-minute price-path approximation or make the strategy validated out of sample.

## Wider-spread stress

The stress importers add 0.005 JPY (half a pip) to every ask and five points to every fallback bar spread, with unchanged bids. They verify imported prices against the originals plus this shift.

```powershell
pwsh -File tools/import.ps1 -Expert ImportStress
pwsh -File tools/import.ps1 -Expert ImportStressGap
python tools/tester.py stress_reproduction_01 GBP100_USDJPY_STRESS
python tools/verify.py evidence/stress_reproduction_01
```

`audit_fills.py` recognises the stress symbol and adds the same five-point ask shift when checking its fills.

## Acquisition and research records

`discover.py`, `history.py` and `export_ticks.py` inspect the demo environment and obtain broker history. `gap_minutes.py` obtains the missing day's minute bars; it also requires the H1 data produced by `history.py`. `build_gap.py` builds the hybrid day from cached IG M1 and the 14 Dukascopy BI5 hours listed in the frozen gap manifest. Restore exactly those files; additional downloaded hours produce a different experiment. Imports must replace ticks first, then minute bars, or MT5 can delete interior minutes without recorded ticks. The gap importer checks every minute OHLC after importing.

`screen.py`, `minute_screen.py`, `refine.py` and retained search CSVs document hypothesis generation. Native directories are authoritative execution evidence. Early tests have different cost, data and margin assumptions and must not be ranked directly against the completed tests. One-off `fix_*`, `upgrade.py` and other development scripts are retained as research history; do not run the whole tools directory as a pipeline.
