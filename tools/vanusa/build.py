# -*- coding: utf-8 -*-
"""Reconstroi o site estatico a partir das paginas publicadas nos artifacts.

As paginas recuperadas trazem CSS, JS, fontes e imagens embutidos como data URI
e com os links apontando para claude.ai. Aqui tudo volta a ser arquivo proprio,
os links voltam a ser relativos e o <head> de cada pagina e reescrito.
"""
import base64, hashlib, os, re, shutil, sys

REC  = 'rec'
OUT  = 'site'
HOST = 'https://vanusaoliveiraadvocacia.com.br'

# ---------------------------------------------------------------- paginas
# slug do artifact -> arquivo, titulo, descricao
PAGES = [
    ('index', 'index.html',
     'Vanusa Oliveira Advocacia | Direito Previdenciário em Taquara, RS',
     'Advocacia especializada em Direito Previdenciário em Taquara, RS. '
     'Orientação clara sobre aposentadoria, auxílio por incapacidade, BPC/LOAS, '
     'pensão por morte e pedidos negados pelo INSS.'),
    ('sobre', 'sobre.html',
     'Sobre o escritório | Vanusa Oliveira Advocacia',
     'Conheça o escritório de Vanusa Oliveira em Taquara, RS: a trajetória da '
     'advogada, a equipe que acompanha cada atendimento e onde nos encontrar.'),
    ('beneficios-inss', 'beneficios-inss.html',
     'Benefícios do INSS | Vanusa Oliveira Advocacia',
     'Aposentadoria, auxílio por incapacidade, BPC/LOAS, pensão por morte e '
     'pedidos negados: o que cada benefício exige e quais documentos costumam '
     'ajudar na análise.'),
    ('conteudos', 'conteudos.html',
     'Conteúdos | Vanusa Oliveira Advocacia',
     'Explicações sobre benefícios do INSS em linguagem simples: aposentadoria, '
     'incapacidade, BPC/LOAS, pensão por morte e negativas do INSS.'),
    ('contato', 'contato.html',
     'Contato | Vanusa Oliveira Advocacia',
     'Fale com o escritório em Taquara, RS: WhatsApp, telefone e endereço na '
     'Galeria Comassetto. Atendimento presencial e online em todo o Brasil.'),
    ('conteudo-beneficio-negado', 'conteudo-beneficio-negado.html',
     'Benefício negado pelo INSS: o que fazer | Vanusa Oliveira Advocacia',
     'O que significa a carta de negativa do INSS, quais são os prazos e os '
     'caminhos possíveis depois de um pedido negado.'),
    ('privacidade', 'privacidade.html',
     'Política de Privacidade | Vanusa Oliveira Advocacia',
     'Como o escritório trata os dados pessoais de quem entra em contato, '
     'conforme a Lei Geral de Proteção de Dados.'),
    ('cookies', 'cookies.html',
     'Política de Cookies | Vanusa Oliveira Advocacia',
     'Quais cookies este site utiliza e como você pode controlá-los.'),
    ('termos', 'termos.html',
     'Termos de Uso | Vanusa Oliveira Advocacia',
     'Condições de uso deste site e o caráter informativo do seu conteúdo.'),
    ('404', '404.html',
     'Página não encontrada | Vanusa Oliveira Advocacia',
     'A página que você procurava não foi encontrada.'),
]
ORDEM = [p[0] for p in PAGES]

# Os atributos do <body> comandam o fundo e a abertura. O empacotador do artifact
# descarta atributos do body, entao a copia publicada vinha sem eles: aqui voltam.
#   data-hero="light"      -> a coluna lateral (.spine) escurece, para paginas de topo claro
#   data-fundo="fachada"   -> a fotografia fixa da fachada atras do conteudo, com veus
#   data-abertura="clara"  -> a home abre com a foto da recepcao atras do texto
BODY = {
    'index':                     'data-hero="light" data-fundo="fachada" data-abertura="clara"',
    'sobre':                     'data-hero="light"',
    'conteudos':                 'data-hero="light"',
    'privacidade':               'data-hero="light"',
    'cookies':                   'data-hero="light"',
    'termos':                    'data-hero="light"',
    'beneficios-inss':           '',
    'contato':                   '',
    'conteudo-beneficio-negado': '',
    '404':                       '',
}

