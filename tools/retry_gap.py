import MetaTrader5 as m,datetime as d,json
assert m.initialize(); assert m.account_info().trade_mode==0
rows=[]
for hour in [0,6,12,18]:
 a=d.datetime(2025,1,14,hour,tzinfo=d.timezone.utc);b=a+d.timedelta(hours=6,milliseconds=-1);r=m.copy_ticks_range('USDJPY',a,b,m.COPY_TICKS_ALL);rows.append({'start':str(a),'ticks':len(r) if r is not None else None,'error':m.last_error()})
print(rows);open('evidence/missing-day-retry.json','w').write(json.dumps(rows,indent=2));m.shutdown()
