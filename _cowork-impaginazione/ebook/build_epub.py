#!/usr/bin/env python3
import os, re, subprocess, pypandoc
HERE=os.path.dirname(os.path.abspath(__file__))
COWORK=os.path.dirname(HERE); REPO=os.path.dirname(COWORK)
MAN=os.path.join(REPO,"manuale"); PANDOC=pypandoc.get_pandoc_path()
STRUCT=[
 ("I","La Visione","Il perché. La filosofia che guida ogni decisione tecnica.",["CAPITOLO 1 - Manifesto"]),
 ("II","L'Architettura","Le fondamenta. Struttura del progetto, database, stack tecnologico.",
   ["CAPITOLO 2 - Architettura e Struttura Progetto","CAPITOLO 3 - Database Strategy","CAPITOLO 4 - Frontend Dependencies"]),
 ("III","I Componenti","I mattoni. Backend, frontend, media, editor: i building block del sistema.",
   ["CAPITOLO 5 - Backend Logic (PHP)","CAPITOLO 6 - Frontend Bridge (API.ts)","CAPITOLO 7 - Media & Optimization","CAPITOLO 8 - Advanced Content Editing & Media Integration"]),
 ("IV","Il Flusso Operativo","Come i contenuti vivono. Dal ciclo di vita alla distribuzione, passando per sicurezza e SEO.",
   ["CAPITOLO 9 - Content Lifecycle","CAPITOLO 10 - Security & Auth","CAPITOLO 11 - SEO Pre-rendering con PHP Entry-Point","CAPITOLO 12 - RSS Feed & Syndication","CAPITOLO 13 - Newsletter & Email System","CAPITOLO 14 - Admin Dashboard & Panels"]),
 ("V","I Casi Reali","Dove la teoria incontra la produzione. Pattern estratti da progetti reali, con le loro cicatrici.",
   ["CAPITOLO 15 - Database Evolution - Da SQLite a MySQL","CAPITOLO 16 - Portfolio & Projects Module","CAPITOLO 17 - Festival Logic - Iscrizioni e Workflow Approvazione","CAPITOLO 18 - Festival Logic - Votazioni e Protezione Anti-Frode","CAPITOLO 19 - Festival Logic - Dashboard Admin, Settings e Reporting","CAPITOLO 20 - Social Interactions & Reactions"]),
 (None,"Appendici","Strumenti pratici e casi di confine.",
   ["BOILERPLATE-CHECKLIST","APPENDICE B - Ciclo di vita di un fork","APPENDICE C - Testing e Deploy"]),
]
def read(stem): return open(os.path.join(MAN,stem+".md"),encoding="utf-8").read()

# estrai la dedica (blockquote epigrafe) dal CAP1 e rimuovila da quel contenuto
cap1=read("CAPITOLO 1 - Manifesto")
m=re.search(r"(^#[^\n]*\n)(.*?)(\n---\n)", cap1, re.S)
dedica_lines=[]
if m:
    head=m.group(1); mid=m.group(2)
    bq=[ln for ln in mid.splitlines() if ln.strip().startswith(">")]
    if bq:
        for ln in bq:
            t=ln.lstrip(">").strip()
            if t: dedica_lines.append(t)
        # rimuovi blockquote + il --- successivo dal cap1
        cap1=cap1.replace(m.group(2)+m.group(3), "\n", 1)
dedica_md="\n\n".join(dedica_lines) if dedica_lines else "*A chi costruisce in piccolo, ma sul serio.*"

out=[]
out.append("::: dedica\n"+dedica_md+"\n:::\n")
for num,title,desc,files in STRUCT:
    label=f"PARTE {num} — {title}" if num else title
    out.append(f"\n# {label}\n\n*{desc}*\n")
    for stem in files:
        txt = cap1 if stem=="CAPITOLO 1 - Manifesto" else read(stem)
        out.append("\n"+txt.strip()+"\n")
out.append("\n# L'autore\n\nSimone Pizzi è autore ed editore. Ha fondato Runtime Edizioni e Runtime Radio, "
"per cui cura progetti editoriali, sonori e digitali. Ha pubblicato la raccolta di racconti "
"«L'Albero dei Racconti» e la novella di fantascienza «Frequenza di Servizio».\n\n"
"Questo manuale nasce dal lavoro reale su quattro siti in produzione (SitoRuntime, "
"DISINTELLIGENZA, FDCA e SimonePizziWebSite) e raccoglie il protocollo «thin stack» "
"con cui li ha costruiti: React e TypeScript per la presentazione, PHP nativo e SQLite "
"o MySQL per i dati, senza framework di backend né infrastruttura sproporzionata.\n")
combined=os.path.join(HERE,"combined.md")
open(combined,"w",encoding="utf-8").write("\n".join(out))

epub=os.path.join(HERE,"React-PHP-The-Thin-Stack.epub")
cmd=[PANDOC, combined, "-o", epub,
     "-f","gfm+alerts+fenced_divs","--toc","--toc-depth=1","--split-level=1",
     "--css",os.path.join(HERE,"epub.css"),
     "--epub-cover-image",os.path.join(COWORK,"copertina","ebook_cover_16.jpg"),
     "--metadata-file",os.path.join(HERE,"metadata.yaml")]
r=subprocess.run(cmd,capture_output=True,text=True)
print("pandoc rc:",r.returncode)
if r.stderr.strip(): print(r.stderr[:1500])
print("EPUB:", epub if os.path.exists(epub) else "NON creato",
      "|", os.path.getsize(epub) if os.path.exists(epub) else 0, "byte")
