# CAPITOLO 14: Admin Dashboard & Panels

Ogni sistema visto finora ha un retro. I contenuti del CAP 9, i media del CAP 7, la newsletter del CAP 13, le reazioni del CAP 20, il festival dei capitoli che seguono: tutti si affacciano, prima o poi, su un pannello da cui un amministratore li guarda e li governa. L'area admin è il tessuto che lega gli altri cluster, il punto in cui diventano numeri da leggere e azioni da compiere. È una superficie che il festival rende facile sottovalutare: l'unica «dashboard» a cui si pensa di solito è quella del concorso, che è invece un caso particolare (lo ritroviamo al CAP 19). Qui ci occupiamo dell'area amministrativa generale, di cui quella del festival è solo una specializzazione.

I tre siti costruiscono la loro console su due domande indipendenti. La prima è *come è fatta*: una struttura a rotte con una guardia dichiarativa, un singolo mega-componente, o una via di mezzo. La seconda è *quanto misura*: un cruscotto analitico con grafici, un menu che non conta nulla, o numeri veri scritti in testo. Le due domande non vanno a braccetto, e la loro combinazione dà tre admin molto diversi.

C'è un ribaltamento che vale la pena anticipare, perché è il filo conduttore. SitoRuntime è il sito delle cicatrici di scalabilità, quello che ha vissuto il crash notturno e la migrazione d'emergenza del CAP 15. Eppure è quello con l'admin meno attrezzato: non misura niente e non ha backup. Cioè non ha né l'occhio per accorgersi di un problema, né la rete per sopravvivergli. È la conferma, ancora una volta, che più ingegnerizzato non significa più protetto.

---

## 1. L'admin è un aggregatore, non un'applicazione

Prima delle differenze, quattro tratti che i tre siti condividono.

L'area riservata non è un'applicazione separata: è un telaio che monta dentro di sé i pannelli degli altri cluster. L'editor del CAP 8, la libreria media del CAP 7, il compositore newsletter del CAP 13, la gestione del festival vivono come pagine di una console comune. Quello che è proprio dell'admin sono il telaio, la guardia, e poche superfici sue: la dashboard, le impostazioni, la gestione utenti.

La guardia, appunto, copre tutta l'area in un punto solo, non pagina per pagina. È il rovescio del backend, dove ogni endpoint chiama il proprio `Auth::check()` (CAP 10): qui il frontend protegge l'intero sotto-albero riservato con un'unica barriera, e tutte le pagine figlie ne ereditano la protezione. È il principio «una guardia, N pagine».

Ogni pannello degrada con grazia per conto suo: se una fonte dati cade (le metriche assenti, una tabella non ancora migrata), quel pannello si nasconde o mostra zero, ma il resto della console resta usabile. La dashboard non è mai una pagina bianca. E in tutti e tre il cambio password admin vive dentro le impostazioni, spesso l'unica voce davvero «di configurazione» presente.

---

## 2. Come è costruita: tre architetture di guardia

Su questo asse, la scala va dal dichiarativo all'imperativo.

SPW usa un *route-guard* dichiarativo: la rotta che monta il layout admin ha un loader, e tutte le figlie ereditano il suo redirect. La sessione viene verificata prima che la pagina si monti; se manca, l'utente non vede nemmeno un lampo di contenuto riservato.

```tsx
// SPW App.tsx:239-258 + loaders.ts:10-20 — una guardia, N pagine
{ element: <AdminLayout />, loader: adminAuthLoader, children: [ /* dashboard, settings, … */ ] }

export const adminAuthLoader = async () => {
    const session = await api.checkSession();
    if (!session || !session.user) return redirect('/admin/login');   // mai un dato admin servito senza sessione
    return session;
};
```

SR sta all'estremo opposto: un solo componente, `Admin.tsx`, quasi seicento righe, che cambia «sezione» in memoria invece di navigare tra rotte. La guardia è un controllo dentro il componente, eseguito al montaggio. DIS prende una via di mezzo che è quasi un ibrido curioso: ha la struttura di SPW (un `AdminLayout` con sidebar e rotte figlie via `Outlet`), gira perfino sull'infrastruttura data-router che permetterebbe i loader, ma poi protegge l'area con un controllo dentro il componente, come SR.

