# Mappatura — DISINTELLIGENZA — C10: Festival Logic (participants / votes / settings / stats)

> **Stato:** COMPLETATO
> **Sessione:** 25 · **Data:** 2026-06-18 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `DISINTELLIGENZA/`)
> - `public/api/participants.php` (ciclo di vita: submit pubblica `pending` → `update_status` approved/rejected → `update_round`)
> - `public/api/votes.php` (meccanica voto: 1–3 preferenze, `in_current_round`, `vote_count`, `session_id`)
> - `public/api/settings.php` (master switch del festival: voting/registration active+period, maintenance; UPSERT)
> - `public/api/stats.php` (classifiche/aggregazioni + storage breakdown)
> - `public/api/reset_votes.php` · `reset_system.php` (reset turno vs reset totale — significato nel flusso)
> - `public/api/init_db.php:46-70` (schema `participants` + `votes`, letto per gli stati e le colonne)
> - confronto: `SPW-C11` (reazioni/voto pubblico) — SPW/SR non hanno festival logic

## 1. Cosa fa (sintesi narrativa)

C10 è **il cuore di DISINTELLIGENZA** e l'unico cluster che **non esiste negli altri due siti**: la
logica di un **concorso musicale a votazione pubblica e a turni**. È ciò che rende DISINTELLIGENZA un
"sito-festival" e non un blog. Tutto ruota attorno a due entità — i **partecipanti** (`participants`)
e i **voti** (`votes`) — governate da una manciata di **interruttori globali** (`settings`) e
osservate da un endpoint di **statistiche** (`stats`).

Il flusso completo del festival:

1. **Iscrizione (pubblica).** `participants.php?action=submit` crea un partecipante in stato
   `pending` (`participants.php:129`), ma solo se `settings.registration_active` è acceso. L'audio
   arriva da `upload.php` (DIS-C5, pubblico). → la *sicurezza* della submit è DIS-C2; qui conta che è
   l'ingresso nel concorso.
2. **Selezione (admin/editor).** `participants.php?action=update_status` porta il partecipante a
   `approved` (con email "Purtroppo sei dei nostri" + iscrizione newsletter) o `rejected` (con email);
   `update_round` accende/spegne il flag `in_current_round` (`participants.php:151-227`).
3. **Voto (pubblico, a turni).** `votes.php` accetta **1–3 preferenze** ma **solo** per partecipanti
   con `in_current_round = 1` (`votes.php:41`), solo se `settings.voting_active` è acceso, una volta
   per IP/24h. Ogni preferenza incrementa il **contatore denormalizzato** `participants.vote_count`.
4. **Classifica.** `stats.php` (gated) e il report email di `settings.php` leggono `vote_count` per
   produrre la **Top 5 / Top 20**.
5. **Reset del turno o totale.** `reset_votes.php` azzera i voti e `vote_count`, chiude le votazioni e
   **mantiene gli iscritti** (per ripartire con un nuovo turno cambiando i flag `in_current_round`);
   `reset_system.php` cancella **tutto** (partecipanti + voti + audio). Entrambi fanno backup (DIS-C2).

La sintesi: un **festival a eliminazione multi-turno gestito a mano** dall'admin (nessun bracket
automatico), con voto pubblico vincolato dai master switch e dal flag di turno.

## 2. Pattern miniCMS rilevanti

- **Macchina a stati del partecipante** (`init_db.php:55` + `participants.php`): stati
  `pending → approved | rejected` (e `finalist` previsto nello schema ma **mai impostato** dal codice
  — vestigiale, vedi §4). La transizione è un semplice `UPDATE participants SET status = ?`
  (`participants.php:178`) con effetti collaterali (email, newsletter) cablati nel ramo.
- **Master switch come righe della tabella `settings`** (`voting_active`, `registration_active`,
  `voting_period`, `registration_period`, `maintenance_mode`): interruttori globali letti dagli
  endpoint pubblici (`votes.php:11`, `participants.php:106`) e scritti solo dall'admin
  (`settings.php:65`). È il "feature flag" del thin stack: niente sistema di config, solo coppie
  chiave/valore nel DB. **`GET settings.php` è pubblico** (`:51`): il frontend legge gli stati per
  sapere se mostrare il form di voto/iscrizione.
- **UPSERT SQLite per i settings** (`settings.php:87,98`): `INSERT INTO settings (key,value) VALUES
  (?,?) ON CONFLICT(key) DO UPDATE SET value = excluded.value`. Sintassi **specifica di SQLite**
  (conferma DB vivo); si appoggia all'unicità di `key` (schema da `update_db_0_1_4`, DIS-C1). Gestisce
  sia update singolo (`{key,value}`) sia bulk (`{k:v,...}`).
