"""Auditable public Dukascopy hourly tick download and lossless daily quote export."""
from pathlib import Path
from datetime import datetime,timedelta,timezone
import argparse,concurrent.futures,http.client,ssl,threading,time,lzma,hashlib,json,urllib.request
import numpy as np
ROOT=Path(__file__).resolve().parents[1];LOCAL=threading.local();CONNECT=threading.Lock();SCHEME='https'
RAW_DTYPE=np.dtype([('ms','>u4'),('ask','>u4'),('bid','>u4'),('ask_volume','>f4'),('bid_volume','>f4')])
DISK_DTYPE=np.dtype([('time_msc','<i8'),('bid','<i4'),('ask','<i4')])
def sha(b):return hashlib.sha256(b).hexdigest()
def download(hour):
 path=f'/datafeed/USDJPY/{hour.year}/{hour.month-1:02}/{hour.day:02}/{hour.hour:02}h_ticks.bi5'
 cache=ROOT/'data/dukascopy/raw'/hour.strftime('%Y%m%d')/f'{hour.hour:02}.bi5'
 cache.parent.mkdir(parents=True,exist_ok=True)
 metadata=cache.with_suffix('.json')
 status=None
 transport=SCHEME
 if cache.exists():
  body=cache.read_bytes()
  if metadata.exists():
   cached_meta=json.loads(metadata.read_text());status=cached_meta['status'];transport=cached_meta.get('transport','https')
  else:transport='https' # Legacy pilot used HTTPS only.
 else:
  for attempt in range(5):
   try:
    if not hasattr(LOCAL,'connection'):
     with CONNECT:
      connection=(http.client.HTTPSConnection('datafeed.dukascopy.com',timeout=15,context=ssl.create_default_context()) if SCHEME=='https' else http.client.HTTPConnection('datafeed.dukascopy.com',timeout=15))
      connection.connect();LOCAL.connection=connection
    transport=SCHEME
    LOCAL.connection.request('GET',path,headers={'User-Agent':'USDJPY-research-data-audit/1.0'})
    response=LOCAL.connection.getresponse();status=response.status;body=response.read()
    if status in (301,302,307,308):
     location=response.getheader('Location')
     if location!='https://datafeed.dukascopy.com'+path:raise RuntimeError(f'Unexpected redirect {location}')
     with urllib.request.urlopen(location,timeout=20) as redirected:
      status=redirected.status;body=redirected.read();transport='https'
    if status==429:
     time.sleep(max(30,int(response.getheader('Retry-After','30')) if response.getheader('Retry-After','30').isdigit() else 30))
     raise RuntimeError('HTTP 429')
    if status in (500,502,503,504):raise RuntimeError(f'HTTP {status}')
    if status in (301,302,307,308):raise RuntimeError(f'HTTP {status} redirect {response.getheader("Location")}')
    if status==404:body=b''
    elif status!=200:raise RuntimeError(f'HTTP {status}')
    raw=lzma.decompress(body) if body else b''
    if len(raw)%20:raise ValueError('Incomplete BI5 record')
    cache.write_bytes(body)
    metadata.write_text(json.dumps({'status':status,'transport':transport,'retrieved_utc':datetime.now(timezone.utc).isoformat()}))
    break
   except Exception as error:
    # A fully consumed HTTP error response leaves keep-alive reusable. Transport
    # failures require reconnecting; avoid unnecessary repeated TLS handshakes.
    if (not isinstance(error,RuntimeError) or 'redirect' in str(error) or '429' in str(error)) and hasattr(LOCAL,'connection'):LOCAL.connection.close();del LOCAL.connection
    if attempt==4:raise
    time.sleep(min(2**attempt,8))
 raw=lzma.decompress(body) if body else b''
 if len(raw)%20:raise ValueError('Incomplete cached BI5 record')
 arr=np.frombuffer(raw,dtype=RAW_DTYPE)
 invalid=int(np.count_nonzero((arr['ms']>=3600000)|(arr['bid']==0)|(arr['ask']<arr['bid'])))
 disorder=int(np.count_nonzero(np.diff(arr['ms'].astype(np.int64))<0))
 if invalid or disorder:raise ValueError(f'Invalid source records: {hour} invalid={invalid} disorder={disorder}')
 ticks=np.empty(len(arr),dtype=DISK_DTYPE);ticks['time_msc']=int(hour.timestamp()*1000)+arr['ms'].astype(np.int64);ticks['bid']=arr['bid'];ticks['ask']=arr['ask']
 record={'hour_utc':hour.isoformat(),'url':transport+'://datafeed.dukascopy.com'+path,'transport_authenticated':transport=='https','bytes':len(body),'sha256':sha(body),'ticks':len(arr),'status':status,'invalid_quotes':invalid,'out_of_order':disorder}
 return record,ticks