```tsx
// DIS AdminLayout.tsx:13-25 — struttura come SPW, guardia come SR
useEffect(() => {
    api.checkAuth().then(u => {
        if (!u) navigate('/admin/login');        // protezione client-side, nessun loader
        else setUser(u);
    });
}, [navigate]);
if (!user) return null;                          // NB: nessun controllo role === 'admin' (vedi sotto)
```

Il confronto pieno tra guardia-loader e guardia-componente, con i suoi compromessi, è al CAP 6. Qui conta una conseguenza di sicurezza che si vede proprio in DIS.

> [!WARNING]
> **Proteggere l'area non basta: serve il ruolo**
> La guardia di DIS verifica che ci sia un utente loggato, non che sia un amministratore. Un *editor*, quindi, vede l'intera console: iscrizioni, voto, reset, gestione utenti. È il backend a dover respingere le azioni che l'editor non può compiere, ma lo fa in modo incoerente (CAP 10): alcuni endpoint sono riservati agli admin, altri accettano qualunque utente loggato. Il risultato è che un editor può davvero approvare partecipanti e cambiare i round dalla UI. È la versione estesa all'intera area del problema «il gate nasconde il contenuto ma non il pulsante» che si vede anche in SR. La regola: nascondere una pagina è esperienza utente; impedire un'azione è sicurezza, e va fatta sul ruolo, sia sul client sia (soprattutto) sul server.

---

## 3. Quanto misura: analitica, console, testuale

L'altro asse è ortogonale al primo, e separa i tre siti in modo netto.

SPW ha un cruscotto analitico vero: sette card di totali, una decina di mini-statistiche con trend percentuale, sei grafici (con un selettore di periodo a 7, 30 o 90 giorni). SR non misura nulla: la sua dashboard è fatta di card che sono pulsanti di navigazione, non contatori. È un menu travestito da cruscotto. DIS sta nel mezzo, ed è la lezione più utile dei tre: misura davvero, ma in testo. Contatori di iscritti e voti, lo spazio su disco diviso per cartella, la classifica provvisoria, gli ultimi arrivati. Niente grafici, niente motore di tracciamento, solo i `COUNT` giusti.

> [!TIP]
> **Quanto cruscotto ti serve davvero**
> La dashboard di DIS dimostra che si può dare valore informativo a un amministratore senza Chart.js e senza un motore di analytics: bastano le query giuste e una pagina che le scrive in chiaro. Il cruscotto analitico di SPW è più ricco, ma costa un intero sistema di tracciamento da mantenere; il «menu» di SR è il gradino sotto al minimo, perché non risponde nemmeno alla domanda più semplice («quanti iscritti ho oggi?»). Tra il troppo e il niente, il cruscotto testuale è spesso il punto giusto: misura ciò che serve decidere, e nient'altro.

---

## 4. Misurare senza terze parti

Quando un sito vuole sapere quante visite riceve senza affidare i dati dei propri lettori a Google Analytics, deve costruirsi un analytics in casa. SPW lo fa con `analytics.php`, un file a doppia personalità: il ramo che *registra* un evento è pubblico (lo chiama il sito live a ogni visita), il ramo che *legge* i report è riservato all'admin.

```php
// SPW analytics.php:16-77 — un file, due pubblici
if ($method === 'POST') {
    // tracking 'view'/'click' dal sito live, anonimo: nessun Auth
    // 'view' deduplicata per IP-hash + articolo + giorno; 'click' a rate-limit
}
elseif ($method === 'GET') {
    Auth::check();        // solo la reportistica è privata
    // ~20 aggregazioni per la dashboard
}
```

Due accortezze rendono questo tracking sano. Le visualizzazioni sono deduplicate per IP e giorno, così un lettore che ricarica dieci volte conta una volta sola: i numeri non si gonfiano. E i click, oltre la soglia di frequenza, ricevono una risposta neutra invece di un errore:

```php
// SPW analytics.php:62 — oltre il limite, risposta neutra: il client non distingue "registrato" da "scartato"
echo json_encode(['status' => 'ok']);   // non un 429
```

È lo stesso `analytics.php` a consumare le reazioni del CAP 20, trasformandole in «articoli più amati» e «reazioni per tipo». Un sito che conta da sé i propri lettori tiene i dati in casa (un vantaggio di privacy concreto) e decide da sé cosa conta come visita vera. Il prezzo è un endpoint pubblico in più da difendere dall'abuso, ed è il motivo della deduplica e del rate-limit.

---

## 5. La rete di salvataggio: il backup, e il paradosso di SitoRuntime

