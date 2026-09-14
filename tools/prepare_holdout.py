"""Prepare the separate 2022 importer without modifying strategy or baseline data."""
from pathlib import Path
import hashlib, json

root=Path(__file__).resolve().parents[1]
frozen=json.loads((root/'evidence/final_verified/manifest.json').read_text())
for name,key in [('Challenge.mq5','source_sha256'),('Challenge.ex5','binary_sha256')]:
    assert hashlib.sha256((root/'src'/name).read_bytes()).hexdigest()==frozen[key]
source=(root/'src/ImportIG.mq5').read_text()
source=source.replace('GBP100_USDJPY"','GBP100_USDJPY_2022"')
source=source.replace('GBP100\\\\USDJPY\\\\','GBP100\\\\USDJPY2022\\\\')
source=source.replace('if(n==0){FileWrite(logfile,day+" EMPTY");return;}','')
source=source.replace('long start=raw[0].time_msc/86400000*86400000,end=start+86400000-1;', 'if(n==0 && ArraySize(rates)==0){FileWrite(logfile,day+" EMPTY");return;}\n long start=(long)StringToTime(StringSubstr(day,0,4)+"."+StringSubstr(day,4,2)+"."+StringSubstr(day,6,2))*1000,end=start+86400000-1;')
source=source.replace('int nr=CustomRatesReplace(target,(datetime)(start/1000),(datetime)(end/1000),rates);int nt=CustomTicksReplace(target,start,end,ticks);','int nt=n>0?CustomTicksReplace(target,start,end,ticks):0;int nr=CustomRatesReplace(target,(datetime)(start/1000),(datetime)(end/1000),rates);')
source=source.replace('int nc=CopyTicksRange(target,check,COPY_TICKS_ALL,(ulong)start,(ulong)end);','int nc=n>0?CopyTicksRange(target,check,COPY_TICKS_ALL,(ulong)start,(ulong)end):0;')
source=source.replace('FileWrite(logfile,StringFormat(', 'MqlRates verified[];int count=CopyRates(target,PERIOD_M1,(datetime)(start/1000),(datetime)(end/1000),verified);if(count!=nr){Finish("ERROR bar count "+day);return;}\n for(int i=0;i<count;i++)if(verified[i].time!=rates[i].time||MathAbs(verified[i].open-rates[i].open)>0.00001||MathAbs(verified[i].high-rates[i].high)>0.00001||MathAbs(verified[i].low-rates[i].low)>0.00001||MathAbs(verified[i].close-rates[i].close)>0.00001){Finish("ERROR bar prices "+day);return;}\n FileWrite(logfile,StringFormat(')
source=source.replace('ALL_QUOTES_MATCH','ALL_QUOTES_AND_BARS_MATCH')
(root/'src/ImportHoldout2022.mq5').write_text(source)
manifest=json.loads((root/'evidence/USDJPY2022-raw-manifest.json').read_text())
ordered=sorted(manifest['days'],key=lambda d:(bool(d.get('fallback')),d['day']))
(root/'data/replay/USDJPY2022/import-list.txt').write_text('\n'.join(d['day'] for d in ordered)+'\n')
print('Prepared isolated GBP100_USDJPY_2022 importer; frozen EA hashes match.')
