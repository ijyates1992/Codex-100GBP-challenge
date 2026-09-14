"""Screen the reconstructed IG quote bars with minute resolution and EA sizing rules."""
import numpy as np,pandas as pd,json,itertools,pathlib
from numba import njit
@njit
def sim(t,o,h,l,c,sp,atr,sig,conv,risk,sm,tm,start,end,direction,cap=.6,guard=.27,fee=.008):
 bal=100.;peak=100.;dd=0.;tr=0;gp=0.;gl=0.;side=0;entry=sl=tp=vol=0.;lastbar=-1;halt=False
 for i in range(len(t)):
  if t[i]<1694476800:continue
  hour=t[i]//3600%24;bar=t[i]//3600
  eq=bal+((o[i]+(sp[i] if side<0 else 0)-entry)*side*vol*100000*conv[i] if side else 0)
  peak=max(peak,eq)
  if eq<=peak*(1-guard):halt=True
  if side and (hour>=20 or halt):
   p=(o[i]+(sp[i] if side<0 else 0)-entry)*side*vol*100000*conv[i];p-=round(abs(p)*fee,2);bal+=p;gp+=max(p,0);gl-=min(p,0);tr+=1;side=0
  if not halt and hour<20 and bar!=lastbar:
   lastbar=bar
   if not side and start<=hour<end and atr[i]>0 and sp[i]<=atr[i]*.2:
    side=int(sig[i]);side=0 if direction!=0 and direction!=side else side
    if side:
     entry=o[i]+(sp[i] if side>0 else 0);sl=np.round((entry-side*atr[i]*sm)*1000)/1000;tp=np.round((entry+side*atr[i]*tm)*1000)/1000
     budget=min(bal*risk/100,max(0.,bal-peak*(1-guard))*.8)
     ml=max(2602.,entry*100000*conv[i]*.0353)*1.15
     vol=np.floor(min(budget/(abs(entry-sl)*100000*conv[i]),bal*cap/ml)/.01+1e-9)*.01
     if vol<.01:side=0
  if side:
   loweq=bal+((max(l[i],sl) if side>0 else min(h[i]+sp[i],sl))-entry)*side*vol*100000*conv[i]
   hieq=bal+((min(h[i],tp) if side>0 else max(l[i]+sp[i],tp))-entry)*side*vol*100000*conv[i]
   peak=max(peak,hieq);dd=max(dd,(peak-loweq)/peak)
   exit=0.
   if (side>0 and l[i]<=sl)or(side<0 and h[i]+sp[i]>=sl):exit=min(o[i],sl)if side>0 else max(o[i]+sp[i],sl)
   elif(side>0 and h[i]>=tp)or(side<0 and l[i]+sp[i]<=tp):exit=tp
   if exit:
    p=(exit-entry)*side*vol*100000*conv[i];p-=round(abs(p)*fee,2);bal+=p;gp+=max(p,0);gl-=min(p,0);tr+=1;side=0
  peak=max(peak,bal);dd=max(dd,(peak-bal)/peak)
 if side:
  p=(c[-1]+(sp[-1]if side<0 else 0)-entry)*side*vol*100000*conv[-1];p-=round(abs(p)*fee,2);bal+=p;gp+=max(p,0);gl-=min(p,0);tr+=1
 return bal,dd,tr,gp/max(gl,1e-9)
def prepare():
 cache=pathlib.Path('data/minutes.pkl')
 if cache.exists():return pd.read_pickle(cache)
 frames=[]
 for f in sorted(pathlib.Path('data/replay/USDJPY').glob('*.bars')):
  if f.stat().st_size:frames.append(pd.read_csv(f,sep=';',header=None,names=['time','open','high','low','close','volume','spread']))
 d=pd.concat(frames,ignore_index=True);d[['open','high','low','close','spread']]*=.001;d.to_pickle(cache);return d
if __name__=='__main__':
 d=prepare();hour=d.time//3600;g=d.groupby(hour);h=g.agg(time=('time','first'),open=('open','first'),high=('high','max'),low=('low','min'),close=('close','last'));at=pd.concat([h.high-h.low,(h.high-h.close.shift()).abs(),(h.low-h.close.shift()).abs()],axis=1).max(axis=1).rolling(14).mean().shift().fillna(0)
 ix=h.index.get_indexer(hour);atr=at.to_numpy()[ix];fx=np.load('data/GBPJPY.npy');fi=np.maximum(np.searchsorted(fx['time'],d.time,side='right')-1,0);conv=1/fx['open'][fi]
 args=[d[x].to_numpy() for x in ['time','open','high','low','close','spread']];rows=[]
 for mode,n in itertools.product(range(3),[4,8,12,24,48,96]):
  if mode==0:sg=np.where(h.close>h.high.shift().rolling(n).max(),1,np.where(h.close<h.low.shift().rolling(n).min(),-1,0))
  elif mode==1:avg=h.close.rolling(n).mean();sg=np.where(h.close<avg-at.shift(-1),1,np.where(h.close>avg+at.shift(-1),-1,0))
  else:sg=np.where(h.close>h.close.shift(n)+at.shift(-1),1,np.where(h.close<h.close.shift(n)-at.shift(-1),-1,0))
  sg=pd.Series(sg).shift().fillna(0).to_numpy()[ix]
  for sm,tm,session,risk,di in itertools.product([1.,1.5,2.,3.],[4.,8.,12.],[(1,19),(7,17),(12,19)],[1.,2.,3.,4.],[0,1,-1]):
   b,dd,tr,pf=sim(*args,atr,sg,conv,risk,sm,tm,*session,di);rows.append(dict(mode=mode,lookback=n,stop=sm,target=tm,start=session[0],end=session[1],risk=risk,direction=di,final=b,dd=dd,trades=tr,pf=pf))
  print(mode,n,'best',max(x['final']for x in rows),flush=True)
 pd.DataFrame(rows).sort_values('final',ascending=False).to_csv('evidence/minute-screen.csv',index=False)
 print(pd.DataFrame(rows).sort_values('final',ascending=False).head(20).to_string(index=False))
