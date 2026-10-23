"""Reproducible teaching simulation. No human responses or measured sessions."""
from pathlib import Path
import csv,json,random,statistics,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]; L6=R.parent/'lab6'
rng=random.Random(20261024)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
def write(path,rows):
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def clip(x):return max(1,min(5,round(x)))
pairs=[('сложный','простой'),('хаотичный','упорядоченный'),('перегруженный','лаконичный'),('устаревший','современный'),('неприятный','приятный'),('тусклый','выразительный'),('неуверенный','надёжный'),('чужой','привычный'),('тяжёлый','лёгкий'),('раздражающий','спокойный'),('нечитабельный','читабельный'),('непоследовательный','целостный'),('холодный','дружелюбный'),('отвлекающий','сосредоточенный'),('любительский','профессиональный')]
semantic=[]
for n in range(1,11):
 preference=rng.choice(['blue','blue','green','plum']);bias=rng.gauss(0,.27)
 for device in ['desktop','mobile']:
  for theme in ['blue','green','plum']:
   for p,(neg,pos) in enumerate(pairs,1):
    base={'blue':3.9,'green':3.66,'plum':3.46}[theme]+bias+(.35 if preference==theme else 0)-(.14 if device=='mobile' else 0)
    # expressive and friendly are not guaranteed to favor the eventual winner
    if p in (6,13) and theme=='plum':base+=.45
    semantic.append(dict(data_origin='synthetic',respondent=f'S{n:02}',device=device,palette=theme,pair=p,negative=neg,positive=pos,rating=clip(rng.gauss(base,.65))))
write(R/'data/semantic.csv',semantic)
means={d:{t:round(statistics.mean(x['rating'] for x in semantic if x['device']==d and x['palette']==t),3) for t in ['blue','green','plum']} for d in ['desktop','mobile']}
fig,ax=plt.subplots(figsize=(8,3.6)); xs=range(15)
for theme,col in [('blue','#345fd1'),('green','#167658'),('plum','#8050a5')]:
 ax.plot(list(xs),[statistics.mean(x['rating'] for x in semantic if x['palette']==theme and x['pair']==p) for p in range(1,16)],'o-',label=theme,color=col)
ax.set(ylim=(1,5),xticks=list(xs),xticklabels=range(1,16),xlabel='Номер пары',ylabel='Средняя оценка',title='Семантический профиль · синтетические данные, n=10');ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(R/'assets/semantic.png',dpi=170);plt.close(fig)
tasks=[('T1','Войти',18),('T2','Создать папку',24),('T3','Найти файл',20),('T4','Создать ссылку с паролем',43),('T5','Восстановить из корзины',34),('T6','Открыть историю версий',29)]
performance=[];sus=[];tree=[];expect=[]
for n in range(1,11):
 pace=rng.uniform(.72,1.4);ability=rng.gauss(0,.5)
 for device in ['desktop','mobile']:
  for tid,title,base in tasks:
   success=rng.random()>(.045+(.06 if device=='mobile' else 0)+(.06 if tid in ['T4','T6'] else 0))
   sec=round(base*pace*(1.27 if device=='mobile' else 1)*rng.uniform(.75,1.4)*(1.45 if not success else 1),1)
   performance.append(dict(data_origin='synthetic',respondent=f'S{n:02}',device=device,task=tid,title=title,success=int(success),time_seconds=sec,errors=rng.choices([0,1,2],[.65,.28,.07])[0]+int(not success),SEQ_1_7=max(1,min(7,round(rng.gauss(5.7 if success else 2.6,.8))))))
  row=dict(data_origin='synthetic',respondent=f'S{n:02}',device=device)
  for i in range(1,11):
   positive=clip(rng.gauss(4.05+ability-(.18 if device=='mobile' else 0),.58));row[f'Q{i}']=positive if i%2 else 6-positive
  row['SUS']=2.5*sum(row[f'Q{i}']-1 if i%2 else 5-row[f'Q{i}'] for i in range(1,11));sus.append(row)
  for tid,target in [('C1','Корзина/Восстановление'),('C2','Мои файлы/Файл/История версий'),('C3','Общий доступ/Ссылки'),('C4','Избранное')]:
   success=int(rng.random()>(.11 if tid=='C2' else .06));direct=int(success and rng.random()>.17)
   tree.append(dict(data_origin='synthetic',respondent=f'S{n:02}',device=device,task=tid,target=target,selected=target if success else 'Мои файлы',success=success,direct=direct,time_seconds=round(rng.uniform(7,24)*(1.2 if device=='mobile' else 1),1),method='local_tree_simulation_not_Treejack'))
  for eid,title in [('E1','Поиск'),('E2','Общий доступ'),('E3','История версий'),('E4','Восстановление')]:
   expect.append(dict(data_origin='synthetic',respondent=f'S{n:02}',device=device,item=eid,title=title,expected_behavior_matches=int(rng.random()>(.23 if eid=='E3' else .10))))
