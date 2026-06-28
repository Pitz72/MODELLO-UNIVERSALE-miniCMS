#!/usr/bin/env python3
# Build EPUB — "React + PHP: The Thin Stack" (EN, US edition).
# EN variant of build_epub.py: source = manuale-en/, EN STRUCT/paratexts/BIO,
# EN metadata (metadata_en.yaml). Reuses epub.css and the ebook cover image
# (front title is already English).
import os, re, subprocess, pypandoc
HERE=os.path.dirname(os.path.abspath(__file__))
COWORK=os.path.dirname(HERE); REPO=os.path.dirname(COWORK)
MAN=os.path.join(REPO,"manuale-en"); PANDOC=pypandoc.get_pandoc_path()
STRUCT=[
 ("I","The Vision","The why. The philosophy that guides every technical decision.",["CHAPTER 01 - Manifesto"]),
 ("II","The Architecture","The foundations. Project structure, database, technology stack.",
   ["CHAPTER 02 - Architecture & Project Structure","CHAPTER 03 - Database Strategy","CHAPTER 04 - Frontend Dependencies"]),
 ("III","The Components","The bricks. Backend, frontend, media, editor: the building blocks of the system.",
   ["CHAPTER 05 - Backend Logic (PHP)","CHAPTER 06 - Frontend Bridge (API.ts)","CHAPTER 07 - Media & Optimization","CHAPTER 08 - Advanced Content Editing & Media Integration"]),
 ("IV","The Operational Flow","How content lives. From the lifecycle to distribution, by way of security and SEO.",
   ["CHAPTER 09 - Content Lifecycle","CHAPTER 10 - Security & Auth","CHAPTER 11 - SEO Pre-rendering with a PHP Entry Point","CHAPTER 12 - RSS Feed & Syndication","CHAPTER 13 - Newsletter & Email System","CHAPTER 14 - Admin Dashboard & Panels"]),
 ("V","The Real-World Cases","Where theory meets production. Patterns extracted from real projects, with their scars.",
   ["CHAPTER 15 - Database Evolution - From SQLite to MySQL","CHAPTER 16 - Portfolio & Projects Module","CHAPTER 17 - Festival Logic - Submissions & Approval Workflow","CHAPTER 18 - Festival Logic - Voting & Anti-Fraud Protection","CHAPTER 19 - Festival Logic - Admin Dashboard, Settings & Reporting","CHAPTER 20 - Social Interactions & Reactions"]),
 (None,"Appendices","Practical tools and edge cases.",
   ["APPENDIX A - Boilerplate Checklist","APPENDIX B - The Life of a Fork","APPENDIX C - Testing & Deployment"]),
]
def read(stem): return open(os.path.join(MAN,stem+".md"),encoding="utf-8").read()

# extract the dedication (epigraph blockquote) from CH1 and remove it from that content
cap1=read("CHAPTER 01 - Manifesto")
m=re.search(r"(^#[^\n]*\n)(.*?)(\n---\n)", cap1, re.S)
dedica_lines=[]
if m:
    head=m.group(1); mid=m.group(2)
    bq=[ln for ln in mid.splitlines() if ln.strip().startswith(">")]
    if bq:
        for ln in bq:
            t=ln.lstrip(">").strip()
            if t: dedica_lines.append(t)
        # remove the blockquote + the following --- from cap1
        cap1=cap1.replace(m.group(2)+m.group(3), "\n", 1)
dedica_md="\n\n".join(dedica_lines) if dedica_lines else "*For those who build small, but in earnest.*"

out=[]
out.append("::: dedica\n"+dedica_md+"\n:::\n")
for num,title,desc,files in STRUCT:
    label=f"PART {num} — {title}" if num else title
    out.append(f"\n# {label}\n\n*{desc}*\n")
    for stem in files:
        txt = cap1 if stem=="CHAPTER 01 - Manifesto" else read(stem)
        out.append("\n"+txt.strip()+"\n")
out.append("\n# The Author\n\nSimone Pizzi is an author and publisher. He founded Runtime Edizioni and Runtime Radio, "
"for which he curates editorial, audio, and digital projects. He has published the short-story collection "
"*L'Albero dei Racconti* (The Tree of Tales) and the science-fiction novella *Frequenza di Servizio* "
"(Service Frequency).\n\n"
"This manual grows out of real work on four production sites (SitoRuntime, DISINTELLIGENZA, FDCA, and "
"SimonePizziWebSite) and gathers the \"thin stack\" protocol he built them with: React and TypeScript for "
"the presentation, native PHP and SQLite or MySQL for the data, with no backend framework and no oversized "
"infrastructure.\n")
combined=os.path.join(HERE,"combined_en.md")
open(combined,"w",encoding="utf-8").write("\n".join(out))

epub=os.path.join(HERE,"React-PHP-The-Thin-Stack-EN.epub")
cmd=[PANDOC, combined, "-o", epub,
     "-f","gfm+alerts+fenced_divs","--toc","--toc-depth=1","--split-level=1",
     "--css",os.path.join(HERE,"epub.css"),
     "--epub-cover-image",os.path.join(COWORK,"copertina","ebook_cover_16.jpg"),
     "--metadata-file",os.path.join(HERE,"metadata_en.yaml")]
r=subprocess.run(cmd,capture_output=True,text=True)
print("pandoc rc:",r.returncode)
if r.stderr.strip(): print(r.stderr[:1500])
print("EPUB:", epub if os.path.exists(epub) else "NOT created",
      "|", os.path.getsize(epub) if os.path.exists(epub) else 0, "bytes")
