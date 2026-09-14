import json,pathlib,datetime as dt,hashlib
m=json.load(open('evidence/USDJPY-raw-manifest.json'));d=m['days'];out={'source':m['source'],'first_day':d[0]['day'],'last_day':d[-1]['day'],'ticks':sum(x['ticks'] for x in d),'minutes':sum(x['bars'] for x in d),'empty_weekdays':[x['day'] for x in d if not x['ticks'] and dt.datetime.strptime(x['day'],'%Y%m%d').weekday()<5]}
pathlib.Path('evidence/quote-coverage.json').write_text(json.dumps(out,indent=2))
