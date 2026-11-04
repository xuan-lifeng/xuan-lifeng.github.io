"""Rebuild NIRF portfolio diagrams and charts from the v04 report values.
Run: python analysis/nirf/build_portfolio_figures.py
The figures visualise reported methods and aggregate results, not new experiments.
"""
from pathlib import Path
import json,html,textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'assets';D=json.loads((OUT/'data/nirf-v04-benchmark.json').read_text())
INK='#172b42';BLUE='#2877b5';TEAL='#087f78';MUTED='#61768b';LINE='#d7e1eb';PALE='#f3f7fa'
def svg_start(w,h,title,subtitle):
 return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}"><style>text{{font-family:Arial,Helvetica,sans-serif;fill:{INK}}}.sub{{fill:{MUTED}}}</style><rect width="100%" height="100%" fill="white"/><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="{BLUE}"/></marker></defs>',f'<text x="30" y="38" font-size="25" font-weight="600">{html.escape(title)}</text>',f'<text class="sub" x="30" y="68" font-size="14">{html.escape(subtitle)}</text>']
def label(out,x,y,lines,size=16,color=INK):
 for i,line in enumerate(lines):out.append(f'<text x="{x}" y="{y+i*(size+7)}" text-anchor="middle" font-size="{size}" style="fill:{color}">{html.escape(line)}</text>')
def box(out,x,y,w,h,lines,accent=False):
 out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{TEAL if accent else PALE}" stroke="{TEAL if accent else LINE}"/>');label(out,x+w/2,y+h/2-(len(lines)-1)*11+5,lines,16,'white' if accent else INK)
def arrow(out,x1,y1,x2,y2):
 dx=x2-x1;dy=y2-y1;length=(dx*dx+dy*dy)**.5;ux=dx/length;uy=dy/length;bx=x2-10*ux;by=y2-10*uy
 out.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{BLUE}" stroke-width="2"/><polygon points="{x2},{y2} {bx-5*uy},{by+5*ux} {bx+5*uy},{by-5*ux}" fill="{BLUE}"/>')
def save(out,name):
 content=''.join(out)+'</svg>';content=content.replace('<text ','<text font-family="Arial,Helvetica,sans-serif" ');(OUT/name).write_text(content)
stages=[['Stereo NIRF','image pair'],['Hysteresis','segmentation'],['EDT centreline','extraction'],['Constrained','correspondence'],['Calibrated','triangulation']]
for mobile in [False,True]:
 if mobile:
  o=svg_start(460,770,'From images to vessel geometry','Classical reconstruction workflow')
  for i,lines in enumerate(stages):
   y=100+i*120;box(o,70,y,320,88,lines,accent=i==3)
   if i<4:arrow(o,230,y+90,230,y+117)
  label(o,230,725,['Diagnostics identified correspondence','as the main depth-error bottleneck.'],14)
 else:
  o=svg_start(1200,300,'From images to vessel geometry','Classical reconstruction workflow / fixed camera calibration')
  for i,lines in enumerate(stages):
   x=30+i*237;box(o,x,110,190,105,lines,accent=i==3)
   if i<4:arrow(o,x+192,162,x+232,162)
  label(o,600,264,['Ground-truth substitutions isolated correspondence as the main depth-error bottleneck.'],16)
 save(o,'nirf-development-pipeline'+('-mobile' if mobile else '')+'.svg')
