# INDICE SINTESI — FASE 2, stato delle schede

> Legenda: ⬜ da fare · 🟨 in corso · ✅ completato
> Metodo: UNA scheda tematica cross-sito per sessione. Fonti = card di mappatura (specialmente i §6).
> Ordine confermato della FASE 2: **S1 → S2 → S3 → S4** (vedi ROADMAP §4).

## S1 — Consolidamento (card per-sito → schede tematiche cross-sito)

Un cluster per scheda. Fonde i 2-3 trattamenti per-sito in una visione comparata
(pattern comune + varianti per sito + GOLD + mappa capitolo).

- ✅ **S1-C1 Backend Core & Bootstrap** — fonti SPW-C1, SR-C1, DIS-C1 (+ FDCA §3). → CAP 3/5/14.
  Scala a 3 gradini (SQLite grado-zero DIS / MySQL essenziale SPW / MySQL ingegnerizzato SR);
  GOLD init-fossile, credenziali-default, errore-connessione. Corregge 2 sviste in CAP 3.
- ✅ **S1-C2 Security & Auth** — fonti SPW-C2, SR-C2, DIS-C2 (+ SPW-C11 voter_hash, DIS-C10 contesto voto). → CAP 10 (princ.) + ponti CAP 13/11/17.
  Scala a 3 gradini RIBALTATA (SPW maturo / SR parziale / DIS grado-zero) — più ingegnerizzato ≠ più sicuro;
  CSRF a 3 gradini, flag cookie, IP grezzo-come-pregio (DIS), anti-frode voto + voter_hash, reset-a-un-clic.
  Corregge/amplia 4 punti in CAP 10 (§1.1 cookie Strict≠Lax, §1.2 username, §3 brute-force, §6 DDoS→CAP 11).
- ✅ **S1-C3 Frontend Bridge & State** — fonti SPW-C3, SR-C3, DIS-C3 (FDCA: nessun api.ts → fuori scala). → CAP 6 (princ.) + ponti CAP 10/9/4.
  Stesso oggetto `api` su fetch, ma tre investimenti diversi attorno a un'API non-uniforme:
  state-layer/loader+Double Read (SPW) / token CSRF in-memory (SR) / codemod fix_api (DIS).
  GOLD: 3 modi di leggere il payload, codemod, messaggio-backend-perso (3 punti stesso esito),
  token CSRF & reload, guard loader-vs-componente, niente interceptor 401. Corregge CAP 6 (§1.1
  "Double Read" è il nome SBAGLIATO; §1.1/3.1/3.2/4 sono prescrizioni DIS-flavored).
- ✅ **S1-C4 Content APIs** — fonti SPW-C4, SR-C4, DIS-C4 (FDCA = DIS). → CAP 9 (princ.) + ponti CAP 6/3/15/10.
  Stesso endpoint-router su REQUEST_METHOD; CHIUDE il Double Read di S1-C3 (contratto non-uniforme lato
  server: solo articles={data,total} SPW / mosaico 3 buste SR / busta-zero DIS). GOLD: paginazione
  (chi conta), "tre modi di sbagliare il fuso" sui post programmati, schema-solo-nel-.sqlite (DIS),
  residui-di-migrazione, tag-doppia-scrittura (SPW), tre-slug (SR), 404-non-403. Corregge CAP 9 (§2.2
  T↔spazio non è "lo standard"; §4 M:N non è esclusivo né universale; §1.1 matrice è SPW; §5 bypass 3 forme).
