"""Verify a combined linked replay dataset and expose its modeled-minute scope."""
from pathlib import Path
import argparse,hashlib,json

p=argparse.ArgumentParser();p.add_argument('dataset');p.add_argument('--fallbacks',required=True);args=p.parse_args()
root=Path(__file__).resolve().parents[1];manifest=json.loads((root/'evidence'/(args.dataset+'-manifest.json')).read_text());base=root/'data/replay'/args.dataset
for day in manifest['days']:
    for ext,key in [('ticks','sha256'),('bars','bars_sha256')]:
        raw=(base/(day['day']+'.'+ext)).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==day[key],day['day']
fallbacks=json.loads(args.fallbacks)
result={'all_hashes_match':True,'days':len(manifest['days']),'recorded_ticks':manifest['recorded_ticks'],'modeled_minutes_by_day':fallbacks,'total_modeled_minutes':sum(fallbacks.values()),'empty_calendar_days':manifest['empty_calendar_days'],'source_manifests_sha256':manifest['source_manifests_sha256']}
(root/'evidence'/(args.dataset+'-data-integrity.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
