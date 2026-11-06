#!/usr/bin/env python3
"""Gerador do site CAOS.

Lê /content (site.json e portfolio.json) e escreve as páginas HTML na raiz.
Roda sem instalar nada (Python 3.8+):

    python3 tools/build.py
"""
import json, os, html, hashlib, datetime
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

def load(name):
    return json.load(open(os.path.join('content', name), encoding='utf8'))

SITE = load('site.json')
PORT = load('portfolio.json')
WORKS = PORT['trabalhos']
BASE = SITE['url'].rstrip('/')
HAS_HERO_VIDEO = os.path.exists('assets/video/hero.mp4')
ASSET_V = str(int(os.path.getmtime('assets/css/style.css'))) if os.path.exists('assets/css/style.css') else '1'

def esc(s): return html.escape(str(s if s is not None else ''), quote=True)
def u(p):
    if not p: return ''
    return p if p.startswith(('http', '/', '#', 'mailto:', 'tel:')) else '/' + p

# ------------------------------------------------------------------ WhatsApp
MSG = {
    'geral': 'Olá, CAOS! Vim pelo site e gostaria de conversar sobre um projeto.',
    'eventos': 'Olá, CAOS! Vim pelo site e gostaria de um orçamento de audiovisual para o meu evento.',
    'casamentos': 'Olá, CAOS! Vim pelo site e gostaria de consultar a disponibilidade da minha data de casamento.',
    'marketing': 'Olá, CAOS! Vim pelo site e gostaria de uma proposta de marketing para a minha empresa.',
}
def wa(key='geral', num=None):
    return f"https://wa.me/{num or SITE['whatsapp_principal']}?text={quote(MSG.get(key, key))}"

# ------------------------------------------------------------------ ícones
def svg(body, vb='0 0 24 24', cls='ico'):
    return f'<svg class="{cls}" viewBox="{vb}" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>'
ICON = {
    'camera': svg('<rect x="2.5" y="6" width="14" height="12" rx="2"/><path d="M16.5 10.5 21.5 8v8l-5-2.5"/>'),
    'rings': svg('<circle cx="9" cy="12" r="5.5"/><circle cx="15" cy="12" r="5.5"/>'),
    'chart': svg('<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 6-7"/><path d="M16 7h4v4"/>'),
    'screen': svg('<rect x="3" y="4" width="18" height="12" rx="1.5"/><path d="M8 21l4-5 4 5"/>'),
    'chat': svg('<path d="M4 5h16v11H11l-5 4v-4H4Z"/>'),
    'arrow': svg('<path d="M5 12h14M13 6l6 6-6 6"/>'),
    'arrow-up': svg('<path d="M7 17 17 7M8 7h9v9"/>'),
    'play': svg('<path d="M7 4.5v15l13-7.5Z" fill="currentColor" stroke="none"/>'),
    'close': svg('<path d="M5 5l14 14M19 5 5 19"/>'),
    'wa': svg('<path d="M20 11.5A8 8 0 0 1 8.2 18.6L4 20l1.4-4.1A8 8 0 1 1 20 11.5Z"/><path d="M9 8.5c.3 2.6 2.700 5 6 6l1.2-1.4-2-1-.8.8c-.8-.3-1.800-1.300-2.200-2.200l.8-.8-1-2Z" fill="currentColor" stroke="none"/>'),
    'ig': svg('<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17" cy="7" r=".8" fill="currentColor"/>'),
    'mail': svg('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 7 8.500 6L20.500 7"/>'),
    'pin': svg('<path d="M12 21s7-6.200 7-11.500A7 7 0 0 0 5 9.500C5 14.800 12 21 12 21Z"/><circle cx="12" cy="9.500" r="2.500"/>'),
}
SIMBOLO = '<img src="/assets/img/brand/simbolo.svg" alt="" class="sym" width="100" height="100" loading="lazy">'

# ------------------------------------------------------------------ componentes
def btn(label, href, kind='solid', track='', extra='', icon='arrow'):
    t = f' data-track="{track}"' if track else ''
    ext = ' target="_blank" rel="noopener"' if href.startswith('https://wa.me') else ''
    return (f'<a class="btn btn--{kind}" href="{esc(href)}"{ext}{t} data-magnetic {extra}>'
            f'<span class="btn__t">{label}</span><span class="btn__i">{ICON[icon]}</span></a>')

def variant(w): return int(hashlib.md5(w['id'].encode()).hexdigest(), 16) % 5

def frame(w, cls=''):
    tipo = w.get('tipo', 'foto')
    if w.get('capa'):
        inner = f'<img src="{esc(u(w["capa"]))}" alt="{esc(w["titulo"])} · {esc(w["cliente"])}" loading="lazy" decoding="async">'
    else:
        inner = f'<span class="frame__ph">{SIMBOLO}</span>'
    label = {'video': 'VÍDEO', 'foto': 'FOTO', 'instagram': 'INSTAGRAM'}.get(tipo, 'FOTO')
    play = f'<span class="frame__play">{ICON["play"]}</span>' if tipo == 'video' else ''
    rec = f'<span class="frame__rec"><b></b>{label}</span>'
    return (f'<div class="frame {cls}" data-v="{variant(w)}" data-tipo="{tipo}">{inner}'
            f'<i class="fc tl"></i><i class="fc tr"></i><i class="fc bl"></i><i class="fc br"></i>{rec}{play}</div>')

def work_card(w, show_front=False):
    front = f'<span class="chip-mini">{w["frente"]}</span>' if show_front else ''
    return (f'<article class="work" data-tipo="{w["tipo"]}" data-frente="{w["frente"]}">'
            f'<button class="work__open" type="button" data-open="{esc(w["id"])}" data-cursor="Ver" aria-label="Abrir {esc(w["titulo"])}">'
            f'{frame(w)}</button>'
            f'<div class="work__meta"><span class="lbl">{esc(w["cliente"])}</span>{front}'
            f'<h3>{esc(w["titulo"])}</h3><p>{esc(w["servico"])}</p></div></article>')

def sect_head(label, title, extra_cls=''):
    return (f'<div class="shead {extra_cls}"><span class="lbl" data-reveal>{label}</span>'
            f'<h2 class="h2" data-split>{title}</h2></div>')

# ------------------------------------------------------------------ layout
NAV = [('/', 'Home', 'home'), ('/eventos/', 'Audiovisual para Eventos', 'eventos'),
       ('/casamentos/', 'Audiovisual para Casamentos', 'casamentos'),
       ('/marketing/', 'Marketing CAOS', 'marketing'), ('/contato/', 'Contato', 'contato')]
