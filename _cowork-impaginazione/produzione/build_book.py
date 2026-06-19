#!/usr/bin/env python3
# Build INTERNO KDP — "React + PHP: The Thin Stack" (3a ed.) — Typst
# .md -> frammenti -> libro.typ -> master PDF (../master/), 2 passate:
#  pass1 conta pagine e individua indice/Parte I/bianche;
#  pass2 inserisce le bianche (multiplo di 4) e un footer deterministico
#  (folio arabo da 1 sul corpo, romano sull'indice, NIENTE folio sulle bianche).
import os, re, subprocess
import pypandoc, typst, pypdf, fitz

PROD   = os.path.dirname(os.path.abspath(__file__))
COWORK = os.path.dirname(PROD)
REPO   = os.path.dirname(COWORK)
MAN    = os.path.join(REPO, "manuale")
FRAG   = os.path.join(PROD, "capitoli-typ")
MASTER = os.path.join(COWORK, "master")
FONTS  = os.path.join(REPO, "fonts", "IBM_Plex")
LIBRO  = os.path.join(PROD, "libro.typ")
OUTPDF = os.path.join(MASTER, "Interno_The-Thin-Stack_3ed_7x10_BN.pdf")
INTER  = os.path.join(PROD, "_interno_rgb.pdf")  # intermedio (gitignore)
os.makedirs(FRAG, exist_ok=True); os.makedirs(MASTER, exist_ok=True)
PANDOC = pypandoc.get_pandoc_path()
LUA = os.path.join(PROD, "alerts.lua")

STRUCT = [
 ("I","La Visione","Il perché. La filosofia che guida ogni decisione tecnica.",
   ["CAPITOLO 1 - Manifesto"]),
 ("II","L'Architettura","Le fondamenta. Struttura del progetto, database, stack tecnologico.",
   ["CAPITOLO 2 - Architettura e Struttura Progetto","CAPITOLO 3 - Database Strategy",
    "CAPITOLO 4 - Frontend Dependencies"]),
 ("III","I Componenti","I mattoni. Backend, frontend, media, editor: i building block del sistema.",
   ["CAPITOLO 5 - Backend Logic (PHP)","CAPITOLO 6 - Frontend Bridge (API.ts)",
    "CAPITOLO 7 - Media & Optimization","CAPITOLO 8 - Advanced Content Editing & Media Integration"]),
 ("IV","Il Flusso Operativo","Come i contenuti vivono. Dal ciclo di vita alla distribuzione, passando per sicurezza e SEO.",
   ["CAPITOLO 9 - Content Lifecycle","CAPITOLO 10 - Security & Auth",
    "CAPITOLO 11 - SEO Pre-rendering con PHP Entry-Point","CAPITOLO 12 - RSS Feed & Syndication",
    "CAPITOLO 13 - Newsletter & Email System","CAPITOLO 14 - Admin Dashboard & Panels"]),
 ("V","I Casi Reali","Dove la teoria incontra la produzione. Pattern estratti da progetti reali, con le loro cicatrici.",
   ["CAPITOLO 15 - Database Evolution - Da SQLite a MySQL","CAPITOLO 16 - Portfolio & Projects Module",
    "CAPITOLO 17 - Festival Logic - Iscrizioni e Workflow Approvazione",
    "CAPITOLO 18 - Festival Logic - Votazioni e Protezione Anti-Frode",
    "CAPITOLO 19 - Festival Logic - Dashboard Admin, Settings e Reporting",
    "CAPITOLO 20 - Social Interactions & Reactions"]),
 (None,"Appendici","Strumenti pratici e casi di confine.",
   ["BOILERPLATE-CHECKLIST","APPENDICE B - Ciclo di vita di un fork","APPENDICE C - Testing e Deploy"]),
]
IMPORT = '#import "../template.typ": admonition, horizontalrule\n'

