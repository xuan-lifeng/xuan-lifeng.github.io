"""Recompute diagnostics and figures from the preserved neural numerical exports.

Run from any directory: python analysis/neural/rebuild_figures.py
Requires numpy, pandas, scipy, matplotlib and Pillow.
This script evaluates exported predictions; it does not train or infer a new model.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'assets';DATA=OUT/'data'
INK='#172b42';MUTED='#61768b';BLUE='#2877b5';TEAL='#168a83';GRID='#e8edf3';ORANGE='#c16f3a'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':INK,'axes.labelcolor':MUTED,'axes.edgecolor':'#cad5df','xtick.color':MUTED,'ytick.color':MUTED,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','savefig.facecolor':'white','axes.titlesize':12,'axes.titleweight':'medium'})
trace=pd.read_csv(DATA/'neural-response-trace.csv');scores=pd.read_csv(DATA/'neural-unit-scores.csv')
t=trace.time_s.to_numpy();obs=trace.real_mean.to_numpy();pred=trace.predicted.to_numpy();v=scores.dynamic_corr_cv_mean.to_numpy();res=obs-pred
assert len(t)==459 and len(v)==46 and np.all(np.isfinite(np.r_[t,obs,pred,v]))
assert np.allclose(np.diff(t),.05) and trace.neuron_id.nunique()==1
r=float(pearsonr(obs,pred).statistic);mse=float(np.mean(res**2));rmse=float(np.sqrt(mse));mae=float(np.mean(np.abs(res)));q1,med,q3=np.quantile(v,[.25,.5,.75])
metrics={'trace':{'n_bins':len(t),'unit_id':int(trace.neuron_id.iloc[0]),'bin_seconds':.05,'start_seconds':float(t.min()),'end_seconds':float(t.max()),'pearson_r':r,'mse':mse,'rmse':rmse,'mae':mae,'evaluation':'Recomputed on the displayed exported segment; its training/test split is unspecified.'},'population':{'n_units':len(v),'median':float(med),'q1':float(q1),'q3':float(q3),'min':float(v.min()),'max':float(v.max()),'column':'dynamic_corr_cv_mean'},'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in DATA.glob('neural-*.csv')}}
(DATA/'neural-recomputed-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
def clean(ax):
 ax.set_axisbelow(True);ax.grid(axis='y',color=GRID,lw=.8);ax.tick_params(length=0,pad=7)
 for side in ['top','right']:ax.spines[side].set_visible(False)
 ax.spines['left'].set_visible(False)
def save(fig,name):
 fig.savefig(OUT/(name+'.svg'));fig.savefig(OUT/(name+'.png'),dpi=140);plt.close(fig)
def response(mobile=False):
 fig=plt.figure(figsize=(6.3,10.2) if mobile else (12,7.4))
 gs=fig.add_gridspec(3,1,height_ratios=[1.25,.8,1.15]) if mobile else fig.add_gridspec(2,2,height_ratios=[1.5,1],width_ratios=[1.9,1])
 ax=fig.add_subplot(gs[0] if mobile else gs[0,:]);err=fig.add_subplot(gs[1] if mobile else gs[1,0]);cal=fig.add_subplot(gs[2] if mobile else gs[1,1])
 for a in [ax,err,cal]:clean(a)
 ax.plot(t,obs,color=INK,lw=1.2,label='Observed trial mean',alpha=.8);ax.plot(t,pred,color=BLUE,lw=1.15,label='Exported model prediction',alpha=.85)
 ax.set_xlim(97,120);ax.set_ylim(-.08,2.4);ax.set_ylabel('Response (export scale)');ax.set_xticks([97,100,105,110,115,120]);ax.set_title('A   Response over time',loc='left',pad=14);ax.legend(frameon=False,ncol=1 if mobile else 2,loc='upper right',fontsize=9);ax.set_xlabel('Time (s)')
 err.fill_between(t,res,0,color=TEAL,alpha=.16);err.plot(t,res,color=TEAL,lw=.9);err.axhline(0,color=MUTED,lw=.7);err.set_xlim(97,120);err.set_ylim(-.3,.3);err.set_xlabel('Time (s)');err.set_ylabel('Observed − predicted');err.set_title('B   Prediction residual',loc='left',pad=12)
 cal.scatter(obs,pred,s=14,alpha=.45,c=BLUE,edgecolors='none');cal.plot([-.05,2.2],[-.05,2.2],ls=(0,(4,4)),lw=1,color=MUTED);cal.set_xlim(-.08,2.25);cal.set_ylim(-.08,2.25);cal.set_xlabel('Observed response');cal.set_ylabel('Predicted response');cal.set_title('C   Observed vs predicted',loc='left',pad=12)
 fig.text(.08,.975,'Neural response diagnostics',fontsize=18 if mobile else 21,weight='medium',va='top')
 fig.text(.08,.97-.50/fig.get_figheight(),f'Cluster 4 · 459 bins · 50 ms sampling',fontsize=10,color=MUTED)
 fig.text(.08,.97-.80/fig.get_figheight(),f'Segment r = {r:.3f}     RMSE = {rmse:.3f}     MAE = {mae:.3f}',fontsize=10,color=BLUE)
 fig.subplots_adjust(left=.12 if mobile else .08,right=.97,top=.97-1.35/fig.get_figheight(),bottom=.07 if mobile else .1,hspace=.75 if mobile else .65,wspace=.35)
 save(fig,'neural-prediction-recomputed'+('-mobile' if mobile else ''))
def population(mobile=False):
 fig,axs=plt.subplots(2,1,figsize=(6.3,7.7)) if mobile else plt.subplots(1,2,figsize=(12,5.4),gridspec_kw={'width_ratios':[1,1.15]})
 a,b=axs
 for ax in axs:clean(ax)
 # Deterministic dot stacking makes every exported observation visible.
 order=np.argsort(v);yy=np.zeros(len(v));placed=[]
 for idx in order:
  for k in [0,1,-1,2,-2,3,-3,4,-4,5,-5,6,-6]:
   y=k*.105
   if all(abs(v[idx]-xx)>.021 or abs(y-y0)>.09 for xx,y0 in placed):break
  yy[idx]=y;placed.append((v[idx],y))
 a.axvspan(q1,q3,color=BLUE,alpha=.09);a.scatter(v,yy,s=43,c=BLUE,alpha=.85,edgecolors='white',linewidths=.7,zorder=3);a.axvline(med,color=TEAL,lw=1.4,ls=(0,(4,3)));a.set_xlim(0,.85);a.set_ylim(-.6,.65);a.set_yticks([]);a.grid(False);a.set_xlabel('Mean cross-validation correlation');a.set_title('A   All 46 unit scores',loc='left',pad=16)
 a.text(.02,.94,f'Median {med:.3f}',transform=a.transAxes,color=TEAL,fontsize=11,va='top');a.text(.02,.02,f'Middle 50%: {q1:.3f}–{q3:.3f}',transform=a.transAxes,color=MUTED,fontsize=9)
 sv=np.sort(v);rank=np.arange(1,47);b.vlines(rank,0,sv,color=BLUE,alpha=.22,lw=1.5);b.scatter(rank,sv,s=23,c=BLUE,edgecolors='white',lw=.4,zorder=3);b.axhline(med,color=TEAL,lw=1,ls=(0,(4,3)));b.set_xlim(0,47);b.set_ylim(0,.85);b.set_xticks([1,10,20,30,40,46]);b.set_xlabel('Unit rank (lowest to highest score)');b.set_ylabel('Mean cross-validation correlation');b.set_title('B   Scores ranked across units',loc='left',pad=16)
 fig.text(.08,.98,'Prediction across the population',fontsize=18 if mobile else 21,weight='medium',va='top');fig.text(.08,.97-.50/fig.get_figheight(),f'46 units · median {med:.3f} · range {v.min():.3f}–{v.max():.3f}',fontsize=10,color=MUTED)
 fig.subplots_adjust(left=.13 if mobile else .08,right=.97,top=.97-1.15/fig.get_figheight(),bottom=.085 if mobile else .16,hspace=.6,wspace=.35)
 save(fig,'neural-population-recomputed'+('-mobile' if mobile else ''))
def hero(mobile=False):
 fig=plt.figure(figsize=(6.3,7.6) if mobile else (12,5.4),facecolor='#f5f8fb')
 gs=fig.add_gridspec(2,1,height_ratios=[1,1]) if mobile else fig.add_gridspec(1,2,width_ratios=[.9,1.5])
 left=fig.add_subplot(gs[0]);right=fig.add_subplot(gs[1]);left.axis('off')
 # This is the existing cluster-4 STA panel, not an invented receptive field.
 left.imshow(Image.open(OUT/'cluster4-sta-receptive-field.png'));left.set_title('Stimulus sensitivity',loc='left',fontsize=12,pad=5)
 sel=(t>=99)&(t<=107);right.set_facecolor('#f5f8fb');clean(right);right.plot(t[sel],obs[sel],color=INK,lw=1.5,label='Observed');right.plot(t[sel],pred[sel],color=BLUE,lw=1.4,label='Predicted');right.set_xlim(99,107);right.set_ylim(-.08,2.25);right.set_xlabel('Time (s)');right.set_ylabel('Response');right.legend(frameon=False,loc='upper left',fontsize=9,ncol=2);right.set_title('Response prediction',loc='left',pad=18,fontsize=12)
 fig.text(.065,.97,'Mapping sound to neural responses',fontsize=17 if mobile else 24,weight='medium',va='top');fig.text(.065,.97-.50/fig.get_figheight(),'Mouse auditory cortex · receptive fields and model predictions',fontsize=9 if mobile else 11,color=MUTED)
 fig.subplots_adjust(left=.07,right=.96,top=.97-1.15/fig.get_figheight(),bottom=.1,wspace=.28,hspace=.55)
 save(fig,'neural-study-opening'+('-mobile' if mobile else ''))
for mobile in [False,True]:response(mobile);population(mobile);hero(mobile)
print(json.dumps(metrics,indent=2))
# Replot every STC eigenvalue directly from the preserved MATLAB export.
from scipy.io import loadmat
mat=loadmat(OUT/'cluster4-stc-eigenvalues.mat',simplify_cells=True)
ev=np.asarray(mat['evals_real'],dtype=float).ravel();thr=float(mat['thr']);ev=ev[np.argsort(-np.abs(ev),kind='stable')];ranks=np.arange(1,len(ev)+1);selected=np.abs(ev)>thr
assert len(ev)==845 and int(selected.sum())==2
for mobile in [False,True]:
 fig,axs=plt.subplots(2,1,figsize=(6.3,8.8)) if mobile else plt.subplots(1,2,figsize=(12,5.7),gridspec_kw={'width_ratios':[1.2,1]})
 a,b=axs
 for ax in axs:
  clean(ax);ax.axhline(0,color='#a8b8c5',lw=.8);ax.axhline(thr,color=TEAL,lw=1,ls=(0,(4,4)));ax.axhline(-thr,color=TEAL,lw=1,ls=(0,(4,4)));ax.set_ylim(-285,535);ax.set_ylabel('Signed eigenvalue')
 a.scatter(ranks[~selected],ev[~selected],s=10,color=MUTED,alpha=.6,edgecolors='none',label='Other components');a.scatter(ranks[selected],ev[selected],s=58,color=BLUE,edgecolors='white',lw=.8,zorder=4,label='Above threshold')
 for x,y in zip(ranks[selected],ev[selected]):a.annotate(f'{x}: {y:.1f}',(x,y),xytext=(9,9),textcoords='offset points',fontsize=9,color=BLUE)
 a.set_xscale('log');a.set_xlim(.8,1100);a.set_xticks([1,10,100,845],['1','10','100','845']);a.set_xlabel('Rank by absolute eigenvalue (log scale)');a.set_title('A   All 845 components',loc='left',pad=16);a.legend(frameon=False,loc='upper right',fontsize=8)
 colors=np.where(selected[:20],BLUE,'#9fadb9');b.vlines(ranks[:20],0,ev[:20],colors=colors,lw=2);b.scatter(ranks[:20],ev[:20],c=colors,s=29,zorder=3,edgecolors='white',lw=.5)
 for x,y in zip(ranks[:2],ev[:2]):b.annotate(f'{y:.1f}',(x,y),xytext=(5,8),textcoords='offset points',fontsize=9,color=BLUE)
 b.set_xlim(.2,21);b.set_xticks([1,5,10,15,20]);b.set_xlabel('Rank by absolute eigenvalue');b.set_title('B   Leading 20 components',loc='left',pad=16)
 fig.text(.09,.97,'STC eigenvalue spectrum',fontsize=18 if mobile else 21,va='top',weight='medium');fig.text(.09,.97-.5/fig.get_figheight(),f'Cluster 4 · dashed lines mark the exported threshold ±{thr:.3f}',fontsize=9 if mobile else 10,color=MUTED)
 fig.subplots_adjust(left=.15 if mobile else .09,right=.96,top=.97-1.15/fig.get_figheight(),bottom=.08 if mobile else .15,hspace=.55,wspace=.35)
 save(fig,'neural-stc-recomputed'+('-mobile' if mobile else ''))
