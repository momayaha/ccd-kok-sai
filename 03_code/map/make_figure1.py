"""Figure 1: PCD reference stations and real GIS linework (no synthetic rivers)."""
import argparse, json, math, re, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.collections import LineCollection
from mpl_toolkits.basemap import Basemap
from pyproj import Geod
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parent
BBOX=(19.82,99.23,20.55,100.25) # S,W,N,E
S,W,N,E=BBOX
COLORS={'Kok':'#125e9b','Sai':'#b52f35'}
WATER='#3686ac'
ENDPOINTS=['https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter']
PATTERNS={
    'Kok':r'(^|\W)(kok|mae kok|nam kok)(\W|$)|แม่น้ำกก|น้ำกก',
    'Sai':r'(^|\W)(sai|mae sai|nam sai|ruak|ruak river)(\W|$)|แม่น้ำสาย|น้ำสาย|แม่น้ำรวก|น้ำรวก',
    'Mekong':r'mekong|แม่น้ำโขง|น้ำโขง',
}
# Ruak is a distinct river; do not identify it as Sai.
PATTERNS['Sai']=r'(^|\W)(sai|mae sai|nam sai)(\W|$)|แม่น้ำสาย|น้ำสาย'

def group(tags):
    names=' / '.join(str(v) for k,v in tags.items() if k=='name' or k.startswith('name:') or k in ('alt_name','official_name','int_name'))
    for name,pat in PATTERNS.items():
        if re.search(pat,names,re.I): return name
    return 'other'

def fetch_osm(path):
    if path.exists(): return json.loads(path.read_text(encoding='utf-8'))
    bbox=','.join(map(str,BBOX))
    # Ways tagged river and waterway relations including their member geometry.
    query=f'[out:json][timeout:90];(way["waterway"="river"]({bbox});way["waterway"="stream"]["name"]({bbox});rel["type"="waterway"]({bbox}););out geom;'
    errors=[]
    for url in ENDPOINTS:
        try:
            r=requests.get(url,params={'data':query},timeout=135,headers={'User-Agent':'Kok-Sai-Research-Figure/1.0 (academic cartography)'})
            r.raise_for_status(); data=r.json()
            if not data.get('elements') or data.get('remark'): raise ValueError(str(data.get('remark','No elements')))
            path.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8'); return data
        except Exception as e: errors.append(f'{url}: {e}')
    raise RuntimeError('\n'.join(errors))

def river_lines(data):
    by_id={}
    def add(key,coords,kind):
        line=[(v['lon'],v['lat']) for v in coords if 'lat' in v and 'lon' in v]
        if len(line)<2: return
        if key not in by_id or (by_id[key][0]=='other' and kind!='other'):
            by_id[key]=(kind,line)
    for el in data.get('elements',[]):
        if el.get('type')=='way': add(el['id'],el.get('geometry',[]),group(el.get('tags',{})))
    for el in data.get('elements',[]):
        if el.get('type')=='relation':
            kind=group(el.get('tags',{}))
            if kind=='other': continue
            for mem in el.get('members',[]):
                if mem.get('type')=='way': add(mem['ref'],mem.get('geometry',[]),kind)
    return by_id

