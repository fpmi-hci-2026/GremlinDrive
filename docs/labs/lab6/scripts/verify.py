"""Independently recompute all submitted quantitative results from raw CSV."""
from pathlib import Path
import csv,json,statistics
L6=Path(__file__).resolve().parents[1];L5=L6.parent/'lab5'
def read(p):
 with p.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
s=json.loads((L5/'data/summary.json').read_text());sem=read(L5/'data/semantic.csv');sus=read(L6/'data/sus.csv');perf=read(L6/'data/performance.csv');tree=read(L6/'data/tree_results.csv')
assert len(sem)==900 and len(sus)==20 and len(perf)==120 and len(tree)==80
for rows in [sem,sus,perf,tree,read(L6/'data/expectancy.csv')]:assert all(x['data_origin']=='synthetic' for x in rows)
for d in ['desktop','mobile']:
 for t in ['blue','green','plum']:
  actual=statistics.mean(int(x['rating']) for x in sem if x['device']==d and x['palette']==t)
  assert round(actual,3)==s['semantic_means'][d][t]
 vals=[]
 for r in [x for x in sus if x['device']==d]:
  q=[int(r[f'Q{i}']) for i in range(1,11)];assert all(1<=x<=5 for x in q)
  total=(sum(q[::2])-5+25-sum(q[1::2]))*2.5
  assert total==float(r['SUS']);vals.append(total)
 assert round(statistics.mean(vals),2)==s['sus'][d]['mean']
 for tid,expected in s['performance'][d].items():
  rows=[x for x in perf if x['device']==d and x['task']==tid];ok=[x for x in rows if x['success']=='1']
  assert len(ok)==expected['success'] and len(rows)==10
  assert round(statistics.median(float(x['time_seconds']) for x in ok),1)==expected['median_success_seconds']
models=read(L6/'data/goms.csv');assert len(models)==12
for r in models:
 assert abs(sum(float(r[k])*v for k,v in [('K',.2),('P',1.1),('H',.4),('M',1.35)])-float(r['estimated_seconds']))<1e-8
for r in read(L6/'data/mobile_klm.csv'):
 assert abs(.2*(int(r['K'])+int(r['T']))+1.35*int(r['M'])-float(r['estimated_seconds']))<1e-8
assert len({(x['respondent'],x['device'],x['task']) for x in perf})==120
assert all(int(x['direct'])<=int(x['success']) for x in tree)
print('OK: provenance, row counts, semantic means, SUS, success, medians, GOMS and mobile KLM')

layout=json.loads((L6/"data/layout-checks.json").read_text())
assert len(layout)==11
assert all(x["width"]==x["scrollWidth"] and x["minActionWidth"]>=44 and x["minActionHeight"]>=44 for x in layout)
print("OK: 11 browser layout measurements, no horizontal overflow, action buttons >=44x44")
