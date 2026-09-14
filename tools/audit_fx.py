"""Independently compare native JPY-to-GBP valuation against recorded GBPJPY quotes."""
from pathlib import Path
import MetaTrader5 as m,pandas as pd,numpy as np,datetime as dt,json,argparse
p=argparse.ArgumentParser();p.add_argument('folder');a=p.parse_args();base=Path(a.folder)
d=pd.read_csv(base/'deals.csv');d=d[d.direction.isin(['in','out'])].copy();d['ts']=pd.to_datetime(d.time,format='%Y.%m.%d %H:%M:%S',utc=True).map(lambda v:int(v.timestamp()))
manifest=json.loads((base/'manifest.json').read_text())
start=dt.datetime.strptime(manifest['start'],'%Y.%m.%d').replace(tzinfo=dt.timezone.utc).timestamp()
end=dt.datetime.strptime(manifest['end'],'%Y.%m.%d').replace(tzinfo=dt.timezone.utc).timestamp()
assert d.ts.min()>=start and d.ts.max()<end, 'Deal timestamps must be seconds within the tested interval'
assert m.initialize();assert m.account_info().trade_mode==0
cache=Path('data/fx-audit');cache.mkdir(parents=True,exist_ok=True);rows=[]
for day,group in d.groupby(d.ts//86400):
 file=cache/(str(day)+'.npy')
 if file.exists():q=np.load(file)
 else:
  q=m.copy_ticks_range('GBPJPY',dt.datetime.fromtimestamp(int(day*86400),dt.timezone.utc),dt.datetime.fromtimestamp(int((day+1)*86400),dt.timezone.utc)-dt.timedelta(milliseconds=1),m.COPY_TICKS_ALL)
  if q is None:raise RuntimeError(m.last_error())
  np.save(file,q)
 for _,r in group.iterrows():
  ix=np.searchsorted(q['time_msc'],r.ts*1000+999,side='right')-1 if len(q)else -1
  if ix<0:rows.append(dict(deal=r.deal,time=r.time,bid=None,ask=None,age_seconds=None));continue
  rows.append(dict(deal=r.deal,time=r.time,bid=float(q['bid'][ix]),ask=float(q['ask'][ix]),age_seconds=float((r.ts*1000+999-q['time_msc'][ix])/1000)))
x=pd.DataFrame(rows);x.to_csv(base/'independent-fx-quotes.csv',index=False);merged=d.merge(x,on=['deal','time']);pairs=[];opened=None
for _,r in merged.iterrows():
 if r.direction=='in':opened=r
 elif opened is not None:
  jpy=(r.price-opened.price)*(1 if opened['type']=='buy'else -1)*opened.volume*100000
  ref=jpy/(r.ask if jpy>=0 else r.bid) if r.bid and r.ask else float('nan')
  pairs.append({'deal':int(r.deal),'native_gbp':r.profit,'reference_gbp':ref,'difference':r.profit-ref,'quote_age_seconds':r.age_seconds});opened=None
z=pd.DataFrame(pairs);z.to_csv(base/'independent-fx-pnl.csv',index=False);matched=z.dropna(subset=['reference_gbp']);result={'trades':len(z),'matched_trades':len(matched),'missing_quotes':int(z.reference_gbp.isna().sum()),'max_quote_age_seconds':float(matched.quote_age_seconds.max()),'native_gbp_matched':float(matched.native_gbp.sum()),'reference_gbp_matched':float(matched.reference_gbp.sum()),'sum_difference_gbp_matched':float(matched.difference.sum()),'max_abs_difference_gbp_matched':float(matched.difference.abs().max())};(base/'independent-fx-summary.json').write_text(json.dumps(result,indent=2));print(result);m.shutdown()
