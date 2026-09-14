"""Render measured equity and hourly drawdown; the tick maximum is annotated."""
from pathlib import Path
import argparse
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p=argparse.ArgumentParser();p.add_argument('folder');p.add_argument('--modeled-minutes',type=int,default=586);a=p.parse_args();f=Path(a.folder)
manifest=json.loads((f/'manifest.json').read_text())
initial=float(manifest['deposit'])
e=pd.read_csv(f/'equity.csv');s=pd.read_csv(f/'stats.csv').iloc[0]
t=pd.to_datetime(e.time,format='%Y.%m.%d %H:%M:%S')
fig,ax=plt.subplots(2,1,figsize=(11,6),sharex=True,gridspec_kw={'height_ratios':[3,1]},layout='constrained')
ax[0].plot(t,e.equity,color='#176b65',linewidth=1,label='Hourly equity')
ax[0].set(ylabel='Equity (GBP)',title=f'{manifest["symbol"]} | £{initial:.0f} → £{initial+s.profit:.2f} | {manifest["start"]} to {manifest["end"]}')
ax[0].legend(loc='upper left');ax[0].grid(alpha=.2)
ax[1].fill_between(t,100*(e.peak-e.equity)/e.peak,color='#b75942',alpha=.6)
ax[1].axhline(30,color='#6c2020',linestyle='--',linewidth=1)
ax[1].set(ylabel='Drawdown (%)',ylim=(max(32,s.equity_dd_relative+2),0),title=f'Maximum measured on ticks: {s.equity_dd_relative:.2f}% | {a.modeled_minutes} modeled minutes')
ax[1].grid(alpha=.2)
fig.savefig(f/'equity.png',dpi=160)
