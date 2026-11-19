"""Exploratory percentile intervals for fixed scores, using cluster resampling.
Usage: python CCD_auc_cluster_bootstrap.py UPDATE.zip OUTPUT.csv
Does not refit models. Two-way crosses independent station/round bootstrap counts.
"""
import sys,zipfile
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.metrics import roc_auc_score

def run(path,out):
    path=Path(path)
    def read(n):
        if path.is_dir(): return pd.read_csv(path/(n+'.csv'))
        with zipfile.ZipFile(path) as z: return pd.read_csv(z.open('04_results/'+n+'.csv'))
    q=read('ground_paired_296'); d=read('D4_arsenic_proxy_predictions'); p=read('ground_grouped_predictions')
    rng=np.random.default_rng(20261119); B=10000; rows=[]
    def analyze(g, label, cols):
        g=g.reset_index(drop=True); y=g.As_above_0_010.to_numpy(); pos=y==1; neg=y==0
        st,ss=pd.factorize(g.station,sort=True); rd,rr=pd.factorize(g['round'],sort=True)
        # reuse weights across scores in a cohort for comparable estimates
        sw=rng.multinomial(len(ss),np.repeat(1/len(ss),len(ss)),size=B)[:,st]
        rw=rng.multinomial(len(rr),np.repeat(1/len(rr),len(rr)),size=B)[:,rd]
        for col,name in cols.items():
            x=g[col].to_numpy(); a=roc_auc_score(y,x)
            for method,w in [('station',sw),('round',rw),('station_x_round',sw*rw)]:
                wp=w[:,pos]; wn=w[:,neg]; den=wp.sum(1)*wn.sum(1); valid=den>0
                # Ties contribute half.
                matrix=(x[pos,None]>x[None,neg]).astype(float)+0.5*(x[pos,None]==x[None,neg])
                v=((wp[valid]@matrix)*wn[valid]).sum(1)/den[valid]
                lo,hi=np.quantile(v,[.025,.975])
                rows.append([label,name,len(g),int(pos.sum()),int(neg.sum()),len(ss),len(rr),a,method,lo,hi,B,int(valid.sum()),'conditional on archived scores; no model refitting'])
    for name,g in [('Both',q),('Kok',q[q.river.eq('Kok')])]:
        g=g.copy()
        cols={'turbidity_NTU_raw':'Measured turbidity'}
        for key in ['station','round']:
            pred=p[(p.river==name)&(p.held_out_group_type==key)].set_index('observation_id').predicted_probability
            g['held_'+key]=g.observation_id.map(pred)
            cols['held_'+key]='LO'+key+'O logistic (fixed predictions)'
        analyze(g,name,cols)
    analyze(d,'Kok D4 50m',{'turbidity_NTU_raw':'Measured turbidity','single_band_NTU':'Single band','single_colour_NTU':'Single colour','two_colours_NTU':'CCD','all_four_bands_NTU':'Four bands'})
    pd.DataFrame(rows,columns=['cohort','score','n','n_above','n_at_or_below','n_stations','n_rounds','AUC','bootstrap_cluster','CI95_low','CI95_high','draws','valid_draws','interpretation']).to_csv(out,index=False)
    print(pd.read_csv(out).query("bootstrap_cluster=='station_x_round'").to_string(index=False))
    print('D4 exact and coordinate status:',d.sampling_date_verified.value_counts().to_dict(),d.max_possible_date_gap_days.value_counts().sort_index().to_dict(),d.coordinate_status.value_counts().to_dict())
if __name__=='__main__':run(sys.argv[1],sys.argv[2])
