"""Run isolated named tester reports; refuses an active terminal to avoid stale results."""
import argparse,pathlib,subprocess,time,json,shutil,hashlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
TD=pathlib.Path(r'C:\Users\ian\AppData\Roaming\MetaQuotes\Terminal\DE9A4B13809164D991CFFF8AF2B25C58')
EXE=r'C:\Program Files\IG Markets MetaTrader 5 Terminal\terminal64.exe'
def run(name,symbol,inputs,model=4,start='2023.09.12',end='2026.09.12',leverage=200,delay=100):
 defaults={k:float(v) for k,v in re.findall(r'input\s+(?:double|int|ulong)\s+(\w+)=(-?[\d.]+);',(ROOT/'src/Challenge.mq5').read_text())}
 if set(inputs)-set(defaults):raise ValueError('Unknown input names')
 inputs=defaults|inputs
 check=subprocess.run(['pwsh','-NoProfile','-Command','if(Get-Process terminal64 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True)
 if check.returncode:raise RuntimeError('Close the active terminal before testing')
 out=ROOT/'evidence'/name;out.mkdir(parents=True,exist_ok=False)
 dest=TD/'TesterReports'/'GBP100';dest.mkdir(parents=True,exist_ok=True)
 report=dest/(name+'.htm')
 if report.exists(): raise RuntimeError('Report already exists; choose a new name')
 lines=['[Tester]','Expert=GBP100\\Challenge.ex5',f'Symbol={symbol}','Period=H1',f'Model={model}',f'FromDate={start}',f'ToDate={end}','ForwardMode=0','Optimization=0',f'ExecutionMode={delay}','Visual=0','ReplaceReport=0',f'Report=\\TesterReports\\GBP100\\{name}.htm','Deposit=100','Currency=GBP',f'Leverage=1:{leverage}','ShutdownTerminal=1','UseLocal=1','UseRemote=0','UseCloud=0','[TesterInputs]']+[f'{k}={v}' for k,v in inputs.items()]
 cfg=out/'tester.ini';cfg.write_text('\n'.join(lines),encoding='ascii')
 binary=(ROOT/'src/Challenge.ex5').read_bytes()
 assert binary==(TD/'MQL5/Experts/GBP100/Challenge.ex5').read_bytes(), 'Installed binary differs'
 provenance={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'evidence/broker.json',ROOT/'evidence/USDJPY-raw-manifest.json',ROOT/'evidence/gap-provenance.json',ROOT/'evidence/gap-import-verified.txt'] if p.exists()}
 if symbol=='GBP100_USDJPY_2022':
  provenance={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'evidence/broker.json',ROOT/'evidence/USDJPY2022-raw-manifest.json',ROOT/'evidence/holdout2022-data-integrity.json',ROOT/'evidence/holdout2022-import-result.txt',ROOT/'docs/UNTESTED-YEAR-PROTOCOL.md']}
 if symbol=='GBP100_USDJPY_2019_2021':
  provenance={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'evidence/broker.json',ROOT/'evidence/USDJPY2019_2021-raw-manifest.json',ROOT/'evidence/holdout2019_2021-data-integrity.json',ROOT/'evidence/holdout2019_2021-import-result.txt',ROOT/'docs/PROTOCOL-2019-2021.md']}
 (out/'manifest.json').write_text(json.dumps(dict(symbol=symbol,inputs=inputs,model=model,start=start,end=end,deposit=100,currency='GBP',leverage=leverage,delay_ms=delay,source_sha256=hashlib.sha256((ROOT/'src/Challenge.mq5').read_bytes()).hexdigest(),binary_sha256=hashlib.sha256(binary).hexdigest(),data_provenance_sha256=provenance),indent=2))
 for f in ['Challenge.mq5','Challenge.ex5']:shutil.copy2(ROOT/'src'/f,out/f)
 log=TD/'Tester'/'logs'/time.strftime('%Y%m%d.log'); offset=log.stat().st_size if log.exists() else 0
 common=pathlib.Path(r'C:\Users\ian\AppData\Roaming\MetaQuotes\Terminal\Common\Files')
 for f in ['ChallengeAudit.csv','ChallengeStats.csv','ChallengeFees.csv','ChallengeEquity.csv']:(common/f).unlink(missing_ok=True)
 p=subprocess.Popen([EXE,'/config:'+str(cfg)],creationflags=0x08000000)
 print('Tester started',name,p.pid,flush=True)
 deadline=time.time()+1800
 while p.poll() is None and time.time()<deadline:time.sleep(2)
 if p.poll() is None:
  p.terminate();raise TimeoutError('Tester exceeded 30 minutes')
 if not report.exists():raise RuntimeError('No fresh tester report: '+str(report))
 for f in dest.glob(name+'*'):shutil.copy2(f,out/f.name)
 audit=pathlib.Path(r'C:\Users\ian\AppData\Roaming\MetaQuotes\Terminal\Common\Files\ChallengeAudit.csv')
 if audit.exists():shutil.copy2(audit,out/'audit.csv')
 stats=audit.with_name('ChallengeStats.csv')
 if stats.exists():shutil.copy2(stats,out/'stats.csv')
 for original,new in [('ChallengeFees.csv','fees.csv'),('ChallengeEquity.csv','equity.csv')]:
  if (common/original).exists():shutil.copy2(common/original,out/new)
 if log.exists():
  raw=log.read_bytes()[offset:]; text=raw.decode('utf-16-le',errors='replace'); (out/'journal.log').write_text(text,encoding='utf-8')
 print('REPORT',out/(name+'.htm'),flush=True)
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('symbol');p.add_argument('--inputs',default='{}');p.add_argument('--model',type=int,default=4);p.add_argument('--start',default='2023.09.12');p.add_argument('--end',default='2026.09.12');p.add_argument('--delay',type=int,default=100);a=p.parse_args();run(a.name,a.symbol,json.loads(a.inputs),a.model,a.start,a.end,delay=a.delay)
