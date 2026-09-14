from pathlib import Path
p=Path('src/Challenge.mq5');s=p.read_text();s=s.replace('input double MarginSafety=1.15;', 'input double MarginSafety=1.15;\ninput double BrokerNotionalRate=0.0353; // measured IG margin / GBP notional')
s=s.replace('double floorlot=BrokerMarginPerLot*MarginSafety;', 'double unitProfit=0;if(!OrderCalcProfit(ORDER_TYPE_BUY,_Symbol,minvol,entry,entry+quantum,unitProfit)||unitProfit<=0)return;\n double notionalLot=entry*unitProfit/quantum/minvol;\n double floorlot=MathMax(BrokerMarginPerLot,notionalLot*BrokerNotionalRate)*MarginSafety;')
s=s.replace('"free_margin","retcode"','"free_margin","notional_per_lot","broker_notional_rate","retcode"')
s=s.replace('floorlot*vol,free,trade.ResultRetcode()', 'floorlot*vol,free,notionalLot,BrokerNotionalRate,trade.ResultRetcode()')
s=s.replace('double OnTester(){return TesterStatistics(STAT_EQUITY_DDREL_PERCENT)<=30?TesterStatistics(STAT_PROFIT):-1e12;}', '''double OnTester(){
 int f=FileOpen("ChallengeStats.csv",FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON,',');
 if(f!=INVALID_HANDLE){FileWrite(f,"profit","equity_dd_relative","profit_factor","trades");FileWrite(f,TesterStatistics(STAT_PROFIT),TesterStatistics(STAT_EQUITY_DDREL_PERCENT),TesterStatistics(STAT_PROFIT_FACTOR),TesterStatistics(STAT_TRADES));FileClose(f);}
 return TesterStatistics(STAT_EQUITY_DDREL_PERCENT)<=30?TesterStatistics(STAT_PROFIT):-1e12;
}''')
p.write_text(s)
p=Path('tools/tester.py');s=p.read_text();s=s.replace("'ExecutionMode=0'","'ExecutionMode=100'")
s=s.replace("p=subprocess.Popen", "for f in ['Challenge.mq5','Challenge.ex5']:shutil.copy2(ROOT/'src'/f,out/f)\n log=TD/'Tester'/'logs'/time.strftime('%Y%m%d.log'); offset=log.stat().st_size if log.exists() else 0\n p=subprocess.Popen")
s=s.replace("print('REPORT',out", "stats=audit.with_name('ChallengeStats.csv')\n if stats.exists():shutil.copy2(stats,out/'stats.csv')\n if log.exists():\n  raw=log.read_bytes()[offset:]; text=raw.decode('utf-16-le',errors='replace'); (out/'journal.log').write_text(text,encoding='utf-8')\n print('REPORT',out")
p.write_text(s)