- ✅ **S1-C5 Media & Upload** — fonti SPW-C5, SR-C5, DIS-C5 (FDCA = DIS, RCE ereditata). → CAP 7 (princ.) + ponti CAP 10/16-17/14.
  Stesso scheletro upload.php+GD, ma la SICUREZZA scala all'inverso: 3 barriere SPW / 1 SR / ≈0 + upload
  PUBBLICO DIS = catena RCE verificata. Ribaltamento: il naming più minimale (SR, nome scartato) è il
  più sicuro; quello più gentile (DIS, nome+ext conservati) abilita la RCE. GOLD: catena-RCE-pubblica,
  difesa-3/1/0-livelli, tre-modi-di-nominare, $_FILES['type']-non-è-validazione, path-guard
  realpath/basename/strpos + delete-senza-CSRF, disco-come-DB-media, WebP-non-universale, one-shot-non-gated.
  Corregge CAP 7 (manca del tutto la sicurezza upload; §3.3 .htaccess è PHP-off non solo cache; §3.1 WebP non universale).
- ✅ **S1-C6 Advanced Editing / Editor** — fonti SPW-C6, SR-C6, DIS-C6 (FDCA = editor assente). → CAP 8 (princ.) + ponti CAP 10/11/7.
  Scala a 3 gradini: Tiptap-blindato SPW / Tiptap + shim migrazione Quill→Tiptap SR / contentEditable+execCommand DIS.
  Difesa XSS-stored = solo render-time DOMPurify (DIS l'UNICO senza = scoperto). GOLD: scala-editor, choke-point-render,
  sito-senza-DOMPurify, shim-Quill→Tiptap, guardie-inserimento, "sembra sanitize ma non lo è". Corregge CAP 8 (§3
  l'editor NON è "native-React senza deps" = è Tiptap; "Paste Protection" sovradichiarata; manca del tutto DOMPurify/sicurezza).
- ✅ **S1-C7 SEO & Prerendering** — fonti SPW-C7, SR-C7, DIS-C7 (FDCA fuori scala). → CAP 11 (princ.) + ponti CAP 8/10/9.
  Scala a 3 gradini: Dynamic Rendering completo SPW≡SR (UA-sniff + body) / OG-proxy leggero solo-meta DIS. SALDA S1-C6→C7:
  il prerender riemette content con strip_tags-allowlist (≠ DOMPurify) = buco XSS-attributi via UA-spoof (SR copia il motore
  di SPW + la falla); DIS immune per sottrazione. GOLD: 3-gradini, buco-XSS-copiato, seo-cache-morta SR, SEO-indicizza-bozze
  SR+DIS, due-sistemi-SEO-divergono, archeologia-SSG. Corregge CAP 11 (raccomanda l'SSG che SPW ha SCARTATO; esempio SQLite
  attribuito a SPW-MySQL; manca Dynamic Rendering, buco XSS, visibilità, seo-cache, sitemap/JSON-LD).
- ⬜ S1-C8 RSS & Feed — fonti SPW-C8, SR-C8, DIS-C8
- ⬜ S1-C9 Newsletter & Email — fonti SPW-C9, SR-C9, DIS-C9
- ⬜ S1-C10 Festival Logic — fonte DIS-C10 (solo DIS; FDCA eredita)
- ⬜ S1-C11 Engagement & Reactions — fonte SPW-C11 (solo SPW)
- ⬜ S1-C12 Admin Dashboard & Panels — fonti SPW-C12, SR-C12, DIS-C12
- ⬜ S1-C13 DB Evolution & Incidenti — fonti SR-C13, DIS-C1 (meccanismo update_db_*), SPW-C1 (init fossile)
- ⬜ S1-FORK FDCA come caso "fork/evoluzione" — fonte FDCA-DIFF (non aggiunge pattern: backend = DIS)

## S2 — Inventario contenuti
- ⬜ Cosa entra / aggiorna / è nuovo / si scarta vs i 19 capitoli esistenti.

## S3 — Scaletta / indice globale
- ⬜ Struttura a Parti + capitoli, con mappa card→capitolo.

## S4 — Validazione indice con Simone
- ⬜ GATE prima della scrittura (FASE 3).

---

### Stato globale FASE 2
- **7 / 14 schede S1 completate** (S1-C1 ✅, S1-C2 ✅, S1-C3 ✅, S1-C4 ✅, S1-C5 ✅, S1-C6 ✅, S1-C7 ✅). Prossima: **S1-C8 RSS & Feed**.
