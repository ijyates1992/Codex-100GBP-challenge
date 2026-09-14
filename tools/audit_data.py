"""Verify preserved data bytes against acquisition manifests before reproducing."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'evidence/USDJPY-raw-manifest.json').read_text())
ticks=0
for day in manifest['days']:
    base=root/'data/replay/USDJPY'/day['day']
    t=base.with_suffix('.ticks').read_bytes()
    b=base.with_suffix('.bars').read_bytes()
    assert hashlib.sha256(t).hexdigest()==day['sha256'],str(base)
    assert hashlib.sha256(b).hexdigest()==day['bars_sha256'],str(base)
    assert len(t)==day['ticks']*16,str(base)
    ticks+=day['ticks']
gap=json.loads((root/'evidence/gap-provenance.json').read_text())
for ext in ['ticks','bars']:
    raw=(root/f'data/replay/Gap/20250114.{ext}').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==gap[ext+'_sha256']
for hour in gap['recorded_hours']:
    raw=(root/f'data/gap/{hour["hour"]:02}.bi5').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==hour['sha256']
summary={'all_pass':True,'ig_days':len(manifest['days']),'ig_recorded_ticks':ticks,'gap_recorded_ticks':gap['recorded_tick_count'],'gap_generated_minutes':gap['fallback_minutes']}
(root/'evidence/data-integrity.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
