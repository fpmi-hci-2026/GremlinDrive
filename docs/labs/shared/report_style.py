"""Report typography and title page continued from the original GremlinDrive reports."""
from pathlib import Path
import html,re
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER,TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate,Frame,PageTemplate,Paragraph,Spacer,PageBreak,Image,Table,TableStyle,KeepTogether,CondPageBreak
from reportlab.platypus.tableofcontents import TableOfContents

def register_fonts():
 candidates=[Path('/usr/share/fonts/truetype/liberation2'),Path('/usr/share/fonts/truetype/liberation'),Path('/Users/alex/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/truetype')]
 folder=next((x for x in candidates if (x/'LiberationSerif-Regular.ttf').exists()),None)
 if not folder:raise FileNotFoundError('Install Liberation Serif or set an available runtime font directory')
 for name,file in [('TimesRU','LiberationSerif-Regular.ttf'),('TimesRU-Bold','LiberationSerif-Bold.ttf'),('TimesRU-Italic','LiberationSerif-Italic.ttf')]:
  if name not in pdfmetrics.getRegisteredFontNames():pdfmetrics.registerFont(TTFont(name,str(folder/file)))
 pdfmetrics.registerFontFamily('TimesRU',normal='TimesRU',bold='TimesRU-Bold',italic='TimesRU-Italic')
 mono=next((p for p in [Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'),Path('/System/Library/Fonts/Supplemental/Courier New.ttf')] if p.exists()),None)
 if mono and 'CodeRU' not in pdfmetrics.getRegisteredFontNames():pdfmetrics.registerFont(TTFont('CodeRU',str(mono)))
register_fonts()
BODY=ParagraphStyle('body',fontName='TimesRU',fontSize=12,leading=15.8,spaceAfter=8,alignment=TA_JUSTIFY,allowWidows=0,allowOrphans=0,splitLongWords=True)
HEAD=ParagraphStyle('h1',parent=BODY,fontName='TimesRU-Bold',fontSize=14.4,leading=18,spaceBefore=10,spaceAfter=8,alignment=0,keepWithNext=True)
SUB=ParagraphStyle('h2',parent=HEAD,fontSize=12,leading=15.8,spaceBefore=7,spaceAfter=5)
CAP=ParagraphStyle('caption',parent=BODY,fontSize=10.5,leading=13.2,alignment=TA_CENTER,spaceAfter=10)
SMALL=ParagraphStyle('small',parent=BODY,fontSize=9.5,leading=12,alignment=0,spaceAfter=0)
CENTER=ParagraphStyle('center',parent=BODY,alignment=TA_CENTER)
TITLE=ParagraphStyle('title',parent=CENTER,fontSize=17.2,leading=22,spaceAfter=8)
CODE=ParagraphStyle('code',fontName='CodeRU',fontSize=8,leading=10,spaceAfter=10)

def footer(canvas,doc):
 if doc.page==1:
  canvas.saveState();canvas.setFont('TimesRU',12);canvas.drawCentredString(canvas._pagesize[0]/2,18*mm,'Минск, 2026 г.');canvas.restoreState()
 if doc.page>1:
  canvas.saveState();canvas.setFont('TimesRU',12);canvas.setFillColor(colors.black);canvas.drawCentredString(canvas._pagesize[0]/2,10*mm,str(doc.page-1));canvas.restoreState()

class ReportDoc(BaseDocTemplate):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self._heading_count=0
 def afterFlowable(self,flowable):
  if isinstance(flowable,Paragraph) and flowable.style.name in ['h1','h2']:
   level=0 if flowable.style.name=='h1' else 1;self._heading_count+=1;key=f'section-{self._heading_count}';self.canv.bookmarkPage(key)
   self.notify('TOCEntry',(level,flowable.getPlainText(),self.page-1,key))
 def beforeDocument(self):self._heading_count=0

def cover(number,title):
 story=[]
 for text,style in [('БЕЛОРУССКИЙ ГОСУДАРСТВЕННЫЙ УНИВЕРСИТЕТ',ParagraphStyle('university',parent=CENTER,fontName='TimesRU-Bold',fontSize=14.4,leading=18)),('Факультет прикладной математики и информатики',ParagraphStyle('faculty',parent=CENTER,fontSize=14.4,leading=18)),('Кафедра технологий программирования',ParagraphStyle('department',parent=CENTER,fontSize=14.4,leading=18))]:story.append(Paragraph(text,style));story.append(Spacer(1,2*mm))
 story.extend([Spacer(1,30*mm),Paragraph('ОТЧЕТ',TITLE),Spacer(1,3*mm),Paragraph(f'<b>Лабораторная работа №{number}</b>',TITLE),Paragraph('«'+title+'»',TITLE),Spacer(1,7*mm),Paragraph('по курсу «Проектирование человеко-машинных интерфейсов»',ParagraphStyle('course',parent=CENTER,fontSize=14.4,leading=18)),Spacer(1,26*mm)])
 author=ParagraphStyle('author',parent=BODY,alignment=0,leftIndent=79*mm,leading=16)
 for text in ['Выполнил: Сытин Александр Леонидович','Студент группы 10а','Команда проекта <i>GremlinDrive</i>']:story.append(Paragraph(text,author))
 story.append(PageBreak())
 return story

def contents():
 toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc1',fontName='TimesRU',fontSize=12,leading=15.5,spaceBefore=5,leftIndent=0,firstLineIndent=0),ParagraphStyle('toc2',fontName='TimesRU',fontSize=11,leading=14,spaceBefore=3,leftIndent=14,firstLineIndent=0)]
 return [Paragraph('Содержание',ParagraphStyle('contents-title',parent=HEAD)),Spacer(1,8),toc,PageBreak()]

def inline(s):
 s=html.escape(s.replace('—','-').replace('–','-').replace('‑','-'));s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s);return s.replace('`','')

def render_markdown(root):
 story=[];lines=(root/'REPORT.md').read_text().splitlines();i=0;fig=0;tab=0
 while i<len(lines):
  line=lines[i].strip()
  if not line:i+=1;continue
  if line.startswith('#'):
   story.extend([CondPageBreak(24*mm),Paragraph(inline(line.lstrip('#').strip()),SUB if line.startswith('##') else HEAD)]);i+=1;continue
  if line.startswith('!['):
   m=re.match(r'!\[([^]]+)\]\(([^)]+)\)',line);img=Image(str(root/m[2]));max_height=182*mm if 'sheet' in m[2] else 150*mm;scale=min(166*mm/img.imageWidth,max_height/img.imageHeight);img.drawWidth=img.imageWidth*scale;img.drawHeight=img.imageHeight*scale;img.hAlign='CENTER';fig+=1
   story.append(KeepTogether([Spacer(1,5),img,Spacer(1,6),Paragraph(inline(f'Рисунок {fig} - '+m[1]),CAP)]));i+=1;continue
  if line.startswith('|'):
   rows=[]
   while i<len(lines) and lines[i].strip().startswith('|'):
    cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
    if not all(re.fullmatch('[-: ]+',x) for x in cells):rows.append(cells)
    i+=1
   n=len(rows[0]);widths={2:[55,115],3:[44,63,63],4:[54,38.7,38.7,38.6],5:[24,63,27,28,28],6:[42,24,24,24,28,28]}.get(n,[170/n]*n)
   if rows[0][0]=='Код':widths=[15,82,73] if n==3 else [15]+[155/(n-1)]*(n-1)
   if rows[0][0]=='Профиль':widths=[26]+[144/(n-1)]*(n-1)
   tab+=1;caption=Paragraph(f'Таблица {tab}',ParagraphStyle('table-caption',parent=CAP,alignment=0,spaceAfter=4))
   t=Table([[Paragraph(inline(x),SMALL) for x in row] for row in rows],colWidths=[x*mm for x in widths],repeatRows=1,hAlign='LEFT')
   t.setStyle(TableStyle([('LINEABOVE',(0,0),(-1,0),.8,colors.black),('LINEBELOW',(0,0),(-1,0),.5,colors.black),('LINEBELOW',(0,-1),(-1,-1),.8,colors.black),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),5)]));fits=len(rows)<=17 and t.wrap(170*mm,10000)[1]<=220*mm
   group=[caption,t]
   if fits and story and isinstance(story[-1],Paragraph) and story[-1].style.name in ['h1','h2']:group.insert(0,story.pop())
   if fits:story.append(KeepTogether(group))
   else:story.extend(group)
   story.append(Spacer(1,10));continue
  para=[line];i+=1
  while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','![')):para.append(lines[i].strip());i+=1
  story.append(Paragraph(inline(' '.join(para)),BODY))
 return story

def render(root,number,title):
 doc=ReportDoc(str(root/f'lab{number}-report.pdf'),pagesize=A4,leftMargin=25*mm,rightMargin=15*mm,topMargin=18*mm,bottomMargin=18*mm,title=f'GremlinDrive. Лабораторная работа {number}',author='Александр Сытин')
 doc.addPageTemplates(PageTemplate(id='portrait',frames=[Frame(25*mm,18*mm,A4[0]-40*mm,A4[1]-36*mm,id='body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=footer))
 doc.multiBuild(cover(number,title)+contents()+render_markdown(root));print(root/f'lab{number}-report.pdf')
