"""Conservative H1 research screen; MT5 real-tick validation is mandatory."""
import numpy as np,pandas as pd,json,itertools,pathlib
from numba import njit
@njit
def sim(o,h,l,c,sp,atr,signals,hour,times,conv,contract,step,vmin,vmax,marginlot,risk,stopmult,targetmult,start,end):
 bal=100.; peak=100.; dd=0.; trades=0; gp=0.; gl=0.; side=0; entry=0.; sl=0.; tp=0.; vol=0.
 for i in range(100,len(o)):
  if times[i]<1694476800: continue
  if side and (hour[i]>=20 or hour[i]<hour[i-1]):
   p=(o[i]+(sp[i] if side<0 else 0)-entry)*side*vol*contract*conv[i]; bal+=p; gp+=max(p,0); gl-=min(p,0); trades+=1; side=0
  if not side and start<=hour[i]<end and atr[i-1]>0 and dd<.28:
   side=int(signals[i-1]); dist=atr[i-1]*stopmult
   if side:
    vol=np.floor(min(bal*risk/100/(dist*contract*conv[i]),bal*.6/marginlot,vmax)/step+1e-9)*step
    if vol<vmin: side=0
    else:
     entry=o[i]+(sp[i] if side>0 else 0); sl=entry-side*dist; tp=entry+side*atr[i-1]*targetmult
  if side:
   worst=(max(l[i],sl) if side>0 else min(h[i]+sp[i],sl))
   best=(min(h[i],tp) if side>0 else max(l[i]+sp[i],tp))
   eqlo=bal+(worst-entry)*side*vol*contract*conv[i]; eqhi=bal+(best-entry)*side*vol*contract*conv[i]
   peak=max(peak,eqhi); dd=max(dd,(peak-eqlo)/peak)
   exitprice=0.
   if (side>0 and l[i]<=sl) or (side<0 and h[i]+sp[i]>=sl): exitprice=min(o[i],sl) if side>0 else max(o[i]+sp[i],sl)
   elif (side>0 and h[i]>=tp) or (side<0 and l[i]+sp[i]<=tp): exitprice=tp
   if exitprice:
    p=(exitprice-entry)*side*vol*contract*conv[i]; bal+=p; gp+=max(p,0); gl-=min(p,0); trades+=1; side=0
  peak=max(peak,bal); dd=max(dd,(peak-bal)/peak)
 if side:
  p=(c[-1]+(sp[-1] if side<0 else 0)-entry)*side*vol*contract*conv[-1];bal+=p;gp+=max(p,0);gl-=min(p,0);trades+=1
 return bal,dd,trades,gp/max(gl,.00001)
def run():
 specs=json.load(open('evidence/broker.json'))['symbols']; rows=[]
 for s in specs:
  path=pathlib.Path('data')/(s['name']+'.npy')
  if not path.exists() or s['custom'] or not s['margin_buy_min'] or s['margin_buy_min']>70: continue
  r=np.load(path); d=pd.DataFrame(r)
  if len(d)<15000: continue
  cur=s['currency_profit']; conv=np.ones(len(d))
  if cur!='GBP':
   cp=pathlib.Path('data')/('GBP'+cur+'.npy')
   if not cp.exists(): continue
   fx=np.load(cp); ix=np.maximum(np.searchsorted(fx['time'],r['time'],side='right')-1,0); conv=1/fx['open'][ix]
  o,h,l,c=[d[x].to_numpy(float) for x in ['open','high','low','close']]; sp=np.maximum(d.spread.to_numpy()*s['point'],s['point']*2)
  atr=pd.concat([d.high-d.low,(d.high-d.close.shift()).abs(),(d.low-d.close.shift()).abs()],axis=1).max(axis=1).rolling(14).mean().to_numpy()
  hour=(r['time']//3600%24).astype(np.int64)
  for mode,n in itertools.product(range(3),[4,12,24,48,96]):
   if mode==0:
    sig=np.where(c>d.high.shift(1).rolling(n).max(),1,np.where(c<d.low.shift(1).rolling(n).min(),-1,0))
   elif mode==1:
    avg=d.close.rolling(n).mean(); sig=np.where(c<avg-atr,1,np.where(c>avg+atr,-1,0))
   else: sig=np.where(c>d.close.shift(n)+atr,1,np.where(c<d.close.shift(n)-atr,-1,0))
   for st,tar,session,risk in itertools.product([1.,2.,3.],[2.,4.,8.],[(1,19),(7,17),(12,19)],[1.,2.,3.,4.]):
    b,dd,tr,pf=sim(o,h,l,c,sp,atr,sig,hour,r['time'],conv,s['trade_contract_size'],s['volume_step'],s['volume_min'],s['volume_max'],max(s['margin_buy_min'],s['margin_sell_min'])/s['volume_min'],risk,st,tar,*session)
    rows.append(dict(symbol=s['name'],mode=mode,lookback=n,stop=st,target=tar,start=session[0],end=session[1],risk=risk,final=b,dd=dd,trades=tr,pf=pf))
  print(s['name'],sorted([x for x in rows if x['symbol']==s['name'] and x['dd']<=.3],key=lambda x:x['final'],reverse=True)[:1],flush=True)
 pd.DataFrame(rows).sort_values('final',ascending=False).to_csv('evidence/screen.csv',index=False)
 print(pd.DataFrame(rows).query('dd<=0.3 and trades>=30').sort_values('final',ascending=False).head(20).to_string(index=False))
if __name__=='__main__':run()
