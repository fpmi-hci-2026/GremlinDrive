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
css='''*{box-sizing:border-box}body{margin:0;background:#f6f8fc;color:#202c40;font:16px/1.65 system-ui,sans-serif}header,main,footer{max-width:1120px;margin:auto;padding:24px}header{display:flex;justify-content:space-between;gap:24px;flex-wrap:wrap}a{color:#345fd1}header a{text-decoration:none}nav{display:flex;gap:20px}.hero{padding:40px 0 30px}.eyebrow{font-size:13px;color:#68768b}h1{font-size:clamp(32px,5vw,54px);line-height:1.15;max-width:900px;letter-spacing:-.04em}h2{margin-top:44px;font-size:27px}h3{margin-top:28px}.actions{display:flex;gap:12px;flex-wrap:wrap}.actions a{background:#345fd1;color:white;padding:12px 20px;border-radius:9px;text-decoration:none}.actions a.secondary{background:white;color:#345fd1;border:1px solid #cbd5e5}.notice{background:#edf2ff;border-left:4px solid #345fd1;padding:18px 22px;border-radius:8px}.report{background:white;border:1px solid #e1e6f0;border-radius:18px;padding:32px;margin-top:30px}.report p{max-width:85ch}figure{margin:28px 0}figure img{display:block;max-width:100%;max-height:950px;margin:auto;border:1px solid #e1e6f0;border-radius:8px}figcaption{font-size:13px;color:#68768b;text-align:center;margin-top:8px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:12px;text-align:left;border:1px solid #dce3ef;vertical-align:top}th{background:#edf2ff}.scroll{overflow:auto}footer{font-size:13px;color:#68768b}a:focus-visible{outline:3px solid #345fd1;outline-offset:4px}@media(max-width:600px){header,main,footer{padding:18px}.report{padding:20px}h2{font-size:24px}.actions a{flex:1;text-align:center}}'''
for n,title,links in [(5,'Проектирование прототипа', [('prototype/','Открыть web-прототип'),('prototype/?mobile=1','Мобильная версия'),('prototype/styleguide.html','Руководство по стилю')]),(6,'Оценка интерфейса и модели действий',[('tree.html','Локальный тест дерева'),('forms.html','Варианты форм'),('../lab5/prototype/','Проверить прототип')])]:
 root=R if n==5 else R.parent/'lab6';(root/'study.css').write_text(css)
 buttons=''.join(f'<a class="secondary" href="{url}">{label}</a>' for url,label in links)
 page=f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ЛР{n} · GremlinDrive</title><link rel="stylesheet" href="study.css"></head><body><header><a href="../../">GremlinDrive</a><nav><a href="../">Лабораторные</a><a href="../lab5/">ЛР5</a><a href="../lab6/">ЛР6</a></nav></header><main><section class="hero"><p class="eyebrow">Лабораторная работа {n} · ФПМИ БГУ</p><h1>{title}</h1><p>GremlinDrive · веб- и мобильный интерфейсы</p><div class="actions"><a href="lab{n}-report.pdf">Отчёт PDF</a>{buttons}<a class="secondary" href="../lab5/lab56-source.zip">Исходники и данные</a></div></section><aside class="notice"><strong>Учебное моделирование.</strong> Оценки десяти профилей синтетические. Реальные участники не опрашивались. Технические проверки прототипа выполнены отдельно. Treejack не запускался.</aside><article class="report">{markdown((root/'REPORT.md').read_text())}</article></main><footer>Александр Сытин · GremlinDrive · 2026</footer></body></html>'''
 (root/'index.html').write_text(page)
print('Web reports built')
