import MetaTrader5 as m,datetime as d,numpy as np,json,pathlib
assert m.initialize(); assert m.account_info().trade_mode==0
out=[]
for symbol in ['USDJPY','USDTRY','EURUSD']:
 for date in ['2023-09-12','2025-02-03','2026-09-10']:
  a=d.datetime.fromisoformat(date).replace(hour=12,tzinfo=d.timezone.utc);b=a+d.timedelta(minutes=5)
  ticks=m.copy_ticks_range(symbol,a,b,m.COPY_TICKS_ALL); bars=m.copy_rates_range(symbol,m.TIMEFRAME_M1,a,b)
  item={'symbol':symbol,'date':str(a),'ticks':len(ticks) if ticks is not None else 0,'bars':len(bars) if bars is not None else 0}
  if ticks is not None and len(ticks):item.update(tick_bid_min=float(ticks['bid'].min()),tick_bid_max=float(ticks['bid'].max()))
  if bars is not None and len(bars):item.update(bar_low=float(bars['low'].min()),bar_high=float(bars['high'].max()))
  out.append(item); print(item,flush=True)
pathlib.Path('evidence/data-samples.json').write_text(json.dumps(out,indent=2));m.shutdown()
