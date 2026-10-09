"""Luca's handwriting renderer. Glyphs cut from his alphabet/number sheet (150 dpi scan)."""
import json, os, random, math, io
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE=os.path.dirname(os.path.abspath(__file__))
DB=json.load(open(os.path.join(HERE,'index.json')))
GL={ch:[(Image.open(os.path.join(HERE,v['file'])).convert('L'),v) for v in vs if v.get('ok',True)] for ch,vs in DB.items()}
GL={k:v for k,v in GL.items() if v}
INK=(200,40,45)   # his red pen; pass color= to change
CAP=float(np.median([v['h'] for c in 'ABDEHKLMNPRT' for _,v in GL[c]]))  # ~50px
XH=float(np.median([v['h'] for c in 'acemnorsuvwxz' for _,v in GL[c]]))
# baseline position as fraction of glyph height measured from top (1.0 = sits on line)
DESC={'g':0.52,'p':0.5,'q':0.55,'y':0.45,'j':0.62,',':0.45}
def _median_h(ch): return float(np.median([v['h'] for _,v in GL[ch]]))
MED={ch:_median_h(ch) for ch in GL}
for _c in 'bdhklt': MED[_c]=min(MED[_c],CAP*0.92)
def _stroke_img(kind,rng):
    """Synthesize punctuation he didn't write on the sheet, with a pen-width stroke."""
    w=int(XH*1.2); h=int(CAP*1.1); im=Image.new('L',(w,h),0); d=ImageDraw.Draw(im); pw=3
    j=lambda: rng.uniform(-1.5,1.5)
    if kind=="'": im=im.crop((0,0,10,int(CAP*0.4))); d=ImageDraw.Draw(im); d.line([(6+j(),1),(4+j(),im.height-2)],255,pw); return im,0.0,'top'
    if kind=='"': im=Image.new('L',(18,int(CAP*0.4)),0); d=ImageDraw.Draw(im); d.line([(5,1),(4,im.height-2)],255,pw); d.line([(13,1),(12,im.height-2)],255,pw); return im,0.0,'top'
    if kind==',': im=Image.new('L',(10,int(XH*0.6)),0); d=ImageDraw.Draw(im); d.line([(7,1),(3,im.height-1)],255,pw); return im,0.4,'base'
    if kind==':': im=Image.new('L',(8,int(XH)),0); d=ImageDraw.Draw(im); d.ellipse([1,2,6,7],fill=255); d.ellipse([1,im.height-7,6,im.height-2],fill=255); return im,1.0,'base'
    if kind==';': im=Image.new('L',(10,int(XH*1.4)),0); d=ImageDraw.Draw(im); d.ellipse([2,2,7,7],fill=255); d.line([(7,int(XH)-6),(3,im.height-1)],255,pw); return im,0.72,'base'
    if kind=='!': im=Image.new('L',(10,int(CAP)),0); d=ImageDraw.Draw(im); d.line([(6,1),(4,im.height-12)],255,pw); d.ellipse([2,im.height-6,7,im.height-1],fill=255); return im,1.0,'base'
    if kind=='?': im=Image.new('L',(int(CAP*0.6),int(CAP)),0); d=ImageDraw.Draw(im); W=im.width; d.arc([2,1,W-3,int(CAP*0.5)],200,90,255,pw); d.line([(W/2,int(CAP*0.5)),(W/2-1,int(CAP*0.75))],255,pw); d.ellipse([W/2-3,im.height-6,W/2+2,im.height-1],fill=255); return im,1.0,'base'
    if kind=='/': im=Image.new('L',(int(CAP*0.55),int(CAP)),0); d=ImageDraw.Draw(im); d.line([(im.width-3,1),(3,im.height-2)],255,pw); return im,1.0,'base'
    if kind=='*': im=Image.new('L',(int(XH),int(XH)),0); d=ImageDraw.Draw(im); s=im.width
    if kind=='*':
        for a in (90,30,150): r=s/2-2; c=s/2; d.line([(c-r*math.cos(math.radians(a)),c-r*math.sin(math.radians(a))),(c+r*math.cos(math.radians(a)),c+r*math.sin(math.radians(a)))],255,pw)
        return im,0.0,'top'
    if kind=='%': im=Image.new('L',(int(CAP*0.8),int(CAP)),0); d=ImageDraw.Draw(im); W,H=im.size; d.line([(W-3,2),(3,H-2)],255,pw); d.ellipse([2,2,W*0.38,H*0.33],outline=255,width=pw); d.ellipse([W*0.6,H*0.66,W-2,H-2],outline=255,width=pw); return im,1.0,'base'
    if kind=='$': return None
    return None
