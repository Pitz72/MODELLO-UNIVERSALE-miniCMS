# S2 — Inventario Contenuti (FASE 2, sotto-fase S2)

> **Stato:** COMPLETATO
> **Data:** 2026-06-19 · **Commit:** _(in corso)_
> **Input:** le 14 schede S1 (`sintesi/S1-*.md`, §4 "Mappa → capitolo" + "Correzioni") · i 19 capitoli esistenti (`CAPITOLO N - *.md`) + `BOILERPLATE-CHECKLIST.md`
> **Output:** mappa scheda→capitolo→azione (A), capitoli/sezioni nuovi (B), cosa si scarta (C), fili trasversali (D). È il ponte tra S1 (cosa dicono i siti) e S3 (scaletta della Terza Edizione).

---

## Legenda azioni
- **CONFERMA** — il capitolo regge, ritocchi minimi.
- **AGGIORNA** — aggiungere sezioni/box senza ribaltare l'impianto.
- **RISCRIVI** — l'impianto attuale è parziale/errato; va rifatto sulla realtà delle fonti.
- **CORREGGI** — c'è almeno un errore fattuale puntuale da sanare (può coesistere con AGGIORNA/RISCRIVI).

---

## A) Inventario capitolo per capitolo (CAP 1 → 19 + Allegato)

