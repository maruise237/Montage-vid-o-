import sys,glob
from PIL import Image,ImageDraw
fs=sorted(glob.glob('planche/p*.jpg')); ts=sys.argv[2:]; n=len(fs); cols=int(sys.argv[1])
ims=[Image.open(f).resize((270,480)) for f in fs]; rows=(n+cols-1)//cols
W=Image.new('RGB',(cols*274,rows*500),'#444');d=ImageDraw.Draw(W)
for i,im in enumerate(ims):
    x,y=(i%cols)*274,(i//cols)*500; W.paste(im,(x,y)); d.text((x+4,y+482),ts[i] if i<len(ts) else '',fill='white')
W.save('planche.jpg',quality=85)
