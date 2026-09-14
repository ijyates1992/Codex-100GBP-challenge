from tester import run
import pandas as pd
cases=[
 {'StopATR':1.25,'RiskPercent':2},
 {'StopATR':1.25,'RiskPercent':2.1},
 {'StopATR':1.25,'RiskPercent':2.2},
 {'StopATR':1.25,'RiskPercent':1.9},
 {'StopATR':1.125,'RiskPercent':2},
 {'StopATR':1.375,'RiskPercent':2},
 {'StopATR':2,'RiskPercent':2.5,'MarginFraction':.8},
 {'StopATR':2,'RiskPercent':2.75,'MarginFraction':.8}]
for i,params in enumerate(cases):
 params.update(Lookback=8,TargetATR=12,StartHour=1,EndHour=19,Direction=1,MaxDrawdown=29)
 out=run('complete_'+str(i+1).zfill(2),'GBP100_USDJPY',params)
 print(out.name,pd.read_csv(out/'stats.csv').to_dict('records'),flush=True)
