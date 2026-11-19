"""Re-fit archived outer-fold predictor choices and verify D4 scores.
Candidate selection itself is independently rerun by CCD_aperture_analysis.py.
Equivalent colour bases can have numerical ties; this verifies the exact archived choices.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
R=Path(__file__).resolve().parents[1]/'04_results'
g=pd.read_csv(R/'D4_50m_SigmaPlot.csv'); p=pd.read_csv(R/'D4_50m_predictions.csv').set_index('observation_id').loc[g.observation_id]; c=pd.read_csv(R/'D4_50m_fold_choices.csv').fillna('')
y=np.log10(g.turbidity_NTU_raw.to_numpy())
for fam,h in c.groupby('family'):
    z=np.full(len(g),np.nan)
    for row in h.itertuples():
        te=(g.station==row.held_out_station).to_numpy();tr=~te
        cols=row.features.split('+') if row.features else []
        z[te]=LinearRegression().fit(g.loc[tr,cols],y[tr]).predict(g.loc[te,cols]) if cols else y[tr].mean()
    np.testing.assert_allclose(z,p[fam+'_log10'],rtol=1e-9,atol=1e-9)
    print(fam, 'RMSE', np.sqrt(np.mean((z-y)**2)), 'PASS')
