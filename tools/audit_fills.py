"""Check recorded execution prices against original quotes or declared gap M1 bounds."""
from pathlib import Path
import argparse, json, datetime as dt
import numpy as np
import pandas as pd

p=argparse.ArgumentParser();p.add_argument('folder');a=p.parse_args();folder=Path(a.folder)
manifest=json.loads((folder/'manifest.json').read_text())
ask_shift=5 if manifest['symbol']=='GBP100_USDJPY_STRESS' else 0
deals=pd.read_csv(folder/'deals.csv');deals=deals[deals.direction.isin(['in','out'])]
dtype=np.dtype([('time_msc','<i8'),('bid','<i4'),('ask','<i4')])
result=[]
for day, group in deals.groupby(deals.time.str[:10]):
    name=day.replace('.','')
    dataset='USDJPY2022' if manifest['symbol']=='GBP100_USDJPY_2022' else 'USDJPY'
    if manifest['symbol']=='GBP100_USDJPY_2019_2021':dataset='USDJPY2019_2021'
    base=Path('data/replay/Gap' if name=='20250114' else 'data/replay/'+dataset)
    raw=np.fromfile(base/(name+'.ticks'),dtype=dtype)
    bars=None
    for _,deal in group.iterrows():
        stamp=int(dt.datetime.strptime(deal.time,'%Y.%m.%d %H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp()*1000)
        lo=np.searchsorted(raw['time_msc'],stamp-2000);hi=np.searchsorted(raw['time_msc'],stamp+3000)
        quote=raw['ask' if deal['type']=='buy' else 'bid'][lo:hi]
        if deal['type']=='buy':quote=quote+ask_shift
        px=int(round(deal.price*1000));comment=str(deal['comment'])
        kind='recorded quote within timestamp tolerance'
        ok=bool(np.any(quote==px))
        if not ok and len(quote) and comment.startswith('tp '):
            # A limit exit at its requested target is conservative if a better quote exists.
            ok=bool(px<=quote.max()) if deal['type']=='sell' else bool(px>=quote.min())
            if ok:kind='conservative target-limit fill'
        if not ok and (name in ['20250114','20220301'] or dataset=='USDJPY2019_2021' and len(raw)==0) and not len(quote):
            if bars is None:
                bars=np.loadtxt(base/(name+'.bars'),delimiter=';',dtype='i8')
            minute=stamp//60000*60;row=bars[bars[:,0]==minute]
            if len(row):
                r=row[0];spread=r[6]+ask_shift if deal['type']=='buy' else 0
                ok=r[3]+spread<=px<=r[2]+spread
                kind='declared IG M1 fallback price bound'
        result.append(dict(deal=int(deal.deal),time=deal.time,type=deal['type'],price=deal.price,check=kind,pass_check=bool(ok)))
frame=pd.DataFrame(result);frame.to_csv(folder/'fill-audit.csv',index=False)
summary={'fills':len(frame),'passed':int(frame.pass_check.sum()),'failures':frame[~frame.pass_check].to_dict('records'),'categories':frame['check'].value_counts().to_dict(),'time_tolerance':'Report timestamps have second precision; original quotes are searched from 2 seconds before through 3 seconds after the reported second.'}
(folder/'fill-audit.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
