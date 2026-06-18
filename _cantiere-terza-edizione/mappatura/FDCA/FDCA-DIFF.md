# Mappatura — FDCA — DIFF (fork di DISINTELLIGENZA)

> **Stato:** COMPLETATO
> **Sessione:** 28 · **Data:** 2026-06-18 · **Commit:** _(in corso)_ · **ULTIMA CARD DELLA FASE 1**
> **Tipo:** documento di DIFF (non mappatura da zero) — cattura solo ciò che cambia vs DISINTELLIGENZA
> **File/elementi confrontati:**
> - `public/api/*.php` (diff di contenuto byte-a-byte vs DISINTELLIGENZA: **tutti identici**)
> - `src/` (App.tsx, pages/, components/ — frontend **completamente diverso**)
> - `package.json`, `metadata.json`, `README.md`, `.env.example`, `ROADMAP-EVOLUZIONE-miniCMS/`, `docs/`
> - base di confronto: le 7 card `DISINTELLIGENZA/DIS-C1,C2,C4,C5,C9,C10,C12`

## 1. Cos'è FDCA

**FDCA = "Festival della Canzone Artificiale"** (by Runtime Radio), un fork di DISINTELLIGENZA
("Festival della Disintelligenza Naturale"). Stesso autore, stesso impianto tecnico, **tema nuovo**:
non più il festival comico-dissacrante dell'errore umano, ma un festival di **musica generativa** —
"Sfida i limiti della creatività umana collaborando con le intelligenze artificiali… Preparate i
vostri prompt" (`src/pages/Home.tsx`, `metadata.json`).

Ma il dato strutturale è netto e va detto subito: **FDCA non è un fork che ha modificato la logica
del festival — è una RI-PELLE in corso d'opera su un backend congelato.** Tre fatti:

1. **Il backend PHP è byte-IDENTICO a DISINTELLIGENZA** (verificato con diff di contenuto su tutti i
   file `public/api/*.php`: zero differenze). Tutta la logica — bootstrap SQLite, auth, voto, upload,
   newsletter, festival — è una **copia verbatim** di DIS.
2. **Il frontend è completamente RISCRITTO, ridotto e NON cablato al backend.** Nessun pannello admin,
   nessuna pagina di voto/iscrizione, nessun `api.ts`, **nessun `fetch` verso `/api/`** (grep
   negativo): è un sito **vetrina pubblico** nuovo, non ancora connesso al PHP.
3. **È stato (ri)generato via Google AI Studio** (README "Run and deploy your AI Studio app",
   `.env.example` con `GEMINI_API_KEY`, `metadata.json` "Remix: Festival della Canzone Artificiale"),
   con la **versione azzerata a 0.0.1** (vs DIS 0.5.x) e una **roadmap AI di ricostruzione** del
   miniCMS (`ROADMAP-EVOLUZIONE-miniCMS/`, 9 capitoli).

In una riga: **FDCA = backend di DIS congelato + frontend nuovo (altro festival) ancora scollegato +
un piano AI per rifare il CMS.** Per il libro è il caso di studio del **ciclo di vita di un fork**.

## 2. Diff strutturale

