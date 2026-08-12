# PROSSIMA SESSIONE — ricognizioni dai siti verso il manuale

> Prompt pronto da incollare. Aggiornato al **12/08/2026**.

---

## Il prompt

```
Riprendiamo il canale ricognizioni: i siti reali producono appunti, io li porto
qui e decidiamo cosa farne per il manuale.

Leggi prima la memoria, poi la mappa già fatta:
_ricognizioni/2026-08-12-SitoRuntime.md

Ho altri appunti da portarti. [dire quale sito / quale file]
```

---

## Stato al 12/08/2026

### Cosa è già stato fatto
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