for mobile in [False,True]:
 if mobile:
  o=svg_start(620,1120,'Learned appearance, fixed geometry','Learned H uses a CNN appearance cost')
  lines=[['Paired 49 × 49 NIRF patches'],['Shared Siamese CNN','64-dimensional, unit-normalised embeddings'],['Compare embeddings','Absolute difference and elementwise product'],['Match probability → appearance cost'],['Unary cost','Epipolar row penalty + weighted CNN cost'],['Monotone sequence matching'],['Accepted matches → calibrated 3D']]
  for i,ls in enumerate(lines):
   y=110+i*120;box(o,55,y,510,90,ls,accent=i in [1,3])
   if i<6:arrow(o,310,y+92,310,y+117)
  box(o,40,975,540,105,['Fixed constraints: disparity bounds, row tolerance,','ordering, smoothness, skipping and endpoints'])
 else:
  o=svg_start(1200,600,'Learned appearance, fixed geometry','Learned H replaces the appearance score inside a shared constrained matcher')
  boxes=[(30,125,190,110,['Paired 49 × 49','NIRF patches'],False),(270,125,240,110,['Shared Siamese CNN','64-dimensional embeddings'],True),(560,125,240,110,['Embedding comparison','|eL − eR| and eL × eR'],False),(850,125,300,110,['Match probability','p(i,j)'],True)]
  for x,y,w,h,ls,a in boxes:box(o,x,y,w,h,ls,a)
  for a,b in zip(boxes[:-1],boxes[1:]):arrow(o,a[0]+a[2]+2,180,b[0]-5,180)
  lower=[(30,335,245,105,['Relative CNN','appearance cost'],True),(325,335,245,105,['Unary cost','Row penalty + CNN cost'],False),(620,335,245,105,['Monotone sequence','dynamic programme'],False),(915,335,245,105,['Accepted matches','Calibrated triangulation'],False)]
  for x,y,w,h,ls,a in lower:box(o,x,y,w,h,ls,a)
  for a,b in zip(lower[:-1],lower[1:]):arrow(o,a[0]+a[2]+2,387,b[0]-5,387)
  o.append(f'<path d="M1000 237 V280 H152 V330" fill="none" stroke="{BLUE}" stroke-width="2" /><polygon points="152,330 147,320 157,320" fill="{BLUE}"/>')
  box(o,110,495,980,70,['Fixed: disparity bounds, epipolar tolerance, ordering, smoothness, skipping and endpoints'])
 save(o,'nirf-learned-matching-v04'+('-mobile' if mobile else '')+'.svg')
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans','Arial','Helvetica','sans-serif'],'svg.fonttype':'none','font.size':11,'text.color':INK,'axes.labelcolor':MUTED,'xtick.color':MUTED,'ytick.color':MUTED,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.edgecolor':LINE,'savefig.facecolor':'white'})
methods=D['methods'];colors=['#98a7b5','#76add2',BLUE,TEAL]
for mobile in [False,True]:
 fig,axs=plt.subplots(2,1,figsize=(6.3,8.5)) if mobile else plt.subplots(1,2,figsize=(12,5.5))
 for ax in axs:ax.set_axisbelow(True);ax.grid(axis='x',color='#e8eef4');ax.tick_params(length=0)
 y=list(range(4));names=[m['name'] for m in methods]
 for ax,key,title,xlabel in [(axs[0],'mean_depth_rmse_mm','A   Mean depth error · lower is better','Depth RMSE (mm)'),(axs[1],'two_tier_passes','B   Successful reconstructions · higher is better','Samples out of 250')]:
  vals=[m[key] for m in methods];ax.barh(y,vals,color=colors,height=.55);ax.set_yticks(y,names);ax.invert_yaxis();ax.set_title(title,loc='left',pad=18,fontsize=12);ax.set_xlabel(xlabel,labelpad=11)
  ax.set_xlim(0,.95 if key=='mean_depth_rmse_mm' else 285)
  for j,v in enumerate(vals):ax.text(v+(.015 if key=='mean_depth_rmse_mm' else 5),j,f'{v:.3f}' if key=='mean_depth_rmse_mm' else f'{v}/250',va='center',fontsize=11,color=INK)
 fig.text(.08,.97,'Frozen test comparison',fontsize=20,va='top',weight='medium');fig.text(.08,.97-.52/fig.get_figheight(),'250 test samples · depth statistics use 248 finite reconstructions',fontsize=10,color=MUTED)
 fig.subplots_adjust(left=.2 if mobile else .12,right=.97,top=.97-1.2/fig.get_figheight(),bottom=.09 if mobile else .18,wspace=.46,hspace=.65)
 fig.savefig(OUT/('nirf-v04-four-methods'+('-mobile' if mobile else '')+'.svg'));fig.savefig(ROOT/('nirf-v04-four-methods'+('-mobile' if mobile else '')+'-check.png'),dpi=140);plt.close(fig)
print('Built method diagrams and benchmark plots from v04.')
