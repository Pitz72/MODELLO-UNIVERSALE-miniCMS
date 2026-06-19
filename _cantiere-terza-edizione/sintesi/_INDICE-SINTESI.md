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
- ✅ **S1-C8 RSS & Feed** — fonti SPW-C8, SR-C8, DIS-C8 (FDCA = DIS, feed podcast ereditato → fuori scala). → CAP 12 (princ.) + ponti CAP 8/11/13/10/9.
  Il feed è l'emettitore PIÙ sicuro del `content` (o non lo emette o lo escapa totalmente): CHIUDE il "quadro
  dei 4 emettitori" (DOMPurify/strip_tags-allowlist/strip_tags+escape/newsletter) — qui il buco XSS NON si
  riapre. Geografia divergente: un file SPW / trittico SR (feed news + proxy inbound + feed_config) / feed
  podcast iTunes DIS. GOLD: quadro-4-emettitori, sottrazione-vs-escape, feed_config security-theater, proxy
  CORS inbound (allowlist+stale), GUID-che-ripubblica (regressione urn→permalink→audio_url), status-dimenticata
  (bozze nel feed SR), catch-vuoto-vs-500, monologhi-AI in feed.php (DIS), config-aspirazionale. Corregge CAP 12
  (§3 feed podcast è DIS non SR; §1 catch-vuoto insegnato come pattern = anti-pattern; §4 feed.php non è alias;
  omette quadro-4-emettitori/proxy-CORS/security-theater/status; §2.5 GUID URN da ampliare = SR/DIS non lo seguono).
- ✅ **S1-C9 Newsletter & Email** — fonti SPW-C9, SR-C9, DIS-C9 (FDCA = DIS). → CAP 13 (princ.) + ponti CAP 8/11/12/10/9/16-18/14.
  La newsletter CHIUDE il "quadro dei 4 emettitori" (nessuno emette content → buco XSS non si riapre, resta
  solo il prerender S1-C7). Lente vera = scala "quanto puoi semplificare la posta": double opt-in pieno +
  2-token + rate-limit SPW / SMTP-PHPMailer ma un-token-riusato + rate-limit ASSENTE (mail-bombing) SR /
  mail() nuda senza opt-in né token DIS. Ribaltamento (gemello S1-C2/C5): il backend più ricco (SR) lascia il
  buco operativo più grave. GOLD: quadro-4-emettitori chiuso, form-che-spara-email rate-limit-dimenticato SR,
  rate-limit-ingresso≠throttle-uscita, double-opt-in 3 gradini + token che diventa uno/zero, header-injection
  via name DIS, invio-sincrono-senza-coda, 3-schemi-subscribers SR, trasporto mail()-vs-SMTP, Telegram-fossile
  chiuso, consenso-implicito festival DIS. Corregge CAP 13 (omette il double opt-in = mostra il modello DIS
  attribuito a SR; §4 unsubscribe-by-email NON è "GDPR-compliant"; §6.3 usleep è throttle non rate-limit;
  §6.4 query-senza-content è anche sicurezza-XSS; omette mail-bombing/header-injection/SMTP-in-prod/2-token).
- ✅ **S1-C10 Festival Logic** — fonte DIS-C10 (solo DIS; FDCA eredita backend byte-identico). → CAP 16/17/18 (princ.) + ponti CAP 10/13/9.
  Modulo OPZIONALE (1 sito su 4): concorso a voto pubblico gestito a INTERRUTTORI BOOLEANI (status +
  in_current_round + master switch settings) + contatore DENORMALIZZATO vote_count = fonte di verità classifica.
  Scheda mono-sito → confronto interno "testo idealizzato CAP 16-18 vs codice reale DIS vs fork FDCA". GOLD:
  round-a-flag (reset cancella la storia del turno), finalist-VESTIGIALE (enum mai impostato), classifica-che-
  deriva (drift del contatore senza reconciliation), report-finale-DORMIENTE (sendVotingReport costruito ma
  commentato "Phase 2"), master-switch difensivo '1'||'true', consenso-implicito (ponte S1-C9), gate-role-blind
  (ponte S1-C2). Anti-frode voto già in S1-C2 (qui solo richiamato). Corregge CAP 18 §4 (report dato come attivo
  = è disabilitato), §3 (finalist mai usato + drift non avvertito), CAP 16 §4 (Newsletter Sync = problema GDPR),
  CAP 17 §2 (cookie cosmetico, la barriera reale è IP/24h); inquadra il festival come modulo opzionale + eredità FDCA.
