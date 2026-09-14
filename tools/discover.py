import MetaTrader5 as m,json,datetime,pathlib
assert m.initialize(path=r'C:\Program Files\IG Markets MetaTrader 5 Terminal\terminal64.exe'), m.last_error()
a=m.account_info(); assert a and a.trade_mode==m.ACCOUNT_TRADE_MODE_DEMO
out={'account':{k:getattr(a,k) for k in ['currency','leverage','margin_so_mode','margin_so_call','margin_so_so','server']},'symbols':[]}
for s in m.symbols_get():
 m.symbol_select(s.name,True)
 s=m.symbol_info(s.name); t=m.symbol_info_tick(s.name)
 d=s._asdict(); d['margin_buy_min']=m.order_calc_margin(m.ORDER_TYPE_BUY,s.name,s.volume_min,t.ask) if t and t.ask else None
 d['margin_sell_min']=m.order_calc_margin(m.ORDER_TYPE_SELL,s.name,s.volume_min,t.bid) if t and t.bid else None
 out['symbols'].append(d)
 print(s.name,s.path,s.volume_min,s.trade_contract_size,d['margin_buy_min'],datetime.datetime.fromtimestamp(t.time,datetime.timezone.utc).isoformat() if t else None,flush=True)
pathlib.Path('evidence/broker.json').write_text(json.dumps(out,indent=2))
m.shutdown()
