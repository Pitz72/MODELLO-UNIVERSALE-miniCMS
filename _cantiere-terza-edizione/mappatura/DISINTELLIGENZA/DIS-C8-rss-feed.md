# Mappatura — DISINTELLIGENZA — C8: RSS & Feed (podcast)

> **Stato:** COMPLETATO · **(card aggiunta in FASE 1-bis: colmatura gap di copertura, 2026-06-18)**
> **Sessione:** 29 · **Data:** 2026-06-18 · **Commit:** _(in corso)_ · **(coppia con DIS-C7)**
> **File sorgente ispezionati:** (percorso relativo al sito `DISINTELLIGENZA/`)
> - `public/api/feed.php` (feed RSS 2.0 **podcast** con namespace iTunes; sorgente = tabella `podcasts`)
> - richiami: `podcasts.php` (CRUD podcast admin, DIS-C4), `settings.php` (chiavi `podcast_*`, DIS-C10), `init_db.php` (schema `podcasts`, DIS-C1)
> - confronto: `SPW-C8-rss-feed.md`, `SR-C8-rss-feed.md`

## 1. Cosa fa (sintesi narrativa)

C8 è la **syndication** di DISINTELLIGENZA, e diverge subito dagli altri due siti: non è un feed di
**news**, è un **feed podcast** in RSS 2.0 con il namespace **iTunes** (`feed.php`). Espone la tabella
`podcasts` (DIS-C4) come un podcast sottoscrivibile (Apple Podcasts/Spotify-style), con canale
(title/description/image/author/owner/category) e item (episodi con `enclosure` audio).

Due osservazioni la caratterizzano:

1. **DIS non ha un RSS di news.** SPW-C8 emette il feed news, SR-C8 ha un *trittico* (feed news +
   proxy podcast esterni + feed_config). DIS ha **solo** questo feed podcast: le news non sono
   sindacate da nessuna parte. È il dominio "emettitore" più ridotto dei tre.
