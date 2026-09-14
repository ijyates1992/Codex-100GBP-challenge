#property strict
#property version "1.00"
#include <Trade/Trade.mqh>
input int Mode=2; // 0 breakout, 1 mean reversion, 2 momentum
input int Lookback=4;
input double StopATR=2;
input double TargetATR=8;
input double RiskPercent=2;
input int StartHour=7;
input int EndHour=17;
input int CloseHour=20;
input double MaxDrawdown=27;
input double MarginFraction=0.60;
input double BrokerMarginPerLot=2602; // GBP floor from IG snapshot; refreshed per selected symbol
input double MarginSafety=1.15;
input double BrokerNotionalRate=0.0353; // measured IG margin / GBP notional
input int Direction=0; // 0 both, 1 long, -1 short
input double SpreadATR=0.20;
input double ConversionFeePercent=0.8;
input ulong Magic=100202609;
CTrade trade;
double peak=0,actualDD=0,totalFees=0,netGrossProfit=0,netGrossLoss=0;
int closedTrades=0,feeLog=INVALID_HANDLE,equityLog=INVALID_HANDLE;
bool feeFailure=false;
datetime equityHour=0;
bool halted=false;
datetime lastbar=0;
int audit=INVALID_HANDLE;
int OnInit(){
 if(!MQLInfoInteger(MQL_TESTER)) {Print("Research EA: Strategy Tester only");return INIT_FAILED;}
 if(AccountInfoString(ACCOUNT_CURRENCY)!="GBP" || Lookback<2 || RiskPercent<=0 || MaxDrawdown>=30 || BrokerMarginPerLot<=0) return INIT_PARAMETERS_INCORRECT;
 peak=AccountInfoDouble(ACCOUNT_EQUITY);
 feeLog=FileOpen("ChallengeFees.csv",FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON,',');
 if(feeLog!=INVALID_HANDLE)FileWrite(feeLog,"time","deal","gross_profit","fee","net_profit");
 equityLog=FileOpen("ChallengeEquity.csv",FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON,',');
 if(equityLog!=INVALID_HANDLE)FileWrite(equityLog,"time","balance","equity","peak","max_drawdown_pct");
 trade.SetExpertMagicNumber(Magic);trade.SetTypeFillingBySymbol(_Symbol);trade.SetDeviationInPoints(10);
 audit=FileOpen("ChallengeAudit.csv",FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON,',');
 if(audit!=INVALID_HANDLE) FileWrite(audit,"time","symbol","side","equity","volume","price","stop","risk_gbp","tester_margin","broker_margin_floor","free_margin","notional_per_lot","broker_notional_rate","retcode");
 double initial,maintenance;SymbolInfoMarginRate(_Symbol,ORDER_TYPE_BUY,initial,maintenance);
 PrintFormat("SPEC %s leverage=%d calc=%d contract=%.4f min=%.4f step=%.4f buy_rate=%.8f maintenance=%.8f",_Symbol,AccountInfoInteger(ACCOUNT_LEVERAGE),SymbolInfoInteger(_Symbol,SYMBOL_TRADE_CALC_MODE),SymbolInfoDouble(_Symbol,SYMBOL_TRADE_CONTRACT_SIZE),SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN),SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP),initial,maintenance);
 return INIT_SUCCEEDED;
}
void OnDeinit(const int reason){if(audit!=INVALID_HANDLE)FileClose(audit);if(feeLog!=INVALID_HANDLE)FileClose(feeLog);if(equityLog!=INVALID_HANDLE)FileClose(equityLog);}
void TrackEquity(){
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
}
void OnTick(){
 TrackEquity();
 datetime eh=(datetime)((long)TimeCurrent()/3600*3600);
 if(eh!=equityHour){equityHour=eh;if(equityLog!=INVALID_HANDLE)FileWrite(equityLog,TimeToString(TimeCurrent(),TIME_DATE|TIME_SECONDS),AccountInfoDouble(ACCOUNT_BALANCE),AccountInfoDouble(ACCOUNT_EQUITY),peak,actualDD);}
 double eq=AccountInfoDouble(ACCOUNT_EQUITY);peak=MathMax(peak,eq);
 if(eq<=peak*(1-MaxDrawdown/100)) halted=true;
 MqlDateTime tm;TimeToStruct(TimeCurrent(),tm);
 if(halted || tm.hour>=CloseHour){if(PositionSelect(_Symbol))trade.PositionClose(_Symbol);return;}
 datetime b=iTime(_Symbol,PERIOD_H1,0);if(b==lastbar)return;lastbar=b;
 if(PositionSelect(_Symbol)||tm.hour<StartHour||tm.hour>=EndHour)return;
 MqlRates r[];ArraySetAsSeries(r,true);int need=MathMax(Lookback+2,16);
 if(CopyRates(_Symbol,PERIOD_H1,0,need,r)!=need)return;
 double atr=0;for(int i=1;i<=14;i++)atr+=MathMax(r[i].high-r[i].low,MathMax(MathAbs(r[i].high-r[i+1].close),MathAbs(r[i].low-r[i+1].close)));atr/=14;
 MqlTick tick;if(!SymbolInfoTick(_Symbol,tick)||atr<=0||(tick.ask-tick.bid)>atr*SpreadATR)return;
 int side=0;
 if(Mode==0){double hi=r[2].high,lo=r[2].low;for(int i=2;i<=Lookback+1;i++){hi=MathMax(hi,r[i].high);lo=MathMin(lo,r[i].low);}if(r[1].close>hi)side=1;else if(r[1].close<lo)side=-1;}
 else if(Mode==1){double avg=0;for(int i=1;i<=Lookback;i++)avg+=r[i].close;avg/=Lookback;if(r[1].close<avg-atr)side=1;else if(r[1].close>avg+atr)side=-1;}
 else if(Mode==2){if(r[1].close>r[Lookback+1].close+atr)side=1;else if(r[1].close<r[Lookback+1].close-atr)side=-1;}
 if(side==0||(Direction!=0&&side!=Direction))return;
 double entry=side>0?tick.ask:tick.bid;
 double quantum=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE);
 double sl=NormalizeDouble(MathRound((entry-side*atr*StopATR)/quantum)*quantum,_Digits);
 double tp=NormalizeDouble(MathRound((entry+side*atr*TargetATR)/quantum)*quantum,_Digits);
 double stopLevel=SymbolInfoInteger(_Symbol,SYMBOL_TRADE_STOPS_LEVEL)*_Point;
 if((side>0&&(tick.bid-sl<stopLevel||tp-tick.bid<stopLevel))||(side<0&&(sl-tick.ask<stopLevel||tick.ask-tp<stopLevel)))return;
 ENUM_ORDER_TYPE type=side>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL;
 double minvol=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN),step=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP),maxvol=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MAX);
 double loss=0,margin=0;if(!OrderCalcProfit(type,_Symbol,1.0,entry,sl,loss)||loss>=0||!OrderCalcMargin(type,_Symbol,minvol,entry,margin))return;
 double perlot=-loss;
 double unitProfit=0;if(!OrderCalcProfit(ORDER_TYPE_BUY,_Symbol,1.0,entry,entry+1.0,unitProfit)||unitProfit<=0)return;
 double notionalLot=entry*unitProfit;
 double floorlot=MathMax(BrokerMarginPerLot,notionalLot*BrokerNotionalRate)*MarginSafety;
 double marginlot=MathMax(margin/minvol,floorlot);
 double free=AccountInfoDouble(ACCOUNT_MARGIN_FREE);
 double budget=MathMin(eq*RiskPercent/100,MathMax(0.,eq-peak*(1-MaxDrawdown/100))*0.80);
 double vol=MathFloor((MathMin(maxvol,MathMin(budget/perlot,MathMin(eq*MarginFraction,free*MarginFraction)/marginlot)))/step+1e-9)*step;
 vol=NormalizeDouble(vol,8);if(vol<minvol)return;
 bool ok=side>0?trade.Buy(vol,_Symbol,0,sl,tp):trade.Sell(vol,_Symbol,0,sl,tp);
 if(audit!=INVALID_HANDLE){FileWrite(audit,TimeToString(TimeCurrent(),TIME_DATE|TIME_SECONDS),_Symbol,side,eq,vol,entry,sl,perlot*vol,margin/minvol*vol,floorlot*vol,free,notionalLot,BrokerNotionalRate,trade.ResultRetcode());FileFlush(audit);}
 if(!ok)Print("Order rejected: ",trade.ResultRetcodeDescription());
}
double OnTester(){
 TrackEquity();double profit=AccountInfoDouble(ACCOUNT_BALANCE)-TesterStatistics(STAT_INITIAL_DEPOSIT);
 double dd=MathMax(actualDD,TesterStatistics(STAT_EQUITY_DDREL_PERCENT));
 int f=FileOpen("ChallengeStats.csv",FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON,',');
 if(f!=INVALID_HANDLE){FileWrite(f,"profit","equity_dd_relative","profit_factor","trades","fees","native_gross_profit","native_dd","tracked_dd","fee_failure");FileWrite(f,profit,dd,netGrossLoss>0?netGrossProfit/netGrossLoss:0,closedTrades,totalFees,TesterStatistics(STAT_PROFIT),TesterStatistics(STAT_EQUITY_DDREL_PERCENT),actualDD,feeFailure);FileClose(f);}
 return dd<=30&&!feeFailure?profit:-1e12;
}