- **Voto multi-preferenza con contatore denormalizzato** (`votes.php:34,71`): 1–3 preferenze per
  sessione, ognuna una riga in `votes` con lo stesso `session_id`, ognuna `+1` a
  `participants.vote_count`. La **classifica si legge dal contatore**, non da `COUNT(votes)`
  (`stats.php:35`, `settings.php:19-22`): denormalizzazione per velocità, da tenere coerente (vedi §4).
- **Flag di turno `in_current_round`** (`participants.php:220` + `votes.php:41`): è il meccanismo dei
  round. L'admin marca chi è "in gara adesso"; il pubblico può votare **solo** quei partecipanti; a
  fine turno `reset_votes` azzera e si riparte cambiando i flag. Round **manuali**, nessuna logica di
  eliminazione automatica.
- **Due "metriche" del voto**: `totalVotes = COUNT(*)` (preferenze totali) vs
  `totalVoters = COUNT(DISTINCT session_id)` (sessioni di voto) (`settings.php:12-16`). Distinzione
  pulita tra "quante preferenze" e "quante persone".
- **Reset come parte del ciclo, non solo manutenzione** (`reset_votes.php`): "Voti resettati. Iscritti
  mantenuti." (`:35`) è un'azione **di gioco** (chiudi turno, riparti), non un'emergenza. Diverso dal
  reset totale `reset_system.php` (azzera il festival). Entrambi cancellano anche `sqlite_sequence`
  (ID reset, SQLite vivo).
