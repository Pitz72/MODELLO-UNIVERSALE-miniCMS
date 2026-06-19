#!/usr/bin/env python3
# Genera la copertina integrale KDP (fronte+dorso+retro) in SVG, misure in mm.
BLEED=3.175; TRIM_W=177.8; TRIM_H=254.0; SPINE=9.15
W=BLEED+TRIM_W+SPINE+TRIM_W+BLEED         # 371.1
Hh=TRIM_H+2*BLEED                          # 260.35
back_x0=BLEED; back_x1=back_x0+TRIM_W
spine_x0=back_x1; spine_x1=spine_x0+SPINE; spine_cx=(spine_x0+spine_x1)/2
front_x0=spine_x1; front_x1=front_x0+TRIM_W
trim_top=BLEED; trim_bot=Hh-BLEED
front_cx=(front_x0+front_x1)/2
back_cx=(back_x0+back_x1)/2
TEAL="#2DD4BF"; WHITE="#eef3f8"; GRAY="#9fb3c8"

S=[]
S.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{Hh}mm" viewBox="0 0 {W:.3f} {Hh:.3f}">')
# defs
S.append('<defs>')
S.append(f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="0.2">'
         f'<stop offset="0" stop-color="#0a111d"/><stop offset="0.6" stop-color="#0f1b2c"/>'
         f'<stop offset="1" stop-color="#16243a"/></linearGradient>')
S.append(f'<radialGradient id="frontglow" cx="{front_cx/W:.3f}" cy="0.62" r="0.42">'
         f'<stop offset="0" stop-color="#13384a" stop-opacity="0.85"/>'
         f'<stop offset="1" stop-color="#13384a" stop-opacity="0"/></radialGradient>')
S.append('<linearGradient id="topface" x1="0" y1="0" x2="0.4" y2="1">'
         '<stop offset="0" stop-color="#2b3e54"/><stop offset="1" stop-color="#1b2a3c"/></linearGradient>')