# artifact -> arquivo local, para os links voltarem a ser relativos
ART = {
    'ab28e3f4-79c8-4626-adba-fd62370f7d8c': 'index.html',
    'N8rw73BTiVcrh6SEw1J1e3':               'index.html',
    '54c92864-a74d-4b1c-ba8f-9669b9ff5615': 'sobre.html',
    '2c0fd056-453d-4593-a0da-ca7d86ef930c': 'beneficios-inss.html',
    'c5649075-ec32-49b3-96fc-618dea981462': 'conteudos.html',
    '4d757d8a-d41a-46e0-9706-b5e8c75ea78a': 'contato.html',
    '9c202fb5-3a22-47da-97df-69b19576966d': 'conteudo-beneficio-negado.html',
    '27d476de-b2ec-4861-a5ce-fcefff6260a0': 'privacidade.html',
    '7c3b00ac-d0c3-4877-bc71-e886f8465746': 'cookies.html',
    '65a66c0c-1a93-4d87-b262-95c9460623b0': 'termos.html',
    '5551a907-e47e-4d42-9461-eeda43d62d42': '404.html',
}

# ---------------------------------------------------------------- nomes
FONTES = {'77531cf3': 'cormorant-garamond-italic-300.woff2',
          '6cc68647': 'cormorant-garamond-300-400.woff2',
          '7b36b31b': 'manrope-300-500.woff2'}

CSS_IMG = {'e408c252': 'shero-foto',
           '61ddf0d6': 'fachada-fundo',
           '06db4d09': 'fachada-fundo-mob'}

POR_CLASSE = {'brand__m': 'emblema', 'foot__logo': 'logo'}

POR_ALT = [
    ('Dra. Vanusa Oliveira em seu escrit', 'vanusa-escritorio'),
    ('Dra. Vanusa Oliveira, advogada',     'vanusa-retrato'),
    ('Fachada do escrit',                  'fachada'),
    ('Entrada do escrit',                  'entrada'),
    ('Paloma Martins',                     'equipe-paloma'),
    ('Micaela Machado',                    'equipe-micaela'),
    ('Ana Clara Martins',                  'equipe-anaclara'),
    ('Casal em idade de aposentadoria',    'beneficio-aposentadoria'),
    ('Homem com dor no ombro',             'beneficio-incapacidade'),
    ('Duas mulheres recebendo explica',    'beneficio-bpc'),
    ('Casal em atendimento sobre pens',    'beneficio-pensao'),
    ('Casal recebendo orienta',            'beneficio-negativa'),
    ('Documento de identidade, CPF',       'doc-sempre-uteis'),
    ('Extrato de contribui',               'doc-aposentadoria'),
    ('Relat',                              'doc-saude'),
    ('Cadastro ',                          'doc-bpc'),
    ('Certid',                             'doc-familia'),
    ('Carta de decis',                     'doc-negativa'),
]

RE_IMG  = re.compile(r'data:image/webp;base64,([A-Za-z0-9+/=]+)')
RE_FONT = re.compile(r'data:font/woff2;base64,([A-Za-z0-9+/=]+)')


def h8(b64):
    return hashlib.sha256(b64.encode()).hexdigest()[:8]


def corpo(slug):
    s = open(os.path.join(REC, slug, 'index.html'), encoding='utf-8').read()
    return s[s.index('<body') + 6:]


def partes(slug):
    b = corpo(slug)
    css = b[b.index('<style>') + 7:b.index('</style>')]
    i, j = b.rindex('<script>'), b.rindex('</script>')
    markup = b[b.index('</style>') + 8:i]
    return css, markup, b[i + 8:j]