Qui i tre siti si separano nel modo più istruttivo. SPW ha il pattern d'oro: il backup automatico viene scritto **fuori dalla document root**, dove nessuna richiesta web può raggiungerlo. E c'è un dettaglio che nasce da una cicatrice reale.

```php
// SPW backup.php:192-213 — il backup va fuori dalla docroot; il fallback si difende a runtime
$outside = dirname(realpath(__DIR__ . '/..')) . '/db_backups_simonepizzi';
if (!is_dir($outside)) @mkdir($outside, 0700, true);
if (is_dir($outside) && is_writable($outside)) {
    $backup_dir = $outside;
} else {
    // Fallback dentro la docroot: ma clean-dist.js (postbuild) elimina .data/ dalla dist,
    // quindi l'.htaccess di deny committato nel repo NON arriva sul server → ricrealo a runtime
    $backup_dir = __DIR__ . '/.data/backups';
    if (!is_dir($backup_dir)) mkdir($backup_dir, 0700, true);
    @file_put_contents($backup_dir . '/.htaccess', "Require all denied\n");
}
$filename = "auto_backup_" . date('Y-m-d_H-i-s') . '_' . bin2hex(random_bytes(8)) . ".sql";  // nome non indovinabile
@chmod($backup_dir . '/' . $filename, 0600);
```

> [!WARNING]
> **Il build può tradire la tua difesa statica: difenditi a runtime**
> Il `.htaccess` con `Require all denied` che protegge la cartella dei backup è committato nel repo. Ma lo script di build (`clean-dist.js`) rimuove la cartella `.data/` dalla distribuzione, per non spedire database di sviluppo in produzione. Effetto collaterale: il file di deny non arriva mai sul server. SPW lo ricrea a runtime, la prima volta che scrive un backup. La lezione è generale: una difesa che vive in un file statico vale solo se quel file arriva fin dove serve; se la tua pipeline di build lo tocca, la difesa va ristabilita a runtime. Conviene sempre chiedersi cosa il build *toglie*, non solo cosa aggiunge.

Il backup di SPW è anche schedulabile da un cron esterno senza login, ma protetto da un segreto confrontato in modo timing-safe, e *fail-closed*: se il segreto non è configurato, il ramo cron è raggiungibile solo da un admin loggato.

```php
// SPW backup.php:156-166 — cron senza login, ma protetto; nega se il secret non è definito
if (!$is_admin && (empty($configured_secret) || !hash_equals($configured_secret, $secret))) {
    http_response_code(403); die("Accesso negato.");
}
```

SR, di tutto questo, non ha niente. Nessun backup, nessun export, nessun cron, e, come abbiamo visto al §3, nessuna metrica.

> [!WARNING]
> **Cura senza prevenzione: il sito che non si fa il backup**
> È il paradosso al cuore di questo capitolo. SitoRuntime ha vissuto un crash notturno del database e una migrazione d'emergenza (CAP 15), e si porta dietro uno script di «revert d'emergenza» del WAL: ha la *cura*. Ma non ha la *prevenzione*: nessun backup automatico, nessuna metrica che lo avverta prima che le cose peggiorino. Il sito mappato proprio per i suoi incidenti è quello meno attrezzato a vederli arrivare e a rimediare. Avere lo script di emergenza ma non il backup è come tenere l'estintore e non l'allarme antincendio.

---

## 6. Le azioni potenti, e come (non) sono protette

Un'area admin contiene le leve più pericolose del sito, e i tre siti le proteggono in modo diseguale.

SR ha quella che si può chiamare una **console nascosta**: dentro il suo `admin.php` vivono azioni potenti, come un `ALTER TABLE` o la riconversione di tutte le immagini, raggiungibili via `GET` digitando l'URL. Sono protette dal solo login, non dal ruolo, non hanno protezione CSRF (sono GET), e soprattutto nessun pulsante della UI le invoca: chi non conosce il nome dell'azione non sa nemmeno che esistono. È manutenzione fatta a mano, senza interfaccia e senza confine di ruolo (la meccanica di quelle migrazioni è al CAP 15).

DIS espone i reset distruttivi in un pannello, e li circonda di conferme. Ma le conferme sono solo esperienza utente:

```tsx
// DIS Settings.tsx:155-163 — doppio confirm CLIENT, fetch POST SENZA token CSRF
if (confirm('⚠️ RESET EDIZIONE: cancellerà TUTTI i partecipanti/voti/audio…')) {
  if (confirm('ULTIMA CONFERMA: i dati saranno persi per sempre. Procedere?')) {
    await fetch('/api/reset_system.php', { method: 'POST',
      body: new URLSearchParams({ action: 'confirm_reset' }) });   // nessun CSRF
  }
}
```

