# Mappatura — SimonePizziWebSite — C4: Content APIs

> **Stato:** COMPLETATO
> **Sessione:** 4 · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SimonePizziWebSite/`)
> - `public/api/articles.php` (CRUD articoli: GET lista/slug/id, POST, PUT, DELETE, PATCH; paginazione, filtri, ricerca `q`, slug, tag sync, pin/featured, draft/published)
> - `public/api/categories.php` (CRUD categorie: gerarchia `parent_id`, `sort_order`)
> - `public/api/navigation.php` (sola GET: menu ad albero categorie→sottocategorie)
> - `public/api/tags.php` (CRUD tag: slug, relazione M:N con articoli)
> - `public/api/projects.php` (CRUD progetti: `is_visible`, `sort_order` per categoria)
> - `public/api/search.php` (ricerca unificata articoli+progetti, sola GET)
> - `src/api.ts:128-287` (firme client di `getArticles`/`getProjects`/`getNavigation`/`getCategories`/`getTags`, letti come consumatori per chiudere il Double Read)

## 1. Cosa fa (sintesi narrativa)

C4 è il **lato server dei contenuti**: gli endpoint PHP che la SPA (mappata in C3) interroga per
leggere e scrivere articoli, categorie, tag, progetti e per la ricerca/navigazione. È il cuore
"CMS" del sito flagship. Ogni endpoint è un **singolo file `.php` che fa da router su
`$_SERVER['REQUEST_METHOD']`**: un `if/elseif` sul verbo HTTP (GET/POST/PUT/DELETE/PATCH) dentro
un unico `try/catch` con `Database::connect()` (singleton PDO di C1) e `Auth::check()` (gate di C2)
sui soli rami mutativi. Niente router framework, niente controller: il "thin stack" allo stato puro.

I cinque domini:

1. **Articoli** (`articles.php`) — l'endpoint più ricco. GET multimodale: singolo per `slug`
   (pubblico, solo `published`), singolo per `id` (admin), oppure **lista paginata** con filtri
   (`category` gerarchica, `tag`, `start_date`/`end_date`, ricerca `q`). È **l'unico endpoint di
   contenuto che risponde con `{data, total, page, limit}`** — paginazione backend-driven. CRUD
   completo + PATCH per i toggle `is_featured`/`is_category_pinned`. Genera slug unici, sincronizza
   i tag M:N, gestisce draft/published con `published_at` futuro (post programmati).

2. **Categorie** (`categories.php`) — CRUD con gerarchia a un livello (`parent_id`) e ordinamento
   manuale (`sort_order` auto-assegnato come `MAX+1`). GET pubblica, mutazioni protette.

3. **Navigazione** (`navigation.php`) — sola lettura, **pubblica e senza `auth_helper`**: legge le
   stesse categorie ma le restituisce **già annidate ad albero** (root → `subcategories[]`),
   pronte per il menu. È la "vista materializzata" client-friendly di `categories.php`.

4. **Tag** (`tags.php`) — CRUD tag con slug normalizzato. La relazione con gli articoli è gestita
   *dentro* `articles.php` (`syncArticleTags`), non qui: `tags.php` è solo l'anagrafica.

5. **Progetti** (`projects.php`) — CRUD "gemello" degli articoli ma più semplice: niente
   paginazione (ritorna **array nudo**), filtro per `category`, visibilità `is_visible`, ordinamento
   `sort_order` per categoria, PATCH per riordino/visibilità.

6. **Ricerca** (`search.php`) — endpoint trasversale: una `LIKE %q%` su articoli **e** progetti,
   unione dei due result-set, sort per data. Ritorna **array nudo** di record eterogenei marcati con
   un campo `type` (`'article'`/`'project'`).

## 2. Pattern miniCMS rilevanti

- **L'endpoint-router su verbo HTTP** (`articles.php:89` `if ($method === 'GET')`, ecc.): un file =
  una risorsa, lo switch sul metodo è il "controller". È IL pattern strutturale del thin stack:
  leggibile, zero dipendenze, ma la logica di una risorsa vive tutta in un file (articles.php = 379
  righe). Lente architetturale centrale per il libro.
- **Chiusura del "Double Read" (lato server, GOLD per C3→C4):** la forma della risposta **non è
  uniforme**, e ora la mappa è completa. **Un solo endpoint** restituisce l'oggetto paginato:
  | Endpoint | GET lista | GET singolo |
  |---|---|---|
  | `articles.php` | **`{data, total, page, limit}`** (`articles.php:231-236`) | oggetto nudo (`:116`, `:130`) |
  | `projects.php` | array nudo (`projects.php:53`) | oggetto nudo (`:21`) |
  | `categories.php` | array nudo (`categories.php:15`) | — |
  | `navigation.php` | array nudo (annidato) (`navigation.php:21`) | — |
  | `tags.php` | array nudo (`tags.php:30`) | — |
  | `search.php` | array nudo (`search.php:80`) | — |
  Quindi il client fa `Array.isArray(res) ? res : res.data` **perché mescola le due famiglie**: gli
  articoli (oggetto, paginati in v1.8.5) e tutto il resto (array). Il `portfolioLoader` di C3 che
  legge articoli+progetti insieme deve gestire entrambe le forme. **Il contratto non è versionato:
  è stato esteso in-place quando è arrivata la paginazione, e il client si è adattato leggendo "due
  volte".** È la prova archeologica dell'evoluzione incrementale dell'API.
- **Paginazione backend-driven con doppia query** (`articles.php:206-236`): prima una `COUNT(*)` con
  le **stesse** condizioni (ma senza `LIMIT`) per il `total` assoluto, poi la query dati con
  `LIMIT/OFFSET`. Il `total` permette al client di calcolare `hasMore` correttamente (vedi bug C3
  "total assente"). I parametri `LIMIT/OFFSET` sono bindati con `PDO::PARAM_INT` esplicito
  (`:225-226`) — necessario perché PDO altrimenti li quota come stringhe e MySQL rompe.
- **Filtro categoria gerarchico trasparente** (`articles.php:151-175`): se la categoria richiesta ha
  sottocategorie (`parent_id`), la query include automaticamente gli articoli di **tutte** le figlie
  via `IN (...)` con placeholder dinamici. La gerarchia di C4 non è solo estetica del menu: cambia i
  risultati. Pattern "categoria-contenitore".
- **Slug unici con normalizzazione accenti italiani** (`articles.php:26-42`, gemello in
  `tags.php:11-25`): tabella `$accents`→`$replacements` *prima* del replace regex, per evitare slug
  monchi (`"caffè"` → `caff-` invece di `caffe`). Su collisione, suffisso `-<timestamp>`. Dettaglio
  "localizzazione del thin stack" molto citabile.
- **Tag a doppia scrittura (M:N + cache legacy)** (`syncArticleTags` `articles.php:45-86`): scrive la
  relazione normalizzata in `article_tags` (DELETE+reinsert, `INSERT IGNORE` sui link) **e** in
  parallelo aggiorna il campo storico `articles.tags` (CSV) come "cache sicura per retrocompatibilità
  in emergenza". In lettura, la lista ricostruisce i tag con `GROUP_CONCAT` da `article_tags`
  (`:137`) sovrascrivendo il legacy (`:106,:129`). Convivenza modello vecchio/nuovo: gold per il box
  "migrazione senza downtime".
- **Visibilità pubblico/admin come condizione SQL** (`articles.php:143-149`, `projects.php:36-38`,
  `search.php:37-40`): la stessa query serve pubblico e dashboard; la differenza è un `AND status =
  'published' AND published_at <= now` aggiunto solo se non admin (`isset($_SESSION['user_id'])` +
  flag `?admin=true`). Un endpoint, due audience, gate dato dalla sessione di C2.
- **Post programmati** (`articles.php:110`, `:147`, `:265-267`): `published_at` nel futuro =
  pubblicato ma non ancora visibile. Il confronto `published_at <= ?` con l'ora **forzata a
  `Europe/Rome`** (`:11-13`, bypass del server in fuso Los Angeles) governa la visibilità temporale.
- **Sanitizzazione URL dei CTA** (`sanitizeUrl` `articles.php:17-23`): i bottoni call-to-action
  accettano solo `http(s)`/`mailto`, rigettano `javascript:` ecc. via whitelist + `FILTER_VALIDATE_URL`.
  Difesa XSS stored a livello di contenuto (ponte a C6 editor).
- **`navigation.php` senza `auth_helper`** (`navigation.php:1-4`): è l'unico endpoint di contenuto
  che **non** include `auth_helper.php`. Essendo sola GET pubblica e read-only va bene, ma è
  un'asimmetria da notare (categorie identiche, due file, due livelli di include).

## 3. Codice chiave (stralci con origine)

**Paginazione backend-driven: COUNT separato + LIMIT/OFFSET con tipi espliciti** — `articles.php:206-236`:

```php
// Calcoliamo il totale assoluto degli articoli filtrati (stesse condizioni, niente LIMIT)
$countQuery = "SELECT COUNT(*) FROM articles a" . $whereClause;
$countStmt = $pdo->prepare($countQuery);
foreach ($params as $k => $v) { $countStmt->bindValue($k+1, $v); }
$countStmt->execute();
$total = (int)$countStmt->fetchColumn();