- **Report finale automatico (disabilitato)** (`settings.php:103-106`): alla chiusura delle votazioni
  (`voting_active` true→false) il codice **rileverebbe** il "closing" e invierebbe via email la
  classifica Top 20 (`sendVotingReport`), ma la chiamata è **commentata** ("REPORT DISABLED AS PER
  REQUIREMENTS (Phase 2)"). Feature costruita e spenta.

## 3. Codice chiave (stralci con origine)

**Voto vincolato al turno + contatore denormalizzato in transazione** — `votes.php:39-76`:

```php
// Verify participants are in current round
$placeholders = implode(',', array_fill(0, count($votes), '?'));
$stmt = $pdo->prepare("SELECT COUNT(*) FROM participants WHERE id IN ($placeholders) AND in_current_round = 1");
$stmt->execute($votes);
if ($stmt->fetchColumn() != count($votes)) { /* 400: 'non sono in gara in questo turno' */ }
// ...
$session_id = uniqid();
$pdo->beginTransaction();
$ins = $pdo->prepare("INSERT INTO votes (participant_id, session_id, ip_address, user_agent) VALUES (?, ?, ?, ?)");
$inc = $pdo->prepare("UPDATE participants SET vote_count = vote_count + 1 WHERE id = ?");
foreach ($votes as $pid) { $ins->execute([$pid, $session_id, $ip, $ua]); $inc->execute([$pid]); }
$pdo->commit();
```

**Macchina a stati del partecipante con effetti collaterali nel ramo** — `participants.php:177-195`:

```php
$pdo->prepare("UPDATE participants SET status = ? WHERE id = ?")->execute([$status, $id]);
if ($status === 'approved') {
    $emailData = getEmailTemplate('approved', $participant['stage_name'] ?: $participant['name']);
    sendEmail($participant['email'], $emailData['subject'], $emailData['body']);          // → C9
    $pdo->prepare("INSERT OR IGNORE INTO newsletter_subscribers (email, subscribed_at) VALUES (?, datetime('now'))")
        ->execute([$participant['email']]);                                                // → C9 (consenso?)
} elseif ($status === 'rejected') {
    $emailData = getEmailTemplate('rejected', ...); sendEmail(...);
}
```

**Master switch: GET pubblico + POST admin con UPSERT + detect "closing voting"** — `settings.php:51-106`:

```php
if ($method === 'GET') {                                   // PUBBLICO: il frontend legge gli stati
    $stmt = $pdo->query("SELECT key, value FROM settings");
    while ($row = $stmt->fetch()) { $settings[$row['key']] = $row['value']; }
    if (!isset($settings['voting_active'])) $settings['voting_active'] = '0';
    echo json_encode($settings);
} elseif ($method === 'POST') {                            // ADMIN
    if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'admin') { /* 401 */ }
    // bulk: normalizza i booleani a stringa 'true'/'false'  <-- ORIGINE dell'ambiguità '1' vs 'true'
    $stmt = $pdo->prepare("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value");
    $stmt->execute([$k, is_bool($v) ? ($v ? 'true' : 'false') : $v]);
    // if ($closingVoting) { sendVotingReport($pdo); }     <-- DISABILITATO (Phase 2)
}
```

**Classifica dal contatore denormalizzato + storage breakdown** — `stats.php:33-41,63-79`:

```php
if ($stats['votes_count'] > 0) {
    $stats['top_voted'] = $pdo->query("SELECT name, stage_name, vote_count FROM participants
                                       ORDER BY vote_count DESC LIMIT 5")->fetchAll(PDO::FETCH_ASSOC);
}
// ...storage via RecursiveDirectoryIterator per cartella (images / audio/participants / audio/podcasts)
$stats['storage_breakdown'] = ['images'=>..., 'audio_participants'=>..., 'audio_podcasts'=>..., 'total'=>...];
```

**Reset del turno (mantiene iscritti) — azione di gioco** — `reset_votes.php:26-35`:

```php
$pdo->exec("DELETE FROM votes");
$pdo->exec("DELETE FROM sqlite_sequence WHERE name='votes'");      // SQLite vivo
$pdo->exec("UPDATE participants SET vote_count = 0");              // riallinea il denormalizzato
$pdo->exec("UPDATE settings SET value = 'false' WHERE key = 'voting_active'");
echo json_encode(['status'=>'success','message'=>'Voti resettati. Iscritti mantenuti.']);
```

## 4. Problemi riscontrati & soluzioni

- **GOLD — il `vote_count` denormalizzato è la fonte di verità della classifica.** Sia `stats.php:35`
  sia `settings.php:19-22` (report) ordinano per `participants.vote_count`, **non** per `COUNT(votes)`.
  Il contatore è incrementato solo nella transazione di `votes.php:71`; se andasse fuori sincrono
  (modifica manuale del `.sqlite`, riga `votes` inserita altrove, vecchi dati) la **classifica
  sarebbe sbagliata** senza che nulla lo segnali. La transazione protegge il caso normale, e
  `reset_votes` riallinea (`UPDATE ... vote_count = 0` insieme al `DELETE FROM votes`), ma manca una
  reconciliation `vote_count = (SELECT COUNT(*) FROM votes ...)`. → Box "il contatore denormalizzato:
  veloce ma da riconciliare".
- **GOLD — lo stato `finalist` è vestigiale.** Lo schema prevede `status` ∈
  `pending/approved/rejected/finalist` (`init_db.php:55`), ma **nessun endpoint** imposta mai
  `finalist` (`update_status` accetta ciò che arriva dal client, ma il frontend invia approved/
  rejected; non c'è logica di "finale"). Probabile residuo di un design a fasi mai completato — i
  "round" sono realizzati con il flag booleano `in_current_round`, non con lo stato `finalist`. →
  Box "stati previsti e mai usati: lo schema che racconta un piano abbandonato".
- **GOLD — round manuali via flag booleano, nessuna meccanica di eliminazione.** Il "turno" è solo
  `in_current_round = 0|1` impostato a mano dall'admin (`update_round`). Non esiste un concetto di
  "turno N", né storicizzazione dei voti per turno (il `reset_votes` **cancella** i voti del turno
  precedente: la storia delle classifiche dei turni passati **va persa**, salvo il backup `.bak`). Il
  festival multi-turno esiste come *procedura manuale*, non come modello dati. → Box "modellare i
  turni: flag booleano vs entità round" (alto valore, anticipa FDCA).
- **GOLD — `update_status`/`update_round` gated solo `isset(user_id)` (NON `isAdmin`).** Confermato da
  DIS-C2: un **editor** può approvare/respingere partecipanti (inviando email reali) e cambiare i
  round. Su un concorso, decidere chi passa il turno è un'azione admin-level. → ponte C2 (ruoli).
- **Terza strategia di "adesso" nello stesso dominio.** Già visto: `news.php`/`votes.php` usano
  `CURRENT_TIMESTAMP`/`datetime('now')` (SQLite, UTC); `participants.php:129` usa `datetime('now')`
  (SQLite). Ma `stats.php:20` usa **PHP** `date('Y-m-d H:i:s', strtotime('-1 day'))` per "iscritti
  nelle ultime 24h" — confronto in fuso server contro `submitted_at` salvato in UTC. Quindi il
  contatore "nuovi iscritti" è sfasato del delta server↔UTC. Tre strategie di tempo, una incoerenza in
  più (consolidare con DIS-C4). → Box "tre modi di dire 'adesso' nello stesso sito".
- **Report finale costruito e disabilitato (codice morto utile).** `sendVotingReport` (`settings.php:
  10-49`) è completo (Top 20 via email a `runtimeradio@gmail.com`) ma **commentato** (`:104-105`). È
  documentazione viva di una feature pianificata ("Phase 2"): da segnalare come debito/feature
  dormiente, e come gemello del Telegram-fossile di SitoRuntime. → nota.
- **`settings.php` GET è pubblico e ritorna TUTTI i settings.** `:51-61` espone l'intera tabella
  chiave/valore senza filtro: oltre a voting/registration active espone anche `voting_period`,
  `registration_period`, `maintenance_mode` e qualunque altra chiave. Innocuo per ora (sono flag), ma
  se un domani entrasse un settaggio sensibile finirebbe pubblico. → nota "GET-all senza allowlist".
- **Email + iscrizione newsletter all'approvazione = consenso implicito.** `participants.php:188`
  fa `INSERT OR IGNORE INTO newsletter_subscribers` quando un partecipante è approvato: l'iscrizione
  alla newsletter è un **effetto collaterale dell'approvazione**, senza un consenso esplicito separato
  (i commenti `:136-143` mostrano lo sviluppatore in dubbio proprio su questo). GDPR/consenso → C9. →
  ponte C9.
- **Codice con artefatti/duplicazioni** (`stats.php:17,44` commenti "Fix: Removed duplicate line",
  "System: Storage Usage (Safe Check)" ripetuto): stessi segni di generazione-AED già visti in
  `init_db.php` ("in repl", DIS-C1). Innocui ma indicativi della genesi del codice. → nota.

## 5. Estetica / UX (moderna ma funzionale)

- **Brand voice dentro la logica.** Le email di concorso (`participants.php:27-60`, template
  received/approved/rejected) sono comico-dissacranti ("il server ha appena ingerito la tua
  candidatura", "Purtroppo sei dei nostri", "Fallimento respinto"): il tono del festival è cablato nel
  backend. La logica di concorso **è** anche identità editoriale.
- **Messaggi di voto guidati** (`votes.php:21,36,47,61`): l'utente sa sempre perché è bloccato
  (votazioni chiuse / 1–3 preferenze / partecipante non in gara / già votato da questo IP). UX di
  errore chiara su un'azione pubblica.
- **Statistiche con storage breakdown** (`stats.php:73-79`): il pannello admin vede non solo
  partecipanti/voti ma anche **quanto spazio** occupano immagini/audio partecipanti/podcast — utile in
  un festival che riceve molti upload audio (ponte all'upload pubblico di DIS-C5). UI = C12.
- **Conferma a due passi sul reset totale** (`reset_system.php`, DIS-C2): rete di sicurezza UX su
  un'azione che cancella il festival.
- **Doppia metrica voti/votanti** esposta nel report: "Voti Totali" vs "Votanti Unici"
  (`settings.php:32-33`) — trasparenza sul significato dei numeri.

## 6. Differenze rispetto agli altri siti

**DISINTELLIGENZA è l'unico sito con festival logic.** SimonePizziWebSite e SitoRuntime **non hanno**
participants/votes/round/settings-switch: il confronto §6 è quindi **prevalentemente interno** + il
rilievo dell'assenza altrove, con un parallelo all'unico meccanismo "di voto pubblico" presente
altrove (le **reazioni** di SPW-C11).

| Aspetto | SimonePizziWebSite | SitoRuntime | **DISINTELLIGENZA (questa card)** |
|---|---|---|---|
| **Festival logic** | **assente** | **assente** | **presente** (cuore del sito) |
| **Voto pubblico** | reazioni emoji (SPW-C11, toggle) | — | **voto a 1–3 preferenze, a turni** |
| **Anti-doppio (identità)** | `voter_hash` SHA256(IP+UA), UNIQUE KEY | — | cookie + IP/24h, **IP/UA in chiaro** (DIS-C2) |
| **Anti-doppio (storage)** | `INSERT IGNORE` su UNIQUE (DB) | — | `COUNT` su IP/24h (applicativo) |
| **Conteggio** | aggregazione `COUNT` a richiesta | — | **contatore denormalizzato** `vote_count` |
| **Stati/workflow** | published/draft (contenuti) | published/draft + status migrato | **pending/approved/rejected** (+finalist vestigiale) |
| **Feature flag** | `app_settings` (admin, C12) | nessun settings store (SR-C12) | **`settings` master switch** letti in pubblico |
| **Turni/round** | — | — | **flag `in_current_round` manuale** |
| **Reset di dominio** | — | — | **reset turno vs reset totale** (+ backup) |

**Sintesi.** Il festival è ciò che giustifica l'intero sito e spiega molte scelte già viste:
l'**upload pubblico** (DIS-C5) serve le candidature; l'**auth grado-zero** (DIS-C2) basta perché le
azioni pubbliche (voto, iscrizione) non sono autenticate per natura; i **master switch pubblici**
(`settings`) pilotano la UI a fasi (iscrizioni aperte → voto aperto → chiuso). Rispetto all'unico
parente (le reazioni di SPW-C11), il voto del festival è **più ricco** (preferenze multiple, turni,
classifica, ciclo di vita partecipante) ma **meno rigoroso sull'identità** (SPW hash + UNIQUE a DB;
DIS contatore denormalizzato + IP/24h applicativo + PII in chiaro). È il caso di studio "logica di
dominio in un thin stack": una macchina a stati + flag globali + un contatore, senza framework né
motore di workflow. **FDCA** (prossimo, fork) andrà confrontato proprio qui: cosa cambia il fork nel
modello festival.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Anatomia di una festival logic nel thin stack** (entità + flag + contatore) | Cap. nuovo/dedicato "Logica di dominio: un concorso a votazione" (alto valore) |
| **Master switch come righe `settings`** (feature flag senza config), GET pubblico | Box "feature flag fai-da-te: la tabella chiave/valore" |
| **UPSERT SQLite `ON CONFLICT DO UPDATE`** | Box "scrivere un setting in modo idempotente" |
| **Contatore denormalizzato vs COUNT** (classifica veloce ma da riconciliare) | Box "denormalizzare un conteggio: quando conviene e cosa rischi" |
| **Round manuali via flag booleano vs entità 'round'** | Box "modellare i turni di un concorso" (anticipa FDCA) |
| **Stati previsti e mai usati** (`finalist`) | Box "lo schema che racconta un piano abbandonato" |
| **Voto pubblico: festival (preferenze/turni) vs reazioni (toggle)** | Cap. "Voto e engagement pubblico" (ponte SPW-C11) |
| **Reset come azione di gioco** (turno) vs reset totale + backup | Box "operazioni di dominio distruttive ma reversibili" (ponte DIS-C2/SR-C13) |
| **Feature costruita e disabilitata** (report finale commentato) | Box "codice dormiente: feature spente nel repo" |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - **Email** (`sendEmail`, template comici, `mail()` nativa, report `sendVotingReport`, iscrizione
    newsletter all'approvazione) → **C9** (Newsletter & Email): la submit/approvazione le innesca; il
    consenso GDPR dell'`INSERT OR IGNORE newsletter` è una domanda C9.
  - **Sicurezza/anti-frode/ruoli** (cookie+IP/24h, REMOTE_ADDR, backup pre-reset, gate
    `update_status`/`update_round` solo `isset(user_id)`) → **C2** (già mappato): qui richiamati come
    puntatori, non ri-descritti.
  - **Upload audio dei partecipanti** (`audio_file`) → **C5** (già mappato): la catena candidatura→file
    è pubblica.
  - **UI admin del festival** (pannelli partecipanti, toggle round, dashboard stats, storage
    breakdown) → **C12** (Admin Dashboard): `stats.php` produce i dati, la *presentazione* è C12.
  - **Schema/DB** (`participants`/`votes`/`sqlite_sequence`, `vote_count`, `in_current_round`) →
    bootstrap = **C1**; eventuale storia/incidenti = DIS-C13 se aperta.
- **Da verificare in C12:** chi chiama `update_round`/`update_status` dalla UI e se l'admin ha un modo
  per riconciliare `vote_count` con `COUNT(votes)` (oggi non risulta).
- **Da verificare in FDCA-DIFF:** se il fork cambia il modello festival (stati, round, conteggio,
  anti-frode) — è il confronto naturale di questa card.
- **Conferma cross-card:** `settings.php` (bulk update `is_bool ? 'true':'false'`, `:99`) è l'**origine**
  dell'ambiguità `'1'` vs `'true'` che `votes.php`/`stats.php`/`participants.php` neutralizzano con
  `=== '1' || === 'true'` (DIS-C1/C2).
- Versione del sito al momento della mappatura: **0.5.x** (`package.json`).
