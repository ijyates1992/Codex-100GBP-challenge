from bs4 import BeautifulSoup
from pathlib import Path
import json
p=Path('evidence/tick_usdjpy_01/tick_usdjpy_01.htm'); s=BeautifulSoup(p.read_text(encoding='utf-16'),'html.parser')
for row in s.select('tr'):
 cells=[' '.join(x.stripped_strings) for x in row.select('td')]
 if any(any(k in x for k in ['History Quality','Drawdown','Total Net','Profit Factor','Total Trades','Leverage','Bars:','Ticks:']) for x in cells):print(cells)
