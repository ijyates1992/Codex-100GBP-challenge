"""Acceptance checks against actual native reports, cash flows and risk audits."""
from pathlib import Path
import argparse, hashlib, json, re
import numpy as np
import pandas as pd
from analyse import analyse

def verify(folder):
    f=Path(folder)
    r=analyse(f)
    manifest=json.loads((f/'manifest.json').read_text())
    stats=pd.read_csv(f/'stats.csv').iloc[0]
    deals=pd.read_csv(f/'deals.csv')
    audit=pd.read_csv(f/'audit.csv')
    fees=pd.read_csv(f/'fees.csv')
    equity=pd.read_csv(f/'equity.csv')
    source=(f/'Challenge.mq5').read_text()
    defaults={k:float(v) for k,v in re.findall(r'input\s+(?:double|int|ulong)\s+(\w+)=(-?[\d.]+);',source)}
    inputs=defaults|manifest['inputs']
    checks={k:bool(r[k]) for k in ['source_match','deal_profit_match','last_balance_match','trade_count_match','volume_grid_ok']}
    report_inputs={k:float(v) for k,v in re.findall(r'<b>(\w+)=(-?[\d.]+)</b>',(f/(f.name+'.htm')).read_text(encoding='utf-16'))}
    checks['effective_report_inputs_match']=all(k in report_inputs and report_inputs[k]==float(v) for k,v in inputs.items())
    checks['full_period']=manifest['start']=='2023.09.12' and manifest['end']=='2026.09.12'
    checks['gbp_100']=manifest['currency']=='GBP' and manifest['deposit']==100
    checks['model_4']=manifest['model']==4
    checks['binary_match']=hashlib.sha256((f/'Challenge.ex5').read_bytes()).hexdigest()==manifest['binary_sha256']
    checks['fees_deducted']=abs(fees.fee.sum()-stats['fees'])<1e-7 and np.allclose(fees.net_profit,fees.gross_profit-fees.fee)
    checks['fee_rate']=np.allclose(fees.fee,np.round(abs(fees.gross_profit)*inputs['ConversionFeePercent']/100,2))
    flows=deals[deals.type=='balance']
    positive=flows[flows.profit>0]
    checks['no_added_capital']=len(positive)==1 and abs(positive.profit.iloc[0]-100)<.001
    checks['withdrawals_only_fees']=abs(flows[flows.profit<0].profit.sum()+fees.fee.sum())<.011
    checks['fee_cash_available']=not bool(stats.fee_failure)
    checks['no_overnight']=r['overnight_trades']==0
    checks['minimum_lot']=r['min_volume']>=.01
    checks['margin_budget']=bool((audit.broker_margin_floor<=audit.equity*inputs['MarginFraction']+1e-7).all())
    checks['free_margin']=bool((audit.broker_margin_floor<=audit.free_margin+1e-7).all())
    checks['risk_budget']=bool((audit.risk_gbp<=audit.equity*inputs['RiskPercent']/100+1e-7).all())
    expected=np.maximum(inputs['BrokerMarginPerLot'],audit.notional_per_lot*inputs['BrokerNotionalRate'])*inputs['MarginSafety']*audit.volume
    checks['independent_margin_formula']=np.allclose(expected,audit.broker_margin_floor,rtol=1e-9)
    checks['peak_monotonic']=bool((equity.peak.diff().dropna()>=-1e-8).all())
    checks['peak_above_equity']=bool((equity.peak+1e-8>=equity.equity).all())
    checks['tick_drawdown_covers_snapshots']=stats.tracked_dd+1e-8>=equity.max_drawdown_pct.max()
    checks['drawdown_at_most_30']=0<=stats.equity_dd_relative<=30
    checks['net_profit_positive']=stats.profit>0
    journal=(f/'journal.log').read_text()
    symbol=manifest['symbol']
    main=[l for l in journal.splitlines() if symbol+' :' in l]
    checks['no_discarded_trading_quotes']=not any('discarded' in l or 'mismatch' in l for l in main)
    absent=[l for l in main if 'real ticks absent for' in l]
    checks['known_fallback_only']=len(absent)==2 and all('586 minutes' in l for l in absent) and any('2025.01.14 23:59' in l for l in absent)
    checks['no_fee_failure_journal']='FEE_WITHDRAWAL_FAILED' not in journal
    out={'scope':'Numeric and execution-accounting acceptance; explicit 586-minute M1 fallback remains an approximation. GBP conversion is audited separately.','checks':{k:bool(v) for k,v in checks.items()},'all_pass':all(checks.values())}
    (f/'acceptance.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2))
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder');args=p.parse_args()
    raise SystemExit(0 if verify(args.folder)['all_pass'] else 1)