FRONT_LABEL = {'eventos': 'Eventos', 'casamentos': 'Casamentos', 'marketing': 'Marketing'}

def header(front):
    logo = 'logo-preto.png' if front == 'casamentos' else 'logo-nevoa.png'
    lab = f'<span class="hdr__front"><i></i>{FRONT_LABEL[front]}</span>' if front in FRONT_LABEL else ''
    items = ''.join(f'<a href="{h}"{" aria-current=page" if k == front else ""} data-nav>{t}</a>' for h, t, k in NAV)
    cta = btn('Orçamento', wa(front if front in MSG else 'geral'), 'solid', f'wa_header_{front}', 'data-cursor="WhatsApp"', 'wa')
    return f'''<header class="hdr" data-hdr>
  <a class="hdr__logo" href="/" aria-label="CAOS · página inicial"><img src="/assets/img/brand/{logo}" alt="CAOS" width="124" height="28"></a>{lab}
  <nav class="hdr__nav" aria-label="Principal">{items}</nav>
  <div class="hdr__cta">{cta}</div>
  <button class="burger" type="button" aria-label="Abrir menu" aria-expanded="false" data-burger><span></span><span></span></button>
</header>
<div class="menu" data-menu aria-hidden="true">
  <nav aria-label="Menu">{''.join(f'<a href="{h}" data-nav><small>0{i}</small><span>{t}</span></a>' for i, (h, t, k) in enumerate(NAV))}</nav>
  <div class="menu__foot"><a href="{wa('geral')}" target="_blank" rel="noopener">WhatsApp {SITE['whatsapp_principal_formatado']}</a><a href="mailto:{SITE['email']}">{SITE['email']}</a></div>
</div>'''

def footer(front):
    cta_key = front if front in MSG else 'geral'
    return f'''<footer class="ftr sec sec--dark">
  <div class="ftr__marquee" aria-hidden="true"><div class="marq" data-marq><span>As melhores ideias surgem do CAOS.&nbsp;</span><span>As melhores ideias surgem do CAOS.&nbsp;</span><span>As melhores ideias surgem do CAOS.&nbsp;</span><span>As melhores ideias surgem do CAOS.&nbsp;</span></div></div>
  <div class="wrap ftr__grid">
    <div class="ftr__brand">
      <img src="/assets/img/brand/logo-nevoa.png" alt="CAOS Produções Multimídia" width="220" height="50" loading="lazy">
      <p><strong>CAOS Produções Multimídia</strong><br>Marketing, conteúdo e audiovisual.<br>Diamantina — Minas Gerais</p>
      <p class="ftr__slogan">As melhores ideias surgem do CAOS.</p>
    </div>
    <nav class="ftr__col" aria-label="Rodapé"><span class="lbl">Páginas</span>{''.join(f'<a href="{h}">{t}</a>' for h, t, k in NAV)}</nav>
    <div class="ftr__col"><span class="lbl">Fale com a gente</span>
      <a href="{wa(cta_key)}" target="_blank" rel="noopener" data-track="wa_footer">{ICON['wa']} {SITE['whatsapp_principal_formatado']}</a>
      <a href="{wa(cta_key, SITE['whatsapp_secundario'])}" target="_blank" rel="noopener" data-track="wa_footer_2">{ICON['wa']} {SITE['whatsapp_secundario_formatado']}</a>
      <a href="mailto:{SITE['email']}">{ICON['mail']} {SITE['email']}</a>
      <a href="{SITE['instagram_url']}" target="_blank" rel="noopener">{ICON['ig']} @{SITE['instagram']}</a>
    </div>
  </div>
  <div class="wrap ftr__base"><span>© {datetime.date.today().year} CAOS Produções Multimídia</span><span>Sediados em Diamantina/MG</span><span class="rec-line"><b></b> REC <time data-timecode>00:00:00:00</time></span></div>
</footer>'''

def jsonld(path, name, desc, front):
    org = {"@context": "https://schema.org", "@type": "ProfessionalService", "name": SITE['nome'], "url": BASE,
           "image": BASE + "/assets/img/og-image.jpg", "logo": BASE + "/assets/img/brand/favicon.svg",
           "telephone": "+" + SITE['whatsapp_principal'], "email": SITE['email'],
           "address": {"@type": "PostalAddress", "streetAddress": "Rua Direita, 180", "addressLocality": "Diamantina",
                       "addressRegion": "MG", "addressCountry": "BR"},
           "areaServed": "Diamantina e região, Minas Gerais", "sameAs": [SITE['instagram_url']]}
    out = [org]
    if front in FRONT_LABEL:
        out.append({"@context": "https://schema.org", "@type": "Service", "name": name, "description": desc,
                    "provider": {"@type": "ProfessionalService", "name": SITE['nome']}, "areaServed": "Diamantina, MG",
                    "url": BASE + path})
    return ''.join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>' for o in out)

def page(path, front, title, desc, body, extra_head=''):
    analytics = f'<script>window.__CAOS_ANALYTICS={json.dumps({"ga4": SITE["ga4"], "pixel": SITE["pixel"]})};</script>'
    works_json = json.dumps({w['id']: w for w in WORKS}, ensure_ascii=False).replace('</', '<\\/')
    return f'''<!doctype html>
<html lang="pt-BR" data-front="{front}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{BASE}{path}">
<meta name="theme-color" content="#0D0C0B">
<meta property="og:type" content="website"><meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="CAOS Produções Multimídia">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{BASE}{path}"><meta property="og:image" content="{BASE}/assets/img/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/img/brand/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/Archivo-100-900-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/fonts/fonts.css">
<link rel="stylesheet" href="/assets/css/style.css?v={ASSET_V}">
<script>document.documentElement.classList.add('js');try{{if(sessionStorage.getItem('caosNav')==='1')document.documentElement.classList.add('is-entering')}}catch(e){{}}</script>
{jsonld(path, FRONT_LABEL.get(front, ''), desc, front)}
{extra_head}
</head>
<body data-front="{front}">
<a class="skip" href="#conteudo">Ir para o conteúdo</a>
<div class="curtain" aria-hidden="true"><i></i><i></i></div>
<div class="cursor" aria-hidden="true"><span></span><em></em></div>
<div class="progress" aria-hidden="true"><i></i></div>
{header(front)}
<main id="conteudo">
{body}
</main>
{footer(front)}
<a class="fab" href="{wa(front if front in MSG else 'geral')}" target="_blank" rel="noopener" data-track="wa_fab" aria-label="Pedir orçamento pelo WhatsApp">{ICON['wa']}<span>Orçamento</span></a>
<div class="lightbox" data-lightbox hidden role="dialog" aria-modal="true" aria-label="Visualizar trabalho">
  <button class="lightbox__x" type="button" data-close aria-label="Fechar">{ICON['close']}</button>
  <div class="lightbox__stage" data-stage></div>
  <div class="lightbox__cap" data-cap></div>
  <button class="lightbox__nav prev" type="button" data-prev aria-label="Anterior">{ICON['arrow']}</button>
  <button class="lightbox__nav next" type="button" data-next aria-label="Próximo">{ICON['arrow']}</button>
</div>
<script type="application/json" id="works-data">{works_json}</script>
{analytics}
<script src="/assets/js/lenis.min.js" defer></script>
<script src="/assets/js/app.js?v={ASSET_V}" defer></script>
</body>
</html>'''

