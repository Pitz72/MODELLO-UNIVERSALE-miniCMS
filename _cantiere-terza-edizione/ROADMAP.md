# ROADMAP — TERZA EDIZIONE del Manuale "React + PHP: The Thin Stack"

> Documento di riferimento condiviso (Simone ⇄ Claude). Tutto il lavoro della Terza Edizione passa di qui.
> **Principio guida:** lavoro **microscopico, atomico, multi-sessione**. Una sessione = una unità di lavoro piccola e isolata. Mai passate globali in un unico contesto.

---

## 0. Regole operative (valide per OGNI sessione)

1. **Una unità per sessione — con accorpamento SELETTIVO.** Un'unità = una "card" di mappatura (1 sito × 1 cluster) oppure 1 micro-step di scrittura. Se troppo grande, si spezza (es. `parte 1/2`). **Dal 2026-06-15** (Opus 4.8 a 1M di contesto): si possono accorpare nella stessa sessione **solo coppie di cluster già accoppiati** (max 2, mai 3), mantenendo **file-card separati + righe LOG separate**. Per SitoRuntime le coppie sono **C4+C5** (Content + Media/Upload) e **C7+C8** (SEO + RSS, emettitori dello stesso contenuto); **C9, C12, C13 restano da sole** (C13 incidenti DB = alto valore e corposo). Motivo: il contesto grande rilassa il limite tecnico, non quello di *qualità* (profondità microscopica + §6 + GOLD dipendono dall'attenzione su una lente e dalla lunghezza dell'output ~250-350 righe/card).
2. **Ciclo di chiusura obbligatorio** ad ogni step: salva → aggiorna `LOG.md` → `git add/commit/push` → verifica sync locale=remoto → scrivi/aggiorna `PROSSIMA-SESSIONE.md` con il prompt pronto.
3. **Criterio di STOP di una sezione:** la card è in stato `COMPLETATO` (tutte le voci del template compilate o marcate `N/A`), committata e pushata, log aggiornato, prompt della sessione successiva preparato.
4. **Fonti = stato reale dei siti, oggi.** Si cita sempre `percorso/file.php:linea`. Niente memoria/supposizioni: si legge il codice.
5. **Niente lavoro distruttivo** sui siti sorgente (sola lettura). Le modifiche avvengono solo nel repo del manuale.
6. **Lingua:** solo italiano. Registro narrativo e chiaro, ma è un **manuale tecnico**: esempi reali e blocchi di codice inclusi.

---

## 1. Le fonti

| Sito | Path | DB | Ultima rel. nota | Ruolo nella mappatura |
|------|------|-----|------|------|
| **SimonePizziWebSite** | `…/SITI-WEB/SimonePizziWebSite` | MySQL (migr.) | v1.21.0 (12/06/26) | Flagship **contenuti/CMS** |
| **SitoRuntime** | `…/SITI-WEB/SitoRuntime` | MySQL (migr.) | v2.9.13 (12/06/26) | Flagship **scalabilità + problemi/soluzioni** |
| **DISINTELLIGENZA** | `…/SITI-WEB/DISINTELLIGENZA` | SQLite | feb 2026 | Base **festival** (votazioni/iscrizioni) |
| **FDCA** | `…/SITI-WEB/FDCA` | SQLite | fork | **Diff** rispetto a DISINTELLIGENZA |

---

## 2. I cluster tematici (cosa cercare in ogni sito)

Ogni cluster è una lente sulla filosofia React+PHP miniCMS — "estetica moderna ma funzionale". Non solo sicurezza/dashboard: **tutto il custom del CMS**.

- **C1 — Backend Core & Bootstrap**: `db.php`, `init_db`, auto-scaffolding, `config`, timezone, struttura `public/api`.
- **C2 — Security & Auth**: `auth`/`auth_helper`, sessioni, cookie, `.htaccess`, CORS, protezione dati/anti-frode.
- **C3 — Frontend Bridge & State**: `api.ts` (pattern Double Read), hooks, loaders, routing, gestione errori.
- **C4 — Content APIs**: news/articles, categorie, tag, ricerca, navigazione, paginazione.
- **C5 — Media & Upload**: `upload.php`, `media.php`, ottimizzazione immagini, `migrate_media`, download.
- **C6 — Advanced Editing / Editor**: editor di testo (Quill o custom), sanitizzazione, embed media nel contenuto.
- **C7 — SEO & Prerendering**: `prerender`, `rebuild_seo_cache`, `debug_seo`, meta/entry-point PHP.
- **C8 — RSS & Feed Syndication**: `rss.php`, `feed*`, `feed_config`, URN/GUID.
- **C9 — Newsletter & Email**: `newsletter`, `newsletter_send`, `subscribers`, `contact`.
- **C10 — Festival Logic**: `participants`, `votes`, `settings` (master switch), `reset_votes`, `stats`. *(solo DIS/FDCA)*
- **C11 — Engagement & Social**: `reactions`, `messages`, `contact`.
- **C12 — Admin Dashboard & Panels**: `admin`/`settings`/`stats`/`analytics`/`backup`, `AdminLayout`, UX admin.
- **C13 — DB Evolution & Incidenti**: `init_mysql`, `migrate_to_mysql`, WAL incidents, emergency reverts, **doc problemi/soluzioni**.