def export_day(day,hours,executor):
 results=list(executor.map(download,hours));records=[r[0] for r in results]
 arrays=[r[1] for r in results if len(r[1])];ticks=np.concatenate(arrays) if arrays else np.empty(0,dtype=DISK_DTYPE)
 out=ROOT/'data/dukascopy/days';out.mkdir(parents=True,exist_ok=True)
 name=day.strftime('%Y%m%d');binary=out/(name+'.ticks');binary.write_bytes(ticks.tobytes())
 bars=[]
 if len(ticks):
  minutes=ticks['time_msc']//60000;unique,start,count=np.unique(minutes,return_index=True,return_counts=True)
  bid=ticks['bid'];ask=ticks['ask'];high=np.maximum.reduceat(bid,start);low=np.minimum.reduceat(bid,start);spread=np.minimum.reduceat(ask-bid,start)
  bars=[(int(m*60),int(bid[i]),int(h),int(l),int(bid[i+n-1]),int(n),int(sp)) for m,i,n,h,l,sp in zip(unique,start,count,high,low,spread)]
 barfile=out/(name+'.bars');barfile.write_text(''.join(';'.join(map(str,row))+'\n' for row in bars),newline='\n')
 audit={'day':day.strftime('%Y-%m-%d'),'ticks':len(ticks),'bars':len(bars),'binary_sha256':sha(binary.read_bytes()),'hours':records,'first_tick_msc':int(ticks['time_msc'][0]) if len(ticks) else None,'last_tick_msc':int(ticks['time_msc'][-1]) if len(ticks) else None,'max_intraday_gap_seconds':float(np.diff(ticks['time_msc']).max()/1000) if len(ticks)>1 else None,'min_spread_points':int(np.min(ticks['ask']-ticks['bid'])) if len(ticks) else None,'median_spread_points':float(np.median(ticks['ask']-ticks['bid'])) if len(ticks) else None}
 audit['bars_sha256']=sha(barfile.read_bytes())
 audit['hours_not_requested']=[h for h in range(24) if h not in [v.hour for v in hours]]
 audit['not_requested_reason']='scheduled weekend closure assumption; not proof of absent quotes'
 meta=ROOT/'evidence/dukascopy-manifests';meta.mkdir(parents=True,exist_ok=True);(meta/(name+'.json')).write_text(json.dumps(audit,indent=2))
 return audit
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--from-date',required=True);p.add_argument('--to-date',required=True);p.add_argument('--workers',type=int,default=4);p.add_argument('--transport',choices=['https','http'],default='https');a=p.parse_args();SCHEME=a.transport
 day=datetime.fromisoformat(a.from_date).replace(tzinfo=timezone.utc);end=datetime.fromisoformat(a.to_date).replace(tzinfo=timezone.utc)
 total=0;days=0;failed=[];began=time.monotonic()
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as executor:
  while day<end:
   # No Saturday trading hours are requested. Sundays include the possible reopen.
   hours=[] if day.weekday()==5 else ([day+timedelta(hours=h) for h in range(20,24)] if day.weekday()==6 else [day+timedelta(hours=h) for h in range(24)])
   try:
    audit=export_day(day,hours,executor);total+=audit['ticks'];days+=1
    if days%7==0 or day+timedelta(days=1)>=end:print(json.dumps({'through':audit['day'],'days':days,'ticks':total,'elapsed_seconds':round(time.monotonic()-began,1)}),flush=True)
   except Exception as e:
    failed.append({'day':day.strftime('%Y-%m-%d'),'error':str(e)})
    print(json.dumps({'failed_day':failed[-1],'action':'retain raw cache; do not export incomplete day; continue'}),flush=True)
   day+=timedelta(days=1)
 summary={'from':a.from_date,'to_exclusive':a.to_date,'complete_days':days,'failed_days':failed,'ticks':total}
 (ROOT/'data/dukascopy'/f'run-{a.from_date}-{a.to_date}.json').write_text(json.dumps(summary,indent=2))
 if failed:raise SystemExit(1)
