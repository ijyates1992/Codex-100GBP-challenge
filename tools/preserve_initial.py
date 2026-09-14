from pathlib import Path
import gzip
p=Path(r'C:\Users\ian\AppData\Roaming\MetaQuotes\Terminal\DE9A4B13809164D991CFFF8AF2B25C58\Tester\logs\20260913.log')
t=p.read_text(encoding='utf-16'); lines=[l for l in t.splitlines() if '\t11:' in l];gzip.open('evidence/tick_usdjpy_01/journal.log.gz','wt',encoding='utf8').write('\n'.join(lines))
print('saved journal lines',len(lines),'discard warnings',sum('discarded' in l for l in lines))