- ✅ **S1-C11 Engagement & Reactions** — fonte SPW-C11 (reazioni solo SPW; ramo contatti cross-sito). → CAP 19 (princ.) + ponti CAP 10/8/13/18.
  L'engagement anonimo = il FRONTE di scrittura pubblica del CMS (uniche superfici dove un visitatore non
  autenticato scrive: reazioni + messaggi). GOLD: le DUE FILOSOFIE di sanitizzazione (write-time messaggi vs
  render-time articoli S1-C6, polarità inversa — input pubblico ripulito all'ingresso, content admin al render);
  rate-limit a DUE strati (voter_hash 20/min bypassabile via UA-rotation → secondo argine solo-IP 30/min);
  hash≠anonimato (SHA256(IP+UA) NON salato, reversibile per forza bruta); integrità-nello-schema (UNIQUE+INSERT
  IGNORE vs drift del vote_count festival S1-C10); IP-grezzo (rimando S1-C2); email-fire-and-forget (S1-C9);
  engagement-leggero vs voto-competitivo (S1-C10). Anti-frode/identità già in S1-C2. Corregge CAP 19 §4 (un solo
  strato mislabeled "per IP" = sono due, il vero per-IP è il secondo), §3 (hash NON salato né irreversibile),
  omette messages.php (metà del cluster) e le due filosofie di sanitizzazione; versione "v2.0" errata (SPW v1.21).
- ✅ **S1-C12 Admin Dashboard & Panels** — fonti SPW-C12, SR-C12, DIS-C12 (FDCA = no admin). → **GAP: nuovo capitolo da proporre in S3** + ponti CAP 10/14/18/19.
  La dashboard = il tessuto che lega tutti i cluster, su DUE assi ortogonali: *quanto misura* (Chart.js SPW /
  NON misura=console-CRUD SR / testuale DIS) e *come è costruita* (route-guard-loader SPW / mega-componente SR /
  AdminLayout+guard-componente DIS). Ribaltamento (gemello S1-C2/C5/C9): il flagship-incidenti SR ha l'admin meno
  attrezzato (né metriche né backup). GOLD: tre-modelli-dashboard, flagship-senza-rete-di-salvataggio (backup
  fuori-docroot+htaccess-runtime SPW vs NIENTE SR → S1-C13), tabella-write-only contacts DIS, guard-role-blind DIS,
  session_version-server-vs-logout-client, console-nascosta (manutenzione GET senza UI SR), confirm≠CSRF, app_settings
  mass-write. GAP STRUTTURALE: manca un capitolo Admin generale (CAP 18 è solo festival) → proporre nuovo CAP in S3.
- ✅ **S1-C13 DB Evolution & Incidenti** — fonti SR-C13 (princ.), DIS-C1 (SQLite vivo), SPW-C1/C12 (migrato + backup). → CAP 14 (princ.) + ponti CAP 3/10/13/18.
  L'evoluzione schema avviene SENZA strumento di migrazione (ALTER+skip-Duplicate idempotente, no schema_version);
  tre rapporti con la stessa tecnica: DIS SQLite VIVO (il motore che gli altri hanno lasciato, WAL/PRAGMA reali) /
  SR migrato a MySQL in FUGA da un crash WAL notturno (sei fossili + niente backup) / SPW migrato in silenzio (con
  backup). Ribaltamento (gemello S1-C2/C5/C9/C12): il flagship-incidenti SR è il meno attrezzato a sopravvivere.
  GOLD: incidente-WAL (l'ottimizzazione che fa crashare, DIS contrappunto vivo), migrazione-come-fuga-non-upgrade,
  sei-fossili-igiene-repo, una-tabella-tre-CREATE subscribers, doppio-binario one-shot-vs-self-healing, cura-senza-
  prevenzione (SR no-backup vs SPW/DIS sì), bug-data-stringa debug_time-T, ETL-2-PDO+COUNT. Init-fossile/versionamento
  già in S1-C1. Corregge CAP 14 (§1 migrazione motivata da soglie-traffico ma il caso reale è l'incidente; §6 checklist
  prescrive backup che SR non ha; SR-centrico = manca DIS-SQLite-vivo-in-prod; omette fossili/3-schemi/doppio-binario).
- ✅ **S1-FORK FDCA come caso "fork/evoluzione"** — fonte FDCA-DIFF. → materiale trasversale/editoriale (no capitolo dedicato → sezione "ciclo di vita di un fork" in S3).
  Non aggiunge pattern (backend byte-identico a DIS): è il CASO-STUDIO del forking. CHIUDE i fili di sicurezza —
  il fork eredita TUTTI i GOLD-bug immutati (RCE upload S1-C5, auth grado-zero S1-C2, no-opt-in S1-C9, reset-senza-
  CSRF, vote_count S1-C10, no-DOMPurify S1-C6). GOLD: il-fork-eredita-i-bug (copiare-backend-verbatim-li-moltiplica,
  fix-RCE-DIS-non-copre-FDCA), guscio-scollegato (frontend nuovo senza api.ts/fetch), versione-0.0.1-su-backend-v0.5.x
  (nasconde il debito), roadmap-AI-che-ricalca-i-cluster (il-progetto-che-si-pianifica-da-solo), un-motore-due-festival
  (modulo concorso riusabile, ponte S1-C10). Il Modello non tratta il forking → proporre sezione/appendice in S3.

## S2 — Inventario contenuti
- ✅ **S2 — Inventario contenuti** → `sintesi/S2-inventario-contenuti.md`. (A) Mappa capitolo-per-capitolo CAP 1→19+All.
  con azione CONFERMA/AGGIORNA/RISCRIVI/CORREGGI: 5 RISCRIVI (CAP 6/7/8/11/13) + CAP 10/12/19, CORREGGI/AGGIORNA
  CAP 3/9/14/16/17/18, AGGIORNA CAP 1/2/4/5/All., CONFERMA solo CAP 15. (B) Nuovi: CAP Admin Dashboard generale,
  appendice "ciclo di vita di un fork", sezione analytics-first-party, box-ancora "4 emettitori". (C) Scarti +
  falsi-pattern da rimuovere. (D) 8 fili trasversali con "una casa + rimandi". → prepara S3.

## S3 — Scaletta / indice globale
- ✅ **S3 — Scaletta globale** → `sintesi/S3-scaletta-globale.md`. Struttura a 5 Parti CONFERMATA; **20 capitoli +
  2 appendici** (era 19+Boilerplate): +1 CAP "Admin Dashboard generale" (Parte IV) + App. B "Ciclo di vita di un
  fork". Indice rinumerato (Parte V +1), mappa card/scheda→capitolo (copertura totale), collocazione 8 fili
  trasversali (una-casa+rimandi), spostamenti di scope (cache→9, SEO→11, DDoS→11), etichetta "Terza Edizione".
  Contiene **7 DECISIONI APERTE per il GATE S4** (con raccomandazioni). È il documento da validare con Simone.

## S4 — Validazione indice con Simone
- ✅ **GATE SUPERATO (2026-06-19).** Decisioni in `S3-scaletta-globale.md` §8: nuovo CAP 14 Admin + rinumerazione
  Parte V (+1) → 20 cap + 2 appendici; appendice Fork a sé; analytics come sezione del CAP Admin; CAP 7
  ribilanciato (cache→9, SEO→11, "Upload & Sicurezza"); etichetta "Terza Edizione"; riscritture CHIRURGICHE;
  ordine FASE 3 = CAP 10 → 8 → 11/12/13 → 14 → 6/7/20 → correzioni → App.B/FASE 4. **FASE 2 CHIUSA.**

---

### Stato globale FASE 2
- **FASE 2 — SINTESI ✅ CONCLUSA: S1 (14/14) · S2 · S3 · S4 (gate superato).** → **FASE 3 (Scrittura) avviata. Prima unità: CAP 10 Security & Auth (riscrittura chirurgica).**
