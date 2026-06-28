#!/usr/bin/env python3
# Build INTERIOR KDP — "React + PHP: The Thin Stack" (EN, US edition) — Typst
# EN variant of build_book.py: source = manuale-en/, EN STRUCT/paratexts/BIO,
# EN template (template_en.typ). Same 7x10" B/W grid, same IBM Plex fonts.
# .md -> fragments -> libro_en.typ -> master PDF (../master/), 2 passes:
#  pass1 counts pages and locates Contents/Part I/blanks;
#  pass2 inserts the blanks (multiple of 4) and a deterministic footer
#  (arabic folio from 1 on the body, roman on the Contents, NO folio on blanks).
import os, re, subprocess, shutil
import pypandoc, typst, pypdf, fitz

GS = shutil.which("gs") or shutil.which("gswin64c") or "gs"  # portable Win/Linux

PROD   = os.path.dirname(os.path.abspath(__file__))
COWORK = os.path.dirname(PROD)
REPO   = os.path.dirname(COWORK)
MAN    = os.path.join(REPO, "manuale-en")
FRAG   = os.path.join(PROD, "capitoli-typ-en")
MASTER = os.path.join(COWORK, "master")
FONTS  = os.path.join(REPO, "fonts", "IBM_Plex")
LIBRO  = os.path.join(PROD, "libro_en.typ")
OUTPDF = os.path.join(MASTER, "Interno_The-Thin-Stack_3ed_7x10_BN_EN.pdf")
INTER  = os.path.join(PROD, "_interno_rgb_en.pdf")  # intermediate (gitignore)
os.makedirs(FRAG, exist_ok=True); os.makedirs(MASTER, exist_ok=True)
PANDOC = pypandoc.get_pandoc_path()
LUA = os.path.join(PROD, "alerts.lua")

STRUCT = [
 ("I","The Vision","The why. The philosophy that guides every technical decision.",
   ["CHAPTER 01 - Manifesto"]),
 ("II","The Architecture","The foundations. Project structure, database, technology stack.",
   ["CHAPTER 02 - Architecture & Project Structure","CHAPTER 03 - Database Strategy",
    "CHAPTER 04 - Frontend Dependencies"]),
 ("III","The Components","The bricks. Backend, frontend, media, editor: the building blocks of the system.",
   ["CHAPTER 05 - Backend Logic (PHP)","CHAPTER 06 - Frontend Bridge (API.ts)",
    "CHAPTER 07 - Media & Optimization","CHAPTER 08 - Advanced Content Editing & Media Integration"]),
 ("IV","The Operational Flow","How content lives. From the lifecycle to distribution, by way of security and SEO.",
   ["CHAPTER 09 - Content Lifecycle","CHAPTER 10 - Security & Auth",
    "CHAPTER 11 - SEO Pre-rendering with a PHP Entry Point","CHAPTER 12 - RSS Feed & Syndication",
    "CHAPTER 13 - Newsletter & Email System","CHAPTER 14 - Admin Dashboard & Panels"]),
 ("V","The Real-World Cases","Where theory meets production. Patterns extracted from real projects, with their scars.",
   ["CHAPTER 15 - Database Evolution - From SQLite to MySQL","CHAPTER 16 - Portfolio & Projects Module",
    "CHAPTER 17 - Festival Logic - Submissions & Approval Workflow",
    "CHAPTER 18 - Festival Logic - Voting & Anti-Fraud Protection",
    "CHAPTER 19 - Festival Logic - Admin Dashboard, Settings & Reporting",
    "CHAPTER 20 - Social Interactions & Reactions"]),
 (None,"Appendices","Practical tools and edge cases.",
   ["APPENDIX A - Boilerplate Checklist","APPENDIX B - The Life of a Fork","APPENDIX C - Testing & Deployment"]),
]
IMPORT = '#import "../template_en.typ": admonition, horizontalrule\n'

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
            if stem=="CHAPTER 01 - Manifesto": txt,dedica=extract_dedica(txt)
            if not txt.startswith("#import"): txt=IMPORT+txt
            open(out,"w",encoding="utf-8").write(txt)
            order.append(("chap",os.path.basename(out)))
    return order,(dedica or "_[ dedication ]_")

BIO=("Simone Pizzi is an author and publisher. He founded Runtime Edizioni and Runtime Radio, "
"for which he curates editorial, audio, and digital projects. He has published the short-story "
"collection _L'Albero dei Racconti_ (The Tree of Tales) and the science-fiction novella "
"_Frequenza di Servizio_ (Service Frequency).\n\n"
"This manual grows out of real work on four production sites — SitoRuntime, DISINTELLIGENZA, "
"FDCA, and SimonePizziWebSite — and gathers the \"thin stack\" protocol he built them with: "
"React and TypeScript for the presentation, native PHP and SQLite or MySQL for the data, "
"with no backend framework and no oversized infrastructure.")