# ================================================================ 1. assets
os.makedirs(f'{OUT}/assets/css', exist_ok=True)
os.makedirs(f'{OUT}/assets/js', exist_ok=True)
os.makedirs(f'{OUT}/assets/fonts', exist_ok=True)
os.makedirs(f'{OUT}/assets/img', exist_ok=True)

gravados = {}          # hash -> nome do arquivo de imagem


def grava_img(b64, nome):
    """Escreve a imagem uma vez e devolve o nome do arquivo."""
    k = h8(b64)
    if k in gravados:
        return gravados[k]
    arq = f'{nome}.webp'
    n = 2
    while arq in gravados.values():
        arq = f'{nome}-{n}.webp'
        n += 1
    with open(f'{OUT}/assets/img/{arq}', 'wb') as fh:
        fh.write(base64.b64decode(b64))
    gravados[k] = arq
    return arq


# --- CSS: o do index tem tudo, mais o ajuste da grade da equipe (3 pessoas)
css, _, js = partes('index')
alvo = '@media (min-width:980px){.team{grid-template-columns:repeat(4,1fr)}}'
assert css.count(alvo) == 1
css = css.replace(alvo, alvo.replace('repeat(4', 'repeat(3'))

# confere que nenhuma pagina tem CSS que o compartilhado nao cubra
base_css = partes('contato')[0]
logo_css = partes('beneficios-inss')[0]
sobre_css = partes('sobre')[0]
for nome, outro in (('contato', base_css), ('beneficios-inss', logo_css), ('sobre', sobre_css)):
    falta = [l for l in outro.split('\n') if l.strip() and l not in css]
    if falta:
        print(f'  ! {nome}: {len(falta)} linhas de CSS fora do compartilhado', file=sys.stderr)
        for l in falta[:6]:
            print('    ', l[:120], file=sys.stderr)

# fontes para fora do CSS
def _font(m):
    arq = FONTES[h8(m.group(1))]
    p = f'{OUT}/assets/fonts/{arq}'
    if not os.path.exists(p):
        open(p, 'wb').write(base64.b64decode(m.group(1)))
    return f'../fonts/{arq}'
css = RE_FONT.sub(_font, css)

# imagens de fundo para fora do CSS
def _cssimg(m):
    return '../img/' + grava_img(m.group(1), CSS_IMG[h8(m.group(1))])
css = RE_IMG.sub(_cssimg, css)

open(f'{OUT}/assets/css/site.css', 'w', encoding='utf-8').write(css.strip() + '\n')
open(f'{OUT}/assets/js/site.js', 'w', encoding='utf-8').write(js.strip() + '\n')


# ================================================================ 2. imagens
def nome_base(tag):
    cls = re.search(r'class="([^"]*)"', tag)
    if cls:
        for c in cls.group(1).split():
            if c in POR_CLASSE:
                return POR_CLASSE[c]
    alt = re.search(r'alt="([^"]*)"', tag)
    if alt and alt.group(1).strip():
        a = alt.group(1)
        for pref, nome in POR_ALT:
            if a.startswith(pref):
                return nome
        if a.startswith('Imagem ilustrativa'):      # conteudos reaproveita
            for chave, nome in (('aposentadoria', 'beneficio-aposentadoria'),
                                ('afastamento', 'beneficio-incapacidade'),
                                ('bpc', 'beneficio-bpc'),
                                ('pens', 'beneficio-pensao'),
                                ('negado', 'beneficio-negativa')):
                if chave in a.lower():
                    return nome
    w = re.search(r'\bwidth="(\d+)"', tag)
    if w and w.group(1) == '1285':
        return 'recepcao'
    return 'img'


