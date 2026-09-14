import MetaTrader5 as m,numpy as np,json,datetime as dt,pathlib,time
assert m.initialize()
assert m.account_info().trade_mode==0
out=[]
for s in m.symbols_get():
 if s.custom: continue
 r=m.copy_rates_range(s.name,m.TIMEFRAME_H1,dt.datetime(2023,9,1,tzinfo=dt.timezone.utc),dt.datetime(2026,9,13,tzinfo=dt.timezone.utc))
 if r is None or not len(r):
  time.sleep(.1); r=m.copy_rates_range(s.name,m.TIMEFRAME_H1,dt.datetime(2023,9,1,tzinfo=dt.timezone.utc),dt.datetime(2026,9,13,tzinfo=dt.timezone.utc))
 if r is not None and len(r):
  np.save('data/'+s.name+'.npy',r)
  d={'symbol':s.name,'bars':len(r),'first':str(dt.datetime.fromtimestamp(int(r[0]['time']),dt.timezone.utc)),'last':str(dt.datetime.fromtimestamp(int(r[-1]['time']),dt.timezone.utc))}
 else: d={'symbol':s.name,'bars':0,'error':m.last_error()}
 out.append(d); print(d,flush=True)
pathlib.Path('evidence/history.json').write_text(json.dumps(out,indent=2))
m.shutdown()
