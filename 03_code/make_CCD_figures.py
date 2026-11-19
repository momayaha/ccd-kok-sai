from pathlib import Path
import zipfile, shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter, MultipleLocator
from matplotlib.colors import LogNorm
from sklearn.metrics import auc
from PIL import Image
import fitz

import argparse
root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--results', type=Path, default=root/'04_results')
p.add_argument('--output', type=Path, default=root/'reproduced'/'manuscript_figures')
a = p.parse_args()
out = a.output.resolve(); out.mkdir(parents=True, exist_ok=True)
source = a.results.resolve()
ground = pd.read_csv(source/'ground_paired_296.csv')
ccd = pd.read_csv(source/'D4_50m_SigmaPlot.csv')
pred = pd.read_csv(source/'D4_50m_predictions.csv')
roc = pd.read_csv(source/'D4_arsenic_proxy_ROC_coordinates.csv')

assert len(ground) == 296 and len(ccd) == len(pred) == 45
assert set(ccd.observation_id) == set(pred.observation_id)
assert ground.As_plot_mgL.gt(0).all() and ground.turbidity_NTU_raw.gt(0).all()

def save(fig, name):
    fig.savefig(out / f'{name}.pdf')
    fig.savefig(out / f'{name}.png', dpi=600)
    plt.close(fig)

def setup(ax):
    ax.tick_params(axis='both', direction='out', length=4, labelsize=10)
    ax.spines[['top','right']].set_visible(False)
    ax.xaxis.label.set_size(11)
    ax.yaxis.label.set_size(11)

# Figure 2: all 296 paired observations, censored values at reporting limits.
fig = plt.figure(figsize=(7.0, 4.85))
ax = fig.add_axes([.13,.14,.83,.79])
ax.set_xscale('log')
ax.set_yscale('log')
ax.axhline(.010, linestyle='--', linewidth=1, alpha=.65, zorder=1)
river_handles=[]
for river, marker in [('Kok','o'), ('Sai','s')]:
    g=ground[ground.river.eq(river)]
    det=g[g.As_censored.eq(0)]
    cens=g[g.As_censored.eq(1)]
    dots=ax.scatter(det.turbidity_NTU_raw,det.As_plot_mgL,
        s=23,marker=marker,alpha=.72,linewidths=.45,label=f'{river} River (n={len(g)})',zorder=3)
    river_handles.append(dots)
    ax.scatter(cens.turbidity_NTU_raw,cens.As_plot_mgL,
        s=31,marker='v',facecolors='none',edgecolors=dots.get_facecolor(),
        linewidths=.9,zorder=4)
threshold_handle = Line2D([],[], linestyle='--', linewidth=1, color=ax.lines[0].get_color(),label='0.010 mg/L threshold')
censored_handle = Line2D([],[], marker='v',linestyle='none', markerfacecolor='none', markeredgecolor='0.3',markersize=6,label='Below reporting limit')
ax.legend(handles=river_handles+[censored_handle,threshold_handle],loc='upper left',fontsize=9,frameon=False)
ax.set(xlabel='Measured turbidity (NTU)',ylabel='Arsenic concentration (mg/L)',xlim=(25,6000),ylim=(.0075,.4))
ax.yaxis.set_major_locator(FixedLocator([.01,.02,.05,.1,.2]))
ax.yaxis.set_major_formatter(FuncFormatter(lambda x,p:f'{x:.2f}'))
ax.xaxis.set_major_locator(FixedLocator([30,100,300,1000,3000]))
ax.xaxis.set_major_formatter(FuncFormatter(lambda x,p:f'{x:g}'))
setup(ax)
save(fig,'fig2-as-turbidity')

# Figure 3: two independent plots, aligned and assembled into one vector PDF.
def ccd_axis(panel):
    fig = plt.figure(figsize=(4.15,3.55))
    ax=fig.add_axes([.19,.25,.59,.63])
    ax.set(xlabel=r'$B-G$',ylabel=r'$G-R$',xlim=(0,.70),ylim=(-.15,.41))
    ax.xaxis.set_major_locator(MultipleLocator(.2))
    ax.yaxis.set_major_locator(MultipleLocator(.1))
    ax.text(0,1.055,panel,transform=ax.transAxes,fontsize=12,fontweight='bold')
    setup(ax)
    return fig, ax

fig, ax = ccd_axis('(a)')
sc=ax.scatter(ccd.B_minus_G,ccd.G_minus_R,c=ccd.turbidity_NTU_raw,
              norm=LogNorm(vmin=ccd.turbidity_NTU_raw.min(),vmax=ccd.turbidity_NTU_raw.max()),
              s=34,linewidths=.45)
cax=fig.add_axes([.81,.27,.035,.59])
cb=fig.colorbar(sc,cax=cax,ticks=[40,100,300,1000])
cb.ax.yaxis.set_major_formatter(FuncFormatter(lambda x,p:f'{x:g}'))
cb.ax.tick_params(labelsize=9)
cb.set_label('Turbidity (NTU)',fontsize=9,labelpad=6)
save(fig,'panel3a')

