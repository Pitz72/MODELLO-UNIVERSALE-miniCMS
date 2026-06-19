# Scheda di Sintesi — S1-FORK — FDCA come caso "fork / evoluzione"

> **Stato:** COMPLETATO
> **Cluster FASE 2:** S1-FORK (ultima scheda S1) · **Data:** 2026-06-19 · **Commit:** _(in corso)_
> **Fonti (card di mappatura):** FDCA-DIFF (unica fonte) · riferimenti incrociati a tutte le schede S1-C1…C13 (il fork eredita i loro GOLD immutati)
> **Capitoli del libro toccati:** materiale **trasversale/editoriale** — nessun capitolo dedicato al forking; va come **box ricorrente** + una **sezione "ciclo di vita di un fork"** (collocazione da decidere in S3, candidata: appendice o CAP 14 §evoluzione) → vedi §4

---

## 0. In una frase
FDCA non aggiunge un quarto set di pattern al Modello: è il **caso-studio del *forking*** — backend PHP
**byte-identico** a DISINTELLIGENZA (copia verbatim) + frontend **riscritto, ridotto e scollegato**
(vetrina nuova senza `api.ts` né `fetch`) + versione **azzerata a 0.0.1** + una `ROADMAP-EVOLUZIONE-
miniCMS` generata da AI. La sua lezione, che **chiude tutti i fili di sicurezza** delle schede
precedenti, è una sola e netta: **forkare copiando un backend verbatim trascina con sé ogni
vulnerabilità, immutata e silenziosa** — e la discontinuità di versione (0.0.1) *nasconde* la continuità
del debito sottostante.

## 1. Il pattern comune — il forking come fase del ciclo di vita del thin stack

Questa scheda non descrive un sito ma un **evento**: cosa succede quando un progetto thin stack viene
forkato per cambiarne il tema. FDCA ("Festival della Canzone Artificiale") è il fork di DISINTELLIGENZA
("Festival della Disintelligenza Naturale") — stesso autore, stesso motore, tema nuovo (musica
generativa invece dell'errore umano). Tre tratti definiscono questa fase.

**1) Il backend si congela, il frontend riparte.** La copia verbatim di `public/api/*.php` (zero
differenze di contenuto) significa che **tutta la logica server è ereditata intatta**, mentre l'energia
del fork va sul *guscio* pubblico: nuove pagine vetrina (Home/Filosofia/Manifesto/EdizioniPassate/
Contattaci), nessun pannello admin, nessun bridge. È il pattern naturale del re-skin: *si cambia ciò che
si vede, non ciò che funziona*.

**2) Il fork passa per un tool e azzera la versione.** FDCA è (ri)generato via **Google AI Studio**
(README "Run and deploy your AI Studio app", `.env.example` con `GEMINI_API_KEY`, `metadata.json`
"Remix:…"), e si presenta come **v0.0.1** — un "prodotto nuovo" che però poggia su un backend a v0.5.x.
La versione racconta una nascita; il codice racconta un'eredità.

**3) Il fork si porta dietro un piano per rifarsi.** FDCA include una `ROADMAP-EVOLUZIONE-miniCMS` (9
capitoli) che pianifica di **ricostruire il miniCMS in modo pulito** — e i suoi titoli **ricalcano i
cluster** di questa stessa mappatura (Backend, API PHP, Frontend Bridge `api.ts`, Admin & Protected
Routes, Festival Engine…). È un fork che documenta l'intenzione di *evolvere* il thin stack — eco diretta
del lavoro che il nostro manuale fa in modo sistematico.

Il punto cross-edizione: il forking è una **fase reale e comune** nella vita di questi progetti (DIS→FDCA
è la sua istanza), e merita di essere raccontata come tale — con i suoi rischi specifici, primo fra tutti
l'eredità silenziosa del debito.

## 2. Le varianti (tabella: cosa cambia e cosa NO nel fork)

Non essendoci più siti da confrontare, la tabella mette a fuoco il **delta** DIS→FDCA: la riga-chiave è
quanto poco cambia *sotto*.

