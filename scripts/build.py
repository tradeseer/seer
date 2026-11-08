import json,datetime,collections,pathlib,html,hashlib
root=pathlib.Path(__file__).resolve().parent.parent
x=json.load(open(root/'data/seer-anonymized.json'))
def ts(v): return int(datetime.datetime.fromisoformat(v).timestamp()*1000)
bars={}
for t in x['trades']:
 for s in ['entry','exit']:
  for b in t[s]['market']['recent_bars']:
   bars[t['symbol'],b['start_at']]=b
out=[]
for t in x['trades']:
 e=t['entry'];a=e['action'];en=t['entry_execution'];ex=t['exit_execution'];m=e['market'];end=ts(ex['at']);start=ts(e['decision_at'])-8*60000
 bs=sorted([b for (sym,k),b in bars.items() if sym==t['symbol'] and start<=ts(k)<end],key=lambda b:b['start_at'])
 out.append(dict(id=t['trade_id'],symbol=t['symbol'],decision=ts(e['decision_at']),eligible=ts(t['entry_latency']['eligible_at']),entry=ts(en['at']),exit=end,decisionClose=m['last_close'],entryPrice=en['effective_price'],exitPrice=ex['effective_price'],entryReference=en['reference_price'],exitReference=ex['reference_price'],quantity=en['quantity'],fraction=a['cash_fraction'],stop=t['exit_plan']['stop_price'],target=t['exit_plan']['target_price'],pnl=t['result']['net_pnl_usd'],cost=t['result']['total_costs_usd'],reason=a['rationale'],observations=a.get('observations',[]),counter=a.get('counter_evidence',[]),trigger=t['exit']['action']['trigger'],exitReason=t['exit']['action']['rationale'],triggerStart=ts(t['exit_latency']['trigger_interval_start']) if 'trigger_interval_start' in t['exit_latency'] else None,news=e.get('news',[]),bars=[[ts(b['start_at']),b['open'],b['high'],b['low'],b['close']] for b in bs]))
data={'trades':out,'sources':[{k:v for k,v in s.items() if k in ['source_id','url','summary','published_at','published_date','modified_at']} for s in x['news_sources']],'performance':x['performance'],'risk':x['risk_metrics']['observed_equity_drawdown']['maximum_drawdown_pct']}
payload=json.dumps(data,separators=(',',':')).replace('<',chr(92)+'u003c')
template=(root/'src/replay.html').read_text().replace('__DATA__',payload)
(root/'replay.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Seer — Weekly replay</title><style>body{margin:0;background:#fff}#seer-replay{max-width:1120px;margin:auto} .report-nav{max-width:1080px;margin:0 auto;padding:14px 20px;display:flex;gap:20px;font:13px system-ui;color:#62685f}.report-nav a{color:inherit;text-underline-offset:4px}#seer-replay .mast{padding-right:0}#seer-replay [data-lucide]{font-style:normal;font-size:18px;line-height:1}</style></head><body>'+template+'</body></html>')
print('Built replay.html from',len(out),'trades')

money=lambda n: f'${n:,.2f}'
signed=lambda n: ('+' if n>=0 else '−')+money(abs(n))
color=lambda n: 'positive' if n>=0 else 'negative'
escape=html.escape
perf=x['performance'];risk=x['risk_metrics']
daily=x['daily_summary'];stocks=sorted(x['stock_summary'],key=lambda s:s['net_pnl_usd'],reverse=True)
daily_rows=''.join(f'<tr><td>{datetime.date.fromisoformat(d["date"]).strftime("%a %d")}</td><td>{d["trades"]}</td><td class="{color(d["net_pnl_usd"])}">{signed(d["net_pnl_usd"])}</td><td>{money(d["closing_cash_usd"])}</td></tr>' for d in daily)
stock_rows=''.join(f'<tr><td>{escape(s["symbol"])}</td><td>{s["trades"]}</td><td class="{color(s["net_pnl_usd"])}">{signed(s["net_pnl_usd"])}</td></tr>' for s in stocks)
trade_rows=[]
for t in x['trades']:
 en=t['entry_execution'];ex=t['exit_execution'];at=datetime.datetime.fromisoformat(en['at']);end=datetime.datetime.fromisoformat(ex['at']);pnl=t['result']['net_pnl_usd']
 trade_rows.append(f'<tr><td>{escape(t["trade_id"].replace("TRADE-",""))}</td><td>{escape(t["symbol"])}</td><td>{at.strftime("%b %d")}</td><td>{at.strftime("%H:%M")} · {money(en["effective_price"])}</td><td>{end.strftime("%H:%M")} · {money(ex["effective_price"])}</td><td>{en["quantity"]}</td><td class="{color(pnl)}">{signed(pnl)}</td></tr>')
values=[e['equity_usd'] for e in x['equity_curve']];lo=8000;hi=18000
start_day=datetime.date.fromisoformat(x['period']['start'][:10])
def point(e):
 at=datetime.datetime.fromisoformat(e['at']);elapsed=(at.date()-start_day).days*390+at.hour*60+at.minute-570+at.second/60
 return f'{max(0,min(1000,elapsed/(5*390)*1000)):.2f},{150-(e["equity_usd"]-lo)/(hi-lo)*150:.2f}'
