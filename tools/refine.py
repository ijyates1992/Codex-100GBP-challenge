import minute_screen as ms
import pandas as pd,numpy as np,itertools
# Shared preparation follows the original screen, using observed minute bars only.
d=ms.prepare();hour=d.time//3600;h=d.groupby(hour).agg(time=('time','first'),open=('open','first'),high=('high','max'),low=('low','min'),close=('close','last'));at=pd.concat([h.high-h.low,(h.high-h.close.shift()).abs(),(h.low-h.close.shift()).abs()],axis=1).max(axis=1).rolling(14).mean().shift().fillna(0);ix=h.index.get_indexer(hour);atr=at.to_numpy()[ix];fx=np.load('data/GBPJPY.npy');fi=np.maximum(np.searchsorted(fx['time'],d.time,side='right')-1,0);conv=1/fx['open'][fi];args=[d[x].to_numpy()for x in ['time','open','high','low','close','spread']];rows=[]
for n in [6,8,10,12,16]:
 sig=np.where(h.close>h.close.shift(n)+at.shift(-1),1,np.where(h.close<h.close.shift(n)-at.shift(-1),-1,0));sg=pd.Series(sig).shift().fillna(0).to_numpy()[ix]
 for stop,target,risk,cap,guard in itertools.product([1.25,1.5,1.75,2.],[4.,8.,12.],[1.5,2.,2.5,3.],[.6,.8],[.27,.29]):
  b,dd,tr,pf=ms.sim(*args,atr,sg,conv,risk,stop,target,1,19,1,cap,guard,.008);rows.append(dict(mode=2,lookback=n,stop=stop,target=target,start=1,end=19,risk=risk,direction=1,cap=cap,guard=guard,final=b,dd=dd,trades=tr,pf=pf))
 print('horizon',n,'best',max(x['final']for x in rows),flush=True)
pd.DataFrame(rows).sort_values('final',ascending=False).to_csv('evidence/refined-screen.csv',index=False);print(pd.DataFrame(rows).sort_values('final',ascending=False).head(15).to_string(index=False))
