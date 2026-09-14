from pathlib import Path
import MetaTrader5 as m,datetime as dt,numpy as np,json
assert m.initialize();assert m.account_info().trade_mode==0
start=dt.datetime(2025,1,14,tzinfo=dt.timezone.utc);end=start+dt.timedelta(days=1)
r=m.copy_rates_range('USDJPY',m.TIMEFRAME_M1,start,end-dt.timedelta(seconds=1));assert r is not None and len(r)>1000,(len(r)if r is not None else m.last_error())
assert r['time'][0]>=int(start.timestamp()) and r['time'][-1]<int(end.timestamp())
np.save('data/gap/ig-m1.npy',r);x=np.load('data/USDJPY.npy');x=x[(x['time']>=int(start.timestamp()))&(x['time']<int(end.timestamp()))]
import pandas as pd
d=pd.DataFrame(r);h=d.groupby(d.time//3600).agg(open=('open','first'),high=('high','max'),low=('low','min'),close=('close','last'));diff=[]
for v in x:
 key=int(v['time']//3600)
 if key in h.index:diff.append(max(abs(float(v[c])-float(h.loc[key,c]))for c in ['open','high','low','close']))
Path('evidence/gap-ig-minute-audit.json').write_text(json.dumps({'minutes':len(r),'first':int(r['time'][0]),'last':int(r['time'][-1]),'h1_comparisons':len(diff),'max_h1_price_difference':max(diff)},indent=2));print('IG gap M1',len(r),'H1 max difference',max(diff));m.shutdown()
