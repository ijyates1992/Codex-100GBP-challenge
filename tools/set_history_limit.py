from pathlib import Path
import argparse,re,subprocess
p_args=argparse.ArgumentParser();p_args.add_argument('--max-bars',type=int,default=2000000);args=p_args.parse_args()
assert args.max_bars>=100000
check=subprocess.run(['pwsh','-NoProfile','-Command','if(Get-Process terminal64 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True)
assert check.returncode==0,'Close MT5 before changing its history limit'
p=Path(r'C:\Users\ian\AppData\Roaming\MetaQuotes\Terminal\DE9A4B13809164D991CFFF8AF2B25C58\config\common.ini')
s=p.read_text(encoding='utf-16');s,n=re.subn(r'MaxBars=\d+',f'MaxBars={args.max_bars}',s);assert n==1;p.write_text(s,encoding='utf-16')
print('Terminal history capacity:',args.max_bars)