points=' '.join(point(e) for e in x['equity_curve'])
metrics=[('Return',f'+{perf["net_return_pct"]:.2f}%'),('Final equity',money(perf['ending_cash_usd'])),('Closed trades',str(perf['closed_trades'])),('Win rate',f'{risk["win_rate_pct"]:.1f}%'),('Profit factor',f'{risk["profit_factor"]:.2f}'),('Max drawdown',f'{risk["observed_equity_drawdown"]["maximum_drawdown_pct"]:.2f}%')]
metric_html=''.join(f'<div class="metric"><span>{label}</span><strong>{value}</strong></div>' for label,value in metrics)
page=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Seer — Trading performance · August 17–21, 2026</title><link rel="stylesheet" href="assets/report.css"></head>
<body><main>
<header><img src="assets/seer.png" alt="Seer"><nav aria-label="Report navigation"><a href="data/seer-anonymized.json" download>Raw JSON</a><a class="play" href="replay.html">Play the week</a></nav></header>
<div class="heading"><h1>Trading performance</h1><span class="date">August 17–21, 2026</span></div>
<p class="intro">Sharing an anonymized trading-performance report. Proprietary features, signal-selection logic, and model architecture have been withheld to protect the strategy’s IP.</p>
<div class="metrics">{metric_html}</div>
<section class="section" aria-labelledby="equity-title"><div class="section-head"><h2 id="equity-title">Equity</h2><span>$10,000 starting capital · USD</span></div>
<div class="equity"><div class="axis" aria-hidden="true"><span>$18K</span><span>$13K</span><span>$8K</span></div><div class="plot"><svg viewBox="0 0 1000 150" preserveAspectRatio="none" role="img" aria-label="Equity during market hours, August 17–21. Starts at 10,000 dollars and ends at 16,522 dollars and 26 cents. Maximum observed drawdown 13.51 percent."><path d="M0 0H1000 M0 75H1000 M0 150H1000" stroke="#e4e7e0" stroke-width="1" fill="none" vector-effect="non-scaling-stroke"/><path d="M0 120H1000" stroke="#c7cec0" stroke-width="1" stroke-dasharray="3 4" fill="none" vector-effect="non-scaling-stroke"/><polyline points="{points}" fill="none" stroke="#80a82b" stroke-width="1.7" stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg><div class="dates"><span>17 Mon</span><span>18 Tue</span><span>19 Wed</span><span>20 Thu</span><span>21 Fri</span></div></div></div>
<p class="stat-note">Market hours · Eastern Time</p></section>
<div class="tables"><section class="section"><div class="section-head"><h2>By day</h2><span>{signed(perf['net_pnl_usd'])} net</span></div><table><thead><tr><th scope="col">August</th><th scope="col">Trades</th><th scope="col">Net P&amp;L</th><th scope="col">Closing cash</th></tr></thead><tbody>{daily_rows}</tbody></table></section>
<section class="section"><div class="section-head"><h2>By stock</h2><span>{perf['distinct_stocks']} stocks</span></div><div class="stock-wrap" tabindex="0" role="region" aria-label="Results by stock"><table><thead><tr><th scope="col">Symbol</th><th scope="col">Trades</th><th scope="col">Net P&amp;L</th></tr></thead><tbody>{stock_rows}</tbody></table></div></section></div>
<details><summary>All {perf['closed_trades']} closed trades</summary><p class="trade-notes">Entry and exit timestamps · Eastern Time. Net P&amp;L includes the modeled transaction costs in the report. Open the replay to explore decisions, risk levels, and sources.</p><div class="table-scroll" tabindex="0" role="region" aria-label="All closed trades"><table><thead><tr><th scope="col">Trade</th><th scope="col">Symbol</th><th scope="col">Date</th><th scope="col">Entry</th><th scope="col">Exit</th><th scope="col">Shares</th><th scope="col">Net P&amp;L</th></tr></thead><tbody>{''.join(trade_rows)}</tbody></table></div></details>
<footer><a href="docs/README.md">Documentation</a><a href="data/seer-anonymized.json" download>Original JSON</a><span>Timestamped decisions · Risk management · Modeled costs</span></footer>
</main></body></html>'''
(root/'index.html').write_text(page)
md_rows='\n'.join(f'| {d["date"]} | {d["trades"]} | {signed(d["net_pnl_usd"])} | {money(d["closing_cash_usd"])} |' for d in daily)
readme=f'''<img src="assets/seer.png" alt="Seer" width="110">

# Trading-performance report

Sharing an anonymized trading-performance report (Aug 17–21, 2026). Proprietary features, signal-selection logic, and model architecture have been withheld to protect the strategy's IP.

**Performance ($10K starting capital):**

- Return: **+{perf['net_return_pct']:.2f}%** ({money(perf['ending_cash_usd'])} final equity)
- Closed trades: {perf['closed_trades']} | Win rate: {risk['win_rate_pct']:.1f}%
- Profit factor: {risk['profit_factor']:.2f}
- Max drawdown: {risk['observed_equity_drawdown']['maximum_drawdown_pct']:.2f}%

The report includes timestamped decisions, trade execution logic, risk management, and modeled transaction costs.

[Raw JSON](data/seer-anonymized.json) · [Readable report](index.html) · [Weekly replay](replay.html) · [Documentation](docs/README.md)

![Performance report preview](assets/report-preview.jpg)

## Daily results

| Date | Closed trades | Net P&L | Closing cash |
| --- | ---: | ---: | ---: |
{md_rows}

## Open the report

Download or clone this repository, then open **`index.html`** in your browser. Use **Play the week** for the interactive replay. The HTML links above show source code on GitHub; the downloaded files run locally without installation.

```sh
git clone https://github.com/tradeseer/seer.git
cd seer
```

The raw JSON is unchanged. Its checksum is in [`data/SHA256SUMS`](data/SHA256SUMS). The readable report and replay are derived views; the proprietary strategy is not included.
'''
(root/'README.md').write_text(readme)
print('Built index.html and README.md')
