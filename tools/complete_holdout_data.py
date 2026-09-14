"""Audit 2022 data and retry any empty weekdays before recording M1 fallback."""
from pathlib import Path
import argparse, datetime as dt, hashlib, json
import MetaTrader5 as mt5
import numpy as np

p=argparse.ArgumentParser();p.add_argument('--dataset',default='USDJPY2022');p.add_argument('--label',default='holdout2022');args=p.parse_args()
root=Path(__file__).resolve().parents[1];base=root/'data/replay'/args.dataset
manifest_path=root/'evidence'/(args.dataset+'-raw-manifest.json')
manifest=json.loads(manifest_path.read_text());fallback=[];retries=[];holidays=[]
assert mt5.initialize() and mt5.account_info().trade_mode==0
for item in manifest['days']:
    day=dt.datetime.strptime(item['day'],'%Y%m%d').replace(tzinfo=dt.timezone.utc)
    if item['ticks'] or day.weekday()>4:continue
    parts=[]
    for hour in range(0,24,6):
        start=day+dt.timedelta(hours=hour)
        q=mt5.copy_ticks_range('USDJPY',start,start+dt.timedelta(hours=6)-dt.timedelta(milliseconds=1),mt5.COPY_TICKS_ALL)
        assert q is not None,mt5.last_error()
        retries.append({'day':item['day'],'hour':hour,'ticks':len(q)})
        if len(q):parts.append(q)
    if parts:
        raise RuntimeError('Retry recovered quotes; preserve and rebuild this day before proceeding')
    rates=mt5.copy_rates_range('USDJPY',mt5.TIMEFRAME_M1,day,day+dt.timedelta(days=1)-dt.timedelta(seconds=1))
    if rates is not None and len(rates)==0 and (day.month,day.day) in [(1,1),(12,25)]:
        holidays.append(item['day']);continue
    assert rates is not None and len(rates)>0,('No M1 coverage',item['day'],mt5.last_error())
    assert rates['time'][0]>=day.timestamp() and rates['time'][-1]<(day+dt.timedelta(days=1)).timestamp()
    np.save(base/(item['day']+'-ig-m1.npy'),rates)
    arr=np.array([[r['time'],*[int(round(r[k]*1000)) for k in ['open','high','low','close']],r['tick_volume'],max(10,r['spread'])] for r in rates],dtype='i8')
    bars=base/(item['day']+'.bars');np.savetxt(bars,arr,fmt='%d',delimiter=';')
    item['bars']=len(arr);item['bars_sha256']=hashlib.sha256(bars.read_bytes()).hexdigest()
    item['fallback']='Observed IG M1; generated intraminute paths; spread at least 0.010 JPY'
    fallback.append({'day':item['day'],'minutes':len(arr),'source_sha256':hashlib.sha256((base/(item['day']+'-ig-m1.npy')).read_bytes()).hexdigest()})
mt5.shutdown()
manifest['fallback']=fallback;manifest['empty_weekday_retries']=retries;manifest['empty_holidays']=holidays
manifest_path.write_text(json.dumps(manifest,indent=2))
for item in manifest['days']:
    for ext,key in [('ticks','sha256'),('bars','bars_sha256')]:
        assert hashlib.sha256((base/(item['day']+'.'+ext)).read_bytes()).hexdigest()==item[key]
result={'all_hashes_match':True,'days':len(manifest['days']),'recorded_quotes':sum(x['ticks'] for x in manifest['days']),'fallback':fallback,'generated_minutes':sum(x['minutes'] for x in fallback),'empty_holidays':holidays}
(root/'evidence'/(args.label+'-data-integrity.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