---

## 3. FASE 1 — MAPPATURA (atomica, una card per sessione)

Output: una **card** per `(sito, cluster)` in `_cantiere-terza-edizione/mappatura/<sito>/`, secondo `_TEMPLATE.md`.
Ordine: prima il flagship contenuti, poi scalabilità, poi festival, infine il diff.

### 3.1 SimonePizziWebSite (flagship contenuti)
- [x] SPW-C1 Backend Core & Bootstrap
- [x] SPW-C2 Security & Auth
- [x] SPW-C3 Frontend Bridge & State
- [x] SPW-C4 Content APIs (articles/categories/tags/search/navigation)
- [x] SPW-C5 Media & Upload
- [x] SPW-C6 Advanced Editing / Editor
- [x] SPW-C7 SEO & Prerendering
- [x] SPW-C8 RSS & Feed
- [x] SPW-C9 Newsletter & Email
- [x] SPW-C11 Engagement & Social (reactions/messages)
- [x] SPW-C12 Admin Dashboard & Panels

### 3.2 SitoRuntime (flagship scalabilità + incidenti)
- [x] SR-C1 Backend Core & Bootstrap
- [x] SR-C2 Security & Auth (+ CORS)
- [x] SR-C3 Frontend Bridge & State
- [x] SR-C4 Content APIs (news + speakers + podcasts) ┐ *(coppia: 1 sessione)*
- [x] SR-C5 Media & Upload                            ┘
- [x] SR-C6 Advanced Editing / Editor *(gap colmato 18/06)* — Tiptap v3 + **shim migrazione Quill→Tiptap**; DOMPurify al render; guardia link più debole di SPW
- [x] SR-C7 SEO & Prerendering (+ seo-cache) ┐ *(coppia: 1 sessione)*
- [x] SR-C8 RSS & Feed                       ┘
- [x] SR-C9 Newsletter & Email *(sola)*
- [x] SR-C12 Admin Dashboard & Panels *(sola)*
- [x] SR-C13 DB Evolution & Incidenti (MySQL, WAL, emergency) — **alto valore** *(sola)* — **(SitoRuntime COMPLETO, 10 card)**

### 3.3 DISINTELLIGENZA (base festival)
- [x] DIS-C1 Backend Core & Bootstrap — **SQLite VIVO** (db-a-file corrente, non fossile): PDO singleton minimale, zero config/segreti, `.data/` auto-creata, init fossile *parziale* (v0.3.6), versionamento per nomi-file `update_db_*`
- [x] DIS-C2 Security & Auth (+ anti-frode voto) — **GOLD: auth grado-zero (no CSRF/rate-limit/fixation/recovery); admin solo nel .sqlite; anti-frode voto IP/24h REMOTE_ADDR; backup pre-distruttivo (≠ SR-C13)**
- [x] DIS-C3 Frontend Bridge & State *(gap colmato 18/06)* — **GOLD: error-handling INIETTATO da codemod `fix_api` (ripetizioni, metodi sfuggiti, riga duplicata)**; oggetto-namespace, no CSRF, "busta zero"
- [x] DIS-C4 Content APIs (news/podcasts) ┐ *(coppia: 1 sessione, come SR-C4+C5)*
- [x] DIS-C5 Media & Upload                ┘ — **GOLD: upload pubblico partecipanti + MIME client spoofabile + no PHP-off = catena RCE**
- [x] DIS-C6 Advanced Editing / Editor *(gap colmato 18/06)* — **GOLD: editor custom `contentEditable`+`execCommand` (no Tiptap), link via `prompt` senza guardia, NESSUN DOMPurify = stored-XSS scoperto**
- [x] DIS-C7 SEO & Prerendering *(gap colmato 18/06)* ┐ *(coppia, come SR-C7+C8)* — OG-proxy leggero (solo meta escaped, no body prerender, no UA-sniff): più sicuro di SR-C7 per sottrazione
- [x] DIS-C8 RSS & Feed *(gap colmato 18/06)*          ┘ — feed **podcast iTunes** (no RSS news); GOLD: commenti "ragionamento ad alta voce" in produzione; settings podcast_* mai popolati
- [x] DIS-C9 Newsletter & Email (+ contact) — **GOLD: mail() nativa, NO double opt-in, NO token disiscrizione (forgeable), invio sincrono nudo, email header injection via name; ma FILTER_VALIDATE_EMAIL + strip_tags write-time**
- [x] DIS-C10 Festival Logic (participants/votes/settings/stats) — **cuore del sito; GOLD: macchina a stati + round manuali via flag + vote_count denormalizzato (classifica) + master switch pubblici + report finale disabilitato + finalist vestigiale**
- [x] DIS-C12 Admin Dashboard & Panels — **via di mezzo SR/SPW: AdminLayout (come SPW) + guard-componente (come SR), dashboard che MISURA (stats.php, no Chart.js); GOLD: contacts write-only (mai letti), guard role-blind, reset senza CSRF** — **(DISINTELLIGENZA COMPLETO, 7 card)**

