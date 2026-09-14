"""Calendar-year contributions from one continuous account, without resets."""
from pathlib import Path
import argparse,json
import pandas as pd

p=argparse.ArgumentParser();p.add_argument('folder');args=p.parse_args();f=Path(args.folder)
m=json.loads((f/'manifest.json').read_text());d=pd.read_csv(f/'deals.csv')
validation=json.loads((f/'validation.json').read_text())
opens=d[d.direction=='in'].reset_index(drop=True);closes=d[d.direction=='out'].reset_index(drop=True)
assert len(opens)==len(closes)
for boundary_year in range(int(m['start'][:4])+1,int(m['end'][:4])):
    boundary=f'{boundary_year}.01.01'
    assert not any(o.time[:10]<boundary<=c.time[:10] for o,c in zip(opens.itertuples(),closes.itertuples())),f'Position open at {boundary}'
d['year']=d.time.str[:4].astype(int);balance=float(m['deposit']);rows=[]
end=pd.Timestamp(m['end'].replace('.','-'))
last_year=end.year-1 if (end.month,end.day)==(1,1) else end.year
for year in range(int(m['start'][:4]),last_year+1):
    part=d[d.year==year];exits=part[part.direction=='out']
    fees=-part[(part.type=='balance')&(part.profit<0)].profit.sum()
    net=exits.profit.sum()-fees;closing=balance+net
    if len(part):assert abs(closing-part.balance.iloc[-1])<.011
    rows.append({'year':year,'opening_gbp':round(balance,2),'closing_gbp':round(closing,2),'net_profit_gbp':round(net,2),'return_pct':100*net/balance,'trades':len(exits),'fees_gbp':round(fees,2)})
    balance=closing
assert abs(balance-validation['final_equity'])<.011
pd.DataFrame(rows).to_csv(f/'annual-results.csv',index=False)
(f/'annual-results.json').write_text(json.dumps({'scope':'Contributions from the continuous test; no annual capital, risk or equity-peak reset. Year-end positions are flat.','years':rows},indent=2))
print(pd.DataFrame(rows).to_string(index=False))
