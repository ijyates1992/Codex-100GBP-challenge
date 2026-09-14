from pathlib import Path
p=Path('src/Challenge.mq5');s=p.read_text().replace(' TrackEquity();\n}\nvoid OnTick()', '}\nvoid OnTick()');p.write_text(s)
p=Path('tools/analyse.py');s=p.read_text().replace("close.profit.sum()-stats['profit']","close.profit.sum()-stats.get('fees',0)-stats['profit']");p.write_text(s)
