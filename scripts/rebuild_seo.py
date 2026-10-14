#!/usr/bin/env python3
"""Greshy Likes Herbal: rebuilds static SEO product/category pages and sitemap.
Run from project root: python scripts/rebuild_seo.py
No external modules required. The public site remains 100% static.
"""
import pathlib, json, re, html, urllib.parse
from xml.etree import ElementTree as ET

ROOT=pathlib.Path(__file__).resolve().parent.parent
DOMAIN='https://www.greshylikes.com'
BRAND='Greshy Likes Herbal'

def load_js(path,global_name):
    data=(ROOT/path).read_text(encoding='utf-8')
    match=re.search(r'window\.'+re.escape(global_name)+r'\s*=\s*',data)
    if not match: raise ValueError('Missing window.'+global_name+' in '+str(path))
    value, end=json.JSONDecoder().raw_decode(data,match.end())
    return value

def h(x): return html.escape(str(x if x is not None else ''),quote=True)
def url(path): return DOMAIN+'/'+path.lstrip('/')
def product_path(p): return 'products/'+urllib.parse.quote(str(p['id']),safe='-')+'.html'
def cents(p):
    price=p.get('price')
    return 'LKR '+format(float(price),',.0f') if price not in (None,'') else 'Price on enquiry'
def ld(data):
    return json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')

def site_head(title,description,canonical,image=None,schema=None):
    tags='''<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#143a2a">'''
    ogimage=image or url('assets/images/bottle-sample-03.webp')
    tags+=f'''\n<title>{h(title)}</title>
<meta name="description" content="{h(description)}">
<link rel="canonical" href="{h(canonical)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{h(title)}">
<meta property="og:description" content="{h(description)}">
<meta property="og:url" content="{h(canonical)}">
<meta property="og:image" content="{h(ogimage)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{h(title)}">
<meta name="twitter:description" content="{h(description)}">
<meta name="twitter:image" content="{h(ogimage)}">
<link rel="icon" type="image/png" href="../assets/images/favicon.png">
<link rel="stylesheet" href="../css/base.css">
<link rel="stylesheet" href="../css/product-pages.css">'''
    if schema:tags+='\n<script type="application/ld+json">'+ld(schema)+'</script>'
    return tags

def layout(title,description,canonical,breadcrumb,body,site,ogimage=None,schema=None):
    brandline=h(site.get('tagline') or 'Luxury with Ayurveda')
    brandname=h(site.get('brand') or BRAND)
    businesslocation=h(site.get('location') or 'Jaffna, Sri Lanka')
    socials=''
    head=site_head(title,description,canonical,ogimage,schema)
    nav=f'''<header class="sub-header"><div class="sub-shell sub-header-inner"><a href="../index.html" class="sub-logo"><img src="../assets/images/logo.webp" width="51" height="51" alt="Greshy Likes Herbal logo"><span><strong>{brandname}</strong><small>{brandline}</small></span></a><nav aria-label="Main navigation"><a href="../index.html#collection">Signature Perfumes</a><a href="../index.html#more-products">More Products</a><a href="../index.html#story">Our Story</a></nav></div></header>'''
    footer=f'''<footer class="sub-footer"><div class="sub-shell"><strong>{brandname}</strong><span>{brandline} · {businesslocation}</span><div><a href="../index.html">Home</a><a href="../privacy.html">Privacy</a><a href="../terms.html">Terms</a><a href="mailto:{h(site.get('email','greshylikes@gmail.com'))}">Email us</a></div></div></footer>'''
    return '<!doctype html>\n<html lang="en"><head>\n'+head+'\n</head><body>'+nav+'\n<main id="main"><div class="sub-shell"><p class="crumb"><a href="../index.html">Home</a> <span aria-hidden="true">/</span> '+breadcrumb+'</p></div>'+body+'</main>'+footer+'</body></html>\n'

def breadcrumb_json(page,name,parent=None):
    items=[{'@type':'ListItem','position':1,'name':'Home','item':DOMAIN+'/'}]
    if parent:
        items.append({'@type':'ListItem','position':2,'name':parent[1],'item':url(parent[0])})
    items.append({'@type':'ListItem','position':len(items)+1,'name':name,'item':url(page)})
    return {'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':items}

def whatsapp(site,p):
    digits=re.sub(r'\D','',str(site.get('whatsapp','94713433403')))
    message='Hello Greshy Likes Herbal, I would like to enquire about '+p['name']
    if p.get('size'): message+=' ('+str(p['size'])+')'
    message+='. Please confirm availability and ordering details.'
    return 'https://wa.me/'+digits+'?text='+urllib.parse.quote(message)

