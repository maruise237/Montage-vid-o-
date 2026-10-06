import sys
from PIL import Image, ImageDraw
im=Image.open(sys.argv[1]).convert('RGB'); d=ImageDraw.Draw(im)
for x in range(0,im.width,100): d.line([(x,0),(x,im.height)],fill=(255,0,0) if x%500==0 else (255,150,150),width=1)
for y in range(0,im.height,100):
    d.line([(0,y),(im.width,y)],fill=(255,0,0) if y%500==0 else (255,150,150),width=1); d.text((2,y+2),str(y),fill=(255,0,0))
im.save(sys.argv[2])
