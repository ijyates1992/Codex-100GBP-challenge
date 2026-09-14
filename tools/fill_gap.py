import concurrent.futures,urllib.request,lzma,numpy as np,pathlib,datetime as dt,json,hashlib,time
base=pathlib.Path('data/gap');base.mkdir(parents=True,exist_ok=True)
D=np.dtype([('ms','>u4'),('ask','>u4'),('bid','>u4'),('av','>f4'),('bv','>f4')]);O=np.dtype([('time_msc','<i8'),('bid','<i4'),('ask','<i4')])
def get(hour):
 url=f'https://datafeed.dukascopy.com/datafeed/USDJPY/2025/00/14/{hour:02}h_ticks.bi5';f=base/f'{hour:02}.bi5'
 for attempt in range(4):
  try:
   body=f.read_bytes() if f.exists() else urllib.request.urlopen(url,timeout=25).read();raw=np.frombuffer(lzma.decompress(body),dtype=D);f.write_bytes(body);break
  except Exception:
   if attempt==3:raise
   time.sleep(60)
 assert len(raw) and np.all(raw['ask']>=raw['bid']) and np.all(raw['bid']>0) and np.all(raw['ms']<3600000)
 tick=np.empty(len(raw),dtype=O);tick['time_msc']=int(dt.datetime(2025,1,14,hour,tzinfo=dt.timezone.utc).timestamp()*1000)+raw['ms'].astype('i8');tick['bid']=raw['bid'];tick['ask']=raw['ask']+10 # add one pip for broker-cost conservatism
 return {'url':url,'sha256':hashlib.sha256(body).hexdigest(),'ticks':len(raw),'transport':'https'},tick
with concurrent.futures.ThreadPoolExecutor(1)as e:res=list(e.map(get,range(24)))
r=np.concatenate([x[1]for x in res]);assert np.all(np.diff(r['time_msc'])>=0);r.tofile(base/'20250114.ticks')
mins=r['time_msc']//60000*60;b=np.r_[0,np.flatnonzero(np.diff(mins))+1];ends=np.r_[b[1:],len(r)];bars=[]
for i,j in zip(b,ends):
 q=r[i:j];bars.append([mins[i],q['bid'][0],q['bid'].max(),q['bid'].min(),q['bid'][-1],j-i,int(np.median(q['ask']-q['bid']))])
np.savetxt(base/'20250114.bars',np.array(bars),fmt='%d',delimiter=';');(base/'import-list.txt').write_text('20250114\n')
pathlib.Path('evidence/gap-provenance.json').write_text(json.dumps({'reason':'IG returned no ticks for 2025-01-14 in whole-day and four six-hour requests','source':'Dukascopy recorded USDJPY ticks','timestamp':'UTC, no shift','cost_overlay':'add 0.010 JPY (one pip) to every ask; bids unchanged','hours':[x[0]for x in res],'ticks':len(r),'minutes':len(bars),'ticks_sha256':hashlib.sha256((base/'20250114.ticks').read_bytes()).hexdigest(),'bars_sha256':hashlib.sha256((base/'20250114.bars').read_bytes()).hexdigest()},indent=2));print('gap recovered',len(r),'ticks',len(bars),'minutes',flush=True)
