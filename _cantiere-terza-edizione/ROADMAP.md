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

- [x] S1 — Consolidamento: da card per-sito a **schede tematiche cross-sito** (dedup, pattern comuni, varianti). **✅ CONCLUSA — 14/14 schede** (stato in `sintesi/_INDICE-SINTESI.md`)
  - [x] S1-C1 Backend Core & Bootstrap → `sintesi/S1-C1-backend-core.md` (scala a 3 gradini SQLite/MySQL-essenziale/MySQL-ingegnerizzato; GOLD init-fossile/credenziali-default/errore-connessione; corregge 2 sviste in CAP 3)
  - [x] S1-C2 Security & Auth → `sintesi/S1-C2-security-auth.md` (scala a 3 gradini RIBALTATA: SPW maturo / SR parziale / DIS grado-zero, "più ingegnerizzato ≠ più sicuro"; GOLD CSRF-a-3-gradini, flag-cookie, IP-grezzo-come-pregio, anti-frode-voto + voter_hash, reset-a-un-clic + backup; corregge/amplia 4 punti in CAP 10)
  - [x] S1-C3 Frontend Bridge & State → `sintesi/S1-C3-frontend-bridge.md` (stesso oggetto `api` su fetch, tre investimenti attorno a un'API non-uniforme: state-layer+Double Read SPW / token CSRF in-memory SR / codemod fix_api DIS; GOLD 3-modi-di-leggere-il-payload, codemod, messaggio-backend-perso, token-CSRF-&-reload, guard loader-vs-componente, niente-interceptor-401; FDCA fuori scala = nessun api.ts; corregge CAP 6 §1.1 nome "Double Read" sbagliato + §1.1/3.1/3.2/4 prescrizioni DIS-flavored)
  - [x] S1-C4 Content APIs → `sintesi/S1-C4-content-apis.md` (stesso endpoint-router su REQUEST_METHOD; CHIUDE il Double Read di S1-C3 lato server: solo articles={data,total} SPW / mosaico 3 buste SR / busta-zero DIS; scala ricco→grado-zero; GOLD paginazione-chi-conta, "tre modi di sbagliare il fuso" sui post programmati, schema-solo-nel-.sqlite DIS, residui-di-migrazione, tag-doppia-scrittura SPW, tre-slug SR, 404-non-403; corregge CAP 9 §2.2/§4/§1.1/§5)
  - [x] S1-C5 Media & Upload → `sintesi/S1-C5-media-upload.md` (stesso scheletro upload.php+GD, ma la SICUREZZA scala all'inverso: 3 barriere SPW / 1 SR / ≈0 + upload PUBBLICO DIS = catena RCE verificata; ribaltamento naming: il più minimale SR è il più sicuro, il più gentile DIS abilita la RCE; GOLD catena-RCE-pubblica, difesa-3/1/0, tre-modi-di-nominare, $_FILES['type']-non-è-validazione, path-guard realpath/basename/strpos + delete-senza-CSRF, disco-come-DB-media, WebP-non-universale, one-shot-non-gated; corregge CAP 7 = manca del tutto la sicurezza upload, §3.3 .htaccess è PHP-off non solo cache, §3.1 WebP non universale)
  - [x] S1-C6 Advanced Editing / Editor → `sintesi/S1-C6-advanced-editing.md` (scala a 3 gradini: Tiptap-blindato SPW / Tiptap + shim migrazione Quill→Tiptap SR / contentEditable+execCommand DIS; difesa XSS-stored = solo render-time DOMPurify, DIS l'UNICO senza = scoperto; GOLD scala-editor, choke-point-render, sito-senza-DOMPurify, shim-Quill, guardie-inserimento, "sembra sanitize ma non lo è"; corregge CAP 8 = l'editor non è "native-React senza deps" ma Tiptap, Paste-Protection sovradichiarata, manca DOMPurify/sicurezza)
  - [x] S1-C7 SEO & Prerendering → `sintesi/S1-C7-seo-prerendering.md` (scala a 3 gradini: Dynamic Rendering completo SPW≡SR UA-sniff+body / OG-proxy leggero solo-meta DIS; SALDA S1-C6→C7: il prerender riemette content con strip_tags-allowlist ≠ DOMPurify = buco XSS-attributi via UA-spoof, SR copia il motore di SPW + la falla, DIS immune per sottrazione; GOLD 3-gradini, buco-XSS-copiato, seo-cache-morta SR, SEO-indicizza-bozze SR+DIS, due-sistemi-SEO-divergono, archeologia-SSG; corregge CAP 11 = raccomanda l'SSG che SPW ha SCARTATO, esempio SQLite attribuito a SPW-MySQL, manca Dynamic Rendering/buco-XSS/visibilità/seo-cache/sitemap/JSON-LD)
  - [x] S1-C8 RSS & Feed → `sintesi/S1-C8-rss-feed.md` (il feed è l'emettitore PIÙ sicuro del `content`: o non lo emette — SPW excerpt / DIS feed podcast — o lo escapa totalmente — SR strip_tags+htmlspecialchars; CHIUDE il quadro dei 4 emettitori, il buco XSS NON si riapre; geografia un-file SPW / trittico SR feed+proxy-inbound+feed_config / feed podcast iTunes DIS; GOLD quadro-4-emettitori, sottrazione-vs-escape, feed_config security-theater, proxy-CORS-inbound allowlist+stale, GUID-che-ripubblica regressione urn→permalink→audio_url, status-dimenticata bozze-nel-feed SR, catch-vuoto-vs-500, monologhi-AI feed.php DIS, config-aspirazionale; corregge CAP 12 = feed podcast è DIS non SR, catch-vuoto insegnato come pattern, feed.php non è alias, omette quadro-4-emettitori/proxy-CORS/security-theater/status, GUID URN da ampliare = SR/DIS non lo seguono)
  - [x] S1-C9 Newsletter & Email → `sintesi/S1-C9-newsletter-email.md` (la newsletter CHIUDE il quadro dei 4 emettitori: nessuno emette content → buco XSS non si riapre, resta solo il prerender S1-C7; lente vera = scala "quanto puoi semplificare la posta" double-opt-in+2-token+rate-limit SPW / SMTP-PHPMailer+un-token-riusato+rate-limit-ASSENTE-mail-bombing SR / mail()-nuda-senza-opt-in-né-token DIS; ribaltamento gemello S1-C2/C5 il backend più ricco SR lascia il buco più grave; GOLD quadro-4-emettitori-chiuso, form-che-spara-email, rate-limit≠throttle, double-opt-in-3-gradini + token-che-diventa-uno/zero, header-injection-via-name DIS, invio-sincrono-senza-coda, 3-schemi-subscribers SR, mail()-vs-SMTP + 2-trasporti, Telegram-fossile-chiuso, consenso-implicito-festival DIS; corregge CAP 13 = omette il double-opt-in mostrando il modello DIS attribuito a SR, §4 unsubscribe-by-email non è GDPR-compliant, §6.3 usleep è throttle non rate-limit, §6.4 query-senza-content è anche XSS, omette mail-bombing/header-injection/SMTP-in-prod/2-token)
  - [x] S1-C10 Festival Logic → `sintesi/S1-C10-festival-logic.md` (modulo OPZIONALE, 1 sito su 4 — solo DIS, FDCA eredita backend byte-identico; concorso a voto pubblico gestito a INTERRUTTORI BOOLEANI status+in_current_round+master-switch settings + contatore DENORMALIZZATO vote_count=fonte-verità-classifica; scheda mono-sito = confronto testo-idealizzato CAP 16-18 vs codice-reale DIS vs fork FDCA; GOLD round-a-flag reset-cancella-storia, finalist-VESTIGIALE enum-mai-impostato, classifica-che-deriva drift-senza-reconciliation, report-finale-DORMIENTE Phase-2, master-switch-difensivo '1'||'true', consenso-implicito ponte-S1-C9, gate-role-blind ponte-S1-C2; anti-frode già in S1-C2; corregge CAP 18 §4 report-dato-attivo-ma-disabilitato + §3 finalist-mai-usato+drift, CAP 16 §4 Newsletter-Sync=problema-GDPR, CAP 17 §2 cookie-cosmetico-barriera-reale-è-IP/24h; inquadra festival come modulo opzionale + eredità FDCA)
  - [x] S1-C11 Engagement & Reactions → `sintesi/S1-C11-engagement-reactions.md` (reazioni solo SPW; lente = la SCRITTURA PUBBLICA non autenticata, l'unico fronte dove un visitatore scrive nel DB: reazioni + messaggi; GOLD le DUE FILOSOFIE di sanitizzazione write-time-messaggi vs render-time-articoli S1-C6 polarità-inversa, rate-limit a DUE strati voter_hash-20/min bypassabile-via-UA-rotation → secondo-argine-solo-IP-30/min, hash≠anonimato SHA256(IP+UA)-NON-salato-reversibile, integrità-nello-schema UNIQUE+INSERT-IGNORE vs drift-vote_count-S1-C10, IP-grezzo rimando-S1-C2, email-fire-and-forget S1-C9, engagement-leggero-vs-voto-competitivo S1-C10; anti-frode/identità già S1-C2; corregge CAP 19 §4 un-solo-strato-mislabeled-per-IP = sono-due, §3 hash-NON-salato-né-irreversibile, omette messages.php + le-due-filosofie, versione v2.0-errata SPW-è-v1.21)
  - [x] S1-C12 Admin Dashboard & Panels → `sintesi/S1-C12-admin-dashboard.md` (la dashboard = tessuto che lega tutti i cluster, su DUE assi ortogonali: *quanto misura* Chart.js-SPW/NON-misura-console-CRUD-SR/testuale-DIS + *come è costruita* route-guard-loader-SPW/mega-componente-SR/AdminLayout+guard-componente-DIS; ribaltamento gemello S1-C2/C5/C9 il flagship-incidenti SR ha l'admin meno attrezzato né-metriche-né-backup; GOLD tre-modelli-dashboard, flagship-senza-rete backup-fuori-docroot+htaccess-runtime-SPW-vs-NIENTE-SR→S1-C13, tabella-write-only-contacts-DIS, guard-role-blind-DIS, session_version-server-vs-logout-client, console-nascosta-manutenzione-GET-senza-UI-SR, confirm≠CSRF, app_settings-mass-write; **GAP STRUTTURALE: manca un capitolo Admin generale, CAP 18 è solo festival → proporre nuovo CAP in S3**)
  - [x] S1-C13 DB Evolution & Incidenti → `sintesi/S1-C13-db-evolution-incidenti.md` (evoluzione schema SENZA strumento di migrazione — ALTER+skip-Duplicate idempotente, no schema_version; tre rapporti con la stessa tecnica: DIS SQLite-VIVO il-motore-che-gli-altri-hanno-lasciato / SR migrato-a-MySQL-in-FUGA da crash-WAL-notturno sei-fossili+niente-backup / SPW migrato-in-silenzio con-backup; ribaltamento gemello S1-C2/C5/C9/C12 il flagship-incidenti SR è il meno attrezzato a sopravvivere; GOLD incidente-WAL-l'ottimizzazione-che-fa-crashare + DIS-contrappunto-vivo, migrazione-come-fuga-non-upgrade, sei-fossili-igiene-repo, una-tabella-tre-CREATE-subscribers, doppio-binario-one-shot-vs-self-healing, cura-senza-prevenzione SR-no-backup-vs-SPW/DIS-sì, bug-data-stringa debug_time-T, ETL-2-PDO+COUNT; init-fossile/versionamento già S1-C1; corregge CAP 14 §1-migrazione-motivata-da-traffico-ma-il-caso-reale-è-l'incidente, §6-checklist-prescrive-backup-che-SR-non-ha, SR-centrico-manca-DIS-SQLite-vivo-in-prod, omette fossili/3-schemi/doppio-binario)
  - [x] S1-FORK FDCA come caso "fork/evoluzione" → `sintesi/S1-FORK-fdca.md` (NON aggiunge pattern, backend byte-identico a DIS = caso-studio del FORKING; CHIUDE i fili di sicurezza — il fork eredita TUTTI i GOLD-bug immutati RCE-upload-S1-C5/auth-grado-zero-S1-C2/no-opt-in-S1-C9/reset-senza-CSRF/vote_count-S1-C10/no-DOMPurify-S1-C6; GOLD il-fork-eredita-i-bug fix-RCE-DIS-non-copre-FDCA, guscio-scollegato frontend-senza-api.ts/fetch, versione-0.0.1-su-backend-v0.5.x-nasconde-il-debito, roadmap-AI-che-ricalca-i-cluster il-progetto-che-si-pianifica-da-solo, un-motore-due-festival modulo-riusabile-S1-C10; il Modello non tratta il forking → proporre sezione/appendice in S3)
- [x] S2 — Inventario contenuti → `sintesi/S2-inventario-contenuti.md` (mappa capitolo-per-capitolo CAP 1→19+All. con azione CONFERMA/AGGIORNA/RISCRIVI/CORREGGI; 5 RISCRIVI CAP 6/7/8/11/13 + CAP 10/12/19; nuovi capitoli/sezioni Admin-generale/appendice-fork/analytics-first-party/box-4-emettitori; scarti + falsi-pattern; 8 fili trasversali con una-casa+rimandi)
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

- **Fase corrente:** 🟨 **FASE 2 — SINTESI. S1 ✅ (14/14) + S2 ✅ (Inventario).** FASE 1 conclusa (4 siti, 34 card). Prossima sotto-fase: **S3 (Scaletta/Indice globale)**, poi S4 (gate validazione con Simone).
- **Prossima unità:** FASE 2 / **S3 — Scaletta/Indice globale** della Terza Edizione: struttura a Parti + capitoli (inclusi i nuovi proposti in S2/B: Admin Dashboard generale, appendice fork, analytics), con mappa card→capitolo e collocazione degli 8 fili trasversali (S2/D). È il documento che va al GATE S4 (validazione con Simone) prima della scrittura. Vedi `PROSSIMA-SESSIONE.md`.
- **Log completo:** `LOG.md`.