# ------------------------------------------------------------------ blocos reutilizáveis
def viewfinder(extra=''):
    return f'''<div class="vf" aria-hidden="true">
  <i class="vf__c tl"></i><i class="vf__c tr"></i><i class="vf__c bl"></i><i class="vf__c br"></i>
  <span class="vf__rec"><b></b>REC</span><time class="vf__tc" data-timecode>00:00:00:00</time>
  <span class="vf__meta l">ISO 800 · 1/50 · F2.8</span><span class="vf__meta r">4K · 24 FPS</span>
  <i class="vf__cross"></i>{extra}</div>'''

def steps(items, cls=''):
    lis = ''.join(f'''<li class="step" data-step><span class="step__n">{i:02d}</span><div><h3>{t}</h3><p>{d}</p></div></li>''' for i, (t, d) in enumerate(items, 1))
    return f'<ol class="steps {cls}" data-steps><i class="steps__line"><b></b></i>{lis}</ol>'

def orb(label, href, track):
    ring = (label.upper() + ' • ') * 3
    return (f'<a class="orb" href="{esc(href)}" target="_blank" rel="noopener" data-track="{track}" data-magnetic data-cursor="WhatsApp">'
            f'<svg viewBox="0 0 200 200" class="orb__ring" aria-hidden="true"><defs><path id="orbp" d="M100,100 m-80,0 a80,80 0 1,1 160,0 a80,80 0 1,1 -160,0"/></defs>'
            f'<text><textPath href="#orbp" textLength="500">{ring}</textPath></text></svg>'
            f'<span class="orb__c">{ICON["arrow-up"]}</span><span class="sr">{label}</span></a>')

def final_cta(front, title, text, button, with_form=''):
    key = front if front in MSG else 'geral'
    return f'''<section class="sec sec--laranja cta" data-sec>
  <div class="wrap cta__in">
    <div class="cta__txt">
      <span class="lbl lbl--k" data-reveal>Contato</span>
      <h2 class="h1 cta__h" data-split>{title}</h2>
      <p class="lead" data-reveal>{text}</p>
      {with_form}
      <div data-reveal>{btn(button, wa(key), 'dark', f'wa_cta_{front}', 'data-cursor="WhatsApp"', 'wa')}</div>
    </div>
    {orb('Vamos conversar', wa(key), f'wa_orb_{front}')}
  </div>
  <i class="dobra dobra--k"></i>
</section>'''

def hidden_form(name):
    return f'<input type="hidden" name="form-name" value="{name}"><p class="sr"><label>Não preencha <input name="bot-field"></label></p>'

def mini_form(name, key, fields, button):
    """Formulário curto que abre o WhatsApp com a mensagem já preenchida e registra o contato no Netlify."""
    inputs = ''.join(fields)
    return f'''<form class="mform js-form" name="{name}" method="POST" action="/contato/obrigado/" data-netlify="true" netlify-honeypot="bot-field" data-wa="{key}" data-track="form_{name}">
  {hidden_form(name)}
  <div class="mform__row">{inputs}</div>
  <button class="btn btn--dark" type="submit" data-magnetic><span class="btn__t">{button}</span><span class="btn__i">{ICON['wa']}</span></button>
</form>'''

def field(label, name, kind='text', ph='', req=False, extra=''):
    r = ' required' if req else ''
    if kind == 'textarea':
        el = f'<textarea name="{name}" rows="3" placeholder="{ph}"{r}></textarea>'
    else:
        el = f'<input type="{kind}" name="{name}" placeholder="{ph}"{r} {extra}>'
    return f'<label class="fld"><span>{label}</span>{el}</label>'

def works_of(front, only_featured=False):
    ws = [w for w in WORKS if w['frente'] == front]
    return [w for w in ws if w.get('destaque')] if only_featured else ws

def portfolio_grid(front, title, label='Portfólio', note=''):
    theme = 'sec--areia' if front == 'casamentos' else 'sec--dark'
    ws = works_of(front)
    tipos = sorted({w['tipo'] for w in ws})
    names = {'video': 'Vídeos', 'foto': 'Fotos', 'instagram': 'Instagram'}
    chips = '<button class="chip is-on" data-filter="*" type="button">Todos</button>' + ''.join(
        f'<button class="chip" data-filter="{t}" type="button">{names[t]}</button>' for t in tipos) if len(tipos) > 1 else ''
    return f'''<section class="sec {theme} sec--portfolio" data-sec id="portfolio">
  <div class="wrap">
    <div class="shead shead--row">{sect_head(label, title)}<div class="chips" data-chips>{chips}</div></div>
    {f'<p class="lead sub" data-reveal>{note}</p>' if note else ''}
    <div class="grid" data-grid>{''.join(work_card(w) for w in ws)}</div>
  </div>
</section>'''

