# ROADMAP — Traduzione integrale in inglese (US)

Piano per tradurre «React + PHP: The Thin Stack» (Terza Edizione, IT congelata) in **inglese
americano**. Metodo coerente col cantiere italiano: **microscopico, atomico, multi-sessione**, un
capitolo per volta, con glossario condiviso e revisione di stile madrelingua.

## 0. Decisioni prese (27/06/2026)
- **Collocazione:** cartella **`manuale-en/`** nello stesso repo, affiancata a `manuale/`. Storia git
  unica, toolchain riusabile con una config EN, confronto IT↔EN immediato.
- **Variante:** **inglese US** (spelling -ize/-or/-er; date M/D; em-dash US senza spazi).
- **Fonte:** il testo **italiano congelato** (`manuale/`). Non si ritocca l'italiano durante la traduzione.

## 1. Numeri del lavoro
- 23 file: 20 capitoli + 3 appendici (A Boilerplate, B Fork, C Testing&Deploy).
- ~50.000 parole. Più corposi: CAP 10 (~5k), 15, 11, 6, 7, 8. Più snelli: CAP 17/19, App. C.
- La convenzione «Dal vivo / Il Canone» + i box admonition sono in **ogni** capitolo (≈148 occorrenze):
  vanno resi con una **policy unica**, non improvvisati capitolo per capitolo.

## 2. Politiche di traduzione (il cuore della qualità)
1. **Codice intatto.** Identificatori, keyword, stringhe, nomi-file, annotazioni `path:linea` restano
   invariati. **DA CONFERMARE (D2):** i **commenti esplicativi** dentro i blocchi codice (oggi in
   italiano, es. `// il pubblico vede solo i visibili`) — proposta: **tradurli in EN** (sono prosa
   didattica che il lettore legge), lasciando intatto tutto il resto del codice.
2. **Nomi propri invariati:** SitoRuntime, DISINTELLIGENZA, FDCA, SimonePizziWebSite, Runtime Radio,
   Runtime Edizioni; dedica (Valerio Galano, Giuseppe Pugliese). **DA CONFERMARE (D3):** i titoli dei
   libri nella BIO («L'Albero dei Racconti», «Frequenza di Servizio») — proposta: **lasciarli in
   italiano**, eventualmente con glossa EN tra parentesi.
3. **Transcreazione, non calco**, per idiomi e immagini vivide: es. «il lucchetto con la chiave appesa
   accanto» → *a padlock with the key hanging right beside it*; «teatro della sicurezza» → *security
   theater* (termine già inglese). L'obiettivo è prosa **madrelingua tecnica**, non «traduttese».
4. **Voce e tesi preservate.** Le posizioni forti del libro (D2 «more engineered ≠ more secure», la
   distinzione norma/codice-reale) non si appiattiscono.
5. **Convenzioni del libro** → vedi `GLOSSARIO-IT-EN.md` §1 (la coppia «Dal vivo / Il Canone», «Quando
   NON usarlo», i titoli dei box).

## 3. Tipografia EN (l'inverso dell'italiano)
- Virgolette **curve** “ ” e ‘ ’ in prosa (stile editoriale); **dritte** solo nel codice.
- **Em-dash** `—` **ammesso** in prosa per gli incisi (US: senza spazi, `word—word`) — ma con parsimonia
  (regola humanizer: non abusarne). *Questo ROVESCIA la regola italiana che lo vietava.*
- **En-dash** `–` per intervalli e relazioni (pp. 10–20, SQLite–MySQL).
- Ellissi `…` carattere unico. **Niente caporali «»**, da nessuna parte.
- Numeri: one–nine a lettere, 10+ in cifre (stile tecnico US).

## 4. Revisione di stile (al posto di prosa-italiana)
Ogni capitolo tradotto passa per:
1. **Rilettura madrelingua tecnica:** caccia al traduttese, ritmo, idiomi, false friend, registro.
2. **Skill `humanizer`** (è basata su segni di scrittura AI **inglese**): em-dash overuse, rule of three,
   AI-vocab, passive, negative parallelism, filler. Pass finale «what still reads as AI/translated?».
3. **Pass tipografico** (§3) + **grep** di controllo (niente «», niente parole IT residue, codice intatto).
NB: la skill `prosa-italiana` **non si applica** all'inglese.

## 5. Ordine ed esecuzione
- **Sessione pilota: CAP 1 (Manifesto).** Fissa voce, dedica, colophon, la coppia «Two Voices», «When NOT
  to use», e popola il glossario sui casi reali. **Gate:** Simone valida voce + glossario prima di proseguire.
- Poi **ordine-libro** 1→20→App. A/B/C, **un capitolo per sessione** (i più corposi, es. CAP 10, possono
  occupare una sessione intera o spezzarsi). Il glossario **cresce e si congela** a ogni capitolo.
- **Ciclo di chiusura per capitolo:** traduci → revisione stile+humanizer → tipografia → aggiorna glossario
  → grep-clean → LOG → **commit/push** (un capitolo = un commit) → verifica sync.

## 6. File e struttura (da creare alla sessione pilota, non ora)
- `manuale-en/` con nomi EN a due cifre: `CHAPTER 01 - Manifesto.md` … `CHAPTER 20 - …`,
  `APPENDIX A - Boilerplate Checklist.md`, `APPENDIX B - The Life of a Fork.md`,
  `APPENDIX C - Testing & Deployment.md` (mappa titoli completa nel glossario §3).
- `_cantiere-traduzione-en/LOG-EN.md` (registro) + `PROSSIMA-SESSIONE-EN.md` (prompt atomico successivo).
- `README-EN.md` (o sezione EN nel README) con l'indice inglese.

## 7. A valle (scope Cowork/impaginazione, NON ora)
- **Build EN:** `build_book.py` e `build_epub.py` hanno lo `STRUCT` IT cablato (nomi-file, titoli di
  Parte, BIO, colophon «Terza Edizione — Giugno 2026»). Serve una **variante EN** dello STRUCT + Part
  titles/descrizioni EN + colophon EN. Stessa gabbia 7×10", stessi font IBM Plex.
- **Copertina EN:** nuova quarta/retro e metadati; il fronte «React + PHP: The Thin Stack» è già inglese.
- **KDP:** l'edizione inglese è un **listing KDP separato** (ISBN/ASIN proprio).
- Tutto questo segue le `_cowork-impaginazione/ISTRUZIONI-COWORK-BUILD.md`, adattate all'EN.

## 8. Rischi / trappole
- **Incoerenza terminologica** tra capitoli → mitigata dal glossario congelato e dal pilota-gate.
- **Traduttese** invisibile a chi ha scritto l'italiano → mitigato dalla skill humanizer + rilettura a freddo.
- **Idiomi italiani** resi alla lettera → marcati per transcreazione (lista crescente nel glossario §4).
- **Commenti-codice** dimenticati in italiano → check grep dedicato (parole-spia IT nei blocchi ```).
- **Em-dash:** rischio di passare dall'astinenza italiana all'abuso inglese → tenere il pass humanizer.

## Stato
- [x] Decisioni 0 prese · piano scritto · glossario proposto (`GLOSSARIO-IT-EN.md`).
- [ ] **GATE Simone:** confermare D2 (commenti-codice), D3 (titoli BIO) e il nome EN di «Dal vivo».
- [ ] Sessione pilota CAP 1 → struttura `manuale-en/` + LOG-EN + validazione voce/glossario.
