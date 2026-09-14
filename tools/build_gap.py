"""Complete the absent IG tick day with recorded ticks and explicit M1 fallback."""
from pathlib import Path
import numpy as np, lzma, datetime as dt, json, hashlib

base = Path('data/gap')
out = Path('data/replay/Gap')
out.mkdir(parents=True, exist_ok=True)
D = np.dtype([('ms','>u4'),('ask','>u4'),('bid','>u4'),('av','>f4'),('bv','>f4')])
O = np.dtype([('time_msc','<i8'),('bid','<i4'),('ask','<i4')])
m1 = np.load(base/'ig-m1.npy')
day = int(dt.datetime(2025,1,14,tzinfo=dt.timezone.utc).timestamp())
parts, hours = [], []
for hour in range(24):
    f = base/f'{hour:02}.bi5'
    if not f.exists():
        continue
    body = f.read_bytes()
    raw = np.frombuffer(lzma.decompress(body), dtype=D)
    assert len(raw) and np.all(raw['bid']>0) and np.all(raw['ask']>=raw['bid'])
    assert np.all(raw['ms']<3600000)
    q = np.empty(len(raw), dtype=O)
    q['time_msc'] = (day+hour*3600)*1000+raw['ms'].astype('i8')
    q['bid'], q['ask'] = raw['bid'], raw['ask']+10
    parts.append(q)
    hours.append(dict(hour=hour, url=f'https://datafeed.dukascopy.com/datafeed/USDJPY/2025/00/14/{hour:02}h_ticks.bi5', sha256=hashlib.sha256(body).hexdigest(), ticks=len(q)))
r = np.concatenate(parts)
assert np.all(np.diff(r['time_msc'])>=0)
r.tofile(out/'20250114.ticks')
bars = {int(v['time']): [int(v['time']), *[int(round(v[k]*1000)) for k in ['open','high','low','close']], int(v['tick_volume']), max(10,int(v['spread']))] for v in m1}
realhours = {x['hour'] for x in hours}
bars = {t:b for t,b in bars.items() if (t-day)//3600 not in realhours}
minute = r['time_msc']//60000*60
starts = np.r_[0,np.flatnonzero(np.diff(minute))+1]
ends = np.r_[starts[1:],len(r)]
for i,j in zip(starts,ends):
    q = r[i:j]
    bars[int(minute[i])] = [minute[i],q['bid'][0],q['bid'].max(),q['bid'].min(),q['bid'][-1],j-i,int(np.median(q['ask']-q['bid']))]
arr = np.array([bars[k] for k in sorted(bars)], dtype='i8')
np.savetxt(out/'20250114.bars', arr, fmt='%d', delimiter=';')
(out/'import-list.txt').write_text('20250114\n')
meta = dict(date='2025-01-14', reason='IG recorded quotes absent; IG M1 matches all original H1 OHLC exactly', recorded_tick_source='Dukascopy HTTPS', recorded_hours=hours, recorded_tick_count=len(r), recorded_minutes=len(starts), fallback_minutes=len(arr)-len(starts), fallback_hours=[h for h in range(24) if h not in realhours], fallback_source='IG-DEMO M1 OHLC; native generated paths in these minutes only', costs='Recorded ask +0.010 JPY; fallback spread at least 0.010 JPY', ticks_sha256=hashlib.sha256((out/'20250114.ticks').read_bytes()).hexdigest(), bars_sha256=hashlib.sha256((out/'20250114.bars').read_bytes()).hexdigest())
Path('evidence/gap-provenance.json').write_text(json.dumps(meta,indent=2))
print({k:v for k,v in meta.items() if k!='recorded_hours'})
