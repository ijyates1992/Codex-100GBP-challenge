from pathlib import Path
import shutil
out=Path('evidence/replay_02');src=Path(r'C:\Users\ian\AppData\Roaming\MetaQuotes\Terminal\DE9A4B13809164D991CFFF8AF2B25C58\TesterReports\GBP100')
for f in src.glob('replay_02*'):shutil.copy2(f,out/f.name)
(out/'status.txt').write_text('Runner stopped after detecting the unit-profit rounding bug. Report retained; no audit or stats accepted for this superseded run.')
p=Path('tools/shortlist.py');s=p.read_text().replace("'replay_'","'corrected_'");p.write_text(s)