$query .= " GROUP BY a.id ORDER BY a.is_category_pinned DESC, a.is_featured DESC,
            CASE WHEN a.published_at IS NOT NULL THEN a.published_at ELSE a.created_at END DESC
            LIMIT ? OFFSET ?";
$stmt = $pdo->prepare($query);
foreach ($params as $k => $v) { $stmt->bindValue($k+1, $v); }
$stmt->bindValue(count($params)+1, $limit, PDO::PARAM_INT);   // PARAM_INT obbligatorio
$stmt->bindValue(count($params)+2, $offset, PDO::PARAM_INT);
$stmt->execute();
$articles = $stmt->fetchAll();

echo json_encode(['data' => $articles, 'total' => $total, 'page' => $page, 'limit' => $limit]);
```

**L'UNICO endpoint con `{data,total}` vs il resto ad array nudo** — confronto:

```php
// articles.php:231 — oggetto paginato
echo json_encode(['data' => $articles, 'total' => $total, 'page' => $page, 'limit' => $limit]);
// categories.php:15 / tags.php:30 / projects.php:53 / search.php:80 — array nudo
echo json_encode($stmt->fetchAll());
```

**Filtro categoria gerarchico: include le sottocategorie** — `articles.php:151-175`:

```php
if ($category) {
    $catStmt = $pdo->prepare("SELECT id FROM categories WHERE slug = ? LIMIT 1");
    $catStmt->execute([$category]);
    $parent_cat_id = $catStmt->fetchColumn();
    if ($parent_cat_id) {
        $subCatStmt = $pdo->prepare("SELECT slug FROM categories WHERE parent_id = ?");
        $subCatStmt->execute([$parent_cat_id]);
        $subSlugs = $subCatStmt->fetchAll(PDO::FETCH_COLUMN);
        if (!empty($subSlugs)) {
            $allSlugs = array_merge([$category], $subSlugs);
            $placeholders = implode(',', array_fill(0, count($allSlugs), '?'));
            $conditions[] = "a.category IN ($placeholders)";
            foreach ($allSlugs as $s) $params[] = $s;
        } else { $conditions[] = "a.category = ?"; $params[] = $category; }
    } else { $conditions[] = "a.category = ?"; $params[] = $category; }
}
```

**Tag a doppia scrittura: relazione M:N + cache CSV legacy** — `articles.php:45-86` (estratto):

```php
function syncArticleTags($pdo, $article_id, $tags_input) {
    $pdo->prepare("DELETE FROM article_tags WHERE article_id = ?")->execute([$article_id]);
    $tags_array = is_array($tags_input) ? $tags_input
        : (is_string($tags_input) && !empty($tags_input) ? explode(',', $tags_input) : []);
    // ... per ogni tag: trova-o-crea in `tags`, poi INSERT IGNORE in `article_tags`
    // Backup sul campo storico 'tags' (CSV) per sicurezza/legacy:
    $stmtUpdateLegacy = $pdo->prepare("UPDATE articles SET tags = ? WHERE id = ?");
    $stmtUpdateLegacy->execute([implode(', ', $cleanNames), $article_id]);
}
```

**Navigazione ad albero costruita in PHP per riferimento** — `navigation.php:8-21`:

```php
foreach ($all as $cat) { $cat['subcategories'] = []; $by_id[$cat['id']] = $cat; }
foreach ($by_id as $id => &$cat) {
    if ($cat['parent_id'] && isset($by_id[$cat['parent_id']])) {
        $by_id[$cat['parent_id']]['subcategories'][] = &$cat;   // append per riferimento
    } elseif (!$cat['parent_id']) { $menu[] = &$cat; }
}
echo json_encode(array_values($menu));
```

**Ricerca unificata: due query, merge, sort per data, campo `type`** — `search.php:73-80`:

```php
$results = array_merge($articles, $projects);   // record eterogenei marcati 'article'/'project'
usort($results, function($a, $b) {
    return strtotime($b['date']) - strtotime($a['date']);
});
echo json_encode($results);   // array nudo
```

**PATCH come "toggle endpoint": un solo pin per categoria** — `articles.php:347-366`:

```php
} elseif (isset($data['is_category_pinned'])) {
    $pin = (int)$data['is_category_pinned'];
    // recupera categoria dell'articolo, poi: un solo pin per categoria
    if ($pin) {
        $pdo->prepare("UPDATE articles SET is_category_pinned=0 WHERE category=? AND id!=?")
            ->execute([$row['category'], $id]);
    }
    $pdo->prepare("UPDATE articles SET is_category_pinned=? WHERE id=?")->execute([$pin, $id]);
}
```

## 4. Problemi riscontrati & soluzioni

- **Contratto di payload non uniforme (la radice del "Double Read").** Solo `articles.php` (lista)
  ritorna `{data,total,...}`; categorie/tag/navigazione/progetti/search ritornano array nudo. Non c'è
  versione né header di forma: il client deve indovinare con `Array.isArray`. **Soluzione "thin
  stack":** invece di rompere il contratto si è esteso in-place e il client legge due volte. **Costo:**
  fragilità (vedi bug C3 `hasMore` sbagliato su array senza `total`) e impossibilità di sapere a priori
  la forma. Gold per il libro: "quando estendere un contratto invece di versionarlo, e cosa costa".
- **Ricerca = `LIKE %q%` su `content`, niente full-text reale.** `articles.php:192-198` e
  `search.php:32` usano `LIKE '%term%'` su `title/content/excerpt/tags`. Niente indice FULLTEXT, niente
  ranking di rilevanza (il commento `search.php:72` lo ammette: "sort semplice per ora"). Funziona su
  cataloghi piccoli; il `q` è cappato a 100 char (`articles.php:193`) "per evitare query lentissime".
  Onesto limite del thin stack — box "quando `LIKE` basta e quando no".
- **`search.php` ordina su date eterogenee** (`search.php:29` `published_at` per articoli vs
  `:56` `created_at` per progetti, entrambe aliasate `date`): se `published_at` è `NULL` (bozza vista da
  admin), `strtotime(null)` → 0 e l'item finisce in fondo. Bordo da conoscere.
- **`projects.php` non pagina:** ritorna sempre tutti i progetti (filtrabili per categoria). Coerente
  oggi (pochi progetti), ma è l'asimmetria che genera il Double Read nel `portfolioLoader`. Se i
  progetti crescessero, servirebbe la stessa paginazione degli articoli.
- **`DELETE` articolo senza cascata esplicita su `article_tags`** (`articles.php:328`): si cancella la
  riga `articles` ma non i link in `article_tags` nel codice — dipende dalla FK `ON DELETE CASCADE` a
  schema (C1). Da verificare lato DB che la FK esista, altrimenti orfani. → puntatore C1/C13.
- **`navigation.php` duplica la query di `categories.php`** con include diverso (`navigation` non ha
  `auth_helper`). Due fonti di verità per la stessa tabella: rischio di drift se cambia l'ordinamento.

## 5. Estetica / UX (moderna ma funzionale)

C4 è back-end, ma alcune scelte server **esistono per la UX**:

- **Ordinamento "editoriale" a tre livelli** (`articles.php:217`): `is_category_pinned DESC,
  is_featured DESC, data DESC`. Il pin di categoria batte la vetrina globale che batte la cronologia:
  è il "controllo redazionale" che si vede in home e nelle pagine categoria, deciso in una sola
  `ORDER BY`.
- **Un solo pin per categoria** (`articles.php:358-365`): impostare un pin ne toglie automaticamente
  il precedente — UX "radio button" lato dati, l'admin non deve sganciare a mano.
- **Navigazione pre-annidata** (`navigation.php`): il menu arriva al client già ad albero, il
  frontend non deve ricostruire la gerarchia → first paint immediato (ponte al fallback ottimistico
  di C3 `useCategories`).
- **Post programmati** (`published_at` futuro): l'admin pubblica "in anticipo" e il contenuto appare
  da solo all'ora prevista — niente cron, solo un confronto in `WHERE`.

## 6. Differenze rispetto agli altri siti

(Da consolidare in FASE 2. Ipotesi/puntatori:)
- **SitoRuntime (SR-C4)**: avrà news + **speakers + podcasts** (domini in più). Da confrontare: usa
  lo stesso pattern `{data,total}` solo sulla lista principale? Ha full-text reale o anche lì `LIKE`?
- **DISINTELLIGENZA/FDCA (SQLite)**: la paginazione `LIMIT ? OFFSET ?` con `PARAM_INT` è un dettaglio
  MySQL/PDO; su SQLite il binding cambia. La ricerca `LIKE` resta. Buon termine di paragone "minimo".
- Verificare se altrove la **gerarchia categorie** è a un livello (come qui, `parent_id` singolo) o
  più profonda, e se il filtro "categoria-contenitore" esiste.
- Il pattern **tag a doppia scrittura (M:N + CSV legacy)** è probabilmente specifico di SPW (eredità
  di una migrazione): da verificare se SR ha lo stesso doppio binario o solo il modello normalizzato.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **L'endpoint-router su `REQUEST_METHOD`** (un file = una risorsa) | Cap. "L'anatomia di un endpoint nel thin stack" (centrale) |
| **Chiusura del Double Read: solo articles ritorna `{data,total}`** | Cap. "Contratti di payload elastici" (ponte C3, alto valore) |
| **Paginazione backend-driven** (COUNT separato + `PARAM_INT`) | Cap. "Paginare senza librerie: COUNT, LIMIT, OFFSET" |
| **Filtro categoria gerarchico** (include sottocategorie via `IN`) | Box "categorie-contenitore: la gerarchia che cambia i risultati" |
| **Tag a doppia scrittura** (M:N + cache CSV legacy) | Box problemi/soluzioni "migrare un modello senza downtime" (alto valore) |
| **Slug unici con normalizzazione accenti italiani** | Box "localizzare lo slug nel thin stack" |
| **Visibilità pubblico/admin come `AND` condizionale** | Box "un endpoint, due audience" (ponte C2) |
| **Post programmati** (`published_at` futuro, no cron) | Box "pubblicazione differita con una sola WHERE" |
| **Ricerca `LIKE` unificata + campo `type`** | Cap. "Ricerca pragmatica: quando `LIKE` basta" |
| **Ordinamento editoriale a 3 livelli + un solo pin per categoria** | Box "controllo redazionale nei dati" |
| **`sanitizeUrl` dei CTA** (whitelist http/mailto) | Box "sanitizzare gli URL di contenuto" (ponte C6) |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - `articles.php:11-13` forza `date_default_timezone_set('Europe/Rome')` → tema C1 (bootstrap/timezone),
    già visto in SPW-C1. Qui rilevante solo perché governa la visibilità dei post programmati.
  - `sanitizeUrl` e la sanitizzazione del `content` → **C6** (Editor/sanitizzazione): qui solo i CTA.
  - `cover_image` è una stringa URL salvata tale e quale → **C5** (Media/Upload): la *gestione* del
    file è altrove, C4 memorizza solo il percorso.
  - `article_views`/analytics (`a.id` viste) → **C11** (Engagement): non toccati qui.
  - La **FK `ON DELETE CASCADE`** su `article_tags`/schema tabelle → **C1/C13** (DB): da verificare che
    la cascata esista, altrimenti la DELETE articolo lascia link orfani (vedi §4).
- **Double Read CHIUSO:** la mappa server è completa (tabella §2). Unico `{data,total}` =
  `articles.php` lista. Tutto il resto = array nudo. Il client (C3) fa Double Read perché *mescola* le
  due famiglie nei loader, non perché un singolo endpoint cambi forma.
- **Da verificare (DB, C1):** esistenza tabella `article_tags` con FK, e se `articles.tags` (CSV) sia
  ancora letto da qualche consumatore oltre alla `search.php:32` (`a.tags LIKE`).
- **`navigation.php`** è l'unico endpoint di contenuto senza `auth_helper`: corretto (read-only
  pubblico) ma asimmetrico vs `categories.php` GET.
- Nessuna credenziale/segreto presente negli endpoint (la connessione passa da `db.php`/`config.php`
  di C1).
- Versione del sito al momento della mappatura: **1.21.0** (coerente con SPW-C1/C2/C3); i filtri
  avanzati GET sono marcati `v1.8.5` (`articles.php:90,135`), la gerarchia categorie `v1.10.2` (`:152`).