def draw(out, df, lines=None):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'ps.fonttype':42})
    fig,ax=plt.subplots(figsize=(10.2,7.6)); fig.subplots_adjust(left=.10,right=.96,bottom=.115,top=.94)
    base=Basemap(projection='cyl',llcrnrlon=W,urcrnrlon=E,llcrnrlat=S,urcrnrlat=N,resolution='i',ax=ax,fix_aspect=False)
    ax.set_facecolor('#f8f8f5')
    base.drawcountries(color='#65676b',linewidth=.85,zorder=2)
    # Country borders are generalized WDBII linework, not exact river boundaries.
    if lines:
        for kind,color,width,z in [('other','#a9c9d9',.52,3),('Mekong','#6e9db4',1.25,4),('Kok','#176a9b',1.85,5),('Sai','#176a9b',1.85,5)]:
            segments=[line for k,line in lines.values() if k==kind]
            if segments: ax.add_collection(LineCollection(segments,colors=color,linewidths=width,zorder=z,clip_on=True))
    if 'preview' in out.name:
        ax.text(.5,.975,'PREVIEW — detailed study-river geometry not verified',transform=ax.transAxes,ha='center',va='top',fontsize=7.6,color='#555555',zorder=10)
    ax.set_xlim(W,E); ax.set_ylim(S,N); ax.set_aspect(1/math.cos(math.radians(20.18)))
    xt=[99.4,99.6,99.8,100.0,100.2]; yt=[19.9,20.0,20.1,20.2,20.3,20.4,20.5]
    ax.set_xticks(xt,labels=[f'{x:.1f}°E' for x in xt]); ax.set_yticks(yt,labels=[f'{y:.1f}°N' for y in yt]); ax.tick_params(axis='both',direction='out',length=3,labelsize=9,top=True,right=True)
    ax.grid(color='#8e999b',linewidth=.45,alpha=.25,zorder=0)
    for s in ax.spines.values(): s.set_color('#5f6266'); s.set_linewidth(.8)
    # Labels use offsets only; actual marker coordinates are unchanged.
    offsets={'KK01':(-5,-13),'KK02':(-1,-13),'KK03':(5,9),'KK04':(-10,10),'KK05':(-5,-16),'KK06':(12,10),'KK07':(-12,-16),'KK08':(2,11),'KK10':(8,-13),'KK11':(9,-3),'KK12':(9,0),'KK13':(8,0),'KK14':(8,0),'KK15':(8,0),'SA01':(-12,-15),'SA02':(-3,14),'SA03':(10,13)}
    for river,c in COLORS.items():
        sub=df[df.river==river]; ax.scatter(sub.longitude,sub.latitude,s=43,c=c,edgecolors='white',linewidths=.8,zorder=8)
    for r in df.itertuples():
        dx,dy=offsets[r.station]; ax.annotate(r.station,(r.longitude,r.latitude),xytext=(dx,dy),textcoords='offset points',ha='left' if dx>4 else 'right' if dx<-4 else 'center',va='center',fontsize=8.4,weight='medium',zorder=9,arrowprops={'arrowstyle':'-','color':'#555','lw':.45,'shrinkA':2,'shrinkB':3})
    ax.text(99.64,20.40,'MYANMAR',color='#595d62',fontsize=11,weight='semibold',ha='center')
    ax.text(99.65,19.86,'THAILAND',color='#595d62',fontsize=11,weight='semibold',ha='center')
    ax.text(100.19,20.33,'LAOS',color='#595d62',fontsize=10,weight='semibold',ha='center')
    if lines:
        # Label representative points on actual named geometries, not station-connecting lines.
        for kind in ['Kok','Sai','Mekong']:
            candidates=[(line,[(x,y) for x,y in line if W+.07<x<E-.09 and S+.06<y<N-.06]) for k,line in lines.values() if k==kind]
            candidates=[(line,inside) for line,inside in candidates if inside]
            if candidates:
                _,inside=max(candidates,key=lambda item:len(item[1])); x,y=inside[len(inside)//2]
                ax.annotate(f'{kind} River',(x,y),xytext=(0,12 if kind!='Sai' else -15),textcoords='offset points',fontsize=9,style='italic',weight='semibold',color='#176a9b',ha='center',zorder=7,bbox={'facecolor':'#f8f8f5','edgecolor':'none','alpha':.85,'pad':1})
    ax.annotate('',xy=(.955,.933),xytext=(.955,.868),xycoords='axes fraction',arrowprops={'arrowstyle':'-|>','lw':1.4,'color':'#30343a'})
    ax.text(.955,.945,'N',transform=ax.transAxes,ha='center',va='bottom',weight='bold')
    # East-west geodesic scale, valid at the displayed latitude.
    geod=Geod(ellps='WGS84'); sx,sy=99.97,19.87
    ticks=[geod.fwd(sx,sy,90,1000*k)[0] for k in (0,5,10,20)]
    for k in range(3): ax.plot(ticks[k:k+2],[sy,sy],lw=3.4,color='#30343a' if k%2==0 else '#a7aaa9',solid_capstyle='butt',zorder=10)
    for x,k in zip(ticks,(0,5,10,20)): ax.text(x,sy+.011,str(k)+(' km' if k==20 else ''),ha='center',va='bottom',fontsize=7.5)
    legend=[Line2D([],[],marker='o',ls='',color=c,markeredgecolor='white',markersize=7,label=f'{river} River stations ({len(df[df.river==river])})') for river,c in COLORS.items()]
    if lines: legend.append(Line2D([],[],color='#176a9b',lw=1.8,label='Named study rivers'))
    ax.legend(handles=legend,loc='lower left',fontsize=8,framealpha=1,facecolor='white',edgecolor='#b4b7b6',borderpad=.65)
    # Geographic inset with genuine country linework, in independent axes.
    iax=ax.inset_axes([.025,.605,.225,.37]); im=Basemap(projection='cyl',llcrnrlon=96,urcrnrlon=106,llcrnrlat=5,urcrnrlat=22,resolution='l',ax=iax)
    im.drawmapboundary(fill_color='#e1edf2',linewidth=.75); im.fillcontinents(color='#f3f1e9',lake_color='#e1edf2'); im.drawcoastlines(color='#8e9395',linewidth=.45); im.drawcountries(color='#777d80',linewidth=.6)
    iax.add_patch(Rectangle((W,S),E-W,N-S,facecolor='none',edgecolor='#b52f35',linewidth=1.6,zorder=7)); iax.text(100.7,15,'Thailand',ha='center',fontsize=7.5,weight='medium'); iax.annotate('Study area',xy=((W+E)/2,(S+N)/2),xytext=(102.7,21.3),ha='center',fontsize=6.8,arrowprops={'arrowstyle':'-','lw':.65,'color':'#b52f35'},zorder=8)
    attribution='Stations: PCD (22–26 September 2025)  |  Boundaries: WDBII / GMT (Basemap)'
    if lines: attribution+='  |  River data: © OpenStreetMap contributors (ODbL), openstreetmap.org/copyright'
    fig.text(.5,.055,attribution,ha='center',fontsize=6.8,color='#4f5356',wrap=True)
    fig.savefig(out.with_suffix('.pdf'),bbox_inches='tight',pad_inches=.16)
    fig.savefig(out.with_suffix('.png'),dpi=600,bbox_inches='tight',pad_inches=.16)
    plt.close(fig)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--stations',type=Path,default=ROOT/'CCD_Figure1_reference_stations_17.csv'); p.add_argument('--osm-json',type=Path,default=ROOT/'osm_waterways_raw.json'); p.add_argument('--offline',action='store_true'); args=p.parse_args()
    df=pd.read_csv(args.stations); assert len(df)==17 and df.station.nunique()==17 and df.river.value_counts().to_dict()=={'Kok':14,'Sai':3}
    if args.offline:
        draw(ROOT/'fig1-study-area-preview',df); return
    try: lines=river_lines(fetch_osm(args.osm_json))
    except Exception as e:
        print('OSM download unavailable:',e,file=sys.stderr); draw(ROOT/'fig1-study-area-preview',df); sys.exit(2)
    # Save extracted geometry with OSM IDs, types and classifications for audit.
    features=[{'type':'Feature','properties':{'osm_way_id':i,'river_group':k},'geometry':{'type':'LineString','coordinates':line}} for i,(k,line) in lines.items()]
    (ROOT/'osm_waterways.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False),encoding='utf-8')
    from collections import Counter
    counts=Counter(k for k,line in lines.values() if any(W<=x<=E and S<=y<=N for x,y in line)); print('OSM segment counts inside map:',dict(counts))
    if not counts['Kok'] or not counts['Sai']:
        print('Named Kok and Sai geometry not both found. Check OSM tags / shapefile before final publication.',file=sys.stderr); draw(ROOT/'fig1-study-area-preview',df,lines); sys.exit(3)
    draw(ROOT/'fig1-study-area',df,lines)
    print('Rendered fig1-study-area.pdf and .png. Check river continuity and named features against GIS before publication.')

if __name__=='__main__': main()