# ------------------------------------------------------------------ HOME
def home():
    feats = [w for w in WORKS if w.get('destaque')] or WORKS
    pool = (WORKS * 3)[:9]
    cols = ''
    for c in range(3):
        cards = ''.join(f'<div class="hcol__i">{frame(w)}</div>' for w in (pool[c * 3:c * 3 + 3]) * 2)
        cols += f'<div class="hcol hcol--{c}"><div class="hcol__t">{cards}</div></div>'
    bg = ('<video class="hero__video" autoplay muted loop playsinline preload="metadata"><source src="/assets/video/hero.mp4" type="video/mp4"></video>'
          if HAS_HERO_VIDEO else f'<div class="hero__cols" aria-hidden="true">{cols}</div>')
    marquee = ''.join(f'<span>{t}</span><i></i>' for t in ['Estratégia', 'Criatividade', 'Produção audiovisual', 'Marketing', 'Eventos', 'Casamentos', 'Conteúdo', 'Tráfego pago'] * 2)
    track = ''.join(
        f'''<article class="hs__card" data-cursor="Ver">
  <button type="button" class="work__open" data-open="{esc(w['id'])}" aria-label="Abrir {esc(w['titulo'])}">{frame(w)}</button>
  <div class="hs__meta"><span class="lbl">{esc(w['cliente'])} · {esc(w['servico'])}</span><h3>{esc(w['titulo'])}</h3>
  <a class="tlink" href="/{w['frente']}/">Ver página de {FRONT_LABEL[w['frente']].lower()} {ICON['arrow']}</a></div></article>''' for w in feats[:8])
    clientes = PORT.get('clientes') or []
    deps = PORT.get('depoimentos') or []
    quem = ''
    if clientes or deps:
        logos = ''.join(f'<li><img src="{esc(u(c["logo"]))}" alt="{esc(c["nome"])}" loading="lazy"></li>' for c in clientes if c.get('logo'))
        quotes = ''.join(f'<blockquote class="quote"><p>{esc(d["texto"])}</p><footer>{esc(d["autor"])} <span>{esc(d.get("detalhe", ""))}</span></footer></blockquote>' for d in deps)
        quem = f'''<section class="sec sec--nevoa" data-sec><div class="wrap">{sect_head('Clientes', 'Quem confia na CAOS.')}
        {f'<ul class="logos">{logos}</ul>' if logos else ''}<div class="quotes">{quotes}</div></div></section>'''
    body = f'''
<section class="hero sec sec--dark" data-sec data-hero>
  {bg}
  <div class="hero__veil"></div>
  <canvas class="hero__canvas" data-chaos-canvas aria-hidden="true"></canvas>
  {viewfinder()}
  <div class="wrap hero__in">
    <span class="lbl" data-reveal><i class="dot"></i> Marketing · Audiovisual · Diamantina–MG</span>
    <h1 class="hero__h" data-chaos aria-label="As melhores ideias surgem do CAOS.">As melhores ideias surgem do <span class="hl">CAOS.</span></h1>
    <p class="lead hero__p" data-reveal>Estratégia, criatividade e produção audiovisual para marcas que querem crescer e histórias que merecem ser registradas. De Diamantina para o seu próximo projeto.</p>
    <div class="hero__btns" data-reveal>{btn('Conheça nossos trabalhos', '#portfolio', 'solid', 'hero_trabalhos')}{btn('Fale com a CAOS', wa('geral'), 'line', 'hero_wa', 'data-cursor="WhatsApp"', 'wa')}</div>
  </div>
  <a class="hero__scroll" href="#portfolio" aria-label="Rolar para os trabalhos"><span>Scroll</span><i></i></a>
</section>

<div class="strip" aria-hidden="true"><div class="marq" data-marq data-tilt-skew>{marquee}</div></div>

<section class="sec sec--dark hs" data-sec id="portfolio" data-hs>
  <div class="hs__pin">
    <div class="wrap hs__head">{sect_head('Portfólio em destaque', 'Veja o que acontece quando a ideia ganha forma.')}
      <p class="lead" data-reveal>Vídeos, campanhas e conteúdos que traduzem a identidade de cada projeto. Conheça alguns dos trabalhos que produzimos para empresas, eventos e casais.</p></div>
    <div class="hs__track" data-hs-track>{track}<div class="hs__end"><a class="btn btn--solid" href="/contato/" data-magnetic><span class="btn__t">Quero um trabalho assim</span><span class="btn__i">{ICON['arrow']}</span></a></div></div>
    <div class="hs__bar" aria-hidden="true"><i data-hs-bar></i></div>
  </div>
</section>

<section class="sec sec--nevoa about" data-sec id="sobre">
  <div class="wrap about__in">
    <div>
      <span class="lbl lbl--b" data-reveal>Sobre a CAOS</span>
      <h2 class="h1 about__h" data-split>Criatividade para pensar. Estrutura para realizar.</h2>
    </div>
    <div class="about__txt">
      <p class="scrub" data-scrub>Somos a CAOS Produções Multimídia, uma empresa de marketing e produção audiovisual sediada em Diamantina, Minas Gerais. Reunimos planejamento, criação e produção para cuidar de cada projeto, da primeira ideia à entrega.</p>
      <p data-reveal>Trabalhamos com marketing digital, gestão de redes sociais, tráfego pago, criação de sites e produção de fotos e vídeos para empresas, eventos e casamentos.</p>
      <p data-reveal>Nosso trabalho começa entendendo o que você precisa comunicar. A partir daí, construímos a estratégia e os conteúdos para fazer essa mensagem chegar ao público.</p>
      <ul class="pills" data-reveal><li>Planejamento</li><li>Criação</li><li>Produção</li></ul>
    </div>
  </div>
  <div class="about__sym" aria-hidden="true" data-speed="-0.15">{SIMBOLO}</div>
</section>

<section class="areas" data-areas id="areas">
  <div class="areas__intro sec sec--dark" data-sec><div class="wrap">{sect_head('Nossas áreas de atuação', 'Três frentes. Uma só marca.')}</div></div>

  <article class="panel panel--eventos" data-panel>
    <div class="wrap panel__in">
      <div class="panel__txt">
        <span class="lbl"><i class="dot"></i> 01 · Eventos</span>
        <h3 class="h1" data-split>Audiovisual para Eventos</h3>
        <p class="lead">A atmosfera, os encontros e os momentos que fazem seu evento acontecer, registrados em fotos, vídeos e conteúdos para as redes sociais.</p>
        {btn('Conheça a cobertura de eventos', '/eventos/', 'solid', 'area_eventos')}
      </div>
      <a class="panel__vis" href="/eventos/" data-cursor="Abrir" aria-label="Audiovisual para eventos">{frame(works_of('eventos')[0] if works_of('eventos') else WORKS[0], 'frame--big')}{viewfinder()}</a>
    </div>
  </article>

  <article class="panel panel--casamentos" data-panel>
    <div class="wrap panel__in">
      <div class="panel__txt">
        <span class="lbl lbl--b">02 · Casamentos</span>
        <h3 class="h1" data-split>Audiovisual para Casamentos</h3>
        <p class="lead">Filmes e fotografias que preservam a história do casal, os detalhes e a emoção de viver esse dia.</p>
        {btn('Conheça nossos casamentos', '/casamentos/', 'dark', 'area_casamentos')}
      </div>
      <a class="panel__vis panel__vis--serif" href="/casamentos/" data-cursor="Abrir" aria-label="Audiovisual para casamentos">{frame(works_of('casamentos')[0] if works_of('casamentos') else WORKS[0], 'frame--big frame--arch')}<span class="serif q">um sim que<br>atravessa o tempo</span></a>
    </div>
  </article>

  <article class="panel panel--marketing" data-panel>
    <div class="wrap panel__in">
      <div class="panel__txt">
        <span class="lbl lbl--k">03 · Marketing CAOS</span>
        <h3 class="h1" data-split>Marketing CAOS</h3>
        <p class="lead">Planejamento, conteúdo e divulgação para empresas que querem fortalecer sua marca e criar mais oportunidades de negócio.</p>
        {btn('Conheça nossas soluções de marketing', '/marketing/', 'dark', 'area_marketing')}
      </div>
      <a class="panel__vis" href="/marketing/" data-cursor="Abrir" aria-label="Marketing CAOS"><div class="mk-mini"><div class="mk-mini__g">{''.join(f'<i style="--i:{i}"></i>' for i in range(9))}</div>
        <svg viewBox="0 0 200 80" class="mk-mini__l" aria-hidden="true"><path d="M4 70 L50 52 L90 58 L130 30 L196 8" pathLength="1"/></svg></div></a>
    </div>
  </article>
</section>
{quem}
{final_cta('home', 'Seu próximo projeto começa com uma conversa.', 'Conte o que você tem em mente. Vamos entender sua necessidade e apresentar uma proposta para tirar a ideia do papel.', 'Vamos conversar')}
'''
    return page('/', 'home', 'CAOS | Marketing e Produção Audiovisual em Diamantina',
                'Conheça a CAOS: marketing digital, produção audiovisual e cobertura de eventos e casamentos em Diamantina. Veja nossos trabalhos e peça uma proposta.', body)

