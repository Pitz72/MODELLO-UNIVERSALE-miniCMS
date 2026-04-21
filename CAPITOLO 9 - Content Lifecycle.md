# CAPITOLO 9: Content Lifecycle (v1.2 - ADVANCED)

Il Modello Universale trasforma un semplice database in un sistema editoriale dinamico. Questa sezione definisce la logica degli stati, la programmazione temporale e il feedback visivo necessario per una gestione professionale del palinsesto.

## 1. Stati Dinamici vs Stati Persistenti
Mentre il database salva uno stato "statico" (`status`), l'applicazione deve calcolare uno stato "dinamico" basato sul tempo.

### 1.1 Matrice degli Stati
| DB Status | Data di Pubblicazione | Stato Reale (UI) | Descrizione |
| :--- | :--- | :--- | :--- |
| `draft` | *Qualsiasi* | **BOZZA** | Mai visibile al pubblico. |
| `published` | `> NOW()` | **PROGRAMMATO** | Visibile solo agli Admin, in attesa del momento giusto. |
| `published` | `<= NOW()` | **PUBBLICATO** | Visibile a tutti. |

## 2. Implementazione della "Programmazione Reale"
La programmazione non richiede cron job. La visibilità è controllata dalla query SQL e riflessa nella logica React.

### 2.1 Logica Frontend (React)
Per fornire feedback immediato all'amministratore, la tabella di gestione deve calcolare lo stato al volo:

```typescript
const isDraft = item.status === 'draft';
const isScheduled = item.status === 'published' && new Date(item.published_at) > new Date();
const isPublished = item.status === 'published' && new Date(item.published_at) <= new Date();
```

### 2.2 Normalizzazione Data/Ora (Input Strategy)
Il formato `datetime-local` del browser utilizza il separatore `T`, mentre il DB richiede uno spazio. Lo standard impone la conversione bidirezionale nel componente di editing:

```typescript
// Da DB a UI
value={published_at.replace(' ', 'T').slice(0, 16)}

// Da UI a DB
onChange={e => setPublishedAt(e.target.value.replace('T', ' ') + ':00')}
```

### 2.3 UX della Tabella di Gestione (Admin)
Mentre le API formiscono i dati bruti, la dashboard amministrativa (rivisitata architetturalmente in SimonePizziWebSite v1.7.x) impone standard visivi di proporzione per la tabella articoli (`ArticlesList.tsx`), vitali per non asfissiare l'editing:
- **Contenimento Titolo**: La main column (Titolo) non deve eccedere il 45% della table-grid.
- **Badge Cromatico Categoria**: Rendere esplicita una colonna per la "Categoria" (15% di footprint) decorata con badge a colori sfalsati per la selezione rapida con lo sguardo.
- **Metadati Fissi**: Riservare il 20% alle Date di pubblicazione ed un 20% allo Stato dinamicamente calcolato (Bozza/Programmato).
- **Icon Actions**: Condensare l'edit/delete in action-button con icona standardizzata a fine riga (senza label text) per salvare la responsività da tablet.

## 3. Workflow Editoriale e Integrità
- **Auto-Slug**: Lo slug deve essere rigenerato solo alla creazione o se esplicitamente richiesto, per evitare di rompere i link esistenti (SEO integrity) in caso di modifica del titolo.
- **Rich Text Reset**: Durante il passaggio tra la modifica di due contenuti diversi, il componente editor deve essere forzatamente rimosso e reinserito (`key={item.id}`) per pulire i buffer interni e prevenire perdite di dati cross-articolo.
- **Anteprima Immediata**: Il form deve mostrare una miniatura (preview) dell'immagine di copertina selezionata, con possibilità di rimozione istantanea prima del salvataggio.

## 4. Gestione Categorie Sincrone e Tagging Relazionale
Storicamente (fino alle versioni 1.6), il tagging veniva gestito come campo testuale e organizzato visivamente dividendo con la virgola. Questa pratica (flat-string) rende i filtri globali fragili e non scalabili.

