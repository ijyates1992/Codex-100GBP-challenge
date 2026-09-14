"""Calendar-year contributions from one continuous account, without resets."""
from pathlib import Path
import argparse,json
import pandas as pd

p=argparse.ArgumentParser();p.add_argument('folder');args=p.parse_args();f=Path(args.folder)
m=json.loads((f/'manifest.json').read_text());d=pd.read_csv(f/'deals.csv')
validation=json.loads((f/'validation.json').read_text())
assert validation['overnight_trades']==0,'Year-end equity requires open-position marks'
d['year']=d.time.str[:4].astype(int);balance=float(m['deposit']);rows=[]
for year in range(int(m['start'][:4]),int(m['end'][:4])):
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
