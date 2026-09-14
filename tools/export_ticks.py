"""Preserve IG recorded quotes and rebuild bars from the same quotes; no interpolation."""
import MetaTrader5 as m,datetime as dt,numpy as np,pathlib,json,hashlib,time,argparse
p=argparse.ArgumentParser();p.add_argument('--symbol',default='USDJPY');a=p.parse_args()
assert m.initialize();assert m.account_info().trade_mode==0
s=m.symbol_info(a.symbol); point=s.point
base=pathlib.Path('data/replay')/a.symbol;base.mkdir(parents=True,exist_ok=True)
start=dt.datetime(2023,9,1,tzinfo=dt.timezone.utc);end=dt.datetime(2026,9,12,tzinfo=dt.timezone.utc);manifest=[]
while start<end:
 day=start.strftime('%Y%m%d');stop=start+dt.timedelta(days=1);f=base/(day+'.ticks');meta=base/(day+'.json')
 if meta.exists():item=json.loads(meta.read_text());manifest.append(item);start=stop;continue
 ticks=m.copy_ticks_range(a.symbol,start,stop-dt.timedelta(microseconds=1000),m.COPY_TICKS_ALL)
 if ticks is None:raise RuntimeError((day,m.last_error()))
 if len(ticks):
  assert np.all(ticks['bid']>0) and np.all(ticks['ask']>=ticks['bid']),day
  assert np.all(np.diff(ticks['time_msc'])>=0),day
  assert ticks['time_msc'][0]>=int(start.timestamp()*1000) and ticks['time_msc'][-1]<int(stop.timestamp()*1000)
 raw=np.empty(len(ticks),dtype=[('time_msc','<i8'),('bid','<i4'),('ask','<i4')]);raw['time_msc']=ticks['time_msc'];raw['bid']=np.rint(ticks['bid']/point).astype('i4');raw['ask']=np.rint(ticks['ask']/point).astype('i4');raw.tofile(f)
 bars=[]
 if len(raw):
  minute=raw['time_msc']//60000*60;beg=np.r_[0,np.flatnonzero(np.diff(minute))+1];fin=np.r_[beg[1:],len(raw)]
  for i,j in zip(beg,fin):
   q=raw[i:j];bars.append([minute[i],q['bid'][0],q['bid'].max(),q['bid'].min(),q['bid'][-1],j-i,int(np.median(q['ask']-q['bid']))])
 bf=base/(day+'.bars');np.savetxt(bf,np.array(bars,dtype='i8').reshape(-1,7),fmt='%d',delimiter=';')
 item={'day':day,'ticks':len(raw),'bars':len(bars),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bars_sha256':hashlib.sha256(bf.read_bytes()).hexdigest()};meta.write_text(json.dumps(item));manifest.append(item)
 if start.day in [1,15]:print(day,'ticks',len(raw),'total',sum(x['ticks'] for x in manifest),flush=True)
 start=stop
(base/'import-list.txt').write_text('\n'.join(x['day'] for x in manifest)+'\n');pathlib.Path('evidence/'+a.symbol+'-raw-manifest.json').write_text(json.dumps({'source':'IG-DEMO CopyTicksRange, unchanged bid/ask and timestamps','point':point,'symbol':a.symbol,'days':manifest},indent=2));m.shutdown()
