"""Render the human-readable supplemental index to a journal-upload PDF.

Requires ReportLab and a directory containing times.ttf/timesbd.ttf/timesi.ttf/
timesbi.ttf (or equivalent Times New Roman files with these names). These fonts
are supplied by the local document environment and are not redistributed.
"""
import argparse
import hashlib
from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, ListFlowable, ListItem

ROOT=Path(__file__).resolve().parents[1]
GITHUB='https://github.com/azureice10/crypto-diffusion/blob/main/'
SUPER=str.maketrans('⁻⁰¹²³⁴⁵⁶⁷⁸⁹','-0123456789')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fonts',type=Path,required=True)
    p.add_argument('--output',type=Path,default=ROOT/'docs/MANUSCRIPT_SUPPLEMENT.pdf')
    args=p.parse_args()
    for name,file in [('TimesStudy','times.ttf'),('TimesStudy-Bold','timesbd.ttf'),('TimesStudy-Italic','timesi.ttf'),('TimesStudy-BoldItalic','timesbi.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(args.fonts/file)))
    pdfmetrics.registerFontFamily('TimesStudy',normal='TimesStudy',bold='TimesStudy-Bold',italic='TimesStudy-Italic',boldItalic='TimesStudy-BoldItalic')
    styles={
      'body':ParagraphStyle('body',fontName='TimesStudy',fontSize=10.5,leading=13.2,spaceAfter=7,alignment=TA_LEFT),
      'title':ParagraphStyle('title',fontName='TimesStudy-Bold',fontSize=15,leading=18,spaceAfter=12),
      'h1':ParagraphStyle('h1',fontName='TimesStudy-Bold',fontSize=12.5,leading=15,spaceBefore=13,spaceAfter=7,keepWithNext=True),
      'h2':ParagraphStyle('h2',fontName='TimesStudy-Bold',fontSize=11,leading=13,spaceBefore=9,spaceAfter=6,keepWithNext=True),
      'table':ParagraphStyle('table',fontName='TimesStudy',fontSize=9,leading=11.2),
      'caption':ParagraphStyle('caption',fontName='TimesStudy',fontSize=9.5,leading=12,spaceAfter=10)
    }
    source=ROOT/'docs/MANUSCRIPT_SUPPLEMENT.md';md=source.read_text(encoding='utf-8')
    def inline(s):
        # Convert relative artifact links to absolute links for standalone reading.
        protected=[]
        def link(m):
            label,target=m[1],m[2]
            if not target.startswith(('http:','https:')):
                target=GITHUB+(source.parent/target).resolve().relative_to(ROOT.resolve()).as_posix()
            protected.append('<link href="'+escape(target,quote=True)+'" color="#243E60">'+escape(label)+'</link>')
            return '\x00'+str(len(protected)-1)+'\x00'
        s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,s)
        s=escape(s)
        s=re.sub(r'`([^`]+)`',r'<font name="Courier" size="8">\1</font>',s)
        s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
        s=re.sub(r'[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+',lambda m:'<super>'+m[0].translate(SUPER)+'</super>',s)
        for i,value in enumerate(protected):s=s.replace('\x00'+str(i)+'\x00',value)
        return s
    story=[Paragraph('Research Supplement S1–S8',styles['title']),
      Paragraph('Prepared 12 November 2026. Companion to the manuscript; the article records the pinned repository version. Author-owned data and documentation: CC BY 4.0, with component exclusions in LICENSE.md.',styles['body'])]
    lines=md.splitlines();i=0;tables=0;images=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('# '):
            story.append(Paragraph(inline(line[2:]),styles['h1']));i+=1;continue
        if line.startswith('## '):
            story.append(Paragraph(inline(line[3:]),styles['h1']));i+=1;continue
        if line.startswith('### '):
            story.append(Paragraph(inline(line[4:]),styles['h2']));i+=1;continue
        if re.match(r'^\d+\. ',line):
            entries=[]
            while i<len(lines) and re.match(r'^\d+\. ',lines[i].strip()):
                entries.append(ListItem(Paragraph(inline(re.sub(r'^\d+\. ','',lines[i].strip())),styles['body'])))
                i+=1
            story.append(ListFlowable(entries,bulletType='1',start='1',leftIndent=16,bulletFontName='TimesStudy',bulletFontSize=10.5))
            continue
        if line.startswith('| '):
            raw=[]
            while i<len(lines) and lines[i].strip().startswith('| '):
                cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
                if cells[0]!='---':raw.append(cells)
                i+=1
            n=len(raw[0]);widths={8:[18,34,58,23,23,36,105,92],7:[44,40,65,48,105,90,90],5:[35,80,85,90,200]}.get(n,[490/n]*n)
            data=[[Paragraph(('<b>'+inline(c)+'</b>') if ri==0 else inline(c),styles['table']) for c in row] for ri,row in enumerate(raw)]
            tab=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
            tab.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEABOVE',(0,0),(-1,0),.65,colors.black),('LINEBELOW',(0,0),(-1,0),.45,colors.black),('LINEBELOW',(0,-1),(-1,-1),.65,colors.black),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3)]))
            story.extend([Spacer(1,5),tab,Spacer(1,10)]);tables+=1;continue
        pic=re.fullmatch(r'!\[([^\]]+)\]\(([^)]+)\)',line)
        if pic:
            path=(source.parent/pic[2]).resolve();img=Image(str(path));scale=min(490/img.imageWidth,320/img.imageHeight)
            img.drawWidth=img.imageWidth*scale;img.drawHeight=img.imageHeight*scale
            story.append(KeepTogether([img,Paragraph(inline(pic[1]),styles['caption'])]));images+=1;i+=1;continue
        paragraph=[line];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(?:#|\| |!\[)',lines[i].strip()):
            paragraph.append(lines[i].strip());i+=1
        story.append(Paragraph(inline(' '.join(paragraph)),styles['body']))
    def page(canvas,doc):
        canvas.setFont('TimesStudy',9)
        canvas.drawString(42,816,'Setiawan et al. — Supplement S1–S8')
        canvas.drawRightString(553,816,str(doc.page))
        canvas.setFont('TimesStudy',8)
        canvas.drawString(42,27,'crypto-diffusion | research artifacts | 12 November 2026')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    SimpleDocTemplate(str(args.output),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=42,bottomMargin=42,invariant=1,
      title='Research Supplement: Calibrated Strict Avalanche Criterion Comparisons',author='Hermawan Setiawan; Raden Budiarto Hadiprakoso; Sri Rosdiana').build(story,onFirstPage=page,onLaterPages=page)
    print('PDF written:',args.output,'tables:',tables,'figures:',images,'source SHA256:',hashlib.sha256(source.read_bytes()).hexdigest())

if __name__=='__main__':main()
