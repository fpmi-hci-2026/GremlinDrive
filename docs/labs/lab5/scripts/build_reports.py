"""Portable Cyrillic PDF renderer for the two laboratory reports."""
from pathlib import Path
import re,html
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER,TA_JUSTIFY
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Image,Table,TableStyle,CondPageBreak
R=Path(__file__).resolve().parents[1]
F=Path('/System/Library/Fonts/Supplemental')
for n,f in [('T','Times New Roman.ttf'),('TB','Times New Roman Bold.ttf'),('TI','Times New Roman Italic.ttf')]:pdfmetrics.registerFont(TTFont(n,str(F/f)))
pdfmetrics.registerFontFamily('T',normal='T',bold='TB',italic='TI')
B=ParagraphStyle('Body',fontName='T',fontSize=12,leading=16,spaceAfter=9,alignment=TA_JUSTIFY,allowWidows=0,allowOrphans=0)
H=ParagraphStyle('Heading',parent=B,fontName='TB',fontSize=16,leading=21,spaceBefore=12,spaceAfter=12,alignment=0,keepWithNext=True)
S=ParagraphStyle('Subheading',parent=H,fontSize=13,leading=17)
C=ParagraphStyle('Caption',parent=B,fontSize=10,leading=13,alignment=TA_CENTER)
T=ParagraphStyle('Table',parent=B,fontSize=9,leading=11.5,alignment=0,spaceAfter=0)
CENTER=ParagraphStyle('Center',parent=B,alignment=TA_CENTER)
TITLE=ParagraphStyle('Title',parent=CENTER,fontName='TB',fontSize=21,leading=28)
def inline(s):
 s=html.escape(s.replace('—','-').replace('–','-'));s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s);return s.replace('`','')
def render(root,number,title):
 story=[]
 for x in ['БЕЛОРУССКИЙ ГОСУДАРСТВЕННЫЙ УНИВЕРСИТЕТ','Факультет прикладной математики и информатики','Кафедра технологий программирования']:story.append(Paragraph(x,CENTER))
 story.extend([Spacer(1,3*cm),Paragraph('Лабораторная работа '+str(number),TITLE),Spacer(1,.4*cm),Paragraph(title,TITLE),Spacer(1,.7*cm),Paragraph('Проект GremlinDrive',CENTER),Spacer(1,2*cm)])
 for x in ['Выполнил студент 4 курса группы 10а','Сытин Александр Леонидович','Проектирование человеко-машинных интерфейсов']:story.append(Paragraph(x,ParagraphStyle('Author',parent=B,alignment=0,leftIndent=5*cm)))
 story.extend([Spacer(1,2*cm),Paragraph('Минск 2026',CENTER),PageBreak()])
 lines=(root/'REPORT.md').read_text().splitlines();i=0
 while i<len(lines):
  line=lines[i].strip()
  if not line:i+=1;continue
  if line.startswith('#'):
   story.append(CondPageBreak(3*cm));story.append(Paragraph(inline(line.lstrip('#').strip()),S if line.startswith('##') else H));i+=1;continue
  if line.startswith('!['):
   m=re.match(r'!\[([^]]+)\]\(([^)]+)\)',line);image=Image(str(root/m[2]));limit=15 if 'sheet' in m[2] else 19;scale=min(17*cm/image.imageWidth,limit*cm/image.imageHeight);image.drawWidth=image.imageWidth*scale;image.drawHeight=image.imageHeight*scale;image.hAlign='CENTER';story.extend([image,Spacer(1,6),Paragraph(inline(m[1]),C),Spacer(1,8)]);i+=1;continue
  if line.startswith('|'):
   rows=[]
   while i<len(lines) and lines[i].strip().startswith('|'):
    cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
    if not all(re.fullmatch('[-: ]+',x) for x in cells):rows.append(cells)
    i+=1
   n=len(rows[0]);widths={2:[5*cm,12*cm],3:[4.5*cm,6.25*cm,6.25*cm],4:[4*cm,4.1*cm,6.3*cm,2.6*cm],5:[3.4*cm]*5}[n]
   if rows[0][0]=='Код':widths=[1.3*cm,8*cm,7.7*cm]
   if rows[0][0]=='Версия':widths=[2*cm,7.4*cm,7.6*cm]
   table=Table([[Paragraph(inline(x),T) for x in r] for r in rows],colWidths=widths,repeatRows=1)
   table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eaf0fa')),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#c6ceda')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.extend([table,Spacer(1,12)]);continue
  p=[line];i+=1
  while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','![')):
   p.append(lines[i].strip());i+=1
  story.append(Paragraph(inline(' '.join(p)),B))
 def footer(c,d):
  if d.page>1:c.setFont('T',9);c.setFillColor(colors.HexColor('#586477'));c.drawString(2*cm,1.1*cm,f'GremlinDrive · ЛР{number}');c.drawRightString(A4[0]-2*cm,1.1*cm,str(d.page))
 doc=SimpleDocTemplate(str(root/f'lab{number}-report.pdf'),pagesize=A4,leftMargin=2*cm,rightMargin=2*cm,topMargin=1.7*cm,bottomMargin=1.8*cm,title=f'GremlinDrive. Лабораторная работа {number}',author='Александр Сытин')
 doc.build(story,onFirstPage=footer,onLaterPages=footer)
 print(root/f'lab{number}-report.pdf')
render(R,5,'Проектирование прототипа приложения')
render(R.parent/'lab6',6,'Тестирование и оценка качества прототипа')
