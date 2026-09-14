"""Create a byte-linked continuous replay dataset from frozen dated sources."""
from pathlib import Path
import argparse, datetime as dt, hashlib, json, os

p=argparse.ArgumentParser();p.add_argument('--dataset',required=True);p.add_argument('--start',required=True);p.add_argument('--end',required=True);p.add_argument('--sources',required=True);args=p.parse_args()
root=Path(__file__).resolve().parents[1];target=root/'data/replay'/args.dataset
assert not target.exists(),f'Refusing to overwrite {target}'
sources=json.loads((root/args.sources).read_text())
start=dt.datetime.fromisoformat(args.start).replace(tzinfo=dt.timezone.utc);end=dt.datetime.fromisoformat(args.end).replace(tzinfo=dt.timezone.utc)
target.mkdir(parents=True);days=[];source_hashes={}
for item in sources:
    manifest=root/item['manifest'];source_hashes[item['manifest']]=hashlib.sha256(manifest.read_bytes()).hexdigest()
    data=json.loads(manifest.read_text())
    if item.get('format')=='gap':
        day=data['date'].replace('-','')
        data={'days':[{'day':day,'ticks':data['recorded_tick_count'],'bars':sum(1 for _ in (root/item['directory']/(day+'.bars')).open()),'sha256':data['ticks_sha256'],'bars_sha256':data['bars_sha256'],'fallback':f"{data['fallback_minutes']} observed IG M1 bars with generated intraminute paths; remaining ticks from independent provider"}]}
    for day in data['days']:
        stamp=dt.datetime.strptime(day['day'],'%Y%m%d').replace(tzinfo=dt.timezone.utc)
        if start<=stamp<end:
            # Adjacent sources overlap only for warm-up. Earlier entries in the
            # explicit source list are authoritative for a duplicated day.
            if any(x['day']==day['day'] for x in days):continue
            src=root/item['directory'];out=dict(day,source_directory=item['directory'],source_manifest=item['manifest'])
            for ext,key in [('ticks','sha256'),('bars','bars_sha256')]:
                original=src/(day['day']+'.'+ext);linked=target/(day['day']+'.'+ext)
                assert original.exists() and hashlib.sha256(original.read_bytes()).hexdigest()==day[key],original
                os.link(original,linked)
                assert hashlib.sha256(linked.read_bytes()).hexdigest()==day[key]
            (target/(day['day']+'.json')).write_text(json.dumps(out))
            days.append(out)
expected=[];cursor=start
while cursor<end:
    expected.append(cursor.strftime('%Y%m%d'));cursor+=dt.timedelta(days=1)
have={x['day'] for x in days}
for day in expected:
    if day not in have:
        out={'day':day,'ticks':0,'bars':0,'sha256':hashlib.sha256(b'').hexdigest(),'bars_sha256':hashlib.sha256(b'').hexdigest(),'empty_calendar_day':True}
        (target/(day+'.ticks')).write_bytes(b'');(target/(day+'.bars')).write_bytes(b'');(target/(day+'.json')).write_text(json.dumps(out));days.append(out)
days.sort(key=lambda x:x['day'])
(target/'import-list.txt').write_text('\n'.join(x['day'] for x in sorted(days,key=lambda x:(bool(x.get('fallback')),x['day'])) )+'\n')
result={'dataset':args.dataset,'start':args.start,'end':args.end,'source_manifests_sha256':source_hashes,'days':days,'recorded_ticks':sum(x['ticks'] for x in days),'fallback_days':[{'day':x['day'],'minutes':x.get('bars',0),'description':x.get('fallback')} for x in days if x.get('fallback')],'empty_calendar_days':[x['day'] for x in days if x.get('empty_calendar_day')]}
(root/'evidence'/(args.dataset+'-manifest.json')).write_text(json.dumps(result,indent=2))
print(json.dumps({'days':len(days),'recorded_ticks':result['recorded_ticks'],'fallback_days':result['fallback_days'],'empty_calendar_days':result['empty_calendar_days']},indent=2))
