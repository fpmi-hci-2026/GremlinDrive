"""Independent consistency checks using only the Python standard library."""
from pathlib import Path
import csv,json,statistics,math
L6=Path(__file__).resolve().parents[1];L5=L6.parent/'lab5'
def read(p):
 with p.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
s=json.loads((L5/'data/summary.json').read_text());sem=read(L5/'data/semantic.csv');sus=read(L6/'data/sus.csv');perf=read(L6/'data/performance.csv');tree=read(L6/'data/tree_results.csv');expect=read(L6/'data/expectancy.csv')
assert s['simulated_profiles']==15
assert [len(x) for x in [sem,sus,perf,tree,expect]]==[1350,30,210,120,120]
for rows in [sem,sus,perf,tree,expect]:
 assert all(x['data_origin']=='synthetic' for x in rows)
 assert {x['respondent'] for x in rows}=={f'S{n:02}' for n in range(1,16)}
assert len({(x['respondent'],x['device'],x['palette'],x['pair']) for x in sem})==1350
assert all(1<=int(x['rating'])<=5 for x in sem)
for d in ['desktop','mobile']:
 for t in ['brand','contrast','emerald']:
  actual=statistics.mean(int(x['rating']) for x in sem if x['device']==d and x['palette']==t)
  assert round(actual,3)==s['semantic_means'][d][t]
 vals=[]
 for r in [x for x in sus if x['device']==d]:
  q=[int(r[f'Q{i}']) for i in range(1,11)];assert all(1<=x<=5 for x in q)
  total=(sum(q[::2])-5+25-sum(q[1::2]))*2.5
  assert total==float(r['SUS']);vals.append(total)
 assert round(statistics.mean(vals),2)==s['sus'][d]['mean'] and min(vals)==s['sus'][d]['min'] and max(vals)==s['sus'][d]['max']
 for tid,expected in s['performance'][d].items():
  rows=[x for x in perf if x['device']==d and x['task']==tid];ok=[x for x in rows if x['success']=='1']
  assert len(ok)==expected['success'] and len(rows)==15 and expected['n']==15
  assert round(statistics.median(float(x['time_seconds']) for x in ok),1)==expected['median_success_seconds']
 for tid,expected in s['tree'][d].items():
  rows=[x for x in tree if x['device']==d and x['task']==tid]
  assert sum(int(x['success']) for x in rows)==expected['success']
  assert sum(int(x['direct']) for x in rows)==expected['direct'] and len(rows)==15
 for eid,expected in s['expectancy'][d].items():assert sum(int(x['expected_behavior_matches']) for x in expect if x['device']==d and x['item']==eid)==expected
assert len({(x['respondent'],x['device'],x['task']) for x in perf})==210
assert all(0<float(x['time_seconds'])<=180 and 1<=int(x['SEQ_1_7'])<=7 for x in perf)
assert all(int(x['direct'])<=int(x['success']) for x in tree)
assert all(x['target'].startswith('Профиль/Корзина') for x in tree if x['device']=='mobile' and x['task']=='C1')
models=read(L6/'data/goms.csv');assert len(models)==12
for r in models:assert math.isclose(sum(float(r[k])*v for k,v in [('K',.2),('P',1.1),('H',.4),('M',1.35)]),float(r['estimated_seconds']))
for r in read(L6/'data/mobile_klm.csv'):assert math.isclose(.2*(int(r['K'])+int(r['T']))+1.35*int(r['M']),float(r['estimated_seconds']))
layout=json.loads((L6/'data/layout-checks.json').read_text());assert len(layout)==11
assert all(x['width']==x['scrollWidth'] and x['minActionWidth']>=44 and x['minActionHeight']>=44 for x in layout)
contrast=read(L6/'data/contrast.csv')
for x in contrast:
 def lum(h):
  vals=[int(h[i:i+2],16)/255 for i in [1,3,5]]
  return sum((v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4)*w for v,w in zip(vals,[.2126,.7152,.0722]))
 a,b=sorted([lum(x['foreground']),lum(x['background'])]);assert round((b+.05)/(a+.05),3)==float(x['ratio'])
 if x['required_selected_pair']=='True':assert float(x['ratio'])>=4.5
qa=json.loads((L6/'data/prototype-checks.json').read_text());assert qa['method']=='manual_IAB' and all(x['passed'] for x in qa['checks'])
print('OK: 15 modeled profiles; raw data, SUS, medians, trees, expectations, 12 GOMS, 3 mobile KLM; 11 viewport checks; selected contrast pairs; observed prototype checks')