def convert(stem):
    src = os.path.join(MAN, stem + ".md")
    out = os.path.join(FRAG, re.sub(r"[^A-Za-z0-9]+","_",stem) + ".typ")
    subprocess.run([PANDOC,"-f","gfm+alerts","-t","typst","--shift-heading-level-by=1",
                    "--lua-filter",LUA, src,"-o",out], check=True)
    return out, open(out,encoding="utf-8").read()

def extract_dedica(txt):
    key="#quote(block: true)["; i=txt.find(key)
    if i<0: return txt,None
    j=i+len(key); d=1
    while j<len(txt) and d:
        if txt[j]=="[":d+=1
        elif txt[j]=="]":d-=1
        j+=1
    inner=txt[i+len(key):j-1].strip()
    rest=txt[:i]+txt[j:]
    rest=re.sub(r"\n\s*#horizontalrule\s*\n","\n",rest,count=1)
    return rest,inner

def build_fragments():
    order=[]; dedica=None
    for num,title,desc,files in STRUCT:
        order.append(("part",num,title,desc))
        for stem in files:
            out,txt=convert(stem)
            if stem=="CAPITOLO 1 - Manifesto": txt,dedica=extract_dedica(txt)
            if not txt.startswith("#import"): txt=IMPORT+txt
            open(out,"w",encoding="utf-8").write(txt)
            order.append(("chap",os.path.basename(out)))
    return order,(dedica or "_[ dedica ]_")

BIO=("Simone Pizzi è autore ed editore. Ha fondato Runtime Edizioni e Runtime Radio, "
"per cui cura progetti editoriali, sonori e digitali. Ha pubblicato la raccolta di racconti "
"«L'Albero dei Racconti» e la novella di fantascienza «Frequenza di Servizio».\n\n"
"Questo manuale nasce dal lavoro reale su quattro siti in produzione — SitoRuntime, "
"DISINTELLIGENZA, FDCA e SimonePizziWebSite — e raccoglie il protocollo «thin stack» "
"con cui li ha costruiti: React e TypeScript per la presentazione, PHP nativo e SQLite "
"o MySQL per i dati, senza framework di backend né infrastruttura sproporzionata.")

def footer_block(blanks, fi, fb):
    if fi is None:  # pass1: nessun footer
        return ""
    arr="("+", ".join(str(x) for x in blanks)+(",)" if len(blanks)==1 else ")")
    return ("#set page(footer: context {\n"
            f"  let pg = here().page()\n"
            f"  let bl = {arr}\n"
            f"  if bl.contains(pg) or pg < {fi} {{ none }}\n"
            f"  else if pg < {fb} {{ align(center, text(size: 9pt, fill: luma(60), numbering(\"i\", pg - {fi} + 1))) }}\n"
            f"  else {{ align(center, text(size: 9pt, fill: luma(60), numbering(\"1\", pg - {fb} + 1))) }}\n"
            "})\n")

