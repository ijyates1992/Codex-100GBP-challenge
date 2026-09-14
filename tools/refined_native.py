from tester import run
import pandas as pd
cases=[
 {'StopATR':1.25,'TargetATR':12,'RiskPercent':2,'MarginFraction':.6,'MaxDrawdown':29},
 {'StopATR':1.25,'TargetATR':4,'RiskPercent':2,'MarginFraction':.6,'MaxDrawdown':27},
 {'StopATR':1.25,'TargetATR':8,'RiskPercent':2,'MarginFraction':.6,'MaxDrawdown':29},
 {'StopATR':2,'TargetATR':12,'RiskPercent':2.5,'MarginFraction':.8,'MaxDrawdown':29},
 {'StopATR':2,'TargetATR':4,'RiskPercent':2.5,'MarginFraction':.8,'MaxDrawdown':29},
 {'StopATR':2,'TargetATR':12,'RiskPercent':3,'MarginFraction':.8,'MaxDrawdown':29},
 {'StopATR':2,'TargetATR':12,'RiskPercent':2,'MarginFraction':.6,'MaxDrawdown':27}]
for i,params in enumerate(cases):
 params.update(Lookback=8,StartHour=1,EndHour=19,Direction=1)
 out=run('refined_'+str(i+1).zfill(2),'GBP100_USDJPY',params)
 print(out.name,pd.read_csv(out/'stats.csv').to_dict('records'),flush=True)
