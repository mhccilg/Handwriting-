"""Fill a PDF with handwriting.
Spec JSON: [{"page":1,"x":72,"y":200,"text":"...","size":11,"width":300,"line_height":18,"color":[200,40,45]}]
x,y = PDF points from top-left; y is the BASELINE of the first line. size = capital height in points."""
import sys, json, io, pymupdf
sys.path.insert(0, __import__('os').path.dirname(__file__))
import handwriting as hw
def fill(src,spec,dst,dpi=300):
    doc=pymupdf.open(src); k=dpi/72
    for i,f in enumerate(spec):
        pg=doc[f['page']-1]; cap=f.get('size',11)*k
        img,base=hw.render_block(f['text'],cap_px=cap,max_w_px=f['width']*k if f.get('width') else None,
            line_h=f.get('line_height',f.get('size',11)*1.9)*k,color=tuple(f.get('color',hw.INK)),seed=f.get('seed',i+7))
        b=io.BytesIO(); img.save(b,'PNG')
        x0=f['x']; y0=f['y']-base/k
        pg.insert_image(pymupdf.Rect(x0,y0,x0+img.width/k,y0+img.height/k),stream=b.getvalue(),overlay=True)
    doc.save(dst,garbage=3,deflate=True)
if __name__=='__main__':
    fill(sys.argv[1],json.load(open(sys.argv[2])),sys.argv[3])
