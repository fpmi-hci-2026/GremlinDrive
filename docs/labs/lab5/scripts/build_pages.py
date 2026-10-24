from pathlib import Path
import html,re
R=Path(__file__).resolve().parents[1]
def fmt(s):
 s=html.escape(s);return re.sub(r'(https://[^\s]+)',lambda m:'<a href="'+m[0].rstrip('.')+'">'+m[0].rstrip('.')+'</a>',s)
def markdown(text):
 lines=text.splitlines();out=[];i=0
 while i<len(lines):
  line=lines[i].strip()
  if not line:i+=1;continue
  if line.startswith('#'):
   level=min(3,len(line)-len(line.lstrip('#'))+1);out.append(f'<h{level}>'+fmt(line.lstrip('#').strip())+f'</h{level}>');i+=1;continue
  if line.startswith('!['):
   m=re.match(r'!\[([^]]+)\]\(([^)]+)\)',line);out.append(f'<figure><a href="{m[2]}"><img loading="lazy" src="{m[2]}" alt="{m[1]}"></a><figcaption>{m[1]}</figcaption></figure>');i+=1;continue
  if line.startswith('|'):
   items=[]
   while i<len(lines) and lines[i].strip().startswith('|'):
    cells=lines[i].strip().strip('|').split('|')
    if not all(re.fullmatch(r'[-: ]+',x) for x in cells):items.append(cells)
    i+=1
   out.append('<div class="scroll"><table>')
   for k,row in enumerate(items):tag='th' if k==0 else 'td';out.append('<tr>'+''.join(f'<{tag}>'+fmt(x.strip())+f'</{tag}>' for x in row)+'</tr>')
   out.append('</table></div>');continue
  para=[line];i+=1
  while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','![' ,'|')):para.append(lines[i].strip());i+=1
  out.append('<p>'+fmt(' '.join(para))+'</p>')
 return '\n'.join(out)
css=(R.parent/'shared/labs.css').read_text()+'\n'+(R.parent/'shared/report-pages.css').read_text()
for n,title,links in [(5,'Проектирование прототипа', [('prototype/','Открыть web-прототип'),('prototype/?mobile=1','Мобильная версия'),('prototype/styleguide.html','Руководство по стилю')]),(6,'Оценка интерфейса и модели действий',[('tree.html','Локальный тест дерева'),('forms.html','Варианты форм'),('../lab5/prototype/','Проверить прототип')])]:
 root=R if n==5 else R.parent/'lab6';(root/'study.css').write_text(css)
 buttons=''.join(f'<a class="button secondary" href="{url}">{label}</a>' for url,label in links)
 page=f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ЛР{n} · GremlinDrive</title><link rel="stylesheet" href="study.css"></head><body><header class="site-header"><a class="brand" href="../../"><span class="brand-mark">G</span>GremlinDrive</a><nav><a href="../">Лабораторные</a><a href="../lab5/">ЛР5</a><a href="../lab6/">ЛР6</a></nav></header><main><section class="hero"><p class="eyebrow">Лабораторная работа {n} · ФПМИ БГУ</p><h1>{title}</h1><p>GremlinDrive · веб- и мобильный интерфейсы</p><div class="actions"><a class="button primary" href="lab{n}-report.pdf">Отчёт PDF</a>{buttons}<a class="button secondary" href="../lab5/lab56-source.zip">Исходники и данные</a></div></section><aside class="notice"><strong>Учебное моделирование.</strong> 15 профилей; исходные данные и способ расчёта открыты. Фактическая проверка прототипа описана отдельно.</aside><article class="report">{markdown((root/'REPORT.md').read_text())}</article></main><footer>Александр Сытин · GremlinDrive · 2026</footer></body></html>'''
 (root/'index.html').write_text(page)
print('Web reports built')