fig, ax = ccd_axis('(b)')
for status, marker, label in [(0,'o','Non-exceedance (n=35)'),(1,'^','Exceedance (n=10)')]:
    g=ccd[ccd.As_above_0_010.eq(status)]
    ax.scatter(g.B_minus_G,g.G_minus_R,marker=marker,s=34 if status==0 else 48,
               alpha=.83,linewidths=.55,label=label)
fig.legend(loc='lower center',bbox_to_anchor=(.485,.008),fontsize=8.5,
           frameon=False,handletextpad=.35,borderpad=.2)
save(fig,'panel3b')

a=fitz.open(out/'panel3a.pdf')
b=fitz.open(out/'panel3b.pdf')
assembled=fitz.open()
w,h=a[0].rect.width,a[0].rect.height
page=assembled.new_page(width=w+b[0].rect.width,height=h)
page.show_pdf_page(fitz.Rect(0,0,w,h),a,0)
page.show_pdf_page(fitz.Rect(w,0,w+b[0].rect.width,h),b,0)
assembled.save(out/'fig3-ccd.pdf')
assembled.close(); a.close(); b.close()
with Image.open(out/'panel3a.png') as pa, Image.open(out/'panel3b.png') as pb:
    combined=Image.new('RGB',(pa.width+pb.width,max(pa.height,pb.height)),'white')
    combined.paste(pa.convert('RGB'),(0,0))
    combined.paste(pb.convert('RGB'),(pa.width,0))
    combined.save(out/'fig3-ccd.png',dpi=(600,600))
for fn in ['panel3a','panel3b']:
    for ext in ['pdf','png']:
        (out/f'{fn}.{ext}').unlink()

# Figure 4: measured and nested-LOSO predicted log10 turbidity.
x=np.log10(pred.turbidity_NTU_raw)
y=pred.two_colours_log10
rmse=float(np.sqrt(np.mean((x-y)**2)))
fig=plt.figure(figsize=(5.55,5.35))
ax=fig.add_axes([.16,.14,.76,.79])
lower,upper=1.35,3.35
ax.plot([lower,upper],[lower,upper],'--',linewidth=1.15,alpha=.7,label='One-to-one line',zorder=1)
ax.scatter(x,y,s=35,alpha=.78,linewidths=.55,label='CCD predictions',zorder=2)
ax.set(xlim=(lower,upper),ylim=(lower,upper),
       xlabel=r'Measured $\log_{10}(T/1\,\mathrm{NTU})$',
       ylabel=r'CCD-estimated $\log_{10}(T/1\,\mathrm{NTU})$')
ax.set_aspect('equal',adjustable='box')
ax.xaxis.set_major_locator(MultipleLocator(.5))
ax.yaxis.set_major_locator(MultipleLocator(.5))
ax.text(.04,.96,f'$n = {len(pred)}$\nRMSE = {rmse:.3f}',transform=ax.transAxes,va='top',fontsize=10)
ax.legend(loc='lower right',fontsize=9,frameon=False)
setup(ax)
save(fig,'fig4-turbidity-prediction')

# Figure 5: ROC for the five archived screening scores.
fig=plt.figure(figsize=(6.15,5.55))
ax=fig.add_axes([.135,.13,.80,.81])
series=[
    ('turbidity_NTU_raw','Measured turbidity','-'),
    ('single_band_NTU','Single band','--'),
    ('single_colour_NTU','Single colour',':'),
    ('two_colours_NTU','CCD','-'),
    ('all_four_bands_NTU','Four bands','-.')
]
for key,label,ls in series:
    d=roc[roc.score.eq(key)]
    area=auc(d.FPR,d.TPR)
    ax.plot(d.FPR,d.TPR,linestyle=ls,
            linewidth=2.3 if key=='two_colours_NTU' else 1.5,
            label=f'{label} ({area:.3f})')
ax.plot([0,1],[0,1],linestyle='--',linewidth=.9,alpha=.65,label='No discrimination')
ax.set(xlim=(0,1.015),ylim=(0,1.02),xlabel='False positive rate',ylabel='True positive rate')
ax.set_aspect('equal',adjustable='box')
ax.xaxis.set_major_locator(MultipleLocator(.2))
ax.yaxis.set_major_locator(MultipleLocator(.2))
ax.legend(loc='lower right',fontsize=9,title='Screening score (AUC)',title_fontsize=9,frameon=True,framealpha=.95)
setup(ax)
save(fig,'fig5-arsenic-roc')

# Keep the exact user-supplied GIS Figure 1 without altering its attribution.
shutil.copy2(root/'05_figures'/'fig1-study-area.pdf',out/'fig1-study-area.pdf')
with fitz.open(out/'fig1-study-area.pdf') as doc:
    doc[0].get_pixmap(dpi=600,alpha=False).save(out/'fig1-study-area.png')

print(f'Created 5 figures in PDF and PNG. CCD RMSE = {rmse:.6f}.')