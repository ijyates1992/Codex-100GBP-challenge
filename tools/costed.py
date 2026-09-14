from tester import run
import pandas as pd
for i,params in enumerate([dict(Lookback=8,StopATR=1.5,TargetATR=4),dict(Lookback=8,StopATR=1.5,TargetATR=12),dict(Lookback=8,StopATR=2,TargetATR=12)]):
 params.update(RiskPercent=2,StartHour=1,EndHour=19,Direction=1)
 out=run('costed_'+str(i+1).zfill(2),'GBP100_USDJPY',params)
 print(pd.read_csv(out/'stats.csv').to_dict('records'),flush=True)
