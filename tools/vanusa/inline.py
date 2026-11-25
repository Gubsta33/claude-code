# -*- coding: utf-8 -*-
"""Empacota uma pagina do site em um arquivo unico, para publicar como artifact.

CSS, JS, fontes e imagens viram data URI e os links passam a apontar para os
artifacts. O empacotador do artifact descarta o <head> e os atributos do <body>,
entao os atributos vao num script curto no inicio da pagina.
"""
import base64, os, re, sys

SITE = 'site'
OUT  = 'pub'

ART = {
    'index.html':                     'ab28e3f4-79c8-4626-adba-fd62370f7d8c',
    'sobre.html':                     '54c92864-a74d-4b1c-ba8f-9669b9ff5615',
    'beneficios-inss.html':           '2c0fd056-453d-4593-a0da-ca7d86ef930c',
    'conteudos.html':                 'c5649075-ec32-49b3-96fc-618dea981462',
    'contato.html':                   '4d757d8a-d41a-46e0-9706-b5e8c75ea78a',
    'conteudo-beneficio-negado.html': '9c202fb5-3a22-47da-97df-69b19576966d',
    'privacidade.html':               '27d476de-b2ec-4861-a5ce-fcefff6260a0',
    'cookies.html':                   '7c3b00ac-d0c3-4877-bc71-e886f8465746',
    'termos.html':                    '65a66c0c-1a93-4d87-b262-95c9460623b0',
    '404.html':                       '5551a907-e47e-4d42-9461-eeda43d62d42',
}
TIPO = {'.webp': 'image/webp', '.woff2': 'font/woff2',
        '.png': 'image/png', '.svg': 'image/svg+xml', '.ico': 'image/x-icon'}


def duri(caminho):
    ext = os.path.splitext(caminho)[1].lower()
    with open(caminho, 'rb') as f:
        return 'data:%s;base64,%s' % (TIPO[ext], base64.b64encode(f.read()).decode())


def empacota(arq):
    html = open(f'{SITE}/{arq}', encoding='utf-8').read()

    titulo = re.search(r'<title>(.*?)</title>', html, re.S).group(1)
    corpo_tag = re.search(r'<body([^>]*)>', html).group(1).strip()
    markup = html[html.index('>', html.index('<body')) + 1:html.rindex('</body>')]
    markup = re.sub(r'\s*<script src="assets/js/site\.js" defer></script>\s*', '\n', markup)

    # CSS, com fontes e imagens de fundo embutidas
    css = open(f'{SITE}/assets/css/site.css', encoding='utf-8').read()
    css = re.sub(r'url\("(\.\./[^"]+)"\)',
                 lambda m: 'url("%s")' % duri(os.path.normpath(f'{SITE}/assets/css/{m.group(1)}')),
                 css)
    # Se o empacotador puser o conteudo fora de um <body> proprio, os atributos
    # acabam no <html>. Soltar o "body" do seletor faz a regra valer nos dois casos.
    css = css.replace('body[data-', '[data-')

    # imagens do markup
    def img(m):
        cam = f'{SITE}/{m.group(1)}'
        return duri(cam) if os.path.exists(cam) else m.group(0)
    markup = re.sub(r'(assets/img/[A-Za-z0-9_.-]+\.(?:webp|png))', img, markup)

    # links internos -> artifacts
    for a, uid in ART.items():
        markup = markup.replace(f'href="{a}"', f'href="https://claude.ai/code/artifact/{uid}"')
        markup = re.sub(r'href="%s#' % re.escape(a),
                        'href="https://claude.ai/code/artifact/%s#' % uid, markup)

    js = open(f'{SITE}/assets/js/site.js', encoding='utf-8').read()

    # o empacotador do artifact descarta atributos do <body>: reposta aqui
    setter = ''
    if corpo_tag:
        pares = re.findall(r'([\w-]+)="([^"]*)"', corpo_tag)
        cmds = ''.join("d.setAttribute('%s','%s');" % p for p in pares)
        setter = ('<script>(function(){var d=document.body||'
                  'document.documentElement;%s})();</script>\n' % cmds)

    os.makedirs(OUT, exist_ok=True)
    doc = (f'<title>{titulo}</title>\n{setter}<style>\n{css}\n</style>\n'
           f'{markup.strip()}\n\n<script>\n{js}\n</script>\n')
    saida = f'{OUT}/{arq}'
    open(saida, 'w', encoding='utf-8').write(doc)
    return saida, len(doc)


if __name__ == '__main__':
    alvos = sys.argv[1:] or list(ART)
    for a in alvos:
        s, n = empacota(a)
        print(f'  {s:42} {n/1024/1024:5.2f} MB')
