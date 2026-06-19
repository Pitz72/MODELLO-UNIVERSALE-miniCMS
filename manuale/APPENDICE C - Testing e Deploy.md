# APPENDICE C: Testing e Deploy (cenni)

Due temi che il corpo del manuale tocca solo di sfuggita meritano almeno un punto di partenza: come si collauda un thin stack senza un framework che ti regali gli strumenti, e come lo si porta in produzione su un hosting economico. Sono cenni, non una guida completa: indicano la direzione e i tranelli principali, non ogni passo. Ma servono a smentire un equivoco, e cioè che «niente framework» voglia dire «niente test» e «deploy a sentimento».

---

## 1. Testing: niente framework non vuol dire niente test

Il modello rinuncia ai framework, non alla verifica. Anzi: la sua forma minimale rende alcuni test più facili, non più difficili.

**Il backend PHP.** La logica pura (slug, validazione, sanitizzazione, calcolo della visibilità) si collauda con PHPUnit come qualsiasi codice. Gli endpoint, invece, conviene provarli *funzionalmente*: una richiesta HTTP vera contro l'endpoint, e una verifica su status e forma del payload. Qui il database-a-file diventa un vantaggio inatteso. Invece di mockare PDO (laborioso e poco fedele), si apre un SQLite usa-e-getta, in memoria o su file temporaneo, lo si popola con dati noti e lo si butta a fine test.

```php
// Un endpoint si collauda meglio con un DB reale effimero che con un mock di PDO
$pdo = new PDO('sqlite::memory:');        // database di test, vive quanto il test
$pdo->exec(file_get_contents('schema_test.sql'));   // schema noto
// poi: chiama l'endpoint (via HTTP o includendo il file con $_GET/$_POST simulati)
// e verifica status code + struttura JSON della risposta
```

**Il frontend.** Vitest e Testing Library coprono i componenti React. Il punto di forza è l'oggetto `api` del Capitolo 6: essendo un canale unico su `fetch`, si mocka in un punto solo, e i test dei componenti non toccano mai la rete vera.

**I test che ripagano di più.** In un sistema così, due famiglie di test valgono più di mille asserzioni di dettaglio:

- **Smoke test del contratto.** Un test che chiama ogni endpoint pubblico e verifica status più forma del payload coglie quasi tutte le regressioni del «contratto instabile» discusso al Capitolo 6. È la rete che manca proprio dove l'API non ha uno schema formale.
- **Test di non-regressione sulla sicurezza.** Un endpoint admin deve rispondere 401 o 403 senza sessione; un file `.php` caricato nella cartella upload non deve essere eseguibile (Capitolo 7); una mutazione senza token CSRF deve fallire (Capitolo 10). Sono i controlli che impediscono a una falla già chiusa di riaprirsi in silenzio.

---

## 2. Deploy: dalla `dist/` all'hosting da cinque euro

Il modello nasce per girare su hosting condivisi economici, e il deploy è volutamente semplice: niente container, niente orchestratori. Ma «semplice» non vuol dire «improvvisato».

**Cosa produce la build.** `npm run build` genera la cartella `dist/` con gli asset statici di React. Due passi del processo di build, già visti nei Capitoli 2 e 11, sono difese, non dettagli: `clean-dist.js` rimuove i file `.sqlite` di sviluppo dalla distribuzione (un database di sviluppo spedito in produzione è un disastro), e se `index.php` vive in `public/` va rinominato `index.html` in `index_react.html`, perché l'entry-point PHP del SEO Engine deve avere la precedenza.

**Cosa si carica, e cosa no.** Sul server vanno la `dist/` compilata e la cartella `public/api/` con il PHP. Il file `db_credentials.php` (per i siti MySQL) si carica **a mano**, una volta, e non sta mai nel repo. Non si caricano mai la cartella `.data/` di sviluppo né i file di test.

**Come si carica.** Le tre vie, in ordine di robustezza: un `git pull` sul server se l'hosting lo consente (la più pulita); un deploy via SFTP scriptato; il caricamento FTP manuale (il più fragile, perché dimenticare un file è facile). Qualunque sia la via, conviene che il deploy sia *ripetibile*: uno script in `scripts/` che fa sempre gli stessi passi vale più di una procedura tenuta a memoria.

**Una CI minima.** Anche senza pipeline complesse, una sola GitHub Action che a ogni push esegue build, lint e i test della sezione precedente intercetta le regressioni prima che arrivino in produzione. I segreti (credenziali, chiavi) vivono nelle variabili d'ambiente del CI, mai nel repository. Un eventuale passo di deploy automatico via FTP/SFTP è un'aggiunta comoda, ma viene dopo: prima la rete dei test, poi l'automazione della consegna.

---

## 3. Il limite di questi cenni

Quanto sopra è una mappa, non il territorio. Un sito con requisiti di disponibilità seri vorrà ambienti separati (staging e produzione), migrazioni di schema versionate (il debito del Capitolo 15), monitoraggio degli errori e backup verificati, non solo eseguiti. Il thin stack non vieta nulla di tutto questo: semplicemente non te lo regala, e sta a te decidere quanto di quella disciplina il tuo progetto merita. La regola è la stessa del resto del libro: parti dal minimo che ti tiene al sicuro, e aggiungi solo quando un bisogno concreto lo chiede.

> [!IMPORTANT]
> **Il Canone**
> - Collauda gli endpoint con un SQLite effimero (`:memory:` o file temporaneo), non mockando PDO.
> - Mocka l'oggetto `api` in un punto solo per i test dei componenti React.
> - Tieni due reti che ripagano: smoke test del contratto (status + forma del payload) e test di non-regressione sulla sicurezza (gate, upload, CSRF).
> - Build con `clean-dist` (via i `.sqlite`); carica `dist/` + `public/api/`, mai `db_credentials.php` dal repo né la `.data/` di sviluppo.
> - Una CI minima (build + lint + test a ogni push), con i segreti nelle variabili d'ambiente, non nel codice.