def write_libro(order,dedica,pad,blanks=(),fi=None,fb=None):
    L=['#import "template.typ": *','#show: conf','']
    L.append(footer_block(blanks,fi,fb))
    L += ['#set page(numbering: none)','',
    '// p.1 FRONTESPIZIO','#align(center + horizon)[',
    '  #text(size: 27pt, weight: "semibold")[React + PHP:\\ The Thin Stack]','  #v(0.6em)',
    '  #text(size: 13pt, style: "italic", fill: luma(60))[Il protocollo miniCMS per Web App moderne]',
    '  #v(3.5em)','  #text(size: 13pt)[Simone Pizzi]','  #v(0.3em)',
    '  #text(size: 10pt, fill: luma(90))[Terza Edizione]','  #v(7em)',
    '  #text(size: 11pt, tracking: 2pt)[RUNTIME EDIZIONI]',']',
    '#pagebreak()','#pagebreak()','',
    '// p.3 COLOPHON','#v(1fr)','#[#set par(justify: false, leading: 0.7em)',
    '#text(size: 9pt, fill: luma(30))[','React + PHP: The Thin Stack \\',
    'Il protocollo miniCMS per Web App moderne \\','Terza Edizione --- Giugno 2026 \\','#v(0.8em)',
    '© 2026 Simone Pizzi \\','© 2026 Runtime Edizioni \\','#v(0.8em)',
    "Tutti i diritti riservati. Nessuna parte di questo libro può essere riprodotta senza il consenso scritto dell'editore, salvo brevi citazioni in recensioni. \\",
    '#v(0.8em)','I marchi e i nomi di prodotto citati sono dei rispettivi proprietari. \\',
    'www.runtimeradio.com',']]','#pagebreak()','#pagebreak()','',
    '// p.5 DEDICA','#align(right + horizon)[',
    '  #block(width: 75%)[#set par(justify: false, leading: 0.8em)','#set align(right)',dedica,'  ]',']',
    '#pagebreak()','',
    '// INDICE','#pagebreak(to: "odd")',
    '#outline(title: [Indice], depth: 2, indent: 1.2em)','',
    '// CORPO','']
    for it in order:
        if it[0]=="part":
            _,num,title,desc=it; na=f'"{num}"' if num else "none"
            L.append(f'#part({na}, "{title}", "{desc}")')
        else:
            L.append(f'#include "capitoli-typ/{it[1]}"')
    L += ['','// BIO','#pagebreak(weak: true)','#v(2cm)',
          '#text(weight: "semibold", size: 18pt)[L\'autore]','#v(0.8em)',
          '#line(length: 100%, stroke: 0.6pt + luma(160))','#v(0.8em)']
    for para in BIO.split("\n\n"): L += [para.strip(),'']
    if pad>0:
        L.append('// pagine bianche -> multiplo di 4')
        for _ in range(pad): L += ['#pagebreak(weak: false)','#text[~]']
    open(LIBRO,"w",encoding="utf-8").write("\n".join(L))

def compile_to(out): typst.compile(LIBRO, output=out, font_paths=[FONTS])

def detect(pdf):
    doc=fitz.open(pdf); H=720; bot=20*72/25.4; fi=fb=None; blanks=[]
    for i,p in enumerate(doc):
        t=p.get_text()
        if fi is None and re.search(r'\bIndice\b',t): fi=i+1
        if fb is None and re.search(r'P\s*A\s*R\s*T\s*E',t): fb=i+1
        # blank = nessuno span dentro la gabbia
        content=False
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines",[]):
                for s in l["spans"]:
                    if s["bbox"][1] < H-bot-5: content=True
        if not content: blanks.append(i+1)
    n=len(doc); doc.close()
    return n,fi,fb,blanks

if __name__=="__main__":
    order,dedica=build_fragments()
    write_libro(order,dedica,0)                 # pass1
    compile_to(INTER)
    n,fi,fb,blanks=detect(INTER)
    pad=(-n)%4
    blanks=list(blanks)+[n+k for k in range(1,pad+1)]
    write_libro(order,dedica,pad,blanks=blanks,fi=fi,fb=fb)   # pass2
    compile_to(INTER)
    # --- conversione DeviceGray (B/N pre-stampa) ---
    subprocess.run(["gs","-q","-dBATCH","-dNOPAUSE","-dSAFER","-sDEVICE=pdfwrite",
        "-dProcessColorModel=/DeviceGray","-dColorConversionStrategy=/Gray",
        "-dCompatibilityLevel=1.6","-dEmbedAllFonts=true","-dSubsetFonts=true",
        "-dAutoRotatePages=/None","-dDownsampleGrayImages=false",
        "-o",OUTPDF, INTER], check=True)
    n2=len(pypdf.PdfReader(OUTPDF).pages)
    print(f"Master DeviceGray: {OUTPDF}")
    print(f"Pagine: {n2} | multiplo4: {n2%4==0} | indice@{fi} | ParteI@{fb}=folio1 | bianche-senza-folio: {len(blanks)}")