| Asse | DISINTELLIGENZA (origine) | FDCA (fork) | Delta |
|---|---|---|---|
| **`public/api/*.php`** | 28 file | **stessi 28 file** | **IDENTICI byte-a-byte** |
| **Logica server** (auth, voto, upload, newsletter, festival) | tutta DIS | **copia verbatim** | nessuno |
| **Debito di sicurezza** (RCE upload, no-CSRF, no-opt-in, reset, `vote_count`) | presente | **presente immutato** | nessuno (ereditato) |
| **Motore DB** | SQLite vivo in `.data/` | identico | nessuno |
| **Frontend router** | `createBrowserRouter` + AdminLayout + ~20 pagine | `BrowserRouter` + 8 pagine pubbliche | **riscritto, ridotto** |
| **`src/pages/admin/`** | 11 pannelli | **assente** | rimosso |
| **`src/api.ts` / `fetch` verso `/api/`** | bridge completo | **assente** (grep negativo) | rimosso → **scollegato** |
| **Tema / branding** | Disintelligenza Naturale (comico) | Canzone **Artificiale** (musica AI) | re-brand completo |
| **Versione** | 0.5.x | **0.0.1** | reset |
| **Tooling / meta** | nessuna config | `.env.example` (GEMINI_API_KEY), README AI Studio, `ROADMAP-EVOLUZIONE-miniCMS/` | boilerplate AI Studio + roadmap |

**Lettura della tabella.** Lo spartiacque è netto: **tutto ciò che è server è invariato, tutto ciò che è
vetrina è nuovo**. Il fork ha cambiato la *pelle* (tema, pagine pubbliche, versione, tooling) e non il
*motore* — al punto che il nuovo frontend **non è nemmeno collegato** al backend ereditato (nessun
`fetch`). FDCA, allo stato, è un sito **vetrina con dietro un CMS pieno e funzionante ma irraggiungibile
dalla sua stessa SPA**. È lo scollamento frontend↔backend tipico di un restyle in corso d'opera.

## 3. GOLD & box problemi-soluzioni

- **Il fork eredita i bug: copiare un backend verbatim li moltiplica** — *(FDCA; CHIUDE i fili di
  sicurezza di tutte le schede S1)* — il GOLD portante, e la chiusura del cerchio di sicurezza dell'intera
  FASE 2. **Nessuno** dei GOLD di sicurezza di DIS è stato risolto nel fork, perché il backend è copiato
  riga per riga:

  | Vulnerabilità ereditata | Scheda d'origine | Stato in FDCA |
  |---|---|---|
  | Catena **RCE da upload pubblico** (`type=audio_participant` no-auth + MIME client + naming + no PHP-off) | S1-C5 | **presente immutata** |
  | **Auth grado-zero** (no CSRF, no rate-limit, no fixation) | S1-C2 | presente |
  | **Newsletter senza double opt-in né token** + header injection | S1-C9 | presente |
  | **Reset distruttivi senza CSRF** | S1-C2/C12 | presente |
  | **`vote_count` denormalizzato** (drift della classifica) | S1-C10 | presente |
  | **Render senza DOMPurify** (stored-XSS DIS) | S1-C6 | presente |

  La lezione: *un fork che copia il backend non eredita solo le feature, eredità ogni falla* — e qui è
  aggravato dal fatto che il fork è passato per un tool AI che ha rigenerato il **frontend** lasciando
  intatto un **backend insicuro**. Il task di fix RCE aperto sul repo DIS **non copre** FDCA: se il
  backend del fork andrà online, la RCE è replicata. → Box "Il fork eredita i bug: copiare codice
  insicuro lo moltiplica" (**altissimo valore**; chiude il filo sicurezza dei tre festival/DIS).

- **Il guscio scollegato: quando il fork riparte dal frontend** — *(FDCA)* — il nuovo frontend non ha
  alcun `fetch` verso `/api/`: è marketing puro (Home/Filosofia/Manifesto/EdizioniPassate/Contattaci) non
  connesso al CMS sottostante. È una **fase reale** del ciclo di vita di un fork/restyle: prima la pelle,
  poi (forse) il ricablaggio. Il rischio latente: il giorno in cui il frontend verrà connesso,
  erediterà *anche operativamente* i comportamenti — e i bug — del backend di DIS. → Box "Il fork che
  riparte dal frontend: il guscio scollegato".

