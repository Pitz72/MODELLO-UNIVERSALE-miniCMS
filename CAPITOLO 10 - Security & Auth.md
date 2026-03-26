# CAPITOLO 10: Security & Auth (v1.2 - ADVANCED)

La sicurezza nel Modello Universale non è un'opzione, ma un'architettura stratificata che protegge l'integrità dei dati e la privacy degli utenti attraverso controlli sia lato client che lato server.

## 1. Gestione della Sessione (Stateful-Sec)
Il sistema utilizza sessioni PHP native, ma con parametri di sicurezza moderni per prevenire il dirottamento (Session Hijacking).

### 1.1 Configurazione Server-Side
Prima di ogni `session_start()`, il sistema deve configurare i cookie per essere inaccessibili agli script JavaScript (prevenzione XSS):
```php
ini_set('session.cookie_httponly', 1);
ini_set('session.cookie_secure', 1); // Solo se HTTPS
ini_set('session.cookie_samesite', 'Lax');
session_start();
```

### 1.2 Endpoint check_auth
Il frontend non deve mai memorizzare la password o lo stato di login in `localStorage`. Deve invece interrogare periodicamente il server per confermare che la sessione sia ancora valida:
```php
if (isset($_SESSION['user_id'])) {
    echo json_encode([
        'status' => 'success',
        'user' => [
            'username' => $_SESSION['username'],
            'role' => $_SESSION['role']
        ]
    ]);
}
```

## 2. Architettura Protected Routes (React)
L'accesso all'area Admin è protetto da un **Higher-Order Component** o un **Layout Wrapper** (`AdminLayout.tsx`).

### 2.1 Bootstrapping della Sicurezza
All'interno del `useEffect` principale, l'app verifica l'identità. Se il server risponde con `401 Unauthorized`, il frontend distrugge lo stato locale e reindirizza istantaneamente alla pagina di login, impedendo flash di contenuti sensibili.

### 2.2 Role-Based UI (RBAC)
La sidebar e le rotte admin vengono generate dinamicamente in base al ruolo ricevuto dal server:
- **Admin**: Accesso a Gestione Utenti, Impostazioni di Sistema, Reset Database.
- **Editor**: Accesso limitato a News, Media e Podcast.

## 3. Sicurezza Crittografica
- **Hashing**: Le password vengono salvate esclusivamente tramite `password_hash($pass, PASSWORD_DEFAULT)`.
- **Verifica**: In fase di login, si utilizza `password_verify($pass, $hash)`. Il sistema non conosce mai la password in chiaro dell'utente.
- **Brute Force Mitigation**: Gli endpoint di login devono implementare un ritardo artificiale (`sleep(1)`) in caso di errore per rallentare i tentativi di attacco automatizzato.

## 4. Protezione del Database SQLite
Il database fisico (`.sqlite`) deve essere protetto da accesso diretto tramite URL.
- **Strategia 1**: Posizionamento del file in una cartella esterna alla root pubblica (es. `../data/`).
- **Strategia 2**: Se all'interno della root, protezione tramite `.htaccess` (`Deny from all`) e scelta di nomi file non prevedibili.

## 5. Sanitizzazione dei Buffer di Output
Per evitare che errori PHP involontari (Notice/Warning) rompano l'output JSON e forniscano indizi ad un attaccante (Path Disclosure), lo standard impone:
- `error_reporting(0);` in produzione.
- Cattura delle eccezioni via `try-catch` e restituzione di messaggi di errore "parlanti" ma generici.

---

## 6. Caso Reale: L'Attacco DDoS a Runtime Radio (Febbraio 2026)

> *"I grafici del traffico hanno iniziato a disegnare picchi anomali, simili a pareti verticali."*

Questa sezione documenta un incidente reale accaduto a **Runtime Radio (runtimeradio.com)** tra il 23 e il 27 febbraio 2026. Non è un caso di studio teorico: è una cicatrice viva nel codice e nell'architettura del progetto.

### 6.1 Il Contesto: Due Crisi Sovrapposte

La settimana del 23 febbraio 2026 ha visto due eventi distinti che si sono sovrapposti in modo devastante:

**Crisi 1 — Collasso del Database (23 febbraio)**
Il traffico crescente sulla piattaforma aveva messo sotto stress il database SQLite per mesi. Il 23 febbraio il sistema ha ceduto: l'infrastruttura database, sottodimensionata rispetto al carico reale, ha smesso di rispondere. *"Il sistema aveva tenuto per mesi, poi è ceduto tutto insieme, e rapidamente."* In meno di 24 ore il team ha completato la migrazione completa dei dati a MySQL — senza perdita di dati (vedi Capitolo 14 per il processo di migrazione).

**Crisi 2 — L'Attacco DDoS (24-27 febbraio)**
Mentre l'infrastruttura era già in fase di stabilizzazione post-migrazione, è arrivato l'attacco. I server hanno iniziato a restituire errori 503 e 500. Il traffico mostrava picchi anomali, verticali, impossibili da spiegare con la crescita organica degli utenti.

