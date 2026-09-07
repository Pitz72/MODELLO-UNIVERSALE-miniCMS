# PROSSIMA SESSIONE — ricognizioni dai siti verso il manuale

> Prompt pronto da incollare. Aggiornato al **14/08/2026**.

---

## Il prompt

```
Riprendiamo il canale ricognizioni: i siti reali producono appunti, io li porto
qui e decidiamo cosa farne per il manuale.

Leggi prima la memoria, poi le mappe già fatte:
_ricognizioni/2026-08-12-SitoRuntime.md
_ricognizioni/2026-08-14-RuntimeMagazine-senza-React.md

Ho altri appunti da portarti. [dire quale sito / quale file]
```

---

## Novità del 07/09/2026 — l'omologazione degli editor, e il verdetto sul libro

- **[2026-09-07-omologazione-editor-tre-siti.md](2026-09-07-omologazione-editor-tre-siti.md)**:
  fotografia degli editor di Festival, SimonePizzi e Runtime Radio, matrice dei divari, piano in tre
  fasi (A Festival, C Runtime **fatte lo stesso giorno**; B SimonePizzi rimandata alla migrazione),
  fattibilità della migrazione di SPW a PHP puro (6-10 sessioni, dopo la Fase A), e la Parte 4 sul
  manuale: **verdetto «libro nuovo, non quarta edizione»**, con l'ossatura proposta e la condizione
  (prima i `NOTE_PER_IL_MANUALE.md` di Festival e SPW, che non esistono).
- Decisione (a)/(b)/(c)/(d) qui sotto: la proposta è **(b) subito**, **(c) scartata** a favore del
  libro nuovo, **(d) capitolo del libro nuovo**. Attende il sì di Simone.
- Dall'omologazione nasce un pezzo che il libro nuovo non aveva: **l'editor di casa** (Festival
  v1.14.0, `assets/js/editor.js`), reference implementation per il capitolo sull'editing senza
  Tiptap, con le due allowlist gemelle (JS e PHP) tenute uguali da una prova.

## Stato al 14/08/2026

### Novità del 14/08 — la ricognizione «senza React»
- **[2026-08-14-RuntimeMagazine-senza-React.md](2026-08-14-RuntimeMagazine-senza-React.md)**.
  Non è una ricognizione di deriva come quella di SR: è la mappatura di un **quinto sito che nasce
  applicando il Modello ma togliendo React** (Runtime Magazine, HTML+PHP puro, Tailwind mantenuto).
- Quattro rilievi che riguardano **il libro, non il sito**:
  1. **Il CAP 11 è per intero una protesi.** Sette costi che il capitolo presenta come inevitabili —
     doppia mappa rotte, `isCrawler()`, buco XSS del prerender, bozze indicizzate, cache orfana,
     vettore DDoS, fossili SSG — sono costi *di React*, non del thin stack. Il capitolo non lo dichiara mai.
  2. **Il filo dei quattro emettitori si chiude da solo** appena si toglie il render client: senza
     DOMPurify la sanitizzazione *deve* stare lato server. Il vincolo architetturale produce la
     prescrizione che quattro capitoli di disciplina non avevano prodotto.
  3. **Sei cicatrici su sei hanno un'unica radice** (una regola di dominio scritta a mano in più posti,
     che diverge) e il libro la nomina solo di sfuggita, parlando del gate. Meriterebbe un principio
     con un nome, accanto a «più ingegnerizzato non vuol dire più sicuro».
  4. **Il CAP 1 e il CAP 4 fanno scivolare insieme Tailwind e React.** Solo framer-motion dipende
     davvero dal framework: la distinzione manca e costerebbe una riga.
- Più: **tre difetti che il libro nomina e non risolve** (feed senza URL pulito, resize senza limite
  in altezza, invio newsletter bloccante) e la **conferma dell'Appendice B per una via nuova** — la
  password `runtime2026` del CAP 10 §9 è ricomparsa in un repo che *non* è un fork, propagata dalla
  memoria di chi scrive invece che da un `git clone`.
- Possibile **quinto sito di riferimento**: sarebbe il primo «gradino-zero del frontend», e renderebbe
  vera la scala del CAP 1 anche sul piano della presentazione, dove oggi c'è un gradino solo. Vale
  però **solo dopo** che il sito sarà in produzione con cicatrici proprie.

### Cosa è già stato fatto (12/08/2026)
- **Ricognizione SitoRuntime** completata e committata (`a75bcb2`):
  [2026-08-12-SitoRuntime.md](2026-08-12-SitoRuntime.md). Sito a **v2.21.0**, il libro lo fotografa
  a v2.9.13. Verifica fatta sul codice, non sul changelog.
