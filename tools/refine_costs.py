from pathlib import Path
p=Path('tools/minute_screen.py');s=p.read_text().replace('start,end,direction):','start,end,direction,cap=.6,guard=.27,fee=.008):').replace('peak*.73','peak*(1-guard)').replace('bal*.6/ml','bal*cap/ml').replace(';bal+=p;',';p-=round(abs(p)*fee,2);bal+=p;');p.write_text(s)
