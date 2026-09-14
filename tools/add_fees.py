from pathlib import Path
p=Path('src/Challenge.mq5');s=p.read_text()
s=s.replace('input ulong Magic=', 'input double ConversionFeePercent=0.8;\ninput ulong Magic=')
s=s.replace('double peak=0;', 'double peak=0,actualDD=0,totalFees=0,netGrossProfit=0,netGrossLoss=0;\nint closedTrades=0,feeLog=INVALID_HANDLE,equityLog=INVALID_HANDLE;\nbool feeFailure=false;\ndatetime equityHour=0;')
s=s.replace('peak=AccountInfoDouble(ACCOUNT_EQUITY);', '''peak=AccountInfoDouble(ACCOUNT_EQUITY);
 feeLog=FileOpen("ChallengeFees.csv",FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON,',');
 if(feeLog!=INVALID_HANDLE)FileWrite(feeLog,"time","deal","gross_profit","fee","net_profit");
 equityLog=FileOpen("ChallengeEquity.csv",FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON,',');
 if(equityLog!=INVALID_HANDLE)FileWrite(equityLog,"time","balance","equity","peak","max_drawdown_pct");''')
s=s.replace('void OnDeinit(const int reason){if(audit!=INVALID_HANDLE)FileClose(audit);}', 'void OnDeinit(const int reason){if(audit!=INVALID_HANDLE)FileClose(audit);if(feeLog!=INVALID_HANDLE)FileClose(feeLog);if(equityLog!=INVALID_HANDLE)FileClose(equityLog);}')
s=s.replace('void OnTick(){', '''void TrackEquity(){
 double eq=AccountInfoDouble(ACCOUNT_EQUITY);peak=MathMax(peak,eq);actualDD=MathMax(actualDD,100*(peak-eq)/peak);
}
void OnTradeTransaction(const MqlTradeTransaction &trans,const MqlTradeRequest &request,const MqlTradeResult &result){
 if(trans.type!=TRADE_TRANSACTION_DEAL_ADD||!HistoryDealSelect(trans.deal))return;
 if(HistoryDealGetInteger(trans.deal,DEAL_MAGIC)!=(long)Magic||HistoryDealGetInteger(trans.deal,DEAL_ENTRY)!=DEAL_ENTRY_OUT)return;
 double gross=HistoryDealGetDouble(trans.deal,DEAL_PROFIT)+HistoryDealGetDouble(trans.deal,DEAL_COMMISSION)+HistoryDealGetDouble(trans.deal,DEAL_SWAP);
 double fee=NormalizeDouble(MathAbs(gross)*ConversionFeePercent/100,2);
 if(fee>0&&!TesterWithdrawal(fee)){feeFailure=true;halted=true;Print("FEE_WITHDRAWAL_FAILED");}
 totalFees+=fee;double net=gross-fee;netGrossProfit+=MathMax(net,0);netGrossLoss-=MathMin(net,0);closedTrades++;
 if(feeLog!=INVALID_HANDLE){FileWrite(feeLog,TimeToString(TimeCurrent(),TIME_DATE|TIME_SECONDS),trans.deal,gross,fee,net);FileFlush(feeLog);}
 TrackEquity();
}
void OnTick(){
 TrackEquity();
 datetime eh=(datetime)((long)TimeCurrent()/3600*3600);
 if(eh!=equityHour){equityHour=eh;if(equityLog!=INVALID_HANDLE)FileWrite(equityLog,TimeToString(TimeCurrent(),TIME_DATE|TIME_SECONDS),AccountInfoDouble(ACCOUNT_BALANCE),AccountInfoDouble(ACCOUNT_EQUITY),peak,actualDD);}''')
pos=s.index('double OnTester(){');s=s[:pos]+'''double OnTester(){
 TrackEquity();double profit=AccountInfoDouble(ACCOUNT_BALANCE)-TesterStatistics(STAT_INITIAL_DEPOSIT);
 double dd=MathMax(actualDD,TesterStatistics(STAT_EQUITY_DDREL_PERCENT));
 int f=FileOpen("ChallengeStats.csv",FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON,',');
 if(f!=INVALID_HANDLE){FileWrite(f,"profit","equity_dd_relative","profit_factor","trades","fees","native_gross_profit","native_dd","tracked_dd","fee_failure");FileWrite(f,profit,dd,netGrossLoss>0?netGrossProfit/netGrossLoss:0,closedTrades,totalFees,TesterStatistics(STAT_PROFIT),TesterStatistics(STAT_EQUITY_DDREL_PERCENT),actualDD,feeFailure);FileClose(f);}
 return dd<=30&&!feeFailure?profit:-1e12;
}
'''
p.write_text(s)
p=Path('tools/tester.py');s=p.read_text().replace("['ChallengeAudit.csv','ChallengeStats.csv']","['ChallengeAudit.csv','ChallengeStats.csv','ChallengeFees.csv','ChallengeEquity.csv']");s=s.replace("if stats.exists():shutil.copy2(stats,out/'stats.csv')","if stats.exists():shutil.copy2(stats,out/'stats.csv')\n for original,new in [('ChallengeFees.csv','fees.csv'),('ChallengeEquity.csv','equity.csv')]:\n  if (common/original).exists():shutil.copy2(common/original,out/new)");p.write_text(s)