def _get(ch,rng):
    """Return (L-image, baseline_frac, mode) for one character."""
    if ch in GL:
        img,v=rng.choice(GL[ch])
        # pull size toward the median for consistency
        s=(0.65*MED[ch]+0.35*v['h'])/v['h']
        img=img.resize((max(1,int(img.width*s)),max(1,int(img.height*s))),Image.LANCZOS)
        if ch in '-_+': return img,None,'mid' if ch!='_' else 'base'
        if ch=='.': return img.resize((max(4,img.width*2//3),max(4,img.height*2//3))),1.0,'base'
        return img,DESC.get(ch,1.0),'base'
    if ch=='=':
        a,_,_=_get('-',rng); b,_,_=_get('-',rng)
        w=max(a.width,b.width); gap=int(XH*0.35); im=Image.new('L',(w,a.height+b.height+gap),0)
        im.paste(a,(0,0)); im.paste(b,(rng.randint(0,max(0,w-b.width)),a.height+gap)); return im,None,'mid'
    if ch=='1' and '1' not in GL: return _get('|',rng)
    r=_stroke_img(ch,rng)
    if r: return r
    if ch.lower() in GL: return _get(ch.lower(),rng)
    if ch.upper() in GL: return _get(ch.upper(),rng)
    raise KeyError(f'no glyph for {ch!r}')
def render_line(text,cap_px=40,color=INK,seed=None,jitter=1.0,tracking=1.0,slant=0.0):
    """Render one line. Returns (RGBA image, baseline_y). cap_px = capital-letter height in output pixels."""
    rng=random.Random(seed)
    k=cap_px/CAP
    pieces=[]; x=0
    gap=CAP*0.07*tracking; space=CAP*0.5
    for ch in text:
        if ch==' ': x+=space*rng.uniform(0.85,1.15); continue
        if ch=='\t': x+=space*4; continue
        img,bf,mode=_get(ch,rng)
        sc=rng.uniform(1-0.05*jitter,1+0.05*jitter)
        img=img.resize((max(1,int(img.width*sc)),max(1,int(img.height*sc))),Image.LANCZOS)
        ang=rng.uniform(-2.5,2.5)*jitter+slant
        img=img.rotate(ang,resample=Image.BICUBIC,expand=True)
        dy=rng.uniform(-0.025,0.025)*CAP*jitter
        if mode=='base': top=-img.height*bf+dy
        elif mode=='mid': top=-XH*0.5-img.height/2+dy
        else: top=-CAP+dy  # 'top' aligned to cap height
        pieces.append((img,x,top)); x+=img.width+gap*rng.uniform(0.7,1.3)
    if not pieces: return Image.new('RGBA',(1,1),(0,0,0,0)),0
    tops=[t for _,_,t in pieces]; bots=[t+i.height for i,_,t in pieces]
    y0=min(min(tops),-CAP); y1=max(bots); W=int(x+4); H=int(y1-y0+4)
    a=Image.new('L',(W,H),0)
    for img,px,t in pieces:
        region=Image.new('L',(W,H),0); region.paste(img,(int(px)+2,int(t-y0)+2))
        a=Image.fromarray(np.maximum(np.array(a),np.array(region)))
    base=-y0+2
    if k<0.9: a=a.filter(ImageFilter.MaxFilter(3))  # keep pen weight when shrinking
    a=a.resize((max(1,int(W*k)),max(1,int(H*k))),Image.LANCZOS)
    out=Image.new('RGBA',a.size,color+(0,)); out.putalpha(a)
    return out, base*k
def wrap(text,max_w_px,cap_px,seed=None):
    """Greedy wrap using measured widths."""
    lines=[]
    for para in text.split('\n'):
        words=para.split(' '); cur=''
        for w in words:
            t=(cur+' '+w).strip()
            if cur and render_line(t,cap_px,seed=seed)[0].width>max_w_px: lines.append(cur); cur=w
            else: cur=t
        lines.append(cur)
    return lines
def render_block(text,cap_px=40,max_w_px=None,line_h=None,color=INK,seed=0,**kw):
    """Multi-line block. Returns RGBA image and the baseline y of the first line."""
    line_h=line_h or cap_px*2.0
    lines=wrap(text,max_w_px,cap_px,seed) if max_w_px else text.split('\n')
    imgs=[render_line(l,cap_px,color,seed=(seed*1000+i),**kw) for i,l in enumerate(lines)]
    above=max(b for _,b in imgs); W=max(i.width for i,_ in imgs)
    H=int(above+line_h*(len(imgs)-1)+max(i.height-b for i,b in imgs)+2)
    out=Image.new('RGBA',(W,H),color+(0,))
    for n,(im,b) in enumerate(imgs):
        out.alpha_composite(im,(0,int(above+n*line_h-b)))
    return out,above