### 3.4 FDCA (diff)
- [x] FDCA-DIFF — **"Festival della Canzone Artificiale", fork di DIS: backend PHP byte-IDENTICO (tutti i GOLD ereditati, RCE inclusa, nessuno risolto); frontend riscritto/ridotto/SCOLLEGATO (no admin, no api.ts, no fetch); re-brand via Google AI Studio; v0.0.1 + ROADMAP-EVOLUZIONE-miniCMS (9 cap)** — **FASE 1 CONCLUSA**

> Stima ~30 sessioni di mappatura. L'elenco è vivo: si aggiungono/splittano card quando il codice lo richiede.

---

## 4. FASE 2 — SINTESI

- [ ] S1 — Consolidamento: da card per-sito a **schede tematiche cross-sito** (dedup, pattern comuni, varianti). *(2/14 schede — stato in `sintesi/_INDICE-SINTESI.md`)*
  - [x] S1-C1 Backend Core & Bootstrap → `sintesi/S1-C1-backend-core.md` (scala a 3 gradini SQLite/MySQL-essenziale/MySQL-ingegnerizzato; GOLD init-fossile/credenziali-default/errore-connessione; corregge 2 sviste in CAP 3)
  - [x] S1-C2 Security & Auth → `sintesi/S1-C2-security-auth.md` (scala a 3 gradini RIBALTATA: SPW maturo / SR parziale / DIS grado-zero, "più ingegnerizzato ≠ più sicuro"; GOLD CSRF-a-3-gradini, flag-cookie, IP-grezzo-come-pregio, anti-frode-voto + voter_hash, reset-a-un-clic + backup; corregge/amplia 4 punti in CAP 10)
- [ ] S2 — Inventario contenuti: cosa entra nel libro, cosa si aggiorna, cosa è nuovo, cosa si scarta.
- [ ] S3 — **Scaletta/Indice globale** della Terza Edizione (struttura a Parti + capitoli, con mappa card→capitolo).
- [ ] S4 — Validazione indice con Simone (gate prima della scrittura).

---

## 5. FASE 3 — SCRITTURA (capitolo per capitolo, micro-step)

Regola: un micro-step = una sezione/capitolo. Ogni capitolo: prosa chiara e "raccontata" + blocchi di codice reali (`path:linea` come origine) + box problemi/soluzioni dove pertinente.
- [ ] (le card di scrittura verranno generate da S3)

---

## 6. FASE 4 — PASSAGGIO EDITORIALE & PUBBLICAZIONE

- [ ] E1 — Uniformità di tono, footer "Prossimo Capitolo", intro di Parte.
- [ ] E2 — **Allineamento etichetta edizione**: oggi incoerente (README/_master = "Prima Edizione"; build-pdf.sh/articolo = "Seconda Edizione"). Decidere e uniformare a **Terza Edizione**.
- [ ] E3 — Build PDF/ebook (`build-pdf.sh`) e verifica.

---

## 7. Stato globale

- **Fase corrente:** 🟨 **FASE 2 — SINTESI, sotto-fase S1 (Consolidamento) avviata.** FASE 1 conclusa (4 siti, 34 card, copertura completa). FASE 2 in corso: **2/14 schede tematiche S1 completate** (S1-C1 Backend Core, S1-C2 Security & Auth).
- **Prossima unità:** FASE 2 / **S1-C3 Frontend Bridge & State** (cross-sito) — fonti SPW-C3, SR-C3, DIS-C3 (pattern api.ts: Double Read SPW / token-CSRF in-memory SR / codemod `fix_api` DIS). Vedi `PROSSIMA-SESSIONE.md`.
- **Log completo:** `LOG.md`.
