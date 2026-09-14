#property strict
struct DiskTick {long time_msc;int bid;int ask;};
string target="GBP500_USDJPY_2019_2026";
int list=INVALID_HANDLE,logfile=INVALID_HANDLE;
void Finish(string s){if(logfile!=INVALID_HANDLE){FileWrite(logfile,s);FileClose(logfile);}if(list!=INVALID_HANDLE)FileClose(list);EventKillTimer();TerminalClose(0);}
int OnInit(){
 if(MQLInfoInteger(MQL_TESTER))return INIT_FAILED;
 bool custom=false;if(SymbolExist(target,custom)){if(!custom)return INIT_FAILED;}else if(!CustomSymbolCreate(target,"GBP100Research","USDJPY"))return INIT_FAILED;
 // Quote-based CFD margin explicitly represents measured IG notional rate.
 if(!CustomSymbolSetInteger(target,SYMBOL_TRADE_CALC_MODE,SYMBOL_CALC_MODE_CFD)||!CustomSymbolSetString(target,SYMBOL_CURRENCY_MARGIN,"JPY")||!CustomSymbolSetDouble(target,SYMBOL_MARGIN_INITIAL,0)||!CustomSymbolSetDouble(target,SYMBOL_MARGIN_MAINTENANCE,0)||!CustomSymbolSetMarginRate(target,ORDER_TYPE_BUY,0.0353,0.0353)||!CustomSymbolSetMarginRate(target,ORDER_TYPE_SELL,0.0353,0.0353))return INIT_FAILED;
 if(!SymbolSelect(target,true))return INIT_FAILED;
 logfile=FileOpen("GBP100\\USDJPY2019_2026_GBP500\\import-result.txt",FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
 list=FileOpen("GBP100\\USDJPY2019_2026_GBP500\\import-list.txt",FILE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON);
 if(list==INVALID_HANDLE||logfile==INVALID_HANDLE)return INIT_FAILED;EventSetMillisecondTimer(10);return INIT_SUCCEEDED;
}
void OnTimer(){
 if(FileIsEnding(list)){Finish("IMPORT_COMPLETE");return;}
 string day=FileReadString(list);if(StringLen(day)!=8){Finish("ERROR day");return;}
 int f=FileOpen("GBP100\\USDJPY2019_2026_GBP500\\"+day+".ticks",FILE_READ|FILE_BIN|FILE_COMMON);if(f==INVALID_HANDLE){Finish("ERROR missing ticks");return;}
 ulong bytes=FileSize(f);DiskTick raw[];uint n=FileReadArray(f,raw);FileClose(f);if(bytes%16!=0||n!=bytes/16){Finish("ERROR bytes");return;}

 MqlTick ticks[];ArrayResize(ticks,(int)n);
 for(uint i=0;i<n;i++){ZeroMemory(ticks[i]);ticks[i].time_msc=raw[i].time_msc;ticks[i].time=(datetime)(raw[i].time_msc/1000);ticks[i].bid=raw[i].bid*0.001;ticks[i].ask=raw[i].ask*0.001;ticks[i].flags=TICK_FLAG_BID|TICK_FLAG_ASK;}
 MqlRates rates[];f=FileOpen("GBP100\\USDJPY2019_2026_GBP500\\"+day+".bars",FILE_READ|FILE_CSV|FILE_ANSI|FILE_COMMON,';');if(f==INVALID_HANDLE){Finish("ERROR missing bars");return;}
 while(!FileIsEnding(f)){int j=ArraySize(rates);ArrayResize(rates,j+1);ZeroMemory(rates[j]);rates[j].time=(datetime)FileReadNumber(f);rates[j].open=FileReadNumber(f)*0.001;rates[j].high=FileReadNumber(f)*0.001;rates[j].low=FileReadNumber(f)*0.001;rates[j].close=FileReadNumber(f)*0.001;rates[j].tick_volume=(long)FileReadNumber(f);rates[j].spread=(int)FileReadNumber(f);}FileClose(f);
 if(n==0 && ArraySize(rates)==0){FileWrite(logfile,day+" EMPTY");return;}
 long start=(long)StringToTime(StringSubstr(day,0,4)+"."+StringSubstr(day,4,2)+"."+StringSubstr(day,6,2))*1000,end=start+86400000-1;
 int nt=n>0?CustomTicksReplace(target,start,end,ticks):0;int nr=CustomRatesReplace(target,(datetime)(start/1000),(datetime)(end/1000),rates);
 if(nr!=ArraySize(rates)||nt!=(int)n){Finish("ERROR import "+day);return;}
 MqlTick check[];int nc=n>0?CopyTicksRange(target,check,COPY_TICKS_ALL,(ulong)start,(ulong)end):0;if(nc!=(int)n){Finish("ERROR count "+day);return;}
 for(int i=0;i<nc;i++)if(check[i].time_msc!=raw[i].time_msc||(int)MathRound(check[i].bid*1000)!=raw[i].bid||(int)MathRound(check[i].ask*1000)!=raw[i].ask){Finish("ERROR quote "+day);return;}
 MqlRates verified[];int count=CopyRates(target,PERIOD_M1,(datetime)(start/1000),(datetime)(end/1000),verified);if(count!=nr){Finish("ERROR bar count "+day);return;}
 for(int i=0;i<count;i++)if(verified[i].time!=rates[i].time||MathAbs(verified[i].open-rates[i].open)>0.00001||MathAbs(verified[i].high-rates[i].high)>0.00001||MathAbs(verified[i].low-rates[i].low)>0.00001||MathAbs(verified[i].close-rates[i].close)>0.00001){Finish("ERROR bar prices "+day);return;}
 FileWrite(logfile,StringFormat("%s ticks=%d bars=%d ALL_QUOTES_AND_BARS_MATCH",day,nt,nr));FileFlush(logfile);
}