def pimage(p):
    image=(p.get('images') or [None])[0]
    if image:
        return f'<img src="../{h(image)}" alt="{h(p["name"])} by Greshy Likes Herbal" width="800" height="600" loading="eager">'
    return f'<div class="sub-no-photo"><span>{h(p["name"])}</span><small>Product photograph coming soon</small></div>'

def product_page(p,site,other):
    path=product_path(p);canonical=url(path);category=p.get('category','Product')
    desc=p.get('description','').strip() or f'Learn more about {p["name"]} from Greshy Likes Herbal.'
    size=p.get('size') or ''
    keyword=('herbal-inspired perfume' if category=='Perfumes' else 'personal care product' if category=='Personal Care' else 'car fragrance')
    title=f'{p["name"]}{(" " + size) if size and size.lower() not in p["name"].lower() else ""} | {keyword.title()} | {site.get("brand") or BRAND}'
    excerpt=f'{p["name"]}: {desc} {size} · {cents(p)}. Explore the product from Greshy Likes Herbal, Sri Lanka.'
    excerpt=' '.join(excerpt.split())[:175]
    image=(p.get('images') or [None])[0]
    ogimg=url(image) if image else url('assets/images/bottle-sample-03.webp')
    offer=None
    if p.get('price') not in (None,''):
        offer={'@type':'Offer','url':canonical,'price':p['price'],'priceCurrency':'LKR','seller':{'@type':'Organization','name':site.get('brand') or BRAND}}
        av={'in_stock':'https://schema.org/InStock','out_of_stock':'https://schema.org/OutOfStock'}
        if p.get('availability') in av: offer['availability']=av[p['availability']]
    obj={'@context':'https://schema.org','@type':'Product','name':p['name'],'description':desc,'brand':{'@type':'Brand','name':site.get('brand') or BRAND},'category':category,'url':canonical}
    if image:obj['image']=url(image)
    if offer:obj['offers']=offer
    breadcrumbs=breadcrumb_json(path,p['name'],('perfumes/','Perfumes') if category=='Perfumes' else ('personal-care/','Personal Care') if category=='Personal Care' else ('car-fragrance/','Car Fragrance'))
    schema={'@context':'https://schema.org','@graph':[obj,breadcrumbs]}
    status={'in_stock':'Available to order','out_of_stock':'Currently unavailable','coming_soon':'Coming soon','enquire':'Please enquire to confirm availability'}.get(p.get('availability'),'Please enquire')
    button='' if p.get('availability')=='coming_soon' else f'<a class="sub-button" href="{h(whatsapp(site,p))}" target="_blank" rel="noopener">Enquire on WhatsApp ↗</a>'
    button=button.replace('class="sub-button"', 'class="sub-button" id="pageWhatsapp"')
    imageblock=pimage(p)
    price=cents(p)
    related=''.join(f'<a class="related-card" href="../{h(product_path(q))}"><span>{h(q["name"])}</span><small>{h(cents(q))}</small></a>' for q in other[:4])
    category_path={'Perfumes':'perfumes/','Personal Care':'personal-care/','Car Fragrance':'car-fragrance/'}.get(category,'index.html')
    body=f'''<article class="sub-shell sub-product" data-product-id="{h(p['id'])}">
<div class="sub-image" id="pageImage">{imageblock}</div>
<div class="sub-detail"><p class="sub-eyebrow" id="pageCategory">{h(category)} · GRESHY LIKES HERBAL</p><h1 id="pageName">{h(p['name'])}</h1><p class="sub-price" id="pagePrice">{h(price)}</p><p class="sub-desc" id="pageDescription">{h(desc)}</p><dl><dt>Size</dt><dd id="pageSize">{h(size or 'Contact us for details')}</dd><dt>Availability</dt><dd id="pageAvailability">{h(status)}</dd><dt>Origin</dt><dd>{h(site.get('location') or 'Jaffna, Sri Lanka')}</dd></dl>{button}<a class="sub-secondary" href="../{h(category_path)}">← Explore the {h(category.lower())} collection</a></div></article>
<section class="sub-shell related"><h2>Explore more from Greshy Likes Herbal</h2><div class="related-grid">{related}</div></section>'''
    page = layout(title,excerpt,canonical,h(p['name']),body,site,ogimg,schema)
    # Browser displays the latest catalogue values even before the next SEO rebuild.
    scripts = '<script defer src="../data/site.js"></script><script defer src="../data/products.js"></script><script defer src="../js/product-live.js"></script>'
    return page.replace('</body>',scripts+'</body>')