| Elemento | DISINTELLIGENZA | FDCA | Delta |
|---|---|---|---|
| **`public/api/*.php`** | 28 file | **stessi 28 file** | **IDENTICI** (contenuto byte-a-byte) |
| **`db.php`** | SQLite `.data/database.sqlite` | identico | nessuno |
| **Versione** | 0.5.x (`package.json`) | **0.0.1** | reset (fork-restart) |
| **Frontend router** | `createBrowserRouter` + AdminLayout + ~20 pagine | `BrowserRouter` + 8 pagine pubbliche | **riscritto, ridotto** |
| **`src/pages/admin/`** | 11 pannelli | **assente** | **rimosso** (nessun admin) |
| **`src/api.ts`** | bridge completo | **assente** | **rimosso** (no wiring) |
| **Pagine pubbliche** | Home/Filosofia/Manifesto/Regolamento/Iscriviti/Vota/News/NewsDetail/Podcast/Press | Home/Filosofia/Manifesto/Regolamento/**EdizioniPassate**/News/Press/**Contattaci** | **rinominate/diverse**: niente Iscriviti/Vota/Podcast; +EdizioniPassate/Contattaci |
| **Componenti** | Layout/NewsletterForm/ContactForm/SEO/RichTextEditor/admin/* | Navigation/CustomCursor | **minimale** (vetrina) |
| **Tooling/meta** | nessun config/.env | `.env.example` (GEMINI_API_KEY), README AI Studio, `metadata.json`, `ROADMAP-EVOLUZIONE-miniCMS/`, `docs/CHANGELOG-v0.0.1.md` | **boilerplate Google AI Studio + roadmap** |
| **Tema** | Disintelligenza Naturale (comico) | Canzone **Artificiale** (musica generativa) | re-branding completo |

## 3. Diff per cluster (vs le card DIS)

Poiché il backend è identico, **ogni cluster lato server è invariato**. Il delta è tutto nel frontend
(che però è scollegato) e nel branding.

- **C1 — Backend Core.** **IDENTICO.** `db.php`, `init_db.php`, la catena `update_db_*`, il bootstrap
  inline: copia verbatim. Stesso SQLite vivo in `.data/`, stesso init fossile parziale ("v0.3.6"),
  stesso versionamento per nomi-file. (Il `.env.example` di FDCA **non** è una config del backend: è
  boilerplate AI Studio per il frontend/Gemini, non viene letto da `db.php`.)
- **C2 — Security & Auth.** **IDENTICO lato server** (auth grado-zero, no CSRF, no rate-limit, anti-
  frode voto IP/24h, admin solo nel `.sqlite`). Lato frontend **non esiste più** la UI di login/admin
  → la superficie d'attacco autenticata non è raggiungibile dalla SPA, ma gli endpoint PHP restano
  esposti e invariati.
- **C4 — Content.** **IDENTICO** (`news.php`/`podcasts.php` verbatim). Il frontend ha una pagina
  `News.tsx` nuova (vetrina), ma non risulta cablata agli endpoint (no `fetch`).
- **C5 — Media/Upload.** **IDENTICO — e qui è il punto più grave.** `upload.php` è copiato verbatim:
  la **catena RCE da upload pubblico** (type=audio_participant senza auth + MIME client spoofabile +
  naming che tiene l'estensione + nessun PHP-off) è **presente immutata** nel fork. Il fork **eredita
  la vulnerabilità senza saperlo** (vedi §4, GOLD).
- **C9 — Newsletter & Email.** **IDENTICO** (`newsletter.php`/`contact.php` verbatim): mail() nativa,
  no double opt-in, no token disiscrizione, header injection via name, `contacts` write-only. Il
  frontend ha una pagina `Contattaci.tsx` nuova (ma scollegata).
- **C10 — Festival Logic.** **IDENTICO** (`participants.php`/`votes.php`/`settings.php`/`stats.php`/
  `reset_*` verbatim): macchina a stati, round manuali via flag, `vote_count` denormalizzato, master
  switch, report finale disabilitato, `finalist` vestigiale. **Il fork NON ha cambiato il modello
  festival** — anche se il tema (musica AI) è diverso, la meccanica di voto/iscrizione è la stessa.
- **C12 — Admin.** **RIMOSSO dal frontend.** Non c'è `AdminLayout`, non ci sono pannelli, non c'è
  `api.ts`. Gli endpoint admin PHP esistono ancora (identici) ma **non hanno più una UI** nel fork.

## 4. GOLD — cosa il fork ha cambiato (e cosa NO)

- **GOLD (1) — il fork EREDITA tutto il debito di sicurezza, immutato.** Nessuno dei GOLD di
  sicurezza di DIS è stato risolto nel fork: la **catena RCE** di `upload.php` (DIS-C5), l'**auth
  grado-zero senza CSRF** (DIS-C2), il **double opt-in assente** (DIS-C9), i **reset senza CSRF**
  (DIS-C12), il **vote_count denormalizzato** (DIS-C10) sono tutti presenti byte-per-byte. È la
  lezione centrale: **forkare copiando il backend verbatim trascina con sé ogni vulnerabilità**, e in
  più qui il problema è aggravato dal fatto che il fork è passato per un tool AI che ha rigenerato il
  *frontend* ma lasciato intatto un backend insicuro. → Box "il fork eredita i bug: copiare codice
  insicuro lo moltiplica" (alto valore, chiude il cerchio della sicurezza dei 3 siti festival/DIS).
- **GOLD (2) — frontend e backend DISALLINEATI (il fork "spento").** Il nuovo frontend non ha alcun
  `fetch` verso `/api/`: è un guscio di marketing (Home/Filosofia/Manifesto/EdizioniPassate/Contattaci)
  **non connesso** al CMS. Quindi FDCA, allo stato, è un sito **vetrina** con dietro un backend pieno
  e funzionante ma irraggiungibile dalla sua stessa SPA. Lo scollamento frontend↔backend è una fase
  reale e comune del ciclo di vita di un fork/restyle. → Box "quando il fork riparte dal frontend: il
  guscio scollegato".
- **GOLD (3) — la versione AZZERATA e il re-branding (fork come 'Remix').** `package.json` 0.0.1,
  `metadata.json` "Remix: Festival della Canzone Artificiale", README di Google AI Studio: il fork si
  presenta come un **prodotto nuovo** (v0.0.1) pur poggiando su un backend a v0.5.x. La discontinuità
  di versione **nasconde** la continuità (e il debito) del codice sottostante. Collegamento al tema
  ricorrente delle "stringhe di versione divergenti" (DIS-C1/C12). → Box "la versione che riparte da
  zero su codice che non riparte".
- **GOLD (4) — la `ROADMAP-EVOLUZIONE-miniCMS` come piano AI di ricostruzione.** Il fork porta una
  cartella con **9 capitoli** (Architettura Backend & Sanitizzazione Build, Unificazione API PHP,
  Frontend Bridge `api.ts`, Architettura Admin & Protected Routes, Advanced Components, Deploy,
  Festival Engine Iscrizioni/Votazioni/Settings) — un documento, verosimilmente AI-assistito, che
  **pianifica di rifare** lo stesso miniCMS in modo pulito. I titoli dei capitoli **ricalcano
  esattamente i cluster** di questa mappatura (C1/C3/C12/C10…). È meta-materiale prezioso: un fork che
  documenta l'intenzione di *evolvere* il thin stack. → Box "il fork che si scrive da solo la roadmap"
  (e nota: è proprio ciò che il NOSTRO manuale fa in modo sistematico e cross-sito).

## 5. Cosa resta identico (sintesi)

Tutto il **backend** (`public/api/*.php`, byte-a-byte) e quindi l'intera logica di DIS: bootstrap
SQLite in `.data/`, init fossile parziale, auth/sessione, anti-frode voto, upload pubblico (con la
RCE), newsletter grezza, festival a turni con `vote_count` denormalizzato, schema frammentato. **Il
fork non ha toccato una riga del server.** Cambiano solo: il **tema/branding** (Canzone Artificiale),
il **frontend** (riscritto, ridotto, scollegato), la **versione** (0.0.1) e il **tooling** (Google AI
Studio + roadmap di ricostruzione).

## 6. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Il fork eredita i bug**: copiare un backend verbatim moltiplica le vulnerabilità | Box sicurezza "forkare codice insicuro" (chiude il filo RCE/CSRF dei festival) |
| **Frontend e backend disallineati**: il guscio scollegato come fase del restyle | Box "il fork che riparte dal frontend" |
| **Versione 0.0.1 su backend v0.5.x**: discontinuità che nasconde continuità | confluisce nel box "la versione che non si allinea mai" |
| **La roadmap AI di ricostruzione del miniCMS** (9 capitoli che ricalcano i cluster) | Box meta "il progetto che si pianifica da solo" (eco del nostro stesso manuale) |
| **Re-skin di un festival** (stesso motore, tema diverso) | Box "un motore, due festival: riusare il dominio cambiando la pelle" |
| **Google AI Studio come tooling di fork/restyle** | nota di contesto (ecosistema di sviluppo dell'autore) |

## 7. Note / domande aperte

- **Stato del fork:** FDCA è **incompleto/in transizione** — frontend nuovo non ancora cablato al
  backend (nessun `api.ts`/`fetch`). Da rivalutare se in futuro il frontend verrà connesso: a quel
  punto erediterà *anche* operativamente i comportamenti (e i bug) del backend di DIS.
- **Sicurezza (ponte ai task):** la **stessa catena RCE** di DIS-C5 è presente in FDCA (`upload.php`
  identico). Il task di fix già aperto sul repo DISINTELLIGENZA **non copre** questo repo: se il
  backend di FDCA verrà messo online, la vulnerabilità è replicata. (Rilievo documentale, sola lettura
  sui siti sorgente.)
- **`.env.example` fuorviante:** contiene `GEMINI_API_KEY`/`APP_URL` (boilerplate AI Studio per il
  front), **non** credenziali DB — coerente col fatto che il backend SQLite non ha config (DIS-C1).
- **Per la FASE 2 (Sintesi):** FDCA **non** aggiunge pattern nuovi alle schede cross-sito (backend =
  DIS); il suo valore è il **caso "fork/evoluzione"** e va trattato come tale (un box/sezione), non
  come un quarto set di pattern. La `ROADMAP-EVOLUZIONE-miniCMS` può essere citata come fonte
  secondaria sull'intento evolutivo.
- **Identità:** FDCA = "Festival della Canzone Artificiale" by Runtime Radio (musica generativa);
  DIS = "Festival della Disintelligenza Naturale" (errore umano). Stesso autore, stesso motore.

---

## ✅ FASE 1 — MAPPATURA: CONCLUSA

Con FDCA-DIFF si chiude la mappatura. **Quadro finale (4 siti, 29 card):**
- **SimonePizziWebSite** (flagship contenuti, MySQL migrato): 11 card (C1–C9, C11, C12). COMPLETO.
- **SitoRuntime** (flagship scalabilità+incidenti, MySQL migrato): 10 card (C1–C5, C7–C9, C12, C13). COMPLETO.
- **DISINTELLIGENZA** (festival, SQLite vivo): 7 card (C1, C2, C4, C5, C9, C10, C12). COMPLETO.
- **FDCA** (fork di DISINTELLIGENZA): 1 card di DIFF. COMPLETO.

Prossima fase: **FASE 2 — SINTESI** (consolidamento card per-sito → schede tematiche cross-sito;
inventario contenuti; scaletta/indice globale della Terza Edizione).
