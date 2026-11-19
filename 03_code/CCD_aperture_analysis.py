from pathlib import Path
import numpy as np,pandas as pd
from itertools import combinations
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from scipy.stats import spearmanr
P=Path(__file__).resolve().parent
A=pd.read_csv(P/'CCD_same_day_date_audit_300.csv')
D=pd.read_csv(P/'CCD_Sentinel2_aperture_v2_r1_r22.csv').merge(A[['observation_id','sampling_date_exact','date_evidence_status','turbidity_NTU_raw','As_mgL_raw','As_censored','As_above_0_010']],on='observation_id',validate='many_to_one')
t=pd.to_datetime(D.satellite_date_th); s=pd.to_datetime(D.sampling_start);e=pd.to_datetime(D.sampling_end);exact=pd.to_datetime(D.sampling_date_exact);good=D.date_evidence_status.eq('verified_date_site_name_and_values');s=s.where(~good,exact);e=e.where(~good,exact)
D['max_possible_date_gap_days']=np.maximum(abs((t-s).dt.days),abs((t-e).dt.days));D['midpoint_gap_days']=abs((t-(s+(e-s)/2)).dt.total_seconds()/86400);D['sampling_date_verified']=good
B=['B2','B3','B4','B8']; I=['B_minus_G','B_minus_R','B_minus_NIR','G_minus_R','G_minus_NIR','R_minus_NIR']
D['valid_water']=D.B2_count.ge(3)&D[[b+'_p50' for b in B]].gt(0).all(axis=1)
for b in B:D[b]=D[b+'_p50']
for (b,c),i in zip(combinations(B,2),I):D[i]=-2.5*np.log10(D[b]/D[c])
D.to_csv(P/'CCD_aperture_audit_all.csv',index=False)
# Rank deterministically by date uncertainty, midpoint gap, valid pixel count, image ID. Never use measured NTU or As.
S=D[D.valid_water].sort_values(['max_possible_date_gap_days','midpoint_gap_days','B2_count','image_id'],ascending=[True,True,False,True]).drop_duplicates(['radius_m','observation_id']).copy()
S.to_csv(P/'CCD_aperture_best_per_radius.csv',index=False)
S[S.max_possible_date_gap_days<=4].to_csv(P/'CCD_aperture_D4_SigmaPlot.csv',index=False)
# Nested LOSO, same linear regression and target across families, exploratory D4 only.
families={'single_band':[(x,) for x in B],'single_colour':[(x,) for x in I],'two_colours':list(combinations(I,2)),'all_four_bands':[tuple(B)]}
rows=[]; fixed=[]; cor=[]
for r,g in S[S.max_possible_date_gap_days<=4].groupby('radius_m'):
 g=g.dropna(subset=['turbidity_NTU_raw']+B+I);g=g[g.turbidity_NTU_raw>0].reset_index(drop=True); y=np.log10(g.turbidity_NTU_raw.to_numpy()); st=g.station.to_numpy(); N=np.arange(len(g))
 def pred(tr,te,cols):
  if not cols:return np.full(len(te),y[tr].mean())
  return LinearRegression().fit(g.loc[tr,list(cols)],y[tr]).predict(g.loc[te,list(cols)])
 def cv(idx,cols):
  z=np.full(len(g),np.nan)
  for a in np.unique(st[idx]):
   tr=idx[st[idx]!=a];te=idx[st[idx]==a];z[te]=pred(tr,te,cols)
  return z[idx]
 def rmse(a,b):return np.sqrt(mean_squared_error(a,b))
 rows.append([r,len(g),len(set(st)),'training_mean',rmse(y,cv(N,()))])
 for fam,sets in families.items():
  z=np.full(len(g),np.nan)
  for a in np.unique(st):
   tr=N[st!=a];te=N[st==a];best=min(sets,key=lambda cols: rmse(y[tr],cv(tr,cols)));z[te]=pred(tr,te,best)
  rows.append([r,len(g),len(set(st)),fam,rmse(y,z)])
  for cols in sets:fixed.append([r,fam,'+'.join(cols),rmse(y,cv(N,cols))])
 for col in B+I:cor.append([r,col,spearmanr(g[col],g.turbidity_NTU_raw).statistic])
R=pd.DataFrame(rows,columns=['radius_m','n','stations','family','RMSE_log10_NTU']);R.to_csv(P/'CCD_aperture_D4_nested_models.csv',index=False);print(R.to_string(index=False))
pd.DataFrame(fixed,columns=['radius_m','family','features','RMSE_log10_NTU']).to_csv(P/'CCD_aperture_D4_fixed_models.csv',index=False)
C=pd.DataFrame(cor,columns=['radius_m','feature','spearman_rho']);C.to_csv(P/'CCD_aperture_D4_correlations.csv',index=False);print(C.pivot(index='feature',columns='radius_m',values='spearman_rho').round(3).to_string())
