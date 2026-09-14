from tester import run
import pandas as pd,json
x=pd.read_csv('evidence/minute-screen.csv').head(5)
for i,r in x.iterrows():
 inputs={'Mode':int(r['mode']),'Lookback':int(r.lookback),'StopATR':r.stop,'TargetATR':r.target,'StartHour':int(r.start),'EndHour':int(r.end),'RiskPercent':r.risk,'Direction':int(r.direction)}
 run('corrected_'+str(i+1).zfill(2),'GBP100_USDJPY',inputs)
 print(pd.read_csv('evidence/replay_'+str(i+1).zfill(2)+'/stats.csv').to_dict('records'),flush=True)