# ------------------------------------------------------------------ EVENTOS
def eventos():
    srv = [('Filmes e vídeos do evento', 'Produções que reúnem os principais acontecimentos e traduzem a atmosfera da experiência.', 'camera'),
           ('Fotografia', 'Registros de público, atrações, estrutura, marcas, bastidores e momentos importantes.', 'screen'),
           ('Conteúdos para redes sociais', 'Vídeos curtos e materiais adaptados para Reels, Stories e divulgação.', 'chat'),
           ('Storymaker e cobertura em tempo real', 'Captação, edição e publicação durante o evento, conforme o planejamento contratado.', 'chart'),
           ('Imagens aéreas', 'Uma perspectiva da estrutura e do cenário, conforme as condições e possibilidades de cada local.', 'rings')]
    rows = ''.join(f'''<li class="row" data-row><span class="row__n">{i:02d}</span><h3>{t}</h3><p>{d}</p><span class="row__i">{ICON[ic]}</span></li>''' for i, (t, d, ic) in enumerate(srv, 1))
    ev = ''.join(f'<li>{t}</li>' for t in ['Corporativos', 'Culturais', 'Esportivos', 'Sociais'])
    hero_w = (works_of('eventos') or WORKS)[0]
    form = mini_form('orcamento-eventos', 'eventos', [
        field('Data do evento', 'data', 'text', 'ex.: 12/09/2027', True), field('Local', 'local', 'text', 'Cidade / espaço', True),
        field('Seu nome', 'nome', 'text', 'Como podemos te chamar?', True), field('O que está planejando?', 'mensagem', 'textarea', 'Conte em poucas palavras')], 'Pedir orçamento para meu evento')
    body = f'''
<section class="hero hero--ev sec sec--dark" data-sec>
  <div class="hero--ev__bg">{frame(hero_w, 'frame--full')}</div>
  <div class="hero__veil"></div>
  <canvas class="hero__canvas" data-chaos-canvas aria-hidden="true"></canvas>
  {viewfinder()}
  <div class="wrap hero__in">
    <span class="lbl" data-reveal><i class="dot"></i> Audiovisual para Eventos</span>
    <h1 class="hero__h hero__h--md" data-split>Seu evento acontece uma vez. <span class="hl"><span class="nw">O conteúdo</span> continua.</span></h1>
    <p class="lead hero__p" data-reveal>Produção audiovisual e cobertura de eventos em Diamantina e região, com fotos, vídeos e conteúdos que levam a experiência além de quem esteve presente.</p>
    <div class="hero__btns" data-reveal>{btn('Solicite um orçamento', wa('eventos'), 'solid', 'ev_hero_wa', 'data-cursor="WhatsApp"', 'wa')}{btn('Ver portfólio', '#portfolio', 'line')}</div>
  </div>
</section>

<section class="sec sec--dark pres" data-sec>
  <div class="wrap pres__in">
    <div><span class="lbl" data-reveal>Apresentação</span><h2 class="h1" data-split>Da preparação ao último momento.</h2></div>
    <div class="pres__txt">
      <p class="lead" data-reveal>Cada evento tem seu ritmo, seu público e sua história. Nosso trabalho é entender essa dinâmica e transformar o que acontece em registros que transmitam a experiência de participar.</p>
      <p data-reveal>Planejamos a cobertura de acordo com a programação e os objetivos do projeto, acompanhando os momentos principais, os bastidores e os detalhes que fazem parte da sua identidade.</p>
      <p data-reveal>Atendemos eventos corporativos, culturais, esportivos e sociais, com possibilidades de entrega para divulgação, redes sociais e memória do evento.</p>
      <ul class="pills" data-reveal>{ev}</ul>
    </div>
  </div>
  <div class="ruler" aria-hidden="true" data-ruler>{''.join('<i></i>' for _ in range(60))}</div>
</section>

<section class="sec sec--grafite" data-sec>
  <div class="wrap">{sect_head('Serviços e entregas', 'O que entra na cobertura.')}<ul class="rows">{rows}</ul></div>
</section>

{portfolio_grid('eventos', 'Cada evento, uma forma de contar.')}

<section class="sec sec--dark" data-sec>
  <div class="wrap">{sect_head('Como funciona', 'Do primeiro contato à entrega.')}
  {steps([('Entendemos o evento', 'Conversamos sobre programação, público, objetivos e entregas.'),
          ('Planejamos a cobertura', 'Definimos equipe, momentos prioritários e formatos.'),
          ('Realizamos a produção', 'Acompanhamos o evento com o olhar e a estrutura necessários.'),
          ('Editamos e entregamos', 'Organizamos os materiais conforme os formatos e prazos combinados.')])}</div>
</section>
{final_cta('eventos', 'Vamos contar a história do seu evento?', 'Envie a data, o local e uma breve descrição do que está planejando. Vamos montar uma proposta de cobertura para você.', 'Pedir orçamento para meu evento', form)}
'''
    return page('/eventos/', 'eventos', 'Cobertura Audiovisual de Eventos em Diamantina | CAOS',
                'Fotos, vídeos e cobertura em tempo real para eventos corporativos, culturais, esportivos e sociais. Conheça o portfólio da CAOS e solicite um orçamento.', body)

