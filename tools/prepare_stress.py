"""Create a separately named quote replay with half a pip added to every ask."""
from pathlib import Path
for original, target in [('ImportIG','ImportStress'),('ImportGap','ImportStressGap')]:
    s=Path(f'src/{original}.mq5').read_text()
    s=s.replace('string target="GBP100_USDJPY";', 'string target="GBP100_USDJPY_STRESS";')
    s=s.replace('ticks[i].ask=raw[i].ask*0.001;', 'ticks[i].ask=(raw[i].ask+5)*0.001;')
    s=s.replace('rates[j].spread=(int)FileReadNumber(f);', 'rates[j].spread=(int)FileReadNumber(f)+5;')
    s=s.replace('(int)MathRound(check[i].ask*1000)!=raw[i].ask)', '(int)MathRound(check[i].ask*1000)!=raw[i].ask+5)')
    s=s.replace('import-result.txt','stress-import-result.txt')
    Path(f'src/{target}.mq5').write_text(s)
