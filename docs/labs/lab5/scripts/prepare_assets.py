from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import csv
R=Path(__file__).resolve().parents[1];L6=R.parent/'lab6'
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',24)
def cropped(name,w,h):
 im=Image.open(R/'assets'/name).convert('RGB');sc=min(1180/w,640/h,1);left=(1280-w*sc)/2
 return im.crop((int(left),64,int(left+w*sc),int(64+h*sc)))
def sheet(name,specs,cols,cell=(800,720)):
 rows=(len(specs)+cols-1)//cols;out=Image.new('RGB',(cols*cell[0],rows*cell[1]),'#f0f3f8');d=ImageDraw.Draw(out)
 for k,(file,w,h,label) in enumerate(specs):
  im=cropped(file,w,h);im.thumbnail((cell[0]-24,cell[1]-62));x=(k%cols)*cell[0]+(cell[0]-im.width)//2;y=(k//cols)*cell[1]+48
  out.paste(im,(x,y));d.text(((k%cols)*cell[0]+15,(k//cols)*cell[1]+12),label,font=font,fill='#202c40')
 out.save(R/'assets'/name)
sheet('palettes-sheet.png',[(f'palette-{t}-{d}.png',390 if d=='mobile' else 1440,844 if d=='mobile' else 900,t+' / '+d) for t in ['blue','green','plum'] for d in ['desktop','mobile']],2,(800,570))
sheet('web-sheet.png',[(f'web{w}.png',w,900,str(w)+' CSS px') for w in [1440,1100,900,650,480,360]],2,(800,650))
sheet('mobile-sheet.png',[(f'{n}.png',w,h,str(w)+' x '+str(h)) for n,w,h in [('mobile360',360,800),('mobile390',390,844),('mobile412',412,915),('tablet768',768,1024),('tablet1024',1024,1366)]],3,(500,760))
def luminance(color):
 vals=[int(color[i:i+2],16)/255 for i in (1,3,5)];linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals];return sum(a*b for a,b in zip(linear,[.2126,.7152,.0722]))
rows=[]
for fg,bg,label in [('#202c40','#ffffff','Основной текст'),('#68768b','#ffffff','Вторичный текст'),('#ffffff','#345fd1','Кнопка Blue'),('#202c40','#f6f8fc','Текст на фоне'),('#345fd1','#edf2ff','Активная навигация')]:
 a,b=sorted([luminance(fg),luminance(bg)]);ratio=(b+.05)/(a+.05);rows.append(dict(foreground=fg,background=bg,usage=label,ratio=round(ratio,3),passes_4_5=ratio>=4.5))
with (L6/'data/contrast.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(rows)
