import json,os
V=os.environ.get('V','')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
h=open('animation.html').read().replace('__TIMELINE__',open(f'timeline{V}.json').read())
open(f'page{V}.html','w').write(h); print(f'page{V}.html',len(h)//1024,'Ko')