write(L6/'data/performance.csv',performance);write(L6/'data/sus.csv',sus);write(L6/'data/tree_results.csv',tree);write(L6/'data/expectancy.csv',expect)
summary={'data_origin':'synthetic','seed':20261024,'simulated_profiles':10,'note':'All respondent rows are generated, not observations of people. Same profiles reused across conditions; conditions are correlated. No inferential claims.', 'semantic_means':means,'performance':{},'sus':{},'tree':{},'expectancy':{}}
for d in ['desktop','mobile']:
 summary['performance'][d]={t[0]:{'success':sum(x['success'] for x in performance if x['device']==d and x['task']==t[0]),'n':10,'median_success_seconds':round(statistics.median(x['time_seconds'] for x in performance if x['device']==d and x['task']==t[0] and x['success']),1)} for t in tasks}
 summary['sus'][d]={'mean':round(statistics.mean(x['SUS'] for x in sus if x['device']==d),2),'min':min(x['SUS'] for x in sus if x['device']==d),'max':max(x['SUS'] for x in sus if x['device']==d)}
 summary['tree'][d]={k:{'success':sum(x['success'] for x in tree if x['device']==d and x['task']==k),'direct':sum(x['direct'] for x in tree if x['device']==d and x['task']==k),'n':10} for k in ['C1','C2','C3','C4']}
 summary['expectancy'][d]={k:sum(x['expected_behavior_matches'] for x in expect if x['device']==d and x['item']==k) for k in ['E1','E2','E3','E4']}
# Explicit sequences make the arithmetic independently checkable.
models=[]
for form,chars in [('Вход',36),('Новая папка',12),('Ссылка с паролем',10)]:
 for variant in ['A','B']:
  for method in ['mouse','mixed']:
   if form=='Вход': counts={'K':chars+(3 if method=='mouse' else 3),'P':3 if method=='mouse' else 1,'H':4 if method=='mouse' else 1,'M':3 if variant=='A' else 2}
   elif form=='Новая папка': counts={'K':chars+(3 if method=='mouse' else 2),'P':3 if method=='mouse' else 1,'H':2 if method=='mouse' else 1,'M':3 if variant=='A' else 2}
   else:counts={'K':chars+(5 if method=='mouse' else 6),'P':5 if method=='mouse' else 2,'H':2 if method=='mouse' else 1,'M':4 if variant=='A' else 2}
   if variant=='A':counts['P']+=2;counts['K']+=2
   time=round(sum(counts[k]*v for k,v in {'K':.2,'P':1.1,'H':.4,'M':1.35}.items()),2)
   models.append(dict(form=form,variant=variant,input_method=method,**counts,estimated_seconds=time,interpretation='analytical_model_not_measured'))
write(L6/'data/goms.csv',models)
mobile=[]
for form,k,t,m in [('Вход',36,3,2),('Новая папка',12,3,2),('Ссылка с паролем',10,5,2)]:
 mobile.append(dict(form=form,K=k,T=t,M=m,estimated_seconds=round(.2*(k+t)+1.35*m,2),assumption='T=K=0.2s; no swipe, no network response; not measured'))
write(L6/'data/mobile_klm.csv',mobile)
(R/'data/summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
for dest in [R/'data',L6/'data']:(dest/'PROVENANCE.json').write_text(json.dumps({'origin':'synthetic','seed':20261024,'generated_by':'scripts/model_study.py','human_participants':0,'purpose':'Учебное моделирование оценок дизайна и тестирования. Не результаты реального исследования.','treejack_run':False},ensure_ascii=False,indent=2),encoding='utf8')
fig,axes=plt.subplots(1,2,figsize=(9,3.6))
for i,d in enumerate(['desktop','mobile']):
 vals=[summary['performance'][d][t[0]]['success']*10 for t in tasks];axes[0].bar([j+(i-.5)*.36 for j in range(6)],vals,width=.35,label=d)
axes[0].set(xticks=range(6),xticklabels=[t[0] for t in tasks],ylim=(0,105),ylabel='Успех, %',title='Выполнение заданий');axes[0].legend()
axes[1].boxplot([[x['SUS'] for x in sus if x['device']==d] for d in ['desktop','mobile']],tick_labels=['desktop','mobile']);axes[1].set(ylim=(0,100),ylabel='SUS, 0-100',title='Распределение SUS');fig.suptitle('Учебная симуляция · 10 профилей, реальные сессии не проводились');fig.tight_layout();fig.savefig(L6/'assets/results.png',dpi=170);plt.close(fig)
print(json.dumps(summary,ensure_ascii=False,indent=2))