### 6.2 Il Vettore di Attacco: I Bot dei Social Media

La vulnerabilità sfruttata era elegante e insidiosa. Runtime Radio, come tutti i siti costruiti con il Modello Universale, implementava il **SEO pre-rendering via PHP entry-point** (Capitolo 11): ogni richiesta in arrivo veniva processata da `index.php`, che interrogava il database per estrarre i meta tag OG corretti da servire ai crawler di Telegram, Facebook e X/Twitter.

Questa funzionalità — progettata per migliorare l'esperienza di condivisione dei link sui social — si è trasformata in un'arma. Migliaia di bot ostili, **simulando i crawler dei social media**, hanno bombardato il server con richieste continue. Ogni richiesta forzava una query al database. Il database — appena migrato, ancora in fase di stabilizzazione — ha ceduto sotto il peso.

```
Bot ostile → simula Telegram/Facebook crawler
→ richiesta a / o /news/slug
→ index.php → query MySQL → meta tag
→ risposta → bot scarta → ripete 1000 volte/secondo
→ MySQL sopraffatto → 503/500
```

**La lezione**: qualsiasi endpoint che interroga il database per rispondere a richieste non autenticate è un potenziale bersaglio. I bot dei social media sono riconoscibili dallo user-agent — e possono essere falsificati.

### 6.3 La Risposta: Tre Livelli di Difesa

La risoluzione è avvenuta in fasi, documentata nell'articolo *"Sopravvivere alla Tempesta"* (27 febbraio 2026):

**Fase 1 — Spegnimento d'Emergenza con Degradazione Controllata**
Il sito principale è stato messo offline, ma lo **streaming audio è rimasto attivo** tramite una pagina statica di manutenzione. Principio fondamentale: il servizio core (la radio) non si interrompe mai, anche durante un attacco. La pagina di manutenzione non interrogava nessun database.

**Fase 2 — Cache Precompilata per i Bot**
La soluzione definitiva ha separato il percorso delle richieste dei bot da quello degli utenti reali:
- Le risposte per i crawler social (i tag OG, i meta SEO) vengono ora servite da **file JSON statici precompilati**, scritti nel momento in cui un articolo viene pubblicato o aggiornato.
- Il bot riceve la risposta in millisecondi, **senza che il database venga mai interrogato**.
- Solo le richieste di utenti reali (browser con JavaScript) ricevono la pagina React completa.

**Fase 3 — Sistema Ibrido Leggero e Corazzato**
L'architettura risultante distingue esplicitamente tra:
- **Richieste bot** (identificate dallo user-agent): servite da cache statica, zero DB access.
- **Richieste umane**: percorso normale, React SPA + API.

```php
// Pattern anti-DDoS: identificazione bot e servizio da cache statica
$userAgent = $_SERVER['HTTP_USER_AGENT'] ?? '';
$isSocialBot = preg_match('/facebookexternalhit|Twitterbot|TelegramBot|LinkedInBot|WhatsApp/i', $userAgent);

if ($isSocialBot && $slug) {
    $cacheFile = __DIR__ . '/api/.cache/seo_' . md5($slug) . '.json';
    if (file_exists($cacheFile)) {
        $seoData = json_decode(file_get_contents($cacheFile), true);
        // Serve meta tag da cache statica — nessuna query DB
        // ... iniezione nell'HTML ...
        exit;
    }
}
// Percorso normale per utenti reali
```

### 6.4 Le Persone

L'incidente non è stato risolto in solitudine. Carlo Santagostino, Walter Sbano, Peppe Pugliese e Valerio Galano (del podcast *Pensieri in Codice*) hanno contribuito alla ricostruzione dell'infrastruttura. La comunità tecnica intorno al progetto si è dimostrata parte dell'architettura di resilienza — non solo il codice.

### 6.5 Le Lezioni da Portare in Ogni Progetto

1. **Ogni endpoint pubblico che interroga il DB è un bersaglio potenziale.** Valutare sempre se la risposta può essere servita da cache statica per le richieste non autenticate.

2. **I bot dei social media possono essere falsificati.** Non fare mai affidamento solo sullo user-agent per decisioni di sicurezza critiche — usarlo solo per ottimizzare le performance (cache bot), mai come gatekeeper di accesso.

3. **Il servizio core deve sopravvivere a qualsiasi crisi.** Progettare sempre una "modalità degradata" che mantenga attiva la funzione principale del sito (streaming, in questo caso) anche quando tutto il resto è offline.

4. **La migrazione del database non è mai un momento sicuro.** Un sistema appena migrato è fragile. Pianificare la migrazione in periodi di basso traffico e avere un piano di emergenza pronto prima di iniziare.

5. **La cache non è solo una ottimizzazione di performance — è un layer di sicurezza.** Un sistema che risponde alle richieste ripetitive senza interrogare il database è intrinsecamente più resiliente agli attacchi volumetrici.

---
*Prossimo Capitolo: SEO Pre-rendering con PHP Entry-Point - Il motore SEO invisibile che trasforma una SPA in un sito indicizzabile.*
