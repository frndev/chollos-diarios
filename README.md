# Ofertas Amazon.es (afiliado frndev12-21)
- `python3 update_deals.py` → descubre ofertas (Chollometro, tienda Amazon), obtiene ASIN, verifica en amazon.es (título, imagen, % ahorro, precio), revalida/elimina antiguas (>7 días o sin descuento), y regenera `site/`.
- `python3 build.py` → solo regenera `site/index.html` desde `data/products.json`.
Rutina diaria sugerida: `cd /workspace/ofertas-amazon && python3 update_deals.py --max 30` y luego desplegar `site/`.
