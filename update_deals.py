#!/usr/bin/env python3
"""Refresca data/products.json con ofertas reales de Amazon.es.
1) Descubre hilos de Chollometro cuya tienda es Amazon.
2) Resuelve su enlace de salida para obtener el ASIN (amazon.es/dp/ASIN).
3) Verifica cada ASIN en la ficha de Amazon.es: título, imagen, categoría y
   que Amazon muestre un % de ahorro. Sin ahorro visible => se descarta.
4) Revalida los productos existentes y elimina los expirados o > MAX_AGE días.
5) Ejecuta build.py.
Uso: python3 update_deals.py [--max 30]
"""
import re, html, json, subprocess, sys, time, datetime, urllib.parse, os
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
HERE=os.path.dirname(os.path.abspath(__file__)); DATA=os.path.join(HERE,'data','products.json')
MAX=int(sys.argv[sys.argv.index('--max')+1]) if '--max' in sys.argv else 30
MAX_AGE=7
def curl(u,follow=True):
    a=['curl','-s','--compressed','--max-time','25','-A',UA,'-H','Accept-Language: es-ES,es;q=0.9']
    if follow: a.append('-L')
    else: a+=['-o','/dev/null','-w','%{redirect_url}']
    return subprocess.run(a+[u],capture_output=True,text=True,errors='ignore').stdout
def discover():
    out={}
    urls=[f"https://www.chollometro.com/search?q=amazon&page={p}" for p in range(1,6)]+["https://www.chollometro.com/populares","https://www.chollometro.com/"]
    for u in urls:
        s=html.unescape(curl(u))
        for m in re.finditer(r'"threadId":"?(\d+)"?',s):
            seg=s[m.start():m.start()+3000]
            mm=re.search(r'"merchantName":"([^"]*)"',seg)
            if mm and mm.group(1)=='Amazon' and '"isExpired":true' not in seg[:3000]: out[m.group(1)]=1
        time.sleep(1)
    return list(out)
def asin_for(tid):
    r=urllib.parse.unquote(curl(f"https://www.chollometro.com/visit/threadmain/{tid}",follow=False))
    m=re.search(r'amazon\.es/(?:[^?]*/)?(?:dp|gp/product)/([A-Z0-9]{10})',r)
    return m.group(1) if m else None
def verify(asin):
    s=curl(f"https://www.amazon.es/dp/{asin}")
    t=re.search(r'id="productTitle"[^>]*>\s*([^<]+?)\s*<',s)
    if not t: return None
    img=re.search(r'"hiRes":"(https://m\.media-amazon\.com/images/I/[^"]+)"',s) or re.search(r'"large":"(https://m\.media-amazon\.com/images/I/[^"]+)"',s)
    i=s.find('id="corePriceDisplay_desktop_feature_div"'); seg=s[i:i+8000] if i>=0 else ''
    sv=re.search(r'savingsPercentage[^>]*>\s*-?(\d+)',seg)
    if not sv: return None
    w=re.search(r'a-price-whole">([\d.]+)',seg); f=re.search(r'a-price-fraction">(\d+)',seg)
    old=re.search(r'basisPrice.*?a-offscreen">([^<]+)',seg,re.S)
    b=s.find('wayfinding-breadcrumbs'); cats=re.findall(r'a-link-normal[^>]*>\s*([^<]+?)\s*<',s[b:b+4000]) if b>=0 else []
    today=datetime.date.today().isoformat()
    return dict(asin=asin,title=html.unescape(t.group(1)),image=img.group(1) if img else None,
        category=html.unescape(cats[0]) if cats else 'Otros',discount=int(sv.group(1)),
        price=(f"{w.group(1).rstrip('.')},{f.group(1) if f else '00'} €" if w else None),
        old_price=(old.group(1).strip().replace('\xa0',' ') if old else None),
        seen_on=today,found=today,url=f"https://www.amazon.es/dp/{asin}")
def main():
    prev={p['asin']:p for p in (json.load(open(DATA)) if os.path.exists(DATA) else [])}
    today=datetime.date.today(); res={}
    for a,p in prev.items():  # revalidar
        if (today-datetime.date.fromisoformat(p['found'])).days>MAX_AGE: continue
        v=verify(a); time.sleep(1.5)
        if v: v['found']=p['found']; res[a]=v
    for tid in discover():
        if len(res)>=MAX: break
        a=asin_for(tid)
        if not a or a in res: continue
        v=verify(a); time.sleep(1.5)
        if v: v['source']=f"https://www.chollometro.com/ofertas/{tid}"; res[a]=v; print('OK',a,v['discount'],v['title'][:60],file=sys.stderr)
    json.dump(sorted(res.values(),key=lambda p:-p['discount']),open(DATA,'w'),ensure_ascii=False,indent=1)
    print(len(res),'productos',file=sys.stderr)
    subprocess.run([sys.executable,os.path.join(HERE,'build.py')])
if __name__=='__main__': main()