Dalla versione 1.7.12 (SimonePizziWebSite), lo standard miniCMS decreta il passaggio esclusivo all'architettura **RDBMS Multi-Tagging Relazionale**:
1. Abbandono stringhe statiche per la generazione delle tabelle relazionali: `tags` e `article_tags` (per le relazioni Many-to-Many).
2. L'editor React per la generazione/scrittura degli articoli fa il preload dei `tags` censiti sul database popolando un sistema **Select Multiplo API-driven**, annullando il tasso d'errore (typo) dell'editor.
3. Questo permette al filesystem SQL di creare rotte parametriche iper-semantiche e query combinate (es: `articoli categoria X e tag Y`) a costo misero.

## 5. Security & Visibility (Bypass Logic)

Gli endpoint API devono implementare una logica di "Bypass" per gli utenti autenticati:
- **Pubblico**: `WHERE status = 'published' AND published_at <= NOW()`
- **Admin**: nessun filtro — lista completa con bozze e articoli programmati nel futuro

Questo permette all'amministratore di testare la visualizzazione di un articolo programmato semplicemente navigando sul sito dopo aver effettuato il login, senza alcun meccanismo di preview separato.

### 5.1 Bypass per Singolo Articolo (via Slug)

L'endpoint recupera sempre l'articolo dal DB indipendentemente dallo stato. La decisione di mostrarlo o meno avviene *dopo* il fetch, in base alla sessione:

```php
// GET /api/articles.php?slug=titolo-articolo
$stmt = $pdo->prepare("SELECT * FROM articles WHERE slug = ?");
$stmt->execute([$_GET['slug']]);
$article = $stmt->fetch();

if ($article) {
    $is_admin = isset($_SESSION['user_id']); // Sessione attiva = admin

    // Articolo pubblico: status=published E data nel passato/presente
    $is_published = $article['status'] === 'published' &&
                    (empty($article['published_at']) || strtotime($article['published_at']) <= $ita_now_time);

    // Fingere il 404 — non 403 — per non rivelare l'esistenza di bozze a utenti non autenticati
    if (!$is_admin && !$is_published) {
        http_response_code(404);
        echo json_encode(['error' => 'Articolo non trovato']);
        exit;
    }

    echo json_encode($article); // Admin vede tutto: bozze, programmati, pubblicati
}
```

**Principio chiave**: il 404 simulato (anziché il 403) è una misura di sicurezza deliberata. Un 403 confermerebbe l'esistenza del contenuto; un 404 lo nega.

### 5.2 Bypass per Lista (via Parametro Admin)

Per la dashboard amministrativa, che deve mostrare *tutti* gli articoli incluse le bozze, si usa un parametro esplicito combinato con il controllo sessione:

```php
// GET /api/articles.php?admin=true (solo da dashboard autenticata)
$is_admin_dashboard = isset($_SESSION['user_id']) &&
                      isset($_GET['admin']) &&
                      $_GET['admin'] === 'true';

if (!$is_admin_dashboard) {
    // Filtri pubblici: solo pubblicati e già usciti
    $conditions[] = "status = 'published'";
    $conditions[] = "(published_at IS NULL OR published_at = '' OR published_at <= ?)";
    $params[] = $ita_now_str; // Stringa datetime calcolata all'inizio dello script
}
// Se $is_admin_dashboard === true: nessun filtro, lista completa
```

Il doppio controllo (`session + parametro`) è fondamentale: il parametro `?admin=true` da solo sarebbe bypassabile da chiunque.

### 5.3 Accesso per ID (Editor Admin)

Un terzo pattern — fetch per ID anziché slug — serve esclusivamente al form di editing in dashboard. Richiede autenticazione obbligatoria:

```php
// GET /api/articles.php?id=42 (solo admin editor)
if (isset($_GET['id'])) {
    Auth::check(); // Termina con 401 se non autenticato
    $stmt = $pdo->prepare("SELECT * FROM articles WHERE id = ?");
    $stmt->execute([$_GET['id']]);
    // ...
}
```

Questo endpoint bypassa il filtro sullo stato perché è progettato per caricare nel form anche le bozze mai pubblicate.

---
*Prossimo Capitolo: Security & Auth - Gestione sessioni, ruoli e protezione avanzata.*
