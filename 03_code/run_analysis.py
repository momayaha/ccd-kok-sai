"""Reproduce manuscript tables and figures from archived inputs and scores."""
from pathlib import Path
import argparse, shutil, subprocess, sys, tempfile, os
ROOT=Path(__file__).resolve().parents[1]; CODE=ROOT/'03_code'; RAW=ROOT/'02_input_and_raw_data'
def call(script,*args):
    subprocess.run([sys.executable,str(CODE/script),*map(str,args)],check=True,env={**os.environ,'MPLBACKEND':'Agg'})
def main(out, figures):
    out=out.resolve()
    if out==ROOT or any((ROOT/d) in [out,*out.parents] for d in ['01_source_data','02_input_and_raw_data','03_code','04_results','05_figures']): raise ValueError('Choose a separate output directory')
    r=out/'04_results';r.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        t=Path(temp)
        for f in [RAW/'CCD_same_day_date_audit_300.csv',RAW/'CCD_Sentinel2_aperture_v2_r1_r22.csv',CODE/'CCD_aperture_analysis.py']:shutil.copy2(f,t/f.name)
        subprocess.run([sys.executable,str(t/'CCD_aperture_analysis.py')],check=True)
        for f in t.glob('CCD_aperture_*.csv'):shutil.copy2(f,r/f.name)
    for name in ['D4_50m_SigmaPlot.csv','D4_50m_predictions.csv','D4_50m_fold_choices.csv','D4_50m_RMSE.csv']:shutil.copy2(ROOT/'04_results'/name,r/name)
    call('ground_arsenic_analysis.py','--root',ROOT,'--out',out)
    call('CCD_sensitivity_analysis.py',out,'--output',r)
    call('CCD_auc_cluster_bootstrap.py',r,r/'CCD_auc_cluster_bootstrap.csv')
    if figures:call('make_CCD_figures.py','--results',r,'--output',out/'manuscript_figures')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'reproduced');p.add_argument('--skip-figures',action='store_true');a=p.parse_args();main(a.output,not a.skip_figures)