- **La versione che riparte da zero su codice che non riparte** — *(FDCA; consolida il filo "versioni
  divergenti")* — `package.json` a **0.0.1** + `metadata.json` "Remix" + README AI Studio presentano un
  prodotto nuovo, mentre sotto gira un backend a v0.5.x con tutto il suo debito. La discontinuità di
  versione **nasconde** la continuità del codice — esattamente il rovescio del problema "stringhe di
  versione divergenti" già visto in DIS (sidebar v0.3.5 / init v0.3.6 / package 0.5.x, S1-C12/C13): lì
  troppe versioni per un solo codice, qui una versione-zero per un codice tutt'altro che zero. → confluisce
  nel box "La versione che non si allinea mai".

- **Il fork che si scrive da solo la roadmap** — *(FDCA; meta)* — la `ROADMAP-EVOLUZIONE-miniCMS` (9
  capitoli AI-assistiti) pianifica di rifare il miniCMS pulito, con titoli che **ricalcano i cluster** di
  questa mappatura. È meta-materiale prezioso: un artefatto del progetto stesso che **conferma
  dall'interno** la struttura a cluster che il nostro manuale ricostruisce dall'esterno. Da citare come
  prova che la "spina dorsale del thin stack" è riconoscibile anche a chi ci lavora dentro. → Box "Il
  progetto che si pianifica da solo" (eco del nostro manuale).

- **Un motore, due festival: riusare il dominio cambiando la pelle** — *(DIS→FDCA)* — il modello festival
  (iscrizione→selezione→voto a turni, master switch, `vote_count`) è **lo stesso**; cambia solo il tema
  (errore umano → musica generativa). È la prova positiva che il **modulo concorso** di S1-C10 è un
  componente *riusabile*: lo stesso engine regge due festival diversi con un re-skin. Il lato luminoso del
  forking, se solo si accompagnasse alla manutenzione del backend. → Box "Un motore, due festival: il
  modulo di dominio riusabile" (ponte S1-C10).

## 4. Mappa → capitolo/i del libro

| Materiale della scheda | Capitolo | Azione |
|---|---|---|
| **Il fork eredita i bug** (tabella delle vulnerabilità trascinate) | trasversale → **CAP sicurezza** + box | **box ricorrente** che chiude il filo sicurezza dei festival |
| **Il guscio scollegato** (frontend nuovo senza wiring) | **sezione "ciclo di vita di un fork"** (S3) | **nuova sezione** (oggi il manuale non tratta il forking) |
| **Versione 0.0.1 su backend v0.5.x** | confluisce nel box "versioni divergenti" (S1-C12/C13) | **aggiungi caso** |
| **`ROADMAP-EVOLUZIONE-miniCMS`** (piano AI che ricalca i cluster) | nota editoriale / introduzione | **cita** come conferma interna della struttura a cluster |
| **Un motore, due festival** (modulo riusabile) | **CAP 16-18** (festival) + ponte S1-C10 | **box**: il festival come modulo re-skinabile |

**Note sul testo attuale / collocazione (nessuna correzione: il forking è assente dal libro):**
- **Il Modello non tratta il forking.** I 19 capitoli descrivono *come costruire* un sito thin stack, non
  *cosa succede quando lo si forka*. FDCA fornisce il materiale per una **sezione nuova** (o appendice)
  sul ciclo di vita di un fork: re-skin, eredità del debito, scollamento temporaneo, ricablaggio. Da
  decidere la collocazione in **S3** (candidate: appendice "Evoluzione & Fork", oppure coda di CAP 14 che
  già parla di evoluzione).
- **FDCA non genera pattern nuovi** per le schede S1-C1…C13 (backend = DIS): il suo valore è **interamente
  come caso-studio del fork**. Va trattato come un box/sezione, non come un quarto sito con pattern propri
  — coerente con la nota di FDCA-DIFF §7.
- **Ponte ai task di sicurezza:** la catena RCE di S1-C5 è replicata in FDCA e **non** coperta dal fix
  aperto su DIS. Da segnalare nel libro come esempio reale di "il fix non segue automaticamente il fork".

## 5. Cosa si scarta / dedup

- **Tutto il backend è già mappato altrove:** essendo byte-identico a DIS, ogni dettaglio server
  (bootstrap SQLite, auth, upload, newsletter, festival) è **già nelle schede S1-C1…C13** e nelle card
  DIS. Questa scheda **non li ri-mappa**: li *richiama* solo nella tabella delle vulnerabilità ereditate
  (§3) per dimostrare la tesi del fork. Zero ripetizione del contenuto tecnico.
- **Dettaglio che NON entra nel libro:** l'elenco esatto delle 8 pagine pubbliche di FDCA, i nomi dei 9
  capitoli della `ROADMAP-EVOLUZIONE-miniCMS`, il contenuto di `metadata.json`/`.env.example`, la
  struttura di `CustomCursor`/`Navigation`. Restano in FDCA-DIFF come fonte.
- **Materiale che appartiene ad altre schede:** ogni singola vulnerabilità ereditata è trattata nella sua
  scheda d'origine (RCE → S1-C5, auth → S1-C2, newsletter → S1-C9, reset/`vote_count` → S1-C2/C10/C12,
  XSS → S1-C6); qui compaiono solo come **lista di ciò che il fork trascina**, non ri-spiegate.
- **Stato della FASE 2/S1:** con questa scheda **la sotto-fase S1 (Consolidamento) è COMPLETA — 14/14**
  (S1-C1…C13 + S1-FORK). Prossimo: **S2 (Inventario contenuti)**, poi S3 (scaletta/indice globale) e S4
  (validazione con Simone).