def troca_imgs(markup):
    """Substitui src/srcset embutidos por caminhos de arquivo."""
    def um(m):
        tag = m.group(0)
        base = nome_base(tag)
        hsrc = None
        s = RE_IMG.search(tag)
        if s:
            hsrc = h8(s.group(1))

        def alvo(b64):
            k = h8(b64)
            if k in gravados:
                return 'assets/img/' + gravados[k]
            if k == hsrc:
                return 'assets/img/' + grava_img(b64, base)
            w = larguras.get(k)
            return 'assets/img/' + grava_img(b64, f'{base}-{w}' if w else base)

        larguras = {}
        ss = re.search(r'srcset="([^"]*)"', tag)
        if ss:
            for mm in re.finditer(r'data:image/webp;base64,([A-Za-z0-9+/=]+)\s+(\d+)w', ss.group(1)):
                larguras[h8(mm.group(1))] = mm.group(2)
        return RE_IMG.sub(lambda mm: alvo(mm.group(1)), tag)
    return re.sub(r'<img\b[^>]*>', um, markup)


# ================================================================ 3. paginas
LOGO_HDR_DE = ('''      <span class="brand__a">Vanusa Oliveira</span>
      <span class="brand__b">Advocacia</span>
    </a>''')
LOGO_HDR_PARA = ('''      <img class="brand__m" src="assets/img/emblema.webp" alt="" width="112" height="112" decoding="async">
      <span class="brand__t">
        <span class="brand__a">Vanusa Oliveira</span>
        <span class="brand__b">Advocacia</span>
      </span>
    </a>''')
LOGO_FOOT_DE = ('''<div class="foot__brand">
        <span class="brand__a">Vanusa Oliveira</span>
        <span class="brand__b">Advocacia</span>''')
LOGO_FOOT_PARA = ('''<div class="foot__brand">
        <img class="foot__logo" src="assets/img/logo.webp"
             alt="Vanusa Oliveira Advocacia" width="584" height="329" loading="lazy" decoding="async">''')

JSONLD = '''{
  "@context": "https://schema.org",
  "@type": "LegalService",
  "@id": "%(host)s/#escritorio",
  "name": "Vanusa Oliveira Advocacia",
  "legalName": "Vanusa de Souza Oliveira Sociedade Individual de Advocacia",
  "url": "%(host)s/",
  "image": "%(host)s/assets/img/fachada.webp",
  "logo": "%(host)s/assets/img/logo.webp",
  "telephone": "+55-51-99688-1523",
  "priceRange": "$$",
  "areaServed": { "@type": "Country", "name": "Brasil" },
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "R. Júlio de Castilhos, 2579, Sala 110, térreo, Galeria Comassetto",
    "addressLocality": "Taquara",
    "addressRegion": "RS",
    "postalCode": "95600-080",
    "addressCountry": "BR"
  },
  "founder": {
    "@type": "Person",
    "name": "Vanusa de Souza Oliveira",
    "jobTitle": "Advogada",
    "identifier": "OAB/RS 107.982"
  },
  "knowsAbout": [
    "Direito Previdenciário", "Aposentadoria", "Auxílio por incapacidade",
    "BPC/LOAS", "Pensão por morte", "Revisão de benefício do INSS"
  ],
  "knowsLanguage": "pt-BR"
}''' % {'host': HOST}

HEAD = '''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(canon)s">
<meta name="author" content="Vanusa Oliveira Advocacia">
<meta name="theme-color" content="#0B0B0B">
<meta name="robots" content="%(robots)s">

<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Vanusa Oliveira Advocacia">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(canon)s">
<meta property="og:image" content="%(host)s/assets/img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">

<link rel="icon" href="favicon.ico" sizes="48x48 32x32 16x16">
<link rel="apple-touch-icon" href="assets/img/icone-180.png">
<link rel="manifest" href="manifest.webmanifest">

<link rel="preload" href="assets/fonts/cormorant-garamond-300-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/manrope-300-500.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/site.css">
%(ld)s</head>
'''


def rel_links(t):
    for uid, arq in ART.items():
        t = t.replace(f'https://claude.ai/code/artifact/{uid}', arq)
        t = t.replace(f'https://claude.ai/artifact/{uid}', arq)
    return t


