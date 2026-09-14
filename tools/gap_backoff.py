from pathlib import Path
p=Path('tools/fill_gap.py');s=p.read_text().replace('ThreadPoolExecutor(4)','ThreadPoolExecutor(1)').replace('time.sleep(1)','time.sleep(60)').replace('body=f.read_bytes() if f.exists() else urllib.request.urlopen(url,timeout=25).read();','body=f.read_bytes() if f.exists() else urllib.request.urlopen(url,timeout=25).read();');p.write_text(s)