S.append('<linearGradient id="seamg" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="#9af7e9"/><stop offset="1" stop-color="{TEAL}"/></linearGradient>')
S.append('<filter id="glow" x="-80%" y="-80%" width="260%" height="260%">'
         '<feGaussianBlur stdDeviation="1.6" result="b"/>'
         '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
S.append('<filter id="softglow" x="-100%" y="-100%" width="300%" height="300%">'
         '<feGaussianBlur stdDeviation="6"/></filter>')
S.append('<pattern id="dots" width="9" height="9" patternUnits="userSpaceOnUse">'
         '<circle cx="1" cy="1" r="0.35" fill="#33485f" fill-opacity="0.35"/></pattern>')
S.append('</defs>')
# background
S.append(f'<rect x="0" y="0" width="{W}" height="{Hh}" fill="url(#bg)"/>')
S.append(f'<rect x="0" y="0" width="{W}" height="{Hh}" fill="url(#dots)"/>')
S.append(f'<rect x="{front_x0}" y="0" width="{W-front_x0}" height="{Hh}" fill="url(#frontglow)"/>')

# ---- helper testo ----
def txt(x,y,s,size,fill=WHITE,family="IBM Plex Serif",weight="400",anchor="start",ls=0,style="normal",opacity=1):
    extra=f' letter-spacing="{ls}"' if ls else ''
    return (f'<text x="{x:.2f}" y="{y:.2f}" font-family="{family}" font-size="{size:.2f}" '
            f'font-weight="{weight}" font-style="{style}" fill="{fill}" fill-opacity="{opacity}" '
            f'text-anchor="{anchor}"{extra}>{s}</text>')

# ===================== FRONTE (destra) =====================
fx=front_cx
S.append(txt(fx, 46, "RUNTIME EDIZIONI", 2.7, TEAL, "IBM Plex Mono", "500", "middle", ls=3.2))
S.append(txt(fx, 70, "React + PHP:", 8.0, WHITE, "IBM Plex Serif", "600", "middle"))
S.append(txt(fx, 84, "The Thin Stack", 13.0, WHITE, "IBM Plex Serif", "600", "middle"))
S.append(txt(fx, 96, "Il protocollo miniCMS per Web App moderne", 3.3, GRAY, "IBM Plex Mono", "400", "middle"))

# ---- motivo isometrico: due lastre + giunzione teal ----
cx=fx; cy=170.0; w=44.0; hh=22.0; t1=6.0; t2=6.0
T=(cx,cy-hh); R=(cx+w,cy); B=(cx,cy+hh); L=(cx-w,cy)
def P(*pts): return " ".join(f"{p[0]:.2f},{p[1]:.2f}" for p in pts)
# glow ambientale
S.append(f'<ellipse cx="{cx}" cy="{cy+8}" rx="74" ry="40" fill="{TEAL}" fill-opacity="0.10" filter="url(#softglow)"/>')
# lastra inferiore - facce
S.append(f'<polygon points="{P(L,B,(B[0],B[1]+t1+t2),(L[0],L[1]+t1+t2))}" fill="#0f1825"/>')
S.append(f'<polygon points="{P(R,B,(B[0],B[1]+t1+t2),(R[0],R[1]+t1+t2))}" fill="#0b121d"/>')
# giunzione luminosa (V frontale) tra le due lastre, a meta'
ys=cy+hh+t1
S.append(f'<polyline points="{P((L[0],L[1]+t1),(B[0],ys),(R[0],R[1]+t1))}" fill="none" '
         f'stroke="url(#seamg)" stroke-width="1.5" filter="url(#glow)"/>')
# lastra superiore - facce
S.append(f'<polygon points="{P(L,B,(B[0],B[1]+t1),(L[0],L[1]+t1))}" fill="#16222f"/>')
S.append(f'<polygon points="{P(R,B,(B[0],B[1]+t1),(R[0],R[1]+t1))}" fill="#101a25"/>')
# faccia superiore
S.append(f'<polygon points="{P(T,R,B,L)}" fill="url(#topface)" stroke="#33випbb" />'.replace('#33випbb','#3a5066'))
# spigolo superiore destro teal tenue
S.append(f'<polyline points="{P(T,R)}" fill="none" stroke="{TEAL}" stroke-width="0.5" stroke-opacity="0.55"/>')

# autore + editore (fronte basso)
S.append(txt(fx, 232, "Simone Pizzi", 6.0, WHITE, "IBM Plex Serif", "500", "middle"))
S.append(txt(fx, 244, "Terza Edizione", 2.8, GRAY, "IBM Plex Mono", "400", "middle", ls=1.5))

# ===================== DORSO (centro) =====================
# testo ruotato 90° (lettura dall'alto in basso)
sp=spine_cx
S.append(f'<g transform="translate({sp:.2f},0) rotate(90)">')
S.append(f'<text x="70" y="1.0" font-family="IBM Plex Serif" font-size="3.0" font-weight="600" '
         f'fill="{WHITE}" text-anchor="start" dominant-baseline="middle">Simone Pizzi&#160;&#160;·&#160;&#160;The Thin Stack</text>')
S.append(f'<text x="{trim_bot-12:.0f}" y="1.0" font-family="IBM Plex Mono" font-size="2.2" '
         f'fill="{TEAL}" text-anchor="end" dominant-baseline="middle" letter-spacing="1.5">RUNTIME</text>')
S.append('</g>')

# ===================== RETRO (sinistra) =====================
bx=back_x0+10
S.append(txt(bx, 40, "IL PROTOCOLLO MINICMS", 2.7, TEAL, "IBM Plex Mono", "500", "start", ls=2.5))
blurb=[
 ("Il frontend è diventato magnifico. Ma sotto ci","s"),
 ("mettiamo troppo: Node, container, CMS in","s"),
 ("abbonamento, servizi cloud, per siti che","s"),
 ("girerebbero benissimo su un hosting da pochi euro.","s"),
 ("","g"),
 ("«The Thin Stack» è il protocollo che separa due","s"),
 ("piani: la presentazione a React e TypeScript, i dati","s"),
 ("a PHP nativo e SQLite (o MySQL quando serve).","s"),
 ("Niente framework di backend, niente overhead: uno","s"),
 ("scheletro minimo ma vero, che scala su tre gradini","s"),
 ("a seconda di ciò che ti serve.","s"),
 ("","g"),
 ("Venti capitoli e tre appendici costruiti su quattro","s"),
 ("siti reali in produzione: sicurezza fatta a mano, SEO","s"),
 ("che funziona, feed, newsletter, dashboard, e tutte","s"),
 ("le cicatrici di chi l'ha messo online sul serio.","s"),
]
y=58
for line,k in blurb:
    if line: S.append(txt(bx, y, line, 3.4, "#cdd9e6", "IBM Plex Serif", "400", "start"))
    y += 5.0 if k=="s" else 3.0

# editore in basso a sinistra
S.append(txt(bx, trim_bot-10, "RUNTIME EDIZIONI", 3.0, WHITE, "IBM Plex Mono", "500", "start", ls=2.0))
S.append(txt(bx, trim_bot-5, "www.runtimeradio.com", 2.6, GRAY, "IBM Plex Mono", "400", "start"))

# area codice a barre KDP (riservata, in basso a destra del retro)
bw=46; bh=28; bxr=back_x1-bw-9; byr=trim_bot-bh-9
S.append(f'<rect x="{bxr}" y="{byr}" width="{bw}" height="{bh}" rx="1.5" fill="#ffffff" fill-opacity="0.92"/>')
S.append(txt(bxr+bw/2, byr+bh/2+1, "area codice a barre", 2.3, "#7a8aa0", "IBM Plex Mono", "400", "middle"))

# ---- guide tecniche (trim + pieghe dorso) su layer tenue (per verifica, NON sul file di stampa finale) ----
guides=[]
for gx in (trim_top,):
    pass
S.append('</svg>')
open("copertina/cover.svg","w",encoding="utf-8").write("\n".join(S))
print("cover.svg generato:", round(W,2),"x",round(Hh,2),"mm | dorso",SPINE,"mm")
