# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟨 FASE 2 (SINTESI) in corso. S1-C1 ✅, S1-C2 ✅, S1-C3 ✅, S1-C4 ✅, S1-C5 ✅ COMPLETATE.
> Questa è la SESTA scheda di sintesi: **S1-C6 Advanced Editing / Editor**. Ordine confermato:
> S1 → S2 → S3 → S4 (nessuna deviazione).

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md, _cantiere-terza-edizione/LOG.md e
_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md per il contesto.

STATO: FASE 1 (mappatura) CONCLUSA — 4 siti, 34 card, copertura COMPLETA. FASE 2 (SINTESI) in corso:
**5/14 schede S1 completate** (S1-C1 Backend Core ✅, S1-C2 Security & Auth ✅, S1-C3 Frontend Bridge
✅, S1-C4 Content APIs ✅, S1-C5 Media & Upload ✅). Metodo: UNA scheda tematica cross-sito per
sessione, che fonde i 2-3 trattamenti per-sito di un cluster in UNA visione comparata (pattern comune
+ varianti per sito in tabella unica + GOLD + mappa→capitoli). Le fonti sono le card di mappatura
(specialmente i loro §6, già a confronto). NON si rilegge il codice sorgente: si consolida ciò che è
già mappato. Il template è `_cantiere-terza-edizione/sintesi/_TEMPLATE-SCHEDA.md`; i modelli già fatti
sono `S1-C1-backend-core.md` … `S1-C5-media-upload.md` (seguine struttura e livello di dettaglio).

UNITÀ DI QUESTA SESSIONE: **S1-C6 — Scheda tematica cross-sito "Advanced Editing / Editor"**.
Fonti primarie: SPW-C6, SR-C6, DIS-C6. Da consolidare (spunti dai §6 già scritti):
- **La scala a 3 gradini dell'editor — il GOLD portante:** SPW = **Tiptap v3 BLINDATO** (StarterKit +
  Image/Color/TextAlign/Table/Youtube-nocookie, guardie `isSafeLinkUrl` blocca javascript:/data: +
  `normalizeYoutubeUrl` host-whitelist); SR = **Tiptap v3 + SHIM di migrazione Quill→Tiptap**
  (`prepareForEditor` converte i vecchi iframe Quill, classe `ql-video` tenuta in config, residuo
  `react-quill.d.ts` → la memoria "SR usa Quill" è STALE: oggi è Tiptap) ma guardia link più DEBOLE
  (`setLink` nudo, no isSafeLinkUrl); DIS = **editor ARTIGIANALE `contentEditable` + `execCommand`**
  (DEPRECATA), zero dipendenze editor (solo `showdown` per paste markdown), link via `prompt()`→
  `createLink` SENZA validazione (javascript: passa).
- **Difesa XSS-stored interamente a RENDER-TIME (pattern comune):** il server salva `content` GREZZO
  (S1-C4), l'unico choke-point è il render React; ma la robustezza scala: SPW DOMPurify + hook iframe
  YouTube-only (SingleArticle dangerouslySetInnerHTML); SR DOMPurify al render pubblico
  (Article/SpeakerDetail/PodcastDetail) = robusto come SPW; DIS NESSUN DOMPurify (non installato) +
  NewsDetail dangerouslySetInnerHTML grezzo = UNICO sito senza difesa XSS-stored (grezzo in scrittura
  S1-C4 E in render) = stored-XSS scoperto.
- **Guardie d'inserimento link/media:** SPW `isSafeLinkUrl` (blocca javascript:/data:) +
  `normalizeYoutubeUrl` host-whitelist; SR setLink nudo (più debole); DIS prompt()→createLink senza
  guardia (javascript: passa). La "pulizia incolla" di DIS (strip stili/classi) è COSMETICA non
  sicurezza.
- **Embed media nel contenuto:** SPW riusa MediaSelectorModal→uploadMediaWithProgress/getMedia (ponte
  S1-C3/C5); SR insert immagine via input file diretto (no modale); DIS niente immagini/YouTube/tabelle
  nel testo (editor poverissimo).
- **Bozza / gotcha runtime:** SPW bozza localStorage no-autosave-server + NavigationBlocker, gotcha
  Tiptap v3 (shouldRerenderOnTransaction, setContent emitUpdate:false anti-bozze-fantasma); SR no
  bozza localStorage (solo beforeunload), preview admin dangerouslySetInnerHTML NON sanitizzato (self,
  basso rischio); DIS nessuna bozza.
- **Dove vive l'editor:** SPW RichTextEditor solo in ArticleEditor (ProjectEditor usa textarea
  semplice); SR Tiptap in ArticleEditor + SpeakerEditor (incorporato, non componente unico); DIS
  editor custom inline.
- **PONTE FORTE da S1-C5/C7:** il content grezzo emesso senza sanitize da prerender/RSS/newsletter è
  il rischio aperto già segnalato (SPW-C6 GOLD); il buco XSS-attributi di strip_tags-allowlist nel
  prerender (S1-C7) è il riemergere dello stesso content. Qui si consolida la mappa "4 emettitori del
  content".

Fai così:
1. Scrivi la scheda in `_cantiere-terza-edizione/sintesi/S1-C6-advanced-editing.md` seguendo
   `_TEMPLATE-SCHEDA.md` (0 una-frase · 1 pattern comune · 2 tabella varianti UNICA e deduplicata · 3
   GOLD/box · 4 mappa→capitoli · 5 scarti/dedup). La tabella comparativa va scritta UNA volta, pulita.
2. Mappa esplicitamente → capitoli esistenti: soprattutto **CAP 8 (Advanced Content Editing & Media
   Integration)**, con ponti a CAP 10 (Security, XSS-stored e guardie link), CAP 11 (SEO, il content
   grezzo nel prerender) e CAP 7 (Media, embed nel contenuto). Segnala eventuali CORREZIONI al testo
   attuale (come fatto per CAP 3/10/6/9/7 nelle schede precedenti). Verifica in particolare se CAP 8
   dice "Quill" — perché SR è migrato a Tiptap (memoria stale).
3. Aggiorna `_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md` (S1-C6 → ✅, contatore 6/14).

Criterio di STOP: scheda S1-C6 in stato COMPLETATO (pattern + varianti + GOLD + mappa capitolo).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna `_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md` (S1-C6 → ✅)
- aggiorna `_cantiere-terza-edizione/ROADMAP.md` (spunta S1-C6 in §4, aggiorna §7 stato globale)
- aggiungi UNA riga a `_cantiere-terza-edizione/LOG.md` (più recente IN BASSO)
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md, sia root sia in _cantiere-terza-edizione/) con la
  prossima scheda: **S1-C7 (SEO & Prerendering)** — fonti SPW-C7, SR-C7, DIS-C7 (Dynamic Rendering
  UA-sniff SPW≡SR / OG-proxy leggero senza UA-sniff DIS; buco XSS-attributi strip_tags-allowlist, seo-cache
  morta SR, regola visibilità dimenticata = bozze trapelano).