# ------------------------------------------------------------------ CASAMENTOS
def casamentos():
    pos = [('Filme de casamento', 'Uma narrativa que conecta os momentos e a emoção do dia.'),
           ('Fotografia', 'Registros do casal, dos convidados e dos detalhes que fazem parte dessa história.'),
           ('Pré-wedding', 'Um momento para registrar a conexão de vocês antes do casamento.'),
           ('Making of, cerimônia e recepção', 'Cobertura organizada conforme a programação e o formato contratado.'),
           ('Vídeos curtos e storymaker', 'Conteúdos para compartilhar a celebração nas redes sociais.')]
    cards = ''.join(f'''<label class="opt" data-opt><input type="checkbox" value="{t}"><span class="opt__box"></span><span class="opt__n serif">{i}</span><h3>{t}</h3><p>{d}</p></label>''' for i, (t, d) in enumerate(pos, 1))
    hero_ws = (works_of('casamentos') or WORKS)
    form = mini_form('casamentos-data', 'casamentos', [
        field('Data do casamento', 'data', 'text', 'ex.: 20/08/2027', True), field('Local', 'local', 'text', 'Cidade / espaço', True),
        field('Nomes do casal', 'nome', 'text', 'Quem vai casar?', True)], 'Consultar disponibilidade')
    deps = PORT.get('depoimentos') or []
    dep_html = ''
    if deps:
        dep_html = '<div class="quotes quotes--serif">' + ''.join(f'<blockquote class="quote"><p class="serif">“{esc(d["texto"])}”</p><footer>{esc(d["autor"])}</footer></blockquote>' for d in deps) + '</div>'
    body = f'''
<section class="hero hero--wd sec sec--areia" data-sec>
  <div class="wrap hero__in hero--wd__in">
    <div class="hero--wd__txt">
      <span class="lbl lbl--b" data-reveal>Audiovisual para Casamentos</span>
      <h1 class="serif hero--wd__h" data-fade>Para reviver o que vocês <em>sentiram.</em></h1>
      <p class="lead" data-reveal>Filmes e fotografias de casamento com um olhar atento à história de vocês, aos encontros e aos detalhes que tornam esse dia único.</p>
      <div data-reveal>{btn('Consulte sua data', '#data', 'dark', 'wd_hero_data')}</div>
    </div>
    <div class="hero--wd__vis" aria-hidden="false">
      <div class="arch arch--1" data-speed="0.05">{frame(hero_ws[0], 'frame--arch frame--full')}</div>
      <div class="arch arch--2" data-speed="-0.08">{frame(hero_ws[min(1, len(hero_ws)-1)], 'frame--arch frame--full')}</div>
      <i class="dobra"></i>
    </div>
  </div>
</section>

<section class="sec sec--areia pres" data-sec>
  <div class="wrap pres__in">
    <div><span class="lbl lbl--b" data-reveal>Apresentação</span><h2 class="h1 h1--soft" data-split>A história de vocês conduz o nosso olhar.</h2></div>
    <div class="pres__txt">
      <p class="serif big" data-reveal>O abraço antes da cerimônia, a voz emocionada nos votos, os olhares de quem acompanhou tudo de perto. São esses momentos que dão sentido ao registro.</p>
      <p data-reveal>Na CAOS, buscamos conhecer o casal e entender o que importa para vocês. Assim, construímos uma cobertura que acompanha o dia com sensibilidade e transforma os acontecimentos em lembranças para revisitar ao longo da vida.</p>
    </div>
  </div>
</section>

<section class="sec sec--areia" data-sec data-wd-builder>
  <div class="wrap">{sect_head('Possibilidades de cobertura', 'Monte a cobertura do jeito de vocês.')}
    <p class="lead sub" data-reveal>Cada serviço pode compor a proposta. Marque os que fazem sentido para vocês e a mensagem já segue com a sua seleção.</p>
    <div class="opts" data-opts>{cards}</div>
    <div class="opts__bar" data-reveal><span class="lbl lbl--b"><b data-opt-count>0</b> selecionado(s)</span>{btn('Pedir proposta com minha seleção', wa('casamentos'), 'dark', 'wd_builder_wa', 'data-opt-cta data-cursor="WhatsApp"', 'wa')}</div>
  </div>
</section>

{portfolio_grid('casamentos', 'Histórias que já passaram pelas nossas lentes.')}
{f'<section class="sec sec--areia" data-sec><div class="wrap">{dep_html}</div></section>' if dep_html else ''}

<section class="sec sec--areia" data-sec>
  <div class="wrap">{sect_head('Como funciona', 'Do primeiro contato ao grande dia.')}
  {steps([('Vocês enviam a data', 'O local e as primeiras informações do casamento.'),
          ('Conversamos sobre a história do casal', 'E sobre as expectativas para o registro.'),
          ('Apresentamos as possibilidades', 'As opções de cobertura e a proposta.'),
          ('Planejamos os detalhes', 'Para acompanhar o dia e realizar as entregas combinadas.')], 'steps--serif')}</div>
</section>

<section class="sec sec--grafite cta cta--wd" data-sec id="data">
  <div class="wrap cta__in">
    <div class="cta__txt">
      <span class="lbl" data-reveal>Disponibilidade</span>
      <h2 class="h1 cta__h" data-split>Vamos conhecer a <em class="serif">história de vocês?</em></h2>
      <p class="lead" data-reveal>Conte quando e onde será o casamento. Vamos conversar sobre como vocês querem guardar esse dia.</p>
      <div class="cta__form">{form}</div>
    </div>
    <div class="cta__vis" aria-hidden="true">{SIMBOLO}</div>
  </div>
</section>
'''
    return page('/casamentos/', 'casamentos', 'Filmagem e Fotografia de Casamentos em Diamantina | CAOS',
                'Conheça os filmes e as fotografias de casamento da CAOS. Registros atentos à história do casal e à emoção do dia. Consulte sua data.', body)

