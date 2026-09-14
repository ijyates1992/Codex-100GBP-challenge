from pathlib import Path
# Read-only research runner use after all tests have stopped.
p=Path(r'C:\Users\ian\AppData\Roaming\MetaQuotes\Terminal\DE9A4B13809164D991CFFF8AF2B25C58\config\common.ini')
s=p.read_text(encoding='utf-16');s=s.replace('MaxBars=100000','MaxBars=2000000');p.write_text(s,encoding='utf-16')
