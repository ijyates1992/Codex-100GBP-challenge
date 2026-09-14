from pathlib import Path
p=Path('src/ImportGap.mq5')
s=p.read_text()
s=s.replace('int nr=CustomRatesReplace(target,(datetime)(start/1000),(datetime)(end/1000),rates);int nt=CustomTicksReplace(target,start,end,ticks);', 'int nt=CustomTicksReplace(target,start,end,ticks);int nr=CustomRatesReplace(target,(datetime)(start/1000),(datetime)(end/1000),rates);')
s=s.replace('FileWrite(logfile,StringFormat("%s ticks=%d bars=%d ALL_QUOTES_MATCH",day,nt,nr));FileFlush(logfile);', '''MqlRates barcheck[];int nb=CopyRates(target,PERIOD_M1,(datetime)(start/1000),(datetime)(end/1000),barcheck);
 if(nb!=nr){Finish("ERROR minute count "+day);return;}
 for(int i=0;i<nb;i++)if(barcheck[i].time!=rates[i].time||MathAbs(barcheck[i].open-rates[i].open)>0.00001||MathAbs(barcheck[i].high-rates[i].high)>0.00001||MathAbs(barcheck[i].low-rates[i].low)>0.00001||MathAbs(barcheck[i].close-rates[i].close)>0.00001){Finish("ERROR minute OHLC "+day);return;}
 FileWrite(logfile,StringFormat("%s ticks=%d bars=%d ALL_QUOTES_MATCH ALL_MINUTE_BARS_MATCH",day,nt,nr));FileFlush(logfile);''')
p.write_text(s)