def footer_block(blanks, fi, fb):
    if fi is None:  # pass1: no footer
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
    L=['#import "template_en.typ": *','#show: conf','']
    L.append(footer_block(blanks,fi,fb))
    L += ['#set page(numbering: none)','',
    '// p.1 FRONTISPIECE','#align(center + horizon)[',
    '  #text(size: 27pt, weight: "semibold")[React + PHP:\\ The Thin Stack]','  #v(0.6em)',
    '  #text(size: 13pt, style: "italic", fill: luma(60))[The miniCMS protocol for modern web apps]',
    '  #v(3.5em)','  #text(size: 13pt)[Simone Pizzi]','  #v(0.3em)',
    '  #text(size: 10pt, fill: luma(90))[Third Edition]','  #v(7em)',
    '  #text(size: 11pt, tracking: 2pt)[RUNTIME EDIZIONI]',']',
    '#pagebreak()','#pagebreak()','',
    '// p.3 COLOPHON','#v(1fr)','#[#set par(justify: false, leading: 0.7em)',
    '#text(size: 9pt, fill: luma(30))[','React + PHP: The Thin Stack \\',
    'The miniCMS protocol for modern web apps \\','Third Edition --- June 2026 \\','#v(0.8em)',
    '© 2026 Simone Pizzi \\','© 2026 Runtime Edizioni \\','#v(0.8em)',
    "All rights reserved. No part of this book may be reproduced without the written consent of the publisher, except for brief quotations in reviews. \\",
    '#v(0.8em)','The trademarks and product names cited are the property of their respective owners. \\',
    'www.runtimeradio.com',']]','#pagebreak()','#pagebreak()','',
    '// p.5 DEDICATION','#align(right + horizon)[',
    '  #block(width: 75%)[#set par(justify: false, leading: 0.8em)','#set align(right)',dedica,'  ]',']',
    '#pagebreak()','',
    '// CONTENTS','#pagebreak(to: "odd")',
    '#outline(title: [Contents], depth: 2, indent: 1.2em)','',
    '// BODY','']
    for it in order:
        if it[0]=="part":
            _,num,title,desc=it; na=f'"{num}"' if num else "none"
            L.append(f'#part({na}, "{title}", "{desc}")')
        else:
            L.append(f'#include "capitoli-typ-en/{it[1]}"')
    L += ['','// BIO','#pagebreak(weak: true)','#v(2cm)',
          '#text(weight: "semibold", size: 18pt)[The Author]','#v(0.8em)',
          '#line(length: 100%, stroke: 0.6pt + luma(160))','#v(0.8em)']
    for para in BIO.split("\n\n"): L += [para.strip(),'']
    if pad>0:
        L.append('// blank pages -> multiple of 4')
        for _ in range(pad): L += ['#pagebreak(weak: false)','#text[~]']
    open(LIBRO,"w",encoding="utf-8").write("\n".join(L))

def compile_to(out): typst.compile(LIBRO, output=out, font_paths=[FONTS])

def detect(pdf):
    doc=fitz.open(pdf); H=720; bot=20*72/25.4; fi=fb=None; blanks=[]
    for i,p in enumerate(doc):
        t=p.get_text()
        if fi is None and re.search(r'\bContents\b',t): fi=i+1
        if fb is None and re.search(r'P\s*A\s*R\s*T(?![a-z])',t): fb=i+1
        # blank = no span inside the grid
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
    print("dedica extracted:", "YES" if dedica and "dedication" not in dedica else "NO (placeholder)")
    write_libro(order,dedica,0)                 # pass1
    compile_to(INTER)
    n,fi,fb,blanks=detect(INTER)
    pad=(-n)%4
    blanks=list(blanks)+[n+k for k in range(1,pad+1)]
    write_libro(order,dedica,pad,blanks=blanks,fi=fi,fb=fb)   # pass2
    compile_to(INTER)
    # --- DeviceGray conversion (B/W pre-press); known to segfault on this Windows gs ---
    gray_ok=False
    try:
        r=subprocess.run([GS,"-q","-dBATCH","-dNOPAUSE","-dSAFER","-sDEVICE=pdfwrite",
            "-dProcessColorModel=/DeviceGray","-dColorConversionStrategy=/Gray",
            "-dCompatibilityLevel=1.6","-dEmbedAllFonts=true","-dSubsetFonts=true",
            "-dAutoRotatePages=/None","-dDownsampleGrayImages=false",
            "-o",OUTPDF, INTER], timeout=600)
        gray_ok = (r.returncode==0 and os.path.exists(OUTPDF)
                   and len(pypdf.PdfReader(OUTPDF).pages)==len(pypdf.PdfReader(INTER).pages))
    except Exception as e:
        print("gs DeviceGray failed:", e)
    if not gray_ok:
        # fallback: the Typst interior is already grayscale (luma()+black only, no images,
        # single-component ICC), so it is print-ready B/W as-is.
        shutil.copyfile(INTER, OUTPDF)
        print("NOTE: ghostscript DeviceGray skipped/failed -> using the Typst grayscale interior as master.")
    n2=len(pypdf.PdfReader(OUTPDF).pages)
    print(f"Master: {OUTPDF}")
    print(f"Pages: {n2} | multiple-of-4: {n2%4==0} | Contents@{fi} | PartI@{fb}=folio1 | blanks-without-folio: {len(blanks)}")