| CAP | Titolo | Schede S1 che lo toccano | Azione | Punti chiave / correzioni |
|---|---|---|---|---|
| **1** | Manifesto | (trasversale) | **AGGIORNA** | Innestare le tesi-filo emerse: "thin stack = scala, non assenza" e **"più ingegnerizzato ≠ più sicuro"** (D2). Nessun errore, ma il manifesto va allineato ai fili trasversali (D). |
| **2** | Architettura e Struttura Progetto | S1-C1 | **AGGIORNA** | Aggiungere **config & segreti** "3-factor senza librerie" (`define()` / `.env` / nessuna), struttura `public/api/` come file-per-endpoint. Oggi il tema config non ha casa. |
| **3** | Database Strategy | S1-C1, S1-C4, S1-C13 | **CORREGGI** | (a) `.data/`+`.htaccess` runtime è di **DIS** (SQLite), **non SPW** (MySQL) — attribuzione errata. (b) `journal_mode=DELETE`/`busy_timeout`/`foreign_keys` è una **prescrizione**, non il codice reale (DIS usa solo ERRMODE+FETCH). Tabella opzioni PDO a 3 colonne. Separare "raccomandato" da "fotografato". |
| **4** | Frontend Dependencies | S1-C3, S1-C6 | **AGGIORNA** | Dichiarare **Tiptap v3 (~10 pacchetti `@tiptap/*`)** come dipendenza reale dei flagship (oggi mai nominato). Esplicitare il **"niente librerie di fetching"** (no Axios/React Query/Redux). |
| **5** | Backend Logic (PHP) | S1-C1, S1-C4 | **AGGIORNA** | Anatomia endpoint-router su `REQUEST_METHOD`; i **3 stili di bootstrap** (inline / prelude `cors.php` / inline-minimale); **errore connessione** 500+log/503/die-leak; timezone forcing + incoerenze. |
| **6** | Frontend Bridge (API.ts) | S1-C3 (princ.), S1-C4 | **RISCRIVI** | §1.1 chiama **"Double Read" il pattern sbagliato** (il `res.clone()` è estrazione-errore, ed è il blocco del **codemod DIS**); §§1.1/3.1/3.2/4 sono spacciati per "il Modello" ma sono **DIS**. Aggiungere **token CSRF client**, **guard loader-vs-componente**, **messaggio backend perso**, **niente interceptor 401/403**. |
| **7** | Media & Optimization | S1-C5 (princ.) | **RISCRIVI** | Manca **del tutto la sicurezza upload** (la lacuna più grave): aggiungere scala difesa **3/1/0**, **catena RCE** (DIS), magic-bytes, naming, path-guard, delete-senza-CSRF. §3.3 `.htaccess` è **PHP-off** non solo cache; §3.1 **WebP non universale** + vincolo "1080px altezza" non nel codice; §4 script non sempre protetti. §1-2 mis-scoped (cache→CAP 9, SEO→CAP 11). |
| **8** | Advanced Content Editing | S1-C6 (princ.) | **RISCRIVI** | L'editor **NON** è "native-React senza dipendenze" (vero solo per DIS): i flagship usano **Tiptap v3** (mai nominato). "Paste Protection" **sovradichiarata** (è cosmesi, non sicurezza). Manca **DOMPurify a render-time** (il vero choke-point) e l'intera dimensione sicurezza. §1-2 mescolano due modelli media (festival-DIS vs picker-SPW). |
| **9** | Content Lifecycle | S1-C4 (princ.), S1-C3 | **CORREGGI** | §2.2 la conversione `T`↔spazio non è "lo standard" = è **una delle 3 strategie del fuso**; §4 il multi-tag M:N è **SPW-only** e mantiene il **doppio binario CSV** (non "esclusivo"); §1.1 matrice stati è SPW (SR ha `status IS NULL`, DIS ha `scheduled` residuo); §5 bypass 404-non-403 realizzato in 3 forme. |
| **10** | Security & Auth | S1-C2 (princ.), S1-C3, S1-C5, S1-C12, S1-C11 | **RISCRIVI** | Oggi **non parla affatto di CSRF/recovery/session_version** (gap enorme). Aggiungere: **CSRF a 3 gradini**, flag cookie + HSTS≠redirect, **brute-force a 3 sedi** + **IP grezzo controintuitivo**, recovery/reset, gate-unico-vs-componibile, **role-blind**. Correzioni: §1.1 SameSite reale=**Strict** non Lax + solo SPW ha i 3 flag; §1.2 username assente in SR; §3 brute-force non è solo `sleep(1)`; §6 DDoS appartiene a CAP 11. |
| **11** | SEO Pre-rendering | S1-C7 (princ.), S1-C2 (§6 DDoS) | **RISCRIVI** | **Raccomanda l'SSG (Puppeteer) che SPW ha PROVATO e SCARTATO**; la soluzione reale è il **Dynamic Rendering** (UA-sniff + body), non descritto. Esempio SQLite attribuito a SPW-MySQL. Aggiungere: **buco XSS-attributi** del prerender (`strip_tags`≠DOMPurify), **SEO indicizza le bozze**, **seo-cache morta** (SR), sitemap/robots dinamici, JSON-LD. Accogliere il caso DDoS-da-bot da CAP 10 §6. |
| **12** | RSS Feed & Syndication | S1-C8 (princ.) | **RISCRIVI/CORREGGI** | §3 il **feed podcast è di DIS, non SR** (SR *proxa* feed esterni); §1 il **catch-vuoto è insegnato come pattern** = è anti-pattern (feed troncato HTTP 200); §4 `feed.php` non è "alias". Aggiungere: **quadro 4 emettitori**, **proxy CORS inbound**, **`feed_config` security-theater**, regola `status` dimenticata, MIME WebP. §2.5 GUID URN: ampliare (SR/DIS non lo seguono). |
| **13** | Newsletter & Email System | S1-C9 (princ.), S1-C2 | **RISCRIVI** | **Omette del tutto il double opt-in** (cardine di SPW+SR) e mostra il **modello DIS** (subscribe-attivo + unsubscribe-by-email) **attribuito a SR**; §4 "GDPR-Compliant" è la versione **forgeable**; §6.3 chiama "Rate Limiting" un **throttle** anti-greylisting (il vero rate-limit manca); §6.4 query-senza-content è **anche** chiusura XSS. Aggiungere: mail-bombing, header-injection, **SMTP/PHPMailer in prod**, 2 trasporti, 2 token, storicizzazione. |
| **14** | Database Evolution (SQLite→MySQL) | S1-C13 (princ.), S1-C1, S1-C5, S1-C9 | **AGGIORNA/CORREGGI** | Buona base, ma: §1 motiva la migrazione con **soglie di traffico**, mentre il caso reale di SR è la **reazione a un crash WAL** (saldare §1+§2); §6 la checklist **prescrive un backup che SR non ha**; il capitolo è **SR-centrico** e non dice che **DIS gira ancora su SQLite** in prod. Aggiungere: **6 fossili** (igiene repo), **3 schemi `subscribers`**, doppio binario one-shot/self-healing, bug data-stringa, debito "schema-as-code". |
| **15** | Portfolio & Projects Module | S1-C4 (ricerca unificata) | **CONFERMA** | Nessuna scheda lo contraddice. Aggiungere solo il ponte: **ricerca `LIKE` unificata** articoli+progetti con campo `type` (vive tra CAP 9 e CAP 15). Verificare in S3 se assorbe materiale SPW-projects. |
| **16** | Festival — Iscrizioni & Approvazione | S1-C10 (princ.), S1-C5, S1-C9 | **AGGIORNA/CORREGGI** | §4 "**Newsletter Sync Strategy**" presentata come pregio = è un **problema di consenso GDPR** (iscrizione implicita). Aggiungere: **upload pubblico delle tracce → catena RCE** (S1-C5), il workflow stati con gate **role-blind** (editor approva). |
| **17** | Festival — Votazioni & Anti-Frode | S1-C10 (princ.), S1-C2 | **AGGIORNA/CORREGGI** | §2 presenta cookie+IP+UA come 3 difese equivalenti = il **cookie è cosmetico**, lo UA solo registrato, la **sola barriera reale è IP/24h** (`REMOTE_ADDR` grezzo, qui un **pregio**). Aggiungere: **`voter_hash` senza PII** (ponte CAP 19), **reset senza CSRF** + backup pre-distruttivo, **drift del `vote_count`** denormalizzato. |
| **18** | Festival — Dashboard Admin | S1-C10, S1-C12 | **AGGIORNA + RIDEFINIRE SCOPE** | §4 il **report finale è dato come attivo ma è disabilitato** ("Phase 2"); §3 "spostare i finalisti" = stato **`finalist` vestigiale** (round = flag). **Diventa l'istanza-festival** del nuovo CAP "Admin Dashboard" generale (B1): qui restano master-switch/KPI festival, la struttura del pannello va nel nuovo capitolo. |
| **19** | Social Interactions & Reactions | S1-C11 (princ.) | **RISCRIVI** | §4 descrive **un solo strato** di rate-limit chiamandolo "per IP" = sono **due** (voter_hash 20/min + solo-IP 30/min, anti-UA-rotation); §3 l'hash è dichiarato **"salato"** = non lo è (reversibile per forza bruta). Aggiungere **`messages.php`** (metà del cluster: write-time sanitization, auto-scaffolding) e le **due filosofie di sanitizzazione** (write-time vs render-time, ponte CAP 8). Versione "v2.0" errata (SPW v1.21). |
| **All.** | Boilerplate Checklist | (tutte) | **AGGIORNA** | Riallineare ogni voce ai capitoli rinumerati/nuovi e aggiungere le checklist-sicurezza emerse (upload PHP-off, CSRF, double opt-in, backup, sanitizzazione condivisa). |

