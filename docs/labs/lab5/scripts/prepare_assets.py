"""Make comparison sheets from native IAB viewport captures, without iframe cropping."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import csv
R=Path(__file__).resolve().parents[1];L6=R.parent/'lab6'
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',23)
def sheet(name,specs,cols,cell):
 out=Image.new('RGB',(cols*cell[0],((len(specs)+cols-1)//cols)*cell[1]),'#f6f8f7');d=ImageDraw.Draw(out)
 for k,(file,label) in enumerate(specs):
  im=Image.open(R/'assets'/file).convert('RGB');im.thumbnail((cell[0]-24,cell[1]-64));x=k%cols*cell[0]+(cell[0]-im.width)//2;y=k//cols*cell[1]+52
  out.paste(im,(x,y));d.text((k%cols*cell[0]+14,k//cols*cell[1]+14),label,font=font,fill='#17251f')
 out.save(R/'assets'/name)
sheet('palettes-sheet.png',[(f'palette-{t}-{d}.png',t+' / '+d) for t in ['brand','contrast','emerald'] for d in ['desktop','mobile']],2,(800,570))
sheet('web-sheet.png',[(f'web{w}.png',str(w)+' CSS px') for w in [1440,1100,900,650,480,360]],2,(800,650))
sheet('mobile-sheet.png',[(f'{n}.png',f'{w} x {h}') for n,w,h in [('mobile375',375,670),('mobile390',390,844),('mobile412',412,915),('tablet768',768,1024),('tablet1024',1024,1366)]],3,(500,760))
sheet('continuity-sheet.png',[('lr2-d_web_files.png','ЛР2 / исходный web'),('web1440.png','ЛР5 / web'),('lr2-d_mob_files.png','ЛР2 / исходный mobile'),('mobile375.png','ЛР5 / mobile')],2,(850,710))
def luminance(color):
 vals=[int(color[i:i+2],16)/255 for i in (1,3,5)];linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals];return sum(a*b for a,b in zip(linear,[.2126,.7152,.0722]))
rows=[]
for fg,bg,label,required in [('#17251f','#ffffff','Основной текст',True),('#5d6f66','#ffffff','Вторичный текст',True),('#ffffff','#1f7a4b','Кнопка выбранного варианта',True),('#17251f','#f6f8f7','Текст на фоне',True),('#1f7a4b','#eaf4ee','Активная навигация',True),('#003c82','#ffffff','Ссылка',True),('#ffffff','#2e9e62','Исходный brand с белым текстом',False)]:
 a,b=sorted([luminance(fg),luminance(bg)]);ratio=(b+.05)/(a+.05);rows.append(dict(foreground=fg,background=bg,usage=label,ratio=round(ratio,3),passes_4_5=ratio>=4.5,required_selected_pair=required))
with (L6/'data/contrast.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
print('Sheets and contrast table built')