# ------------------------------------------------------------------ MARKETING
def marketing():
    sol = [('Gestão de redes sociais', 'Planejamento de conteúdo, organização do cronograma, criação de publicações e acompanhamento da comunicação, respeitando a identidade e a rotina da empresa.', 'chat'),
           ('Produção de fotos e vídeos', 'Captação e edição de materiais para apresentar produtos, serviços, equipe, estrutura e bastidores com qualidade profissional.', 'camera'),
           ('Gestão de tráfego pago', 'Planejamento e acompanhamento de campanhas no Instagram e no Facebook, com criativos em vídeo e arte produzidos pela CAOS e ajustes orientados pelos resultados.', 'chart'),
           ('Criação de sites e landing pages', 'Páginas para apresentar sua empresa, destacar seus serviços e facilitar o contato de potenciais clientes.', 'screen'),
           ('Campanhas e ações de comunicação', 'Conceito, planejamento e produção de materiais para lançamentos, datas comerciais, eventos e ações de posicionamento.', 'rings')]
    cards = ''.join(f'''<article class="sol" data-tilt><span class="sol__n">{i:02d}</span><span class="sol__i">{ICON[ic]}</span><h3>{t}</h3><p>{d}</p><i class="dobra dobra--s"></i></article>''' for i, (t, d, ic) in enumerate(sol, 1))
    ws = works_of('marketing')
    cases = ''.join(f'''<article class="case" data-reveal><div class="case__vis"><button type="button" class="work__open" data-open="{esc(w['id'])}" data-cursor="Ver" aria-label="Abrir {esc(w['titulo'])}">{frame(w)}</button></div>
      <div class="case__txt"><span class="lbl lbl--k">{esc(w['cliente'])}</span><h3>{esc(w['titulo'])}</h3><p>{esc(w['descricao'])}</p>
      <ul class="pills pills--k"><li>{esc(w['servico'])}</li></ul></div></article>''' for w in ws)
    path = ''.join(f'<span class="gline" style="--i:{i}"></span>' for i in range(1))
    body = f'''
<section class="hero hero--mk sec sec--laranja" data-sec>
  <div class="wrap hero__in hero--mk__in">
    <div class="hero--mk__txt">
      <span class="lbl lbl--k" data-reveal>Marketing CAOS</span>
      <h1 class="hero__h hero__h--md hero--mk__h" data-split>Sua empresa tem muito a mostrar. Vamos fazer isso chegar às pessoas certas.</h1>
      <p class="lead" data-reveal>Marketing digital em Diamantina, com estratégia, produção de conteúdo e tráfego pago para fortalecer sua marca e gerar oportunidades de negócio.</p>
      <div class="hero__btns" data-reveal>{btn('Quero uma proposta para minha empresa', wa('marketing'), 'dark', 'mk_hero_wa', 'data-cursor="WhatsApp"', 'wa')}</div>
    </div>
    <div class="hero--mk__vis" aria-hidden="true" data-mkfeed>
      <div class="phone"><div class="phone__top"><span></span></div>
        <div class="phone__grid">{''.join(f'<i style="--i:{i}"></i>' for i in range(12))}</div>
        <svg viewBox="0 0 200 90" class="phone__l"><path d="M6 78 L48 60 L86 66 L126 34 L194 10" pathLength="1"/><circle cx="194" cy="10" r="4"/></svg>
      </div>
      <div class="float float--a"><span class="ico-w">{ICON['chat']}</span>Conteúdo</div>
      <div class="float float--b"><span class="ico-w">{ICON['chart']}</span>Tráfego pago</div>
      <div class="float float--c"><span class="ico-w">{ICON['camera']}</span>Vídeo</div>
    </div>
  </div>
  <i class="dobra dobra--k"></i>
</section>

<section class="sec sec--dark pres" data-sec>
  <div class="wrap pres__in">
    <div><span class="lbl" data-reveal>Apresentação</span><h2 class="h1" data-split>Da estratégia ao conteúdo que vai para a rua.</h2></div>
    <div class="pres__txt">
      <p class="lead" data-reveal>Uma comunicação consistente começa com entendimento: o que sua empresa oferece, quem você quer alcançar e por que esse público deve escolher sua marca.</p>
      <p data-reveal>A CAOS conecta planejamento, criação, produção audiovisual e divulgação para transformar essas respostas em ações. Organizamos a presença digital da empresa com conteúdos que apresentam seus diferenciais, aproximam o público e apoiam os objetivos comerciais.</p>
      <ul class="pills" data-reveal><li>O que você oferece</li><li>Quem você quer alcançar</li><li>Por que te escolher</li></ul>
    </div>
  </div>
</section>

<section class="sec sec--nevoa" data-sec>
  <div class="wrap">{sect_head('Soluções', 'O que a CAOS faz pela sua marca.')}<div class="sols">{cards}</div></div>
</section>

<section class="sec sec--dark sec--portfolio" data-sec id="portfolio">
  <div class="wrap">{sect_head('Cases', 'Conheça o trabalho por trás de cada marca.')}
    <p class="lead sub" data-reveal>Cada empresa tem uma necessidade. Veja como organizamos estratégia, conteúdo e divulgação em projetos de diferentes segmentos.</p>
    <div class="cases">{cases}</div>
  </div>
</section>

<section class="sec sec--grafite" data-sec>
  <div class="wrap">{sect_head('Nosso processo', 'Um ciclo que não para de melhorar.')}
  {steps([('Briefing', 'Entendemos a empresa, o público e os objetivos.'), ('Planejamento', 'Definimos os temas, os formatos e as ações.'),
          ('Produção', 'Criamos artes, fotos, vídeos e textos.'), ('Publicação e divulgação', 'Colocamos o planejamento em prática nos canais definidos.'),
          ('Acompanhamento', 'Analisamos os resultados e ajustamos as próximas ações.')], 'steps--loop')}</div>
</section>
{final_cta('marketing', 'O que sua empresa precisa comunicar agora?', 'Conte sobre seu negócio e os desafios da sua comunicação. Vamos apresentar as soluções que fazem sentido para esse momento.', 'Conversar com a CAOS')}
'''
    return page('/marketing/', 'marketing', 'Agência de Marketing Digital em Diamantina | CAOS',
                'Gestão de redes sociais, produção de conteúdo, tráfego pago e criação de sites. Conheça as soluções da CAOS para sua empresa e solicite uma proposta.', body)

