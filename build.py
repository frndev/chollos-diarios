#!/usr/bin/env python3
import json, os, html, datetime
HERE=os.path.dirname(os.path.abspath(__file__)); TAG="frndev12-21"
P=json.load(open(os.path.join(HERE,'data','products.json')))
e=html.escape
cats=sorted({p['category'] for p in P})
def fd(d): return datetime.date.fromisoformat(d).strftime('%d/%m/%Y')
cards=[]
for p in P:
    url=f"https://www.amazon.es/dp/{p['asin']}?tag={TAG}"
    img=f'<img src="{e(p["image"])}" alt="{e(p["title"])}" loading="lazy">' if p.get('image') else '<div class="ph">Sin imagen</div>'
    price=''
    if p.get('price'):
        price=f'<p class="price">{e(p["price"])}' + (f' <s>{e(p["old_price"])}</s>' if p.get('old_price') else '') + f'<br><small>Precio visto el {fd(p["seen_on"])}. Puede haber cambiado.</small></p>'
    cards.append(f'''<article class="card" data-cat="{e(p['category'])}"><span class="badge">-{p['discount']}%</span>
<a href="{url}" target="_blank" rel="sponsored noopener nofollow" class="imgw">{img}</a>
<h2>{e(p['title'][:110])}{'…' if len(p['title'])>110 else ''}</h2><p class="cat">{e(p['category'])}</p>{price}
<a class="btn" href="{url}" target="_blank" rel="sponsored noopener nofollow">Ver oferta en Amazon</a></article>''')
opts=''.join(f'<button data-c="{e(c)}">{e(c)}</button>' for c in cats)
out=f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Chollos Diarios – ofertas y descuentos de hoy</title><meta name="description" content="Chollos y ofertas seleccionadas cada día: tecnología, hogar, videojuegos y más, con descuentos reales comprobados.">
<link rel="canonical" href="https://frndev.github.io/chollos-diarios/"><meta name="robots" content="index,follow">
<meta property="og:type" content="website"><meta property="og:locale" content="es_ES"><meta property="og:title" content="Chollos Diarios – ofertas y descuentos de hoy"><meta property="og:description" content="Chollos y ofertas seleccionadas cada día con descuentos reales comprobados."><meta property="og:url" content="https://frndev.github.io/chollos-diarios/">
<meta name="twitter:card" content="summary"><meta name="google-site-verification" content="7hHaYig-lav-W99AxpycY2RHe8s50GVDp-eUggo91SQ" />
<style>
*{{box-sizing:border-box}}body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#f4f5f7;color:#1b1f24}}
header{{background:#131921;color:#fff;padding:24px 16px;text-align:center}}header h1{{margin:0;font-size:1.8rem}}header h1 span{{color:#ff9900}}header p{{margin:6px 0 0;opacity:.8}}
.filters{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;padding:16px}}.filters button{{border:1px solid #ccc;background:#fff;border-radius:20px;padding:6px 14px;cursor:pointer;font-size:.9rem}}.filters button.on{{background:#ff9900;border-color:#ff9900;color:#111;font-weight:600}}
main{{max-width:1200px;margin:0 auto;padding:0 16px 32px;display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px}}
.card{{position:relative;background:#fff;border-radius:12px;padding:14px;display:flex;flex-direction:column;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
.badge{{position:absolute;top:10px;left:10px;background:#cc0c39;color:#fff;font-weight:700;padding:4px 8px;border-radius:6px;font-size:.9rem}}
.imgw{{display:flex;align-items:center;justify-content:center;height:180px}}.imgw img{{max-width:100%;max-height:180px;object-fit:contain}}.ph{{color:#999}}
.card h2{{font-size:.95rem;line-height:1.3;margin:10px 0 4px;flex-grow:1}}.cat{{color:#666;font-size:.8rem;margin:0 0 6px}}.price{{margin:0 0 10px;font-weight:700}}.price s{{color:#888;font-weight:400}}.price small{{font-weight:400;color:#888;font-size:.72rem}}
.btn{{display:block;text-align:center;background:#ffd814;color:#111;text-decoration:none;padding:10px;border-radius:20px;font-weight:600}}.btn:hover{{background:#f7ca00}}
footer{{background:#232f3e;color:#ddd;padding:20px 16px;text-align:center;font-size:.85rem;line-height:1.5}}
</style></head><body>
<header><h1>Chollos <span>Diarios</span></h1><p>Chollos seleccionados · actualizado el {datetime.date.today().strftime('%d/%m/%Y')}</p></header>
<nav class="filters"><button class="on" data-c="*">Todas</button>{opts}</nav>
<main>{''.join(cards)}</main>
<footer><p><strong>Como afiliado de Amazon, obtengo ingresos por las compras adscritas que cumplen los requisitos aplicables.</strong></p>
<p>Los precios y descuentos pueden cambiar en cualquier momento. El precio y la disponibilidad que se muestran en Amazon.es en el momento de la compra son los que se aplicarán.</p></footer>
<script>document.querySelectorAll('.filters button').forEach(b=>b.onclick=()=>{{document.querySelectorAll('.filters button').forEach(x=>x.classList.remove('on'));b.classList.add('on');document.querySelectorAll('.card').forEach(c=>c.style.display=(b.dataset.c=='*'||c.dataset.cat==b.dataset.c)?'':'none')}})</script>
</body></html>'''
os.makedirs(os.path.join(HERE,'site'),exist_ok=True); open(os.path.join(HERE,'site','index.html'),'w').write(out); open(os.path.join(HERE,'site','robots.txt'),'w').write('User-agent: *\nAllow: /\nSitemap: https://frndev.github.io/chollos-diarios/sitemap.xml\n')
open(os.path.join(HERE,'site','sitemap.xml'),'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://frndev.github.io/chollos-diarios/</loc><lastmod>'+datetime.date.today().isoformat()+'</lastmod><changefreq>daily</changefreq></url></urlset>\n')
print('site/index.html:',len(P),'productos')
