import urllib.request
u='http://datafeed.dukascopy.com/datafeed/USDJPY/2025/00/14/05h_ticks.bi5'
try:
 with urllib.request.urlopen(u,timeout=20)as r:
  b=r.read();print('status',r.status,'bytes',len(b),'final_scheme',r.url.split(':')[0]);open('data/gap/05-http.bi5','wb').write(b)
except Exception as e:print(type(e).__name__,str(e))