- Esito: **Canone intatto (0 prescrizioni smentite)**, ma lo strato «dal vivo» su SR è scaduto in
  blocco — **11 affermazioni del libro sono oggi false**, perché il sito ha usato il manuale come
  griglia di audit e ha chiuso tutti i 17 item del piano di rientro entro il 18/07/2026.
- Materiale nuovo disponibile: **15 reference implementation**, **14 gotcha**, un filo concettuale
  nuovo (i «requisiti di seconda battuta»), e la proposta di **un capitolo che oggi manca**
  (pattern per hosting condiviso + privacy a costo zero).

### ⚠️ La decisione aperta — è il primo punto da sciogliere
Il §9 della mappa elenca quattro strade **senza sceglierne una**. Vanno decise prima di aprire
qualunque cantiere, perché cambiano la natura del lavoro:

- **(a)** Errata/appendice per la terza edizione — costo minimo, non tocca lo stampato.
- **(b)** **Datare esplicitamente il «dal vivo»** («le sezioni *dal vivo* fotografano lo stato al
  giugno 2026; il Canone è la parte durevole»). *Indipendente dalle altre e senza controindicazioni:
  qualunque cosa si decida sul resto, questa resta vera e costa quasi nulla.*
- **(c)** Quarta edizione — l'unica che sfrutta davvero le 15 reference implementation.
- **(d)** Il capitolo mancante su hosting condiviso e privacy a costo zero.

### Dove nascono gli appunti
Ogni sito tiene i propri in `docs/NOTE_PER_IL_MANUALE.md` (SitoRuntime ce l'ha e lo aggiorna a ogni
sessione che produce una lezione «da manuale»). È il canale: **lì si scrive, qui si decide**.

---

## Lavoro già identificato, non ancora fatto

### Sul manuale (qui)
1. **Sciogliere la decisione (a)/(b)/(c)/(d).**
2. **Ricognizione degli altri tre siti.** SPW (fotografato a v1.21.0), DISINTELLIGENZA, FDCA non sono
   stati riaperti. Se SR è derivato di 12 versioni minori in due mesi, non c'è motivo di assumere che
   gli altri siano fermi: le loro fotografie nel libro potrebbero avere lo stesso problema.
3. **Chiudere la riga A13 della mappa**: `admin.php` righe 260-668 di SitoRuntime, le azioni
   `?action=apply_*`. È l'unico punto della tabella A rimasto non verificato, e alimenta la critica
   della «console nascosta» del CAP 14.
4. Non letti: la Live Room di SR (~670 righe, sottosistema nato dopo il libro, da leggere con le lenti
   del CAP 18/20) e la suite di test (~2.000 righe).

### Sul sito Runtime Radio (repo `SitoRuntime`, **NON toccato da qui**)
Due rilievi emersi dalla ricognizione che appartengono alla roadmap di quel repo, non a questo.
Nessun file di SitoRuntime è stato modificato: se vanno riportati lì, va fatto in una sessione su
quel repo.

1. **Deriva della documentazione del sito.** `README.md` dichiara «v2.16.0», «Vite 7», «Tailwind CSS 3»;
   `package.json` dice **v2.21.0, Vite 8, Tailwind 4**. `docs/architecture/ARCHITETTURA.md:3` si dichiara
   aggiornato a v2.15.0 e ripete «Vite 7 + Tailwind 3» nel titolo del §2. È la stessa lezione della nota
   H.6 («il testo è l'unica parte del sistema che nessun meccanismo tiene onesta») applicata alla
   documentazione invece che alle didascalie.
2. **Due meccanismi di rate-limit convivono senza dichiararlo.** `api/rate_limit.php` è il componente
   condiviso su file, con un commento che spiega perché *non* su DB; ma `newsletter.php:95-102` fa il
   proprio rate-limit **con una query sul DB**. Funziona ed è difendibile, ma è il tipo di incoerenza
   che il CAP 13 rimprovera a SR in un altro punto.

Restano aperti anche i 5 debiti già nella roadmap di SitoRuntime (dipendenza implicita `live_*` →
`live.php`, log mancante del cron di backup, bollino LIVE sempre acceso, incolla markdown
nell'editor, icone del pannello admin).

---

## Il libro, per memoria
Terza Edizione **pubblicata e in distribuzione** su KDP in due listing separati (IT 160 pp, EN 164 pp).
Contenuti congelati al 19/06/2026. Tutto ciò che arriva da qui in poi è materiale per un'edizione
successiva o per un'errata — non si tocca l'edizione in vendita senza una decisione esplicita.