**Sintesi azioni:** 5 RISCRIVI (CAP 6, 7, 8, 11, 13) · 1 RISCRIVI/CORREGGI (CAP 12) · 1 RISCRIVI grande (CAP 10) · 1 RISCRIVI (CAP 19) · CORREGGI/AGGIORNA (CAP 3, 9, 14, 16, 17, 18) · AGGIORNA (CAP 1, 2, 4, 5, All.) · CONFERMA (CAP 15). **Nessun capitolo resta intatto al 100%** — la mappatura ha prodotto correzioni o aggiunte ovunque tranne (quasi) CAP 15.

## B) Capitoli / sezioni NUOVI proposti

- **B1 — NUOVO CAP "Admin Dashboard & Panels" (generale).** *Fonte: S1-C12.* Oggi **non esiste**: l'unica
  "dashboard" è il CAP 18, specifico del festival. Materiale: i **tre modelli** (analitica Chart.js /
  console-CRUD / testuale), le **tre architetture** (route-guard-loader / mega-componente / AdminLayout+
  guard), **backup fuori-docroot + `.htaccess` runtime**, **cura-senza-prevenzione**, **tabella
  write-only** (`contacts`), gestione utenti. CAP 18 diventa la sua *specializzazione festival*.
- **B2 — NUOVA SEZIONE/APPENDICE "Ciclo di vita di un fork".** *Fonte: S1-FORK.* Il Modello non tratta il
  forking. Materiale: il fork **eredita tutto il debito** (RCE inclusa, il fix non segue il fork), il
  **guscio scollegato** (frontend nuovo senza wiring), **v0.0.1 su backend v0.5.x**, la roadmap AI che
  ricalca i cluster, **un motore-due-festival** (modulo riusabile). Collocazione (decisione S3): appendice
  "Evoluzione & Fork" oppure coda di CAP 14.
- **B3 — NUOVA SEZIONE "Misurare senza terze parti" (analytics first-party).** *Fonte: S1-C12 (`analytics.php`),
  S1-C11 (consumer reazioni).* View dedup per IP-giorno, click rate-limited con risposta neutra, niente
  Google Analytics. Candidata: sezione del nuovo CAP Admin (B1) o box in CAP 10/privacy. Da decidere in S3.
- **B4 — BOX TRASVERSALE RICORRENTE "I quattro emettitori del `content`".** *Fonte: S1-C6→C7→C8→C9.* Non un
  capitolo ma il **filo portante della sicurezza dei contenuti**: lo stesso `content` grezzo riemesso da
  render (DOMPurify) / prerender (`strip_tags`-allowlist = **buco attributi**) / feed (sottrazione|escape) /
  newsletter (non emette). Va come **box-ancora** in CAP 8 e richiamato in CAP 11/12/13, con la tesi
  "serve **una sanitizzazione server-side condivisa**". → vedi D1.

## C) Cosa si SCARTA (dai §5 delle schede)

