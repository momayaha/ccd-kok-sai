"""Exploratory aperture sensitivity; no validated same-day satellite inference.
Run: python CCD_sensitivity_analysis.py /path/to/CCD_repository_snapshot --output .
Uses archived candidate ranking (independent of outcome). No new extraction.
"""
from pathlib import Path
import argparse
from itertools import combinations
import numpy as np
import pandas as pd

B=['B2','B3','B4','B8']
I=['B_minus_G','B_minus_R','B_minus_NIR','G_minus_R','G_minus_NIR','R_minus_NIR']
F={'training_mean':[()], 'single_band':[(b,) for b in B], 'single_colour':[(i,) for i in I], 'two_colours':list(combinations(I,2)), 'all_four_bands':[tuple(B)]}

def fit_predict(x,y,tr,te):
    if x.shape[1]==0: return np.repeat(y[tr].mean(),len(te))
    # Centered least-squares (equivalent to OLS with intercept).
    m=x[tr].mean(axis=0); ym=y[tr].mean()
    co=np.linalg.lstsq(x[tr]-m,y[tr]-ym,rcond=None)[0]
    return ym+(x[te]-m)@co

def run(g,group):
    y=np.log10(g.turbidity_NTU_raw.to_numpy(float)); grp=g[group].to_numpy(); idx=np.arange(len(g))
    arrays={c:g[list(c)].to_numpy(float) for cs in F.values() for c in cs}
    def cv(ind,c):
        p=np.full(len(g),np.nan)
        for a in np.unique(grp[ind]):
            tr=ind[grp[ind]!=a]; te=ind[grp[ind]==a]; p[te]=fit_predict(arrays[c],y,tr,te)
        return p[ind]
    for fam, candidates in F.items():
        p=np.full(len(g),np.nan); choices=np.empty(len(g),object)
        for a in np.unique(grp):
            tr=idx[grp!=a]; te=idx[grp==a]
            errs=[np.mean((y[tr]-cv(tr,c))**2) for c in candidates] if len(candidates)>1 else [0]
            # Algebraically equivalent coordinates can tie to numerical precision;
            # use original candidate order for ties within 1e-12 MSE.
            best=next(c for c,e in zip(candidates,errs) if e<=min(errs)+1e-12)
            p[te]=fit_predict(arrays[best],y,tr,te); choices[te]='+'.join(best) or 'mean'
        yield fam,p,choices,y

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('repository',type=Path); ap.add_argument('--output',type=Path,default=Path('.')); args=ap.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    d=pd.read_csv(args.repository/'04_results/CCD_aperture_best_per_radius.csv')
    d=d[d.turbidity_NTU_raw.gt(0)].dropna(subset=B+I).copy()
    summaries=[]; predictions=[]; cover=[]
    for gap in [0,2,3,4]:
        e=d[d.max_possible_date_gap_days.le(gap)]
        p=e.pivot(index='observation_id',columns='radius_m',values='image_id').reindex(columns=[20,30,50]).dropna()
        ids=p.index[p.nunique(axis=1).eq(1)]
        for r in [20,30,50]:
            g=e[e.radius_m.eq(r)]
            cover.append(dict(max_gap_days=gap,radius_m=r,n=len(g),stations=g.station.nunique(),rounds=g['round'].nunique(),common_same_image_n=len(ids),verified_date_n=int(g.sampling_date_verified.sum()),Sai_n=int(g.river.eq('Sai').sum())))
        # D0/D2 have insufficient independent groups for nested CV.
        if gap not in [3,4]: continue
        for mode in ['available','common_same_image']:
            for r in [20,30,50]:
                g=e[e.radius_m.eq(r)]
                if mode=='common_same_image': g=g[g.observation_id.isin(ids)]
                g=g.sort_values('observation_id').reset_index(drop=True)
                for group in ['station','round']:
                    if g[group].nunique()<4: continue
                    for fam,pred,choice,y in run(g,group):
                        err=pred-y
                        summaries.append(dict(max_gap_days=gap,sample=mode,radius_m=r,cv_group=group,n=len(g),stations=g.station.nunique(),rounds=g['round'].nunique(),family=fam,RMSE_log10_NTU=np.sqrt(np.mean(err**2)),MAE_log10_NTU=np.mean(np.abs(err))))
                        z=g[['observation_id','station','river','round','image_id','satellite_date_th','max_possible_date_gap_days','turbidity_NTU_raw','sampling_date_verified','coordinate_status']].copy()
                        z=z.assign(max_gap_days=gap,sample=mode,radius_m=r,cv_group=group,family=fam,features=choice,observed_log10_NTU=y,predicted_log10_NTU=pred,error_log10_NTU=err)
                        predictions.append(z)
    s=pd.DataFrame(summaries); s.to_csv(args.output/'CCD_sensitivity_RMSE.csv',index=False); pd.concat(predictions,ignore_index=True).to_csv(args.output/'CCD_sensitivity_predictions.csv',index=False); pd.DataFrame(cover).to_csv(args.output/'CCD_sensitivity_coverage.csv',index=False)
    wide=s.pivot(index=['max_gap_days','sample','cv_group','radius_m','n','stations','rounds'],columns='family',values='RMSE_log10_NTU').reset_index(); wide.columns.name=None
    wide.to_csv(args.output/'CCD_sensitivity_SigmaPlot.csv',index=False)
    print(wide.round(4).to_string(index=False)); print(pd.DataFrame(cover).to_string(index=False))
if __name__=='__main__': main()