def category_page(slug,title,desc,entries,site):
    path=slug+'/'; canonical=url(path)
    links=''.join(f'<article class="category-card"><a class="category-img" href="../{h(product_path(p))}">{pimage(p)}</a><h2><a href="../{h(product_path(p))}">{h(p["name"])}</a></h2><p>{h((p.get("description") or "")[:140])}</p><strong>{h(cents(p))}</strong><a href="../{h(product_path(p))}">View product ↗</a></article>' for p in entries)
    schema=breadcrumb_json(path,title)
    body=f'<section class="sub-shell sub-category"><p class="sub-eyebrow">GRESHY LIKES HERBAL · SRI LANKA</p><h1>{h(title)}</h1><p class="category-lead">{h(desc)}</p><div class="category-grid">{links}</div></section>'
    return layout(title+' | '+(site.get('brand') or BRAND)+' Sri Lanka',desc,canonical,h(title),body,site,None,schema)


def sync_home_content(source, site):
    """Keep the pre-rendered homepage HTML synchronized with data/site.js.

    The browser still uses main.js for display, but this also writes the same text
    into index.html so crawlers, previews and View Source see current content.
    """
    def replace_element_text(markup, element_id, value):
        if not isinstance(value, str):
            return markup
        pat = r'(<(?P<tag>h1|h2|p|span|div|strong)\b(?=[^>]*\bid="' + re.escape(element_id) + r'")[^>]*>).*?(</(?P=tag)>)'
        return re.sub(pat, lambda m: m.group(1) + h(value) + m.group(3), markup, count=1, flags=re.S)

    def render_title(value):
        # Mirrors js/main.js setTitle: | toggles emphasis, newline means <br>.
        sections=[]
        emphasized=False
        for segment in value.split('|'):
            pieces=[]
            for index, part in enumerate(segment.split('\n')):
                if index: pieces.append('<br>')
                if part:
                    pieces.append('<em>'+h(part)+'</em>' if emphasized else h(part))
            sections.extend(pieces)
            emphasized=not emphasized
        return ''.join(sections)

    def replace_title(markup, element_id, value):
        if not isinstance(value, str):
            return markup
        pat = r'(<(?P<tag>h1|h2)\b(?=[^>]*\bid="' + re.escape(element_id) + r'")[^>]*>).*?(</(?P=tag)>)'
        return re.sub(pat, lambda m: m.group(1) + render_title(value) + m.group(3), markup, count=1, flags=re.S)

    def replace_attr_by_id(markup, element_id, attr, value):
        if not isinstance(value, str):
            return markup
        pattern = r'<(?P<tag>img|a)\b(?=[^>]*\bid="' + re.escape(element_id) + r'")[^>]*>'
        def modify(match):
            tag=match.group(0)
            expression=r'\b' + re.escape(attr) + r'="[^"]*"'
            replacement=attr+'="'+h(value)+'"'
            if re.search(expression,tag):
                return re.sub(expression,lambda _m:replacement,tag,count=1)
            return tag[:-1] + ' ' + replacement + '>'
        return re.sub(pattern,modify,markup,count=1)

    text_fields = ('heroEyebrow','heroText','heroTagline','introText',
                   'collectionText','moreText','giftText','storyEyebrow',
                   'storyText','contactText')
    for field in text_fields:
        # heroTagline always follows site tagline instead of a separate setting.
        value = site.get('tagline') if field=='heroTagline' else site.get(field)
        source=replace_element_text(source,field,value)

    for field in ('heroTitle','introTitle','collectionTitle','moreTitle',
                  'giftTitle','storyTitle','contactTitle'):
        source=replace_title(source,field,site.get(field))

    for element_id in ('headerTagline','footerTagline'):
        source=replace_element_text(source,element_id,site.get('tagline'))

    name=(site.get('brand') or BRAND).upper()
    if name.endswith(' HERBAL'):
        name=name[:-len(' HERBAL')]
    source=replace_element_text(source,'brandDisplay',name)
    source=replace_element_text(source,'footerBrandDisplay',name)

    for element_id,setting in (('contactEmailText','email'),('footerEmail','email')):
        source=replace_element_text(source,element_id,site.get(setting))
    for element_id,key in (('brandSymbolImage','logo'),('footerLogo','logo'),
                           ('heroImage','heroImage'),('storyImage','storyImage'),
                           ('featureImage','featureImage')):
        image_path=site.get(key)
        if image_path:
            source=replace_attr_by_id(source,element_id,'src',image_path)

    email=site.get('email')
    if email:
        for element_id in ('contactEmail','questionEmail','footerEmail'):
            source=replace_attr_by_id(source,element_id,'href','mailto:'+email)

    digits=re.sub(r'\D','',str(site.get('whatsapp') or '94713433403'))
    message=urllib.parse.quote('Hello Greshy Likes Herbal, I would like to enquire about your products.')
    target='https://wa.me/'+digits+'?text='+message
    for element_id in ('navWhatsapp','heroWhatsapp','contactWhatsapp','questionWhatsapp','socialFallback','footerWhatsapp'):
        source=replace_attr_by_id(source,element_id,'href',target)
    # Render phone text in the source, not just its WhatsApp destination.
    if digits:
        phone='+'+digits[:2]+' '+digits[2:4]+' '+digits[4:7]+' '+digits[7:] if len(digits)==11 else '+'+digits
        for element_id in ('socialFallback','footerWhatsapp'):
            source=replace_element_text(source,element_id,phone)

    # Reflect social URLs in source and match JS visibility behavior.
    for key,element_id in (('instagram','instagramLink'),('facebook','facebookLink'),('tiktok','tiktokLink')):
        value=site.get(key) or ''
        if value.startswith('https://'):
            source=replace_attr_by_id(source,element_id,'href',value)
            pat=r'<a\b(?=[^>]*\bid="'+re.escape(element_id)+r'")[^>]*>'
            source=re.sub(pat,lambda m: re.sub(r'\s+hidden(?:="[^"]*")?', '',m.group(0)),source,count=1)
        else:
            pat=r'<a\b(?=[^>]*\bid="'+re.escape(element_id)+r'")[^>]*>'
            source=re.sub(pat,lambda m: m.group(0) if re.search(r'\shidden(?:\s|=|>)',m.group(0)) else m.group(0)[:-1]+' hidden>',source,count=1)
    # The preload should point to the same image displayed in the hero.
    hero=site.get('heroImage')
    if hero:
        pat=r'<link\b(?=[^>]*\brel="preload")(?=[^>]*\bas="image")[^>]*>'
        def change_preload(m):
            return re.sub(r'\bhref="[^"]*"',lambda _: 'href="'+h(hero)+'"',m.group(0),count=1)
        source=re.sub(pat,change_preload,source,count=1)
    return source

