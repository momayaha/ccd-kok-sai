"""Reproduce descriptive ground and exploratory satellite-to-arsenic analysis.
Run from the repository root: python 03_code/ground_arsenic_analysis.py
Optional: --root path --out path. No external network calls.
"""
import argparse, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, LogLocator, NullFormatter
from matplotlib import font_manager
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

def main(root, out):
    r=out/'04_results'; f=out/'05_figures'; r.mkdir(parents=True,exist_ok=True); f.mkdir(parents=True,exist_ok=True)
    def locate(name, folder):
        for p in [root/folder/name,root/name,root/'CCD_D4_figures'/name]:
            if p.exists(): return p
        raise FileNotFoundError(name)
    m=pd.read_csv(locate('CCD_master_dataset_v0.1.csv','02_input_and_raw_data'))
    a=pd.read_csv(locate('arsenic_water_mgL_r01-r22.csv','01_source_data'),dtype=str).melt('station',var_name='rnd',value_name='a')
    t=pd.read_csv(locate('turbidity_NTU_r01-r22.csv','01_source_data')).melt('station',var_name='rnd',value_name='t')
    for x in [a,t]: x['round']=x.rnd.str[1:].astype(int)
    j=m.merge(a[['station','round','a']],on=['station','round'],validate='one_to_one').merge(t[['station','round','t']],on=['station','round'],validate='one_to_one')
    assert len(j)==len(m) and j.As_mgL_raw.eq(j.a).all() and (j.turbidity_NTU_raw.eq(j.t)|(j.t.isna()&j.turbidity_NTU_raw.isna())).all()
    m[['observation_id','station','river','round','As_mgL_raw','As_censored','As_above_0_010','turbidity_NTU_raw']].to_csv(r/'ground_all_300.csv',index=False)
    q=m.dropna(subset=['turbidity_NTU_raw']).copy(); assert q.turbidity_NTU_raw.gt(0).all()
    q['As_plot_mgL']=q.As_mgL_numeric.where(q.As_censored.eq(0),q.As_reporting_limit_mgL)
    q.to_csv(r/'ground_paired_296.csv',index=False)
    groups={'Both':q,'Kok':q[q.river.eq('Kok')],'Sai':q[q.river.eq('Sai')]}
    summary=[]; metrics=[]; strata=[]; preds=[]; curves=[]
    for name,g in groups.items():
        y=g.As_above_0_010.to_numpy(); x=g.turbidity_NTU_raw.to_numpy()
        for k,h in g.groupby('As_above_0_010'):
            v=h.turbidity_NTU_raw
            summary.append([name,k,len(h),int(h.As_censored.sum()),v.min(),v.quantile(.25),v.median(),v.quantile(.75),v.max()])
        metrics.append([name,'raw_turbidity',len(g),np.nan,np.nan,roc_auc_score(y,x)])
        if name!='Sai':
            fp,tp,th=roc_curve(y,x,drop_intermediate=False)
            curves.extend([[name,'raw_turbidity',i,j,k] for i,j,k in zip(fp,tp,th)])
        for key in ['station','round']:
            s=[]
            for k,h in g.groupby(key):
                n1=int(h.As_above_0_010.sum()); n0=len(h)-n1; w=n0*n1
                auc=roc_auc_score(h.As_above_0_010,h.turbidity_NTU_raw) if w else np.nan
                strata.append([name,key,k,n0,n1,w,auc])
                if w: s.append((w,auc))
            if s: metrics.append([name,'within_'+key,len(g),len(s),sum(i[0] for i in s),np.average([i[1] for i in s],weights=[i[0] for i in s])])
            if name=='Sai':continue # one negative; no defensible grouped fitting
            z=np.empty(len(g)); X=np.log10(x.reshape(-1,1))
            for tr,te in LeaveOneGroupOut().split(X,y,g[key]):
                z[te]=make_pipeline(StandardScaler(),LogisticRegression(C=1e6,max_iter=1000)).fit(X[tr],y[tr]).predict_proba(X[te])[:,1]
            metrics.append([name,'LO'+key+'O_logistic',len(g),g[key].nunique(),np.nan,roc_auc_score(y,z)])
            preds.extend([[name,key,i,v] for i,v in zip(g.observation_id,z)])
            fp,tp,th=roc_curve(y,z,drop_intermediate=False)
            curves.extend([[name,'LO'+key+'O_logistic',i,j,k] for i,j,k in zip(fp,tp,th)])
    pd.DataFrame(summary,columns=['river','above_threshold','n','n_censored','min_NTU','q25_NTU','median_NTU','q75_NTU','max_NTU']).to_csv(r/'ground_summary.csv',index=False)
    pd.DataFrame(metrics,columns=['river','method','n','n_groups','comparable_pairs','AUC']).to_csv(r/'ground_auc.csv',index=False)
    pd.DataFrame(strata,columns=['river','grouping','group','n_at_or_below','n_above','comparable_pairs','AUC']).to_csv(r/'ground_stratified_auc.csv',index=False)
    pd.DataFrame(preds,columns=['river','held_out_group_type','observation_id','predicted_probability']).to_csv(r/'ground_grouped_predictions.csv',index=False)
    pd.DataFrame(curves,columns=['river','method','FPR','TPR','threshold']).to_csv(r/'ground_ROC_coordinates.csv',index=False)
    d=pd.read_csv(locate('D4_50m_SigmaPlot.csv','04_results'))
    try: p=pd.read_csv(locate('D4_50m_predictions.csv','04_results'))
    except FileNotFoundError:
        with zipfile.ZipFile(root/'CCD_D4_figures_and_data.zip') as z: p=pd.read_csv(z.open('D4_50m_predictions.csv'))
    d=d.merge(p,on=['observation_id','station','radius_m','turbidity_NTU_raw'],validate='one_to_one')
    d.to_csv(r/'D4_arsenic_proxy_predictions.csv',index=False)
    models={'turbidity_NTU_raw':'Measured turbidity','single_band_NTU':'Single band','single_colour_NTU':'Single colour index','two_colours_NTU':'CCD','all_four_bands_NTU':'Four bands'}
    vals=[]; y=d.As_above_0_010; cr=[]
    for col,label in models.items():
        v=roc_auc_score(y,d[col]); vals.append([col,label,len(d),int(y.sum()),v]); fp,tp,th=roc_curve(y,d[col],drop_intermediate=False); cr.extend([[col,i,j,k] for i,j,k in zip(fp,tp,th)])
    pd.DataFrame(vals,columns=['score','model','n','n_above','AUC']).to_csv(r/'D4_arsenic_proxy_auc.csv',index=False)
    pd.DataFrame(cr,columns=['score','FPR','TPR','threshold']).to_csv(r/'D4_arsenic_proxy_ROC_coordinates.csv',index=False)
    available={x.name for x in font_manager.fontManager.ttflist}; font=next((x for x in ['Palatino Linotype','TeX Gyre Pagella','DejaVu Serif'] if x in available),'serif')
    plt.rcParams.update({'font.family':font,'font.size':11,'pdf.fonttype':42})
    def style(ax,logx=False,logy=False):
        ax.tick_params(which='both',direction='in',top=True,right=True)
        for axis,log in [(ax.xaxis,logx),(ax.yaxis,logy)]:
            axis.set_minor_locator(LogLocator(base=10,subs=np.arange(2,10)) if log else AutoMinorLocator(2))
            if log:axis.set_minor_formatter(NullFormatter())
    def save(fig,name):
        fig.tight_layout(); fig.savefig(f/(name+'.pdf'));plt.close(fig)
    for n,g in [('Kok',groups['Kok']),('Sai',groups['Sai'])]:
        fig,ax=plt.subplots(figsize=(6,4.5)); det=g[g.As_censored.eq(0)]; cen=g[g.As_censored.eq(1)]
        ax.scatter(det.turbidity_NTU_raw,det.As_plot_mgL,s=25,alpha=.65,label=f'Detected (n={len(det)})')
        ax.scatter(cen.turbidity_NTU_raw,cen.As_plot_mgL,marker='v',s=25,alpha=.7,label=f'Below reporting limit (n={len(cen)})')
        ax.axhline(.01,ls='--',lw=1,label='0.010 mg/L threshold')
        ax.set(xscale='log',yscale='log',xlabel='Turbidity (NTU)',ylabel='Total arsenic (mg/L)',xlim=(25,6000),ylim=(.008,1.2*q.As_plot_mgL.max()))
        style(ax,True,True);ax.legend(frameon=False,fontsize=9);save(fig,'06_'+n+'_arsenic_vs_turbidity')
    fig,ax=plt.subplots(figsize=(5.2,4.8))
    for n in ['Both','Kok']:
        g=groups[n]; x,y=g.turbidity_NTU_raw,g.As_above_0_010; fp,tp,_=roc_curve(y,x); ax.plot(fp,tp,label=f'{n} (AUC = {roc_auc_score(y,x):.3f})')
    ax.plot([0,1],[0,1],ls='--',lw=1);ax.set(xlim=(0,1),ylim=(0,1),xlabel='False positive rate',ylabel='True positive rate');ax.set_aspect('equal');style(ax);ax.legend(frameon=False,loc='lower right');save(fig,'07_ground_turbidity_ROC')
    fig,ax=plt.subplots(figsize=(5.8,5))
    for col,label,_,_,v in vals:
        fp,tp,_=roc_curve(d.As_above_0_010,d[col]);ax.plot(fp,tp,label=f'{label} ({v:.3f})')
    ax.plot([0,1],[0,1],ls='--',lw=1);ax.set(xlim=(0,1),ylim=(0,1),xlabel='False positive rate',ylabel='True positive rate');ax.set_aspect('equal');style(ax);ax.legend(frameon=False,fontsize=8,loc='lower right');save(fig,'08_D4_arsenic_proxy_ROC')
    print('Verified all 300 values against original tables. Font:',font);print(pd.DataFrame(vals).to_string(index=False,header=False))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path.cwd());ap.add_argument('--out',type=Path);args=ap.parse_args();main(args.root,args.out or args.root)