> [!WARNING]
> **Il `confirm()` non è una difesa di sicurezza**
> Un doppio `window.confirm` riduce l'errore umano: è utile contro il clic distratto. Ma non ferma una richiesta forgiata da un altro sito mentre l'admin è loggato, perché quella richiesta non passa dal dialogo del browser. La difesa contro quel vettore è il token CSRF (CAP 10), che qui manca. Confondere la conferma con la protezione è un errore comune: la prima parla all'utente onesto, la seconda all'attaccante. Servono entrambe, e fanno cose diverse.

SPW è il più disciplinato anche qui, ma non immune da nei. Il suo cambio password incrementa il `session_version` lato server, invalidando le altre sessioni aperte (CAP 10); però il salvataggio delle impostazioni accetta qualunque chiave, senza una lista di quelle ammesse. È un rischio basso, perché tutto è dietro la guardia admin, ma è il genere di porta che conviene chiudere prima che qualcuno ci appoggi qualcosa di sensibile.

---

## 7. Dati senza consumatore: la tabella che nessuno legge

Un difetto più sottile, e tutto di DIS, riguarda i messaggi del form contatti. Vengono salvati nella tabella `contacts`, e poi non li legge nessuno: non esiste un pannello che li mostri, né un endpoint che li recuperi. L'unico modo in cui l'admin «vede» un messaggio è l'email di notifica che parte al momento dell'invio; la copia nel database resta lì, scritta e mai consultata.

> [!WARNING]
> **Raccogliere e dimenticare**
> Persistere un dato senza avere un posto dove leggerlo è un costo nascosto, e per i dati personali è anche un rischio. Quella tabella accumula nomi, email e messaggi (con l'indirizzo IP) senza uno scopo applicativo e, soprattutto, senza un punto dove cancellarli quando andrebbero cancellati. La regola è semplice e spesso ignorata: se salvi un dato, devi avere un consumatore che lo usa e un modo per dismetterlo. Una tabella di sola scrittura non è un archivio, è un debito.

---

## 8. Il festival è un caso particolare di questo capitolo

Tutto quello che abbiamo visto (il telaio con la guardia, il cruscotto, le impostazioni come interruttori, la valutazione delle candidature) ha una specializzazione nel modulo festival, che ha pannelli suoi (l'ascolto delle tracce dei partecipanti, i master switch di registrazione e voto, la classifica). Quella dashboard è il CAP 19, e va letta come l'istanza-festival del pattern generale descritto qui: la struttura, la guardia e il backup appartengono a questo capitolo; i master switch e i KPI del concorso restano là.

---

## In sintesi

L'area admin si misura su due assi indipendenti, e i tre siti li occupano in modo rivelatore. SPW è alto su entrambi: cruscotto analitico e architettura dichiarativa, con il backup fuori docroot a fare da rete. SR è basso su entrambi: un mega-componente che non misura nulla e non salva nulla, il paradosso del sito che ha sofferto di più senza essersi attrezzato per vederlo arrivare. DIS sta nel mezzo in modo istruttivo: la struttura del primo, la guardia (e i buchi) del secondo, e un cruscotto testuale che dimostra quanto si può misurare con poco. La lezione del capitolo non è «aggiungi più grafici»: è che un buon admin ti fa *vedere* lo stato del sistema e ti dà la *rete* per quando qualcosa va storto. L'apparato conta meno della domanda a cui risponde.

> [!IMPORTANT]
> **Il Canone**
> - Una sola guardia per l'intera area riservata (route-guard o controllo al montaggio), con verifica di **ruolo**, non solo di login.
> - Backup automatico fuori docroot, con cron protetto da un segreto timing-safe e fail-closed; ricrea a runtime le difese che il build strippa.
> - Le azioni potenti passano per POST + token CSRF, non per GET nascoste; nessuna tabella di sola scrittura (un dato salvato ha un consumatore e un modo per cancellarlo).
> - Misura ciò che serve a decidere: anche un cruscotto testuale è abbastanza.

---
*Prossimo Capitolo: Database Evolution, da SQLite a MySQL. La notte di febbraio in cui un database è caduto, e la migrazione d'emergenza raccontata ora per ora.*