def rebuild():
    site=load_js(pathlib.Path('data/site.js'),'GRESHY_SITE')
    all_products=load_js(pathlib.Path('data/products.js'),'GRESHY_PRODUCTS')
    products=[p for p in all_products if p.get('published') is not False]
    # Validate IDs before using them as filenames or links. This also prevents accidental overwrites.
    seen=set()
    for p in all_products:
        slug=p.get('id','')
        if not isinstance(slug,str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):
            raise ValueError(f'Invalid product id {slug!r}; use lowercase letters, digits and hyphens')
        if slug in seen:
            raise ValueError(f'Duplicate product id {slug!r}; each product needs a unique ID')
        if not isinstance(p.get('name'),str) or not p['name'].strip():
            raise ValueError(f'Missing product name for {slug!r}')
        if p.get('price') not in (None,'') and (not isinstance(p['price'], (float,int)) or isinstance(p['price'],bool) or p['price']<0):
            raise ValueError(f'Invalid price for {slug!r}')
        seen.add(slug)
    (ROOT/'products').mkdir(exist_ok=True)
    old={f.name for f in (ROOT/'products').glob('*.html')}
    created=set()
    for p in products:
        similar=[q for q in products if q.get('category')==p.get('category') and q['id']!=p['id']]
        if len(similar)<4: similar += [q for q in products if q!=p and q not in similar]
        name=pathlib.Path(product_path(p)).name
        (ROOT/'products'/name).write_text(product_page(p,site,similar),encoding='utf8')
        created.add(name)
    for stale in old-created:(ROOT/'products'/stale).unlink()
    collections=[('perfumes','Herbal-Inspired Perfumes in Sri Lanka','Explore Greshy Likes Herbal signature fragrances, including the 50 ml perfume collection and 10 ml perfume, inspired by botanical traditions and created in Jaffna, Sri Lanka.',lambda p:p.get('category')=='Perfumes'),('personal-care','Herbal-Inspired Personal Care in Sri Lanka','Discover Greshy Likes Herbal face cream, face wash, body wash and lip balm. Explore sizes and prices, then enquire directly through WhatsApp.',lambda p:p.get('category')=='Personal Care'),('car-fragrance','Car Fragrance in Sri Lanka','Explore car diffuser fragrance products from Greshy Likes Herbal and enquire about availability and ordering.',lambda p:p.get('category')=='Car Fragrance')]
    category_paths=[]
    for slug,title,desc,condition in collections:
        matches=[p for p in products if condition(p)]
        directory=ROOT/slug
        if matches:
            directory.mkdir(exist_ok=True)
            (directory/'index.html').write_text(category_page(slug,title,desc,matches,site),encoding='utf8')
            category_paths.append(slug+'/')
        elif (directory/'index.html').exists(): (directory/'index.html').unlink()
    # Update fallback links if homepage HTML contains optional noscript placeholder.
    home=ROOT/'index.html';source=home.read_text(encoding='utf8')
    fallback='<p>Browse product pages:</p><ul>'+''.join(f'<li><a href="{h(product_path(p))}">{h(p["name"])}</a></li>' for p in products)+'</ul>'
    source=re.sub(r'(<noscript id="seoNoScriptLinks">).*?(</noscript>)',lambda m:m.group(1)+fallback+m.group(2),source,flags=re.S)
    # Keep homepage SEO tags & Organization metadata aligned with data/site.js.
    def swap_meta(src,kind,key,value):
        pat=r'<meta(?=[^>]*\b'+re.escape(kind)+r'="'+re.escape(key)+r'")[^>]*>'
        def change(m):
            tag=m.group(0)
            if re.search(r'\bcontent="[^"]*"',tag):
                return re.sub(r'\bcontent="[^"]*"','content="'+h(value)+'"',tag,count=1)
            return tag
        return re.sub(pat,change,src,count=1)
    newtitle=site.get('seoTitle') or BRAND+' | Herbal Perfumes & Personal Care in Sri Lanka'
    newdesc=site.get('seoDescription') or 'Herbal-inspired perfumes and personal care by Greshy Likes Herbal, Jaffna, Sri Lanka.'
    source=re.sub(r'<title>.*?</title>','<title>'+h(newtitle)+'</title>',source,count=1,flags=re.S)
    for kind,key,val in [('name','description',newdesc),('property','og:title',newtitle),('property','og:description',newdesc),('name','twitter:title',newtitle),('name','twitter:description',newdesc)]:
        source=swap_meta(source,kind,key,val)
    hero=site.get('heroImage') or 'assets/images/bottle-sample-03.webp'
    for kind,key in [('property','og:image'),('name','twitter:image')]:
        source=swap_meta(source,kind,key,url(hero))
    org={'@type':'Organization','@id':DOMAIN+'/#organization','name':site.get('brand',BRAND),'url':DOMAIN+'/','logo':url(site.get('logo','assets/images/logo.webp')),'email':site.get('email',''),'telephone':'+'+re.sub(r'\D','',str(site.get('whatsapp',''))),'slogan':site.get('tagline','')}
    if site.get('location'):org['address']=site['location']
    same=[site[k] for k in ('instagram','facebook','tiktok') if str(site.get(k,'')).startswith('https://')]
    if same: org['sameAs']=same
    web={'@type':'WebSite','@id':DOMAIN+'/#website','name':site.get('brand',BRAND),'url':DOMAIN+'/','publisher':{'@id':DOMAIN+'/#organization'}}
    orgld=ld({'@context':'https://schema.org','@graph':[org,web]})
    source=re.sub(r'(<script type="application/ld\+json">).*?(</script>)',lambda m:m.group(1)+orgld+m.group(2),source,count=1,flags=re.S)
    source=sync_home_content(source,site)
    home.write_text(source,encoding='utf8')
    # Sitemap includes canonical, indexable pages only. No made-up lastmod dates.
    links=['']+category_paths+[product_path(p) for p in products]+['privacy.html','terms.html']
    xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('  <url><loc>'+html.escape(url(path))+'</loc></url>\n' for path in links)+'</urlset>\n'
    (ROOT/'sitemap.xml').write_text(xml,encoding='utf8')
    (ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /tools/\nDisallow: /scripts/\nSitemap: '+DOMAIN+'/sitemap.xml\n',encoding='utf8')
    print('SEO rebuild complete:',len(products),'product pages,',len(category_paths),'category pages,',len(links),'sitemap URLs.')

if __name__=='__main__': rebuild()