# ------------------------------------------------------------------ CONTATO
def contato():
    opts = ''.join(f'<option value="{v}">{t}</option>' for v, t in [
        ('', 'Selecione'), ('Audiovisual para Eventos', 'Audiovisual para Eventos'), ('Audiovisual para Casamentos', 'Audiovisual para Casamentos'),
        ('Marketing CAOS', 'Marketing CAOS'), ('Outro assunto', 'Outro assunto')])
    body = f'''
<section class="sec sec--dark contact" data-sec>
  <div class="wrap contact__in">
    <div class="contact__l">
      <span class="lbl" data-reveal><i class="dot"></i> Contato</span>
      <h1 class="hero__h hero__h--md" data-split>Vamos tirar seu projeto <span class="hl">do papel?</span></h1>
      <p class="lead" data-reveal>Seja para cuidar da comunicação da sua empresa, cobrir um evento ou registrar seu casamento, queremos entender o que você está planejando.</p>
      <p data-reveal>Fale diretamente com a nossa equipe ou preencha o formulário. Para eventos e casamentos, informe também a data e o local.</p>
      <div class="ccards" data-reveal>
        <a class="ccard" href="{wa('geral')}" target="_blank" rel="noopener" data-track="wa_contato_1" data-cursor="WhatsApp"><span>{ICON['wa']} WhatsApp</span><strong>{SITE['whatsapp_principal_formatado']}</strong><i>{ICON['arrow-up']}</i></a>
        <a class="ccard" href="{wa('geral', SITE['whatsapp_secundario'])}" target="_blank" rel="noopener" data-track="wa_contato_2" data-cursor="WhatsApp"><span>{ICON['wa']} WhatsApp</span><strong>{SITE['whatsapp_secundario_formatado']}</strong><i>{ICON['arrow-up']}</i></a>
        <a class="ccard" href="mailto:{SITE['email']}"><span>{ICON['mail']} E-mail</span><strong>{SITE['email']}</strong><i>{ICON['arrow-up']}</i></a>
        <a class="ccard" href="{SITE['instagram_url']}" target="_blank" rel="noopener"><span>{ICON['ig']} Instagram</span><strong>@{SITE['instagram']}</strong><i>{ICON['arrow-up']}</i></a>
      </div>
      <p class="loc" data-reveal>{ICON['pin']} {SITE['endereco']}.<br>Sediados em Diamantina/MG. Para projetos em outras cidades, consulte nossa disponibilidade.</p>
    </div>
    <form class="cform js-form" name="contato" method="POST" action="/contato/obrigado/" data-netlify="true" netlify-honeypot="bot-field" data-wa="geral" data-track="form_contato" data-reveal>
      {hidden_form('contato')}
      <h2 class="h3">Envie sua mensagem</h2>
      {field('Nome', 'nome', 'text', 'Seu nome', True)}
      {field('Telefone / WhatsApp', 'telefone', 'tel', '(00) 00000-0000', True)}
      {field('E-mail', 'email', 'email', 'voce@email.com')}
      <label class="fld"><span>Serviço de interesse</span><select name="servico" required data-service>{opts}</select></label>
      <div class="cform__extra" data-extra hidden>{field('Data do evento / casamento', 'data', 'text', 'ex.: 12/09/2027')}{field('Local', 'local', 'text', 'Cidade / espaço')}</div>
      {field('Mensagem', 'mensagem', 'textarea', 'Conte um pouco sobre o que você tem em mente', True)}
      <button class="btn btn--solid" type="submit" data-magnetic><span class="btn__t">Enviar mensagem</span><span class="btn__i">{ICON['arrow']}</span></button>
      <p class="fine">Ao enviar, o WhatsApp abre com sua mensagem pronta e seu contato também chega até nossa equipe por aqui.</p>
    </form>
  </div>
</section>'''
    return page('/contato/', 'contato', 'Fale com a CAOS | Contato e Orçamentos',
                'Entre em contato com a CAOS para projetos de marketing, produção audiovisual, eventos e casamentos. Fale pelo WhatsApp ou envie sua mensagem.', body)

def obrigado():
    body = f'''<section class="sec sec--dark contact" data-sec><div class="wrap" style="min-height:70vh;display:grid;align-content:center;gap:24px">
    <span class="lbl"><i class="dot"></i> Mensagem recebida</span><h1 class="hero__h hero__h--md">Obrigado! <span class="hl">Já vamos conversar.</span></h1>
    <p class="lead">Sua mensagem chegou até a equipe da CAOS. Se preferir agilizar, fale direto pelo WhatsApp.</p>
    <div>{btn('Chamar no WhatsApp', wa('geral'), 'solid', 'wa_obrigado', '', 'wa')} {btn('Voltar ao início', '/', 'line')}</div></div></section>'''
    return page('/contato/obrigado/', 'contato', 'Mensagem recebida | CAOS', 'Recebemos sua mensagem.', body, '<meta name="robots" content="noindex">')

def notfound():
    body = f'''<section class="sec sec--dark contact" data-sec><div class="wrap" style="min-height:70vh;display:grid;align-content:center;gap:24px">
    <span class="lbl"><i class="dot"></i> Erro 404</span><h1 class="hero__h">Aqui é só <span class="hl">caos.</span></h1>
    <p class="lead">A página que você procura não existe ou mudou de lugar.</p><div>{btn('Voltar ao início', '/', 'solid')}</div></div></section>'''
    return page('/404.html', 'home', 'Página não encontrada | CAOS', 'Página não encontrada.', body, '<meta name="robots" content="noindex">')

# ------------------------------------------------------------------ saída
def write(path, content):
    d = os.path.dirname(path)
    if d: os.makedirs(d, exist_ok=True)
    open(path, 'w', encoding='utf8').write(content)

PAGES = {'index.html': home(), 'eventos/index.html': eventos(), 'casamentos/index.html': casamentos(),
         'marketing/index.html': marketing(), 'contato/index.html': contato(),
         'contato/obrigado/index.html': obrigado(), '404.html': notfound()}
for p, c in PAGES.items():
    write(p, c)

today = datetime.date.today().isoformat()
urls = ['/', '/eventos/', '/casamentos/', '/marketing/', '/contato/']
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      ''.join(f'  <url><loc>{BASE}{p}</loc><lastmod>{today}</lastmod><priority>{"1.0" if p == "/" else "0.8"}</priority></url>\n' for p in urls) + '</urlset>\n')
write('robots.txt', f'User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: {BASE}/sitemap.xml\n')
print(f'Site gerado: {len(PAGES)} páginas · {len(WORKS)} trabalhos no portfólio')