- **Dettaglio per-sito non-libro:** numeri di riga, nomi esatti di migrazioni/azioni/file
  (`update_db_*`, `apply_v29x`, `migrate_*`), hash di commit, liste UA di `isCrawler`, le 7 euristiche del
  `SeoScorePanel`, palette/microcopy, header diagnostici (`X-Cache`), le dead-deps `@tiptap/*` dubbie. →
  restano nelle card di mappatura come fonte, non entrano nei capitoli.
- **Falsi pattern già smentiti:** il "Double Read = response cloning" (CAP 6), la "Paste Protection che
  rimuove script" (CAP 8), l'"SSG Puppeteer raccomandata" (CAP 11), il "catch-vuoto come fallback valido"
  (CAP 12), l'"unsubscribe-by-email GDPR-compliant" (CAP 13). → da **rimuovere/riscrivere**, non riproporre.
- **Doppioni cross-scheda fusi:** il quadro 4-emettitori (scritto una volta in B4, richiamato altrove);
  l'anti-frode voto (pieno in CAP 17, box-ancora in CAP 10); guard loader-vs-componente (pieno in CAP 6,
  richiamato in CAP Admin); i 3 schemi `subscribers` (pieno in CAP 14, citato in CAP 13). → ogni tema ha
  **una casa** e altrove solo rimandi.
- **Materiale mis-scoped da spostare:** CAP 7 §1 (cache TTL)→CAP 9; CAP 7 §2 (SEO)→CAP 11; CAP 10 §6
  (DDoS bot)→CAP 11. → decisione operativa in S3.

## D) Fili trasversali (attraversano più capitoli — una casa + rimandi)

1. **I quattro emettitori del `content`** *(CAP 8→11→12→13)* — casa: **box-ancora in CAP 8** (B4) + tabella
   completata in CAP 13; richiami in CAP 11 (il buco vivo) e CAP 12 (il feed lo chiude). Tesi:
   *sanitizzazione server-side condivisa*. Unica falla residua nel quadro: il prerender (CAP 11).
2. **"Più ingegnerizzato ≠ più sicuro"** *(CAP 3/5/7/10/13/14)* — casa: enunciato in **CAP 1 (Manifesto)**
   come tesi, dimostrato nei capitoli (SR è il più ricco e spesso il più fragile: password hardcoded,
   niente backup, rate-limit assente, cookie senza Secure). Richiamo in ogni capitolo dove emerge.
3. **Due filosofie di sanitizzazione: write-time vs render-time** *(CAP 8/19, ponte CAP 10)* — casa: **CAP 19**
   (lo mette a confronto: messaggi write-time vs articoli render-time); CAP 8 lo richiama. Input pubblico →
   neutralizza all'ingresso; contenuto ricco editoriale → sanitizza al render.
4. **Il forking eredita il debito** *(appendice B2, ponte CAP 10/sicurezza)* — casa: **appendice/sezione fork**;
   richiamo nel capitolo sicurezza ("il fix non segue il fork").
5. **La scala a 3 gradini come dispositivo narrativo** *(CAP 3/7/8/10/11 + Admin)* — casa: **CAP 1** come
   chiave di lettura ("grado-zero → essenziale → ingegnerizzato"); ricompare come struttura in molti
   capitoli (SQLite/MySQL, difesa upload 3/1/0, editor, SEO, dashboard). Da usare come **forma editoriale
   coerente**, non ripetere la spiegazione.
6. **"L'init mente / la verità è nel file" + versionamento senza registro** *(CAP 3/14)* — casa: **CAP 14**;
   anticipato in CAP 3. Nessuno ha `schema_version`; la verità è nel `.sqlite`/git/nomi-file.
7. **L'IP grezzo: buco o pregio secondo il modello d'abuso** *(CAP 10/17/19)* — casa: **CAP 10** (box
   anti-spoof); richiami in CAP 17 (voto: grezzo = pregio non-falsificabile) e CAP 19 (reazioni).
8. **Cura senza prevenzione (backup)** *(CAP 14/18/Admin)* — casa: **CAP 14**; richiamo nel CAP Admin
   (backup fuori-docroot SPW vs niente SR vs `.bak` pre-reset DIS).

---

## Conseguenze per S3 (scaletta globale) — decisioni da prendere
- **Aggiungere B1 (CAP Admin generale)** e decidere la collocazione di **B2 (fork)** e **B3 (analytics)**.
- **Ribilanciare CAP 7** (Media oggi mis-scoped) e spostare i materiali §C "mis-scoped".
- **Decidere le "case"** dei fili D (sopra già proposte) per evitare ripetizioni nella scrittura.
- **Allineare l'etichetta edizione** (oggi incoerente: README/_master "Prima"; build-pdf/articolo "Seconda")
  → "Terza Edizione" (è il punto E2 della ROADMAP, da chiudere in FASE 4 ma da decidere la label in S3).
- **Verificare la struttura a Parti** (oggi 5 Parti + Allegati) e dove inserire i nuovi capitoli/appendici.
