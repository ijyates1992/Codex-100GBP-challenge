import urllib.request,concurrent.futures
urls=['https://datafeed.dukascopy.com/datafeed/USDJPY/2025/00/14/12h_ticks.bi5','http://datafeed.dukascopy.com/datafeed/USDJPY/2025/00/14/12h_ticks.bi5']
def get(u):
 try:
  with urllib.request.urlopen(u,timeout=15)as r:return u,r.status,len(r.read())
 except Exception as e:return u,str(e)
with concurrent.futures.ThreadPoolExecutor(2)as e:print(list(e.map(get,urls)))
