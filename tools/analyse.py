"""Reconcile native reports, sizing audit and immutable source snapshots."""
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd,json,re,hashlib,argparse
ROOT=Path(__file__).resolve().parents[1]
def analyse(folder):
 f=Path(folder);manifest=json.loads((f/'manifest.json').read_text());name=f.name
 soup=BeautifulSoup((f/(name+'.htm')).read_text(encoding='utf-16'),'html.parser');rows=[[' '.join(c.stripped_strings) for c in r.select('td')]for r in soup.select('tr')]
 deals=pd.DataFrame([r for r in rows if len(r)==13 and re.match(r'\d{4}\.\d\d\.\d\d ',r[0])],columns=['time','deal','symbol','type','direction','volume','price','order','commission','swap','profit','balance','comment'])
 for c in ['volume','price','commission','swap','profit','balance']:deals[c]=pd.to_numeric(deals[c].str.replace(' ',''),errors='coerce')
 stats=pd.read_csv(f/'stats.csv').iloc[0].to_dict();audit=pd.read_csv(f/'audit.csv');j=(f/'journal.log').read_text();symbol=manifest['symbol']
 warnings=[line for line in j.splitlines() if any(k in line for k in ['discarded','mismatch','generation used','no real ticks'])]
 mainwarnings=[l for l in warnings if symbol+' :' in l or symbol+':' in l]
 close=deals[deals.direction=='out'];opens=deals[deals.direction=='in'];overnight=sum(a[:10]!=b[:10]for a,b in zip(opens.time,close.time))
 initial=float(manifest['deposit'])
 result={'name':name,'final_equity':initial+stats['profit'],'return_pct':100*stats['profit']/initial,'cagr_pct':((1+stats['profit']/initial)**(1/3)-1)*100,'dd_pct':stats['equity_dd_relative'],'profit_factor':stats['profit_factor'],'trades':int(stats['trades']),'main_symbol_tick_warnings':len(mainwarnings),'conversion_tick_warnings':len(warnings)-len(mainwarnings),'overnight_trades':overnight,'min_volume':float(opens.volume.min()),'max_volume':float(opens.volume.max()),'max_margin_fraction':float((audit.broker_margin_floor/audit.equity).max()),'max_risk_fraction':float((audit.risk_gbp/audit.equity).max()),'source_match':hashlib.sha256((f/'Challenge.mq5').read_bytes()).hexdigest()==manifest['source_sha256'],'deal_profit_match':abs(close.profit.sum()-stats.get('fees',0)-stats['profit'])<.011,'last_balance_match':abs(deals.balance.iloc[-1]-(initial+stats['profit']))<.011,'trade_count_match':len(close)==stats['trades'],'volume_grid_ok':bool(((opens.volume/.01-round(opens.volume/.01)).abs()<1e-7).all()),'report_sha256':hashlib.sha256((f/(name+'.htm')).read_bytes()).hexdigest()}
 start=pd.Timestamp(manifest['start'].replace('.','-'));end=pd.Timestamp(manifest['end'].replace('.','-'))
 whole=end.year-start.year
 if start+pd.DateOffset(years=whole)>end:whole-=1
 anniversary=start+pd.DateOffset(years=whole);following=start+pd.DateOffset(years=whole+1)
 years=whole+(end-anniversary).days/(following-anniversary).days
 result['cagr_pct']=((1+stats['profit']/initial)**(1/years)-1)*100
 result['duration_years']=years
 result['numeric_pass']=result['dd_pct']<=30 and result['final_equity']>initial
 (f/'validation.json').write_text(json.dumps(result,indent=2,default=lambda x:x.item()));deals.to_csv(f/'deals.csv',index=False);return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('folders',nargs='*');a=p.parse_args();folders=[Path(x)for x in a.folders]if a.folders else [p.parent for p in (ROOT/'evidence').glob('*/stats.csv')];r=[analyse(f)for f in folders];pd.DataFrame(r).sort_values('final_equity',ascending=False).to_csv(ROOT/'evidence/native-ranking.csv',index=False);print(pd.DataFrame(r).to_string(index=False))