for slug, arq, title, desc in PAGES:
    css_p, markup, js_p = partes(slug)
    markup = troca_imgs(markup)
    markup = rel_links(markup)

    if 'brand__m' not in markup:                      # paginas que ficaram sem a logo
        assert markup.count(LOGO_FOOT_DE) == 1, (slug, 'rodape')
        markup = markup.replace(LOGO_FOOT_DE, LOGO_FOOT_PARA)
        assert markup.count(LOGO_HDR_DE) == 1, (slug, 'cabecalho')
        markup = markup.replace(LOGO_HDR_DE, LOGO_HDR_PARA)

    canon = f'{HOST}/' if arq == 'index.html' else f'{HOST}/{arq}'
    head = HEAD % {
        'title': title, 'desc': desc, 'canon': canon, 'host': HOST,
        'robots': 'noindex,follow' if slug == '404' else 'index,follow',
        'ld': f'\n<script type="application/ld+json">\n{JSONLD}\n</script>\n' if slug == 'index' else '',
    }
    at = BODY[slug]
    doc = head + '<body' + (' ' + at if at else '') + '>\n' + markup.strip() + \
          '\n\n<script src="assets/js/site.js" defer></script>\n</body>\n</html>\n'
    open(f'{OUT}/{arq}', 'w', encoding='utf-8').write(doc)
    print(f'  {arq:34} {len(doc)/1024:7.1f} KB')

print(f'\n  CSS {os.path.getsize(f"{OUT}/assets/css/site.css")/1024:.1f} KB · '
      f'JS {os.path.getsize(f"{OUT}/assets/js/site.js")/1024:.1f} KB · '
      f'{len(gravados)} imagens · {len(os.listdir(f"{OUT}/assets/fonts"))} fontes')


# ================================================================ 4. extras
open(f'{OUT}/manifest.webmanifest', 'w', encoding='utf-8').write("""{
  "name": "Vanusa Oliveira Advocacia",
  "short_name": "Vanusa Oliveira",
  "description": "Advocacia especializada em Direito Previdenciário em Taquara, RS.",
  "lang": "pt-BR",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "background_color": "#0B0B0B",
  "theme_color": "#0B0B0B",
  "icons": [
    { "src": "/assets/img/icone-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/assets/img/icone-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/assets/img/icone-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
""")

PRIOR = {'index.html': ('1.0', 'monthly'), 'beneficios-inss.html': ('0.9', 'monthly'),
         'sobre.html': ('0.8', 'yearly'), 'contato.html': ('0.8', 'yearly'),
         'conteudos.html': ('0.7', 'monthly'), 'conteudo-beneficio-negado.html': ('0.6', 'yearly')}
hoje = __import__('datetime').date.today().isoformat()
linhas = []
for slug, arq, *_ in PAGES:
    if slug == '404':
        continue
    loc = f'{HOST}/' if arq == 'index.html' else f'{HOST}/{arq}'
    pr, freq = PRIOR.get(arq, ('0.3', 'yearly'))
    linhas.append(f'  <url>\n    <loc>{loc}</loc>\n    <lastmod>{hoje}</lastmod>\n'
                  f'    <changefreq>{freq}</changefreq>\n    <priority>{pr}</priority>\n  </url>')
open(f'{OUT}/sitemap.xml', 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + '\n'.join(linhas) + '\n</urlset>\n')

open(f'{OUT}/robots.txt', 'w', encoding='utf-8').write(
    f'User-agent: *\nAllow: /\n\nSitemap: {HOST}/sitemap.xml\n')

# Netlify: a pagina 404 e servida automaticamente; cabecalhos de cache para os assets
open(f'{OUT}/_headers', 'w', encoding='utf-8').write(
    '/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n'
    '/*.html\n  Cache-Control: public, max-age=0, must-revalidate\n')

print('  manifest, sitemap, robots, _headers')