2. **Il file è pieno di commenti "ragionamento ad alta voce".** `feed.php:26-34,57` contiene il più
   estremo esempio del repo di codice AI-assistito che **discute con sé stesso** dentro la sorgente di
   produzione ("During init_db.php step… I created a 'podcasts' table? Let's check init_db.php if I
   can. If not, I'll check if I need to CREATE it.", "Fallback: …create it via SQL here? No, bad
   practice on GET."). È un GOLD documentale (vedi §4).

## 2. Pattern miniCMS rilevanti

- **Feed podcast RSS 2.0 + iTunes** (`feed.php:37-78`): `<rss>` con
  `xmlns:itunes`/`xmlns:content`, canale con `itunes:author`/`itunes:owner`/`itunes:category`/
  `itunes:image`, item con `enclosure` audio e `itunes:duration`/`itunes:image`. È il formato standard
  per le directory podcast — un dominio che SPW/SR non coprono così.
- **Canale configurabile via `settings` con fallback hardcoded** (`feed.php:9-22`): legge le chiavi
  `podcast_*` da `settings` (title/description/image/author/copyright) e, se assenti, usa default
  hardcoded. **Nota:** queste chiavi **non** sono create da alcun `update_db_*` (DIS-C1) → in pratica
  il feed gira quasi sempre sui **default hardcoded** (la configurabilità è aspirazionale). Ponte
  DIS-C10 (settings).
- **Item dal `podcasts`** (`feed.php:59-72`): `SELECT * FROM podcasts ORDER BY published_at DESC`,
  ogni riga → `<item>` con `title`/`link`/`guid`/`pubDate`/`description`/`enclosure`/durata/immagine.
- **Escape parziale** (`feed.php:63-70`): `title`, `link`, `guid`, `audio_url`, `duration`,
  `cover_image` passano da `htmlspecialchars`; la **`description`** è emessa **grezza dentro `CDATA`**
  (`:67`). Mix di escape (la maggior parte) + CDATA (la description).
- **`pubDate` in formato RFC** (`feed.php:61`): `date(DATE_RSS, strtotime($published_at))` — conversione
  corretta al formato RSS.
- **Degradazione a feed vuoto** (`feed.php:56,73-75`): se la tabella `podcasts` non esiste o la query
  fallisce, `catch` vuoto → feed senza item (channel comunque emesso). Stessa filosofia "catch vuoto"
  di SPW-C8.
- **`Content-Type: application/xml`** (`feed.php:3`): corretto-ish (più preciso sarebbe
  `application/rss+xml`).

## 3. Codice chiave (stralci con origine)

**Canale podcast da settings con fallback hardcoded** — `feed.php:8-22`:

```php
$stmt = $pdo->query("SELECT key, value FROM settings WHERE key LIKE 'podcast_%'");
while ($row = $stmt->fetch()) { $settings[$row['key']] = $row['value']; }
$channelTitle = $settings['podcast_title'] ?? "Festival della Disintelligenza Naturale";   // chiavi mai create -> fallback
$channelDesc  = $settings['podcast_description'] ?? "Il podcast ufficiale del festival disintelligente.";
$author       = $settings['podcast_author'] ?? "Disintelligenza Team";
```

**Item podcast: escape parziale + description in CDATA** — `feed.php:59-71`:

```php
$stmt = $pdo->query("SELECT * FROM podcasts ORDER BY published_at DESC");
while ($row = $stmt->fetch()) {
    $date = date(DATE_RSS, strtotime($row['published_at']));
    echo "<item>
        <title>".htmlspecialchars($row['title'])."</title>
        <link>".htmlspecialchars($channelLink.'/podcast/'.$row['id'])."</link>
        <guid>".htmlspecialchars($row['audio_url'])."</guid>          <!-- GUID = URL audio (instabile) -->
        <pubDate>$date</pubDate>
        <description><![CDATA[".$row['description']."]]></description>  <!-- description GREZZA in CDATA -->
        <enclosure url=\"".htmlspecialchars($row['audio_url'])."\" length=\"0\" type=\"audio/mpeg\"/>  <!-- length=0 hardcoded -->
        <itunes:duration>".htmlspecialchars($row['duration'])."</itunes:duration>
    </item>";
}
```

**GOLD documentale — il "ragionamento ad alta voce" in produzione** — `feed.php:26-34`:

```php
// Fetch episodes (assuming news category 'podcast' OR new table 'podcasts')
// Decision: Using 'podcasts' table (defined in init_db.php? Let's assume yes or create it).
// During init_db.php step (Log 0.0.1) I created a 'podcasts' table?
// Let's check init_db.php if I can. If not, I'll check if I need to CREATE it.
// Fallback: if table doesn't exist, I'll create it via SQL here for safety if not present? No, bad practice on GET.
// I'll assume it exists or use NEWS with a category.
```

## 4. Problemi riscontrati & soluzioni

- **GOLD documentale — codice che "pensa ad alta voce" in produzione.** `feed.php:26-34,57` è il caso
  più estremo del repo di commenti-monologo lasciati dall'assistente AI nel sorgente: l'autore si
  chiede se la tabella `podcasts` esista, se crearla al volo, conclude "bad practice on GET", e tira a
  indovinare ("I'll assume it exists"). È lo stesso tell di `init_db.php` ("ignored for brevity in
  repl", DIS-C1), `api.ts` (DIS-C3) e `participants.php`. Per il manuale è materiale prezioso su come
  appare un codebase generato in conversazione con un LLM — e sul perché vada **ripulito** prima del
  deploy. → Box "quando il codice ti racconta i suoi dubbi: i monologhi dell'AI nel sorgente" (alto
  valore, tema ricorrente DIS).
- **GOLD — la configurabilità del canale è aspirazionale.** Il feed legge `settings.podcast_*` ma
  **nessun `update_db_*`** crea quelle chiavi (DIS-C1) e nessuna UI le scrive (DIS-C10/C12 gestiscono
  voting/registration, non `podcast_*`): di fatto il canale gira **sempre sui default hardcoded**
  (`feed.php:17-22`). Codice "pronto a essere configurabile" ma mai cablato. → Box "il setting che
  nessuno popola".
- **`description` grezza in CDATA.** `feed.php:67`: la description dell'episodio è emessa senza escape
  dentro `CDATA`. È admin-authored (i podcast si creano solo da admin, DIS-C4) e CDATA protegge la
  struttura XML, ma un `]]>` nella description romperebbe il blocco, e — non essendoci DOMPurify in
  tutto DIS (DIS-C6) — un eventuale HTML nella description arriverebbe al reader RSS grezzo. Rischio
  basso (admin + CDATA), ma è l'unico campo non escaped. → nota sicurezza.
- **GUID = URL audio (instabile).** `feed.php:65`: il `<guid>` è l'`audio_url`. Se l'audio viene
  rispostato/rinominato (es. dopo `migrate_media.php`, DIS-C5), il GUID cambia → i reader podcast
  ri-scaricano l'episodio come "nuovo". SPW-C8 usava un `urn:` stabile proprio per evitarlo; SR-C8 il
  permalink. DIS usa l'URL del file = il meno stabile. → Box "il GUID che cambia sotto i piedi"
  (ponte SPW-C8).
- **`enclosure length="0"` hardcoded** (`feed.php:68`): la lunghezza in byte dell'audio è fissa a `0`
  invece della dimensione reale del file. Alcuni client podcast la usano per la barra di download →
  comportamento impreciso. → nota.
- **Niente filtro visibilità/pubblicazione** (`:59`): emette **tutti** i podcast (`SELECT *` senza
  `WHERE`). I podcast non hanno colonna `status` (DIS-C4), quindi non è un bug di bozze trapelate come
  in SR-C8, ma è un feed "tutto o niente". → nota.
- **Non emette `news.content`** (è il feed podcast, non news): a differenza di SR-C8 (feed news che
  emette una preview del content escaped), DIS-C8 **non tocca** il content delle news → sul fronte
  XSS-emettitori, il feed di DIS è neutro rispetto al `content` (che resta non sanitizzato solo nel
  render `NewsDetail`, DIS-C6). → chiude il quadro emettitori di DIS (vedi §6).

## 5. Estetica / UX (moderna ma funzionale)

- **Feed podcast "vero"**: con namespace iTunes, `owner`/`email`/`category Arts`/`image`, è
  sottoscrivibile in un'app podcast — esperienza standard per l'ascoltatore, non un semplice RSS di
  testo.
- **Brand voice nei default** (`:17-22`): "Il podcast ufficiale del festival disintelligente." — il
  tono resta on-brand anche nei fallback.
- **CDATA per le description**: permette description ricche (HTML) negli episodi senza rompere l'XML —
  scelta UX corretta per i reader che le renderizzano (col caveat sicurezza di §4).

## 6. Differenze rispetto agli altri siti

Confronto a **TRE** (coppia con DIS-C7).

| Aspetto | SimonePizziWebSite (SPW-C8) | SitoRuntime (SR-C8) | **DISINTELLIGENZA (questa card)** |
|---|---|---|---|
| **Cosa sindaca** | **news** (RSS 2.0) | **trittico**: feed news + proxy podcast esterni + feed_config | **solo podcast** (RSS iTunes) |
| **Feed news** | sì | sì | **assente** |
| **Formato** | RSS 2.0 | RSS 2.0 + proxy XML | **RSS 2.0 + iTunes** |
| **Config canale** | hardcoded + TODO settings | `feed_config` (security theater) | **settings `podcast_*` mai popolati** → hardcoded |
| **GUID** | `urn:` stabile (anti-doppione) | permalink | **URL audio** (il meno stabile) |
| **Escape** | `htmlspecialchars` (excerpt) | strip_tags+escape (content) | **parziale** (description grezza in CDATA) |
| **Emette `content`?** | no (excerpt) | sì (preview escaped) | **no** (feed podcast, non news) |
| **Visibilità** | `status=published` | dimenticata (bozze nel feed) | **N/A** (podcast senza status) |
| **Errori** | catch vuoto → 200 troncato | `PDOException`→500 | **catch vuoto → feed senza item** |

**Sintesi.** DIS-C8 è l'emettitore più **specializzato e ridotto**: niente RSS di news (a differenza
di SPW/SR), solo un feed **podcast iTunes** che gira sui default perché i suoi settings non sono mai
popolati. Sul fronte sicurezza è quasi tutto escaped (tranne la description in CDATA, admin-authored)
e **non emette il content** delle news → non aggrava il buco XSS di DIS-C6. I suoi tratti di valore
per il manuale sono due: il **feed podcast iTunes** (formato che gli altri siti non hanno) e,
soprattutto, i **commenti-monologo** che lo rendono il ritratto più nitido di un codebase
AI-assistito non ripulito.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Feed podcast RSS + iTunes** (il formato che SPW/SR non hanno) | Cap. "Syndication": la variante podcast |
| **I monologhi dell'AI nel sorgente** (codice che racconta i suoi dubbi) | Box "ripulire il codice generato in conversazione" (alto valore, tema DIS) |
| **Il setting che nessuno popola** (config aspirazionale → fallback hardcoded) | Box "feature configurabile mai cablata" |
| **GUID = URL audio**: il guid instabile | confluisce nel box "il GUID che cambia" (ponte SPW-C8) |
| **Escape parziale + CDATA** | confluisce nel box "escape vs CDATA nei feed" |
| **Emettitori del content: DIS non lo tocca nel feed** | confluisce nel quadro "4 emettitori" cross-sito |

## 8. Note / domande aperte

- **Puntatori ad altri cluster:**
  - Tabella `podcasts` e CRUD → **C4** (già mappato): il feed la espone in RSS.
  - `settings.podcast_*` → **C10** (già mappato): chiavi previste ma mai create/scritte.
  - `audio_url` (enclosure/guid) e `migrate_media.php` (sposta gli audio → cambia il GUID) → **C5**
    (già mappato): il legame file↔feed è fragile.
  - Render `news.content` non sanitizzato → **C6** (già mappato): il feed **non** lo emette, quindi
    non propaga il rischio XSS.
- **Quadro "emettitori del content" di DIS (completo con questa card):** il `content` grezzo delle
  news (DIS-C4) è emesso **solo** dal render `NewsDetail` (DIS-C6, senza DOMPurify); la newsletter lo
  escapa/non lo emette (DIS-C9), il proxy SEO non emette il body (DIS-C7), il feed è podcast e non
  tocca le news (questa card). Quindi l'**unico** punto di esposizione XSS-stored del content è il
  render client (DIS-C6) — circoscritto ma privo di difesa.
- Versione del sito: **0.5.x** (`package.json`).
