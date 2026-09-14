"""Revalue executed trades and margin with independent GBPJPY quotes.

For the sole missing quote day, use the adverse edge of the observed IG M1
bar. This is a conservative conversion bound, not a claim of recorded ticks.
"""
from pathlib import Path
import argparse, datetime as dt, json
import numpy as np
import pandas as pd
import MetaTrader5 as mt5

p=argparse.ArgumentParser();p.add_argument('folder');args=p.parse_args();f=Path(args.folder)
q=pd.read_csv(f/'independent-fx-quotes.csv');q['reference_kind']='recorded GBPJPY quote'
missing=q.bid.isna()|q.ask.isna()
if missing.any():
    assert mt5.initialize() and mt5.account_info().trade_mode==0
    for i in q.index[missing]:
        t=dt.datetime.strptime(q.loc[i,'time'],'%Y.%m.%d %H:%M:%S').replace(tzinfo=dt.timezone.utc)
        start=t.replace(second=0);end=start+dt.timedelta(minutes=5)
        bars=mt5.copy_rates_range('GBPJPY',mt5.TIMEFRAME_M1,start,end)
        assert bars is not None and len(bars)>0 and int(bars[0]['time'])>=int(start.timestamp())
        r=bars[0]
        q.loc[i,'bid']=float(r['low'])
        q.loc[i,'ask']=float(r['high'])+max(.01,float(r['spread'])*.001)
        q.loc[i,'reference_kind']='adverse nearest IG M1 conversion bound'
    mt5.shutdown()
q.to_csv(f/'reference-fx-complete.csv',index=False)
deals=pd.read_csv(f/'deals.csv');deals=deals[deals.direction.isin(['in','out'])].merge(q,on=['deal','time'],validate='one_to_one')
audit=pd.read_csv(f/'audit.csv')
assert (audit.retcode==10009).all(), 'Handle partial/rejected orders explicitly'
assert len(audit)==sum(deals.direction=='in')
initial=float(json.loads((f/'manifest.json').read_text())['deposit'])
balance=initial;entry=None;rows=[];opened=0
for _,d in deals.iterrows():
    if d.direction=='in':
        entry=d
        margin=float(d.price*d.volume*100000*.0353/d.bid)
        rows.append(dict(event='entry',deal=int(d.deal),time=d.time,reference_equity=balance,real_margin=margin,margin_fraction=margin/balance,volume=d.volume,reference_kind=d.reference_kind,feasible=bool(margin<balance)))
        opened+=1
    else:
        assert entry is not None
        jpy=(d.price-entry.price)*(1 if entry['type']=='buy' else -1)*entry.volume*100000
        profit=jpy/(d.ask if jpy>=0 else d.bid)
        fee=round(abs(profit)*.008,2)
        balance+=profit-fee
        rows.append(dict(event='exit',deal=int(d.deal),time=d.time,reference_equity=balance,profit_gbp=profit,fee_gbp=fee,reference_kind=d.reference_kind,feasible=bool(balance>0)))
        entry=None
assert entry is None
frame=pd.DataFrame(rows);frame.to_csv(f/'reference-capital-ledger.csv',index=False)
native=float(pd.read_csv(f/'stats.csv').iloc[0]['profit'])+initial
result={'all_entries_margin_feasible':bool(frame[frame.event=='entry'].feasible.all()),'entries':opened,'initial_gbp':initial,'reference_final_gbp':balance,'native_final_gbp':native,'difference_gbp':native-balance,'maximum_reference_margin_fraction':float(frame.margin_fraction.max()),'minimum_reference_cash_gbp':float(frame.reference_equity.min()),'m1_conversion_bounds':int(q.reference_kind.str.startswith('adverse').sum()),'assumption':'Observed 3.53% IG notional margin rate applied historically. Actual recorded fills are fixed for this independent capital-feasibility audit; this is not a separate strategy simulation.'}
(f/'reference-capital-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
