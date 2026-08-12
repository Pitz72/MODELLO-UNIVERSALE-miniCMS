# Ricognizione — SitoRuntime (Runtime Radio) vs «The Thin Stack» 3ª ed.

> **Data:** 12/08/2026 · **Repo esaminato:** `C:\Users\Utente\Documents\GitHub\SITI-WEB\SitoRuntime`
> **Stato repo:** `main` pulito, allineato a `origin/main`, ultimo commit `c4fb93a`
> **Versione del sito:** **v2.21.0** — il libro lo fotografa a **v2.9.13** (giugno 2026)
> **Tipo di documento:** sola lettura e mappatura. Nessun file del libro è stato modificato.

---

## 1. In una riga

Simone ha lasciato gli appunti dove servivano — `docs/NOTE_PER_IL_MANUALE.md`, 33 KB, tre parti, già
scritti *per* il manuale — e sono buoni; ma la scoperta più importante non è negli appunti: è che
**il sito ha chiuso tutti i debiti che il libro gli attribuisce**, e con essi cade il filo narrativo
che attraversa cinque capitoli.

---

## 2. Cosa ho letto

**Documenti del sito**
`docs/NOTE_PER_IL_MANUALE.md` (integrale) · `docs/INDICE.md` · `docs/README.md` ·
`docs/planning/roadmap.md` · `docs/archivio/analisi/AUDIT_THIN_STACK.md` ·
`docs/archivio/analisi/revisione-11-08-2026.md` · `docs/architecture/ARCHITETTURA.md` (parziale) ·
`README.md`, `package.json`, `.github/workflows/ci.yml` · log git (40 commit).

**Codice verificato riga per riga**
`public/api/`: `sanitize_html.php`, `auth_utils.php`, `db.php`, `db_maintenance.php`, `rate_limit.php`,
`live.php`, `analytics.php`, `uploads_guard.php`, `admin.php` (metà), `newsletter.php` (parziale),
`media.php`, `feed_news_rss.php` · `public/uploads/.htaccess` · `public/index.php` (parziale) ·
`src/api.ts` (integrale) · `tests/php/_api_harness.php`.

**Nel libro** ho grepato i 20 capitoli sulle affermazioni che riguardano SR.

Ogni riga delle tabelle che seguono è **verificata sul codice**, non dedotta dal changelog.

---

## 3. Il fatto centrale: SR non è più il sito del paradosso

Il libro costruisce su SitoRuntime una tesi che ricorre in cinque capitoli e ha perfino un nome —
**«cura senza prevenzione»**, il sito più ingegnerizzato e insieme il meno difeso:

> «SitoRuntime è il sito delle cicatrici di scalabilità, quello che ha vissuto il crash notturno […]
> Eppure è quello con l'admin meno attrezzato: non misura niente e non ha backup. Cioè non ha né
> l'occhio per accorgersi di un problema, né la rete per sopravvivergli.»
> — [CAP 14 §intro](../manuale/CAPITOLO%2014%20-%20Admin%20Dashboard%20%26%20Panels.md), riga 7

**Oggi è falso in entrambe le metà.** SR misura (analytics first-party dalla v2.12.0) e ha la rete
(backup piggyback dalla v2.11.10, più un cron vero sul server dall'11/08/2026).

La causa è documentata: il **29/06/2026** — dieci giorni dopo la chiusura dei contenuti della terza
edizione — Simone ha usato il libro come griglia di audit
(`docs/archivio/analisi/AUDIT_THIN_STACK.md`), ne ha estratto 17 item di rientro numerati per
capitolo, e li ha **chiusi tutti** entro il 18/07. Il documento si chiude da sé con la riga:

> «🏁 PIANO DI RIENTRO COMPLETATO — ultimo item chiuso il 2026-07-18 (v2.11.11).»

Detto altrimenti: **il libro ha funzionato**. Ed è proprio per questo che adesso non descrive più il
sito che descriveva.

---

## 4. Tabella A — dove il libro è smentito dai fatti

Sono affermazioni «dal vivo», cioè fotografie datate: non erano sbagliate, sono **scadute**. Le
elenco perché sono le uniche che, lette oggi da un terzo che apra il repo di SR, farebbero sembrare
il libro impreciso.

| # | Il libro dice | Dove | Oggi | Prova in SR |
|---|---|---|---|---|
| A1 | SR «non ha alcun backup automatico» | CAP 3:99 · CAP 14:7,137,186 · CAP 10:445 · CAP 15:301 | **Falso.** Backup gz fuori docroot, rotazione 14, + cron sul server | `api/db_maintenance.php:97-132`; cron in `roadmap.md:25` |
| A2 | SR «non misura nulla: la sua dashboard è un menu travestito da cruscotto» | CAP 14:7,65,69,186 | **Falso.** Analytics first-party senza cookie + Panoramica | `api/analytics.php` (282 righe, v2.12.0) |
| A3 | «Nessuno dei tre siti ha un interceptor che riconosca il 401/403» | CAP 6:198 · CAP 4:24 | **Falso.** Interceptor unico, con ri-login in overlay | `src/api.ts:12-23` |
| A4 | «Nessun sito ha una tabella `schema_version`» / «i siti reali non ce l'hanno» | CAP 3:83,132 · CAP 15:60,92 | **Falso.** Registro + auto-registrazione delle migrazioni lazy | `api/db_maintenance.php:12-34` |
| A5 | Il cookie di SR «viaggia senza `Secure`», niente `session_regenerate_id`, rate-limit aggirabile con un header | CAP 10:5,169-174,194,477 | **Falso** su tutti e tre | `auth_utils.php:10-15,97-116`; `admin.php:124` |
| A6 | SR non ha `uploads/.htaccess`: «una sola rete, la validazione applicativa» | CAP 7:98,102 | **Falso.** Difesa statica **e** ricreata a runtime | `public/uploads/.htaccess`; `api/uploads_guard.php` |
| A7 | Il prerender SEO riemette il corpo con `strip_tags`, «gli attributi sopravvivono» (la falla viva del filo dei 4 emettitori) | CAP 8:§4 · CAP 11:§4 | **Chiusa.** Sanitizzatore condiviso con bonifica attributi e URL | `api/sanitize_html.php`; usato in `index.php:317` |
| A8 | SR usa il permalink come GUID (`isPermaLink="true"`): al cambio slug ripubblica | CAP 12:144,147-148 | **Falso.** GUID a URN | `feed_news_rss.php:45,71` |
| A9 | Bozze backdatate esposte a crawler/feed/sitemap (nessun filtro `status`) | CAP 9 · CAP 11 · CAP 12 | **Falso.** Filtro presente in tutti e tre | `feed_news_rss.php:18`; `index.php:131,217`; `sitemap.php:42` |
| A10 | Newsletter di SR: «un solo token» fuso, nessun rate-limit sull'iscrizione, unsubscribe via GET | CAP 13:53,109,122-123,184 | **Falso** su tutti e tre. Token separati, 5/ora/IP, unsubscribe in POST | `newsletter.php:19-20,95-102`; `src/api.ts:263` |
| A11 | La seo-cache «scritta ma mai letta», scudo anti-DDoS orfanato | CAP 11:149-194 (§6 e §7, due sezioni intere) | **Rimossa** (scelta dichiarata: rimuovere invece che ricollegare) | `rebuild_seo_cache.php` non esiste più; zero occorrenze di `seo_news_*` |
| A12 | SR ha «due editor separati» e il residuo `react-quill.d.ts` | CAP 8:54 (nota) | **Parzialmente falso.** Un `RichTextEditor` unico, `react-quill.d.ts` rimosso. **Lo shim Quill→Tiptap resta**, per scelta motivata (contenuti legacy in DB) | `src/components/admin/RichTextEditor.tsx:36-38,104` |
| A13 | La «console nascosta» di `admin.php`: azioni potenti via GET, protette dal solo login, senza CSRF né ruolo | CAP 14:146 | **Da riverificare.** Le azioni di gestione utenti sono passate a `requireCap` + `validateCsrf`; **non ho letto le migrazioni `?action=apply_*`**, che il README elenca ancora | `admin.php:207-260` (verificato); resto non letto |

**Nota su A12 e A13:** sono le due sole righe di questa tabella che non sono un «falso» netto. Le
tengo separate apposta — lo shim è un debito *scelto*, e la console nascosta l'ho verificata solo a
metà.

### La riga che *non* è caduta

CAP 14 §2 dice che in SR «il gate nasconde il contenuto ma non il pulsante». Con `requireCap()` su
tutti gli endpoint e la mappa speculare lato client dichiarata «solo estetica»
(`auth_utils.php:56-61`), questa critica è chiusa **meglio** di come il libro chiedeva: il sito ha
prodotto la formulazione che il Canone dovrebbe adottare.

---

## 5. Tabella B — il Canone che ha retto

Non tutto è da riscrivere: queste sono le prescrizioni del libro che, applicate a un sito vero,
**hanno funzionato senza modifiche**. Vale la pena registrarle perché sono la prova che il Canone è
implementabile, non solo predicabile.

| Prescrizione | Capitolo | Come si è dimostrata giusta |
|---|---|---|
| PDO singleton, `EMULATE_PREPARES=false`, utf8mb4 | 3 | Mai messa in discussione in 12 versioni |
| Separazione dei piani, niente framework, file-per-endpoint | 1, 2, 5 | Regge a 25 endpoint |
| DOMPurify al render come choke-point | 8 | Invariato; il sanitizzatore server-side gli si è affiancato, non sostituito |
| Dynamic Rendering per il SEO | 11 | Invariato — e ha prodotto un effetto collaterale che il libro non dichiara (vedi C.7) |
| Double opt-in con due token distinti | 13 | Implementato *dopo* averlo letto nel libro |
| Fuso orario in prelude condiviso | 5, 9 | `tz.php`. Ed è qui che si è manifestato l'incidente più istruttivo di tutti (C.4) |
| Backup fuori docroot | 14 | `dirname(__DIR__, 2) . '/db_backups'` |
| Rate-limit ≠ throttle | 13 | La distinzione è finita **nel commento del codice**, `rate_limit.php:11-12` |
| `.htaccess` deny-by-prefix + `clean-dist` | 2, 15 | Invariati |
| Proxy RSS con allowlist + stale fallback | 12 | Invariato |

---

## 6. Tabella C — il materiale nuovo (le note di Simone, verificate)

Le note sono organizzate in tre parti (A–D, E–G, H–J). Le rimappo **per capitolo del libro**, che è
il taglio che serve per decidere cosa farne. Ho verificato ogni riferimento sul codice.

### C.1 — Implementazioni di riferimento che il libro chiede senza darle

Il libro prescrive cinque cose senza mostrarne il codice. SR le ha dovute inventare, e ora esistono.

| Cosa | Capitolo | File in SR | Perché vale |
|---|---|---|---|
| **Sanitizzatore HTML server-side condiviso** | 8, 11 | `api/sanitize_html.php` (109 righe) | È **il filo rosso del libro** («una sola funzione, usata da tutti gli emettitori») e la funzione non c'è mai. Risolve il punto che il libro solleva e non chiude: `strip_tags` non tocca gli attributi |
| **`getClientIp()`** | 10 | `auth_utils.php:97-116` | La regola «REMOTE_ADDR salvo proxy fidato» è enunciata; la forma corretta (`NO_PRIV_RANGE\|NO_RES_RANGE` per capire *se* siamo dietro proxy) no |
| **`uploads/.htaccess` completo** | 7, 2 | `public/uploads/.htaccess` + `uploads_guard.php` | **Correzione tecnica al libro**, non solo aggiunta: `php_flag engine off` funziona **solo con mod_php**, su PHP-FPM non fa nulla. La difesa universale è il blocco `<FilesMatch>`. Il libro mostra solo la prima |
| **Cookie `Secure` condizionale** | 10 | `auth_utils.php:10-15` | Il Canone dice `cookie_secure=1`; applicato alla lettera **rompe il dev server in HTTP** |
| **Path-guard con `realpath`** | 7 | `media.php:63-65` | Il libro lo cita, non lo mostra |
| **Rate-limit come componente riusabile** | 10, 13, 20 | `api/rate_limit.php` (75 righe) | Il libro lo tratta come caso speciale del login; qui è un componente usato da login, contatti e reazioni |
| **Sessione a scorrimento** | 10 | `auth_utils.php:26-42` | Gotcha vero: `cookie_lifetime` dà scadenza **assoluta dal login**, non timeout d'inattività → admin sloggato *durante una diretta di due ore* |
| **`session_version`, implementazione completa** | 10 | `db.php:66-92` + `db_maintenance.php:42-51` | Il libro lo nomina accanto a `session_regenerate_id`; sono interventi di taglia diversissima |
| **Capability invece di ruoli sparsi** | 10, 14 | `auth_utils.php:63-89` | Da `$_SESSION['role'] !== 'admin'` in 14 file a una mappa + `requireCap()` |
| **Migrazioni lazy + registro + manutenzione piggyback** | 14, 15 | `db_maintenance.php` | Il trittico per hosting condiviso **senza cron e senza SSH** |
| **Cucitura `function_exists`** | 13, App. C | `live.php:98`, `mailer.php` | Il libro la mostra come guardia anti-doppio-include; è anche **il modo di rendere collaudabile una dipendenza esterna senza lasciare porte in produzione** |
| **Sonda a tre stati** | — (nuovo) | `live.php:89-118` | `true` / `false` / **`null` = non lo so**. Con un booleano «non lo so» diventa «no» e l'automatismo scatta a ogni disservizio di rete |
| **Turno prenotato con la stessa UPDATE che lo registra** | — (nuovo) | `live.php:129-135` | Lock distribuito in sei righe SQL, senza tabelle di lock né file |
| **Avanzamento upload a due stati** | 7 | `src/api.ts:109-141` | `fetch` non espone l'avanzamento; e al 100% dei byte **il server deve ancora lavorare** |
| **Banco di prova per riflessione** | App. C | `tests/php/_api_harness.php` | Collaudare gli endpoint **senza aprire una porta nel codice di produzione** |

### C.2 — Gotcha nuovi (materiale da box «Attenzione»)

| Gotcha | Capitolo | Sintesi |
|---|---|---|
| **Il buco CSRF non è solo lato server** | 6 + 10 | Un componente che chiama con `fetch` diretto **bypassa `csrfHeaders()`**: aggiungere `validateCsrf()` lato server senza spostare la chiamata dentro `api` *rompe la feature*. I due capitoli vanno collegati |
| **`php -S` non applica `.htaccess`** | App. C | Per testare il front controller SEO serve Apache; col server integrato serve un `router.php` |
| **Una `.htaccess` va *eseguita* per essere verificata** | 2, 7 | Ispezionarla non basta: la prova è la richiesta HTTP |
| **Il codice HTTP non è mai la prova, per un file** | 2, 7 | Apache dà **403 anche per file inesistenti**; e su SPA con fallback un file *cancellato* risponde **200** col guscio dell'app. Né il 403 prova la presenza né il 200 prova l'assenza: la prova è il listing |
| **CLI PHP ≠ PHP di Apache** | App. C | `pdo_mysql` spesso assente nella `php.ini` della CLI |
| **I booleani PDO/MySQL arrivano al JSX come `0`/`1`** | 6 | `{poll.is_open && …}` con `0` stampa **«0»** in pagina. *Il* bug di frontiera dello stack PHP→JSON→React |
| **Unsubscribe via GET = disiscrizione da prefetch** | 13 | Antivirus e scanner *visitano i link*. Il libro chiede il POST ma non dice perché in modo memorabile |
| **I ruoli in sessione invecchiano** | 10, 14 | Cambiare ruolo sul DB non tocca le sessioni emesse; + i due anti-lockout (vietato eliminarsi, vietato declassarsi) |
| **Un filtro di visibilità è una policy, non una `WHERE`** | 9 | Le bozze trapelavano dagli emettitori *secondari*. È la mappa «una difesa, dove vive» applicata ai **dati** |
| **Un cancello scritto a mano invecchia peggio del resto** | 10 | Cinque azioni con guardia a mano *sopra* il gate generale: da sloggati davano **403 dove il contratto dice 401**. Non si vede rileggendo il codice; si vede con un test che chiede a ogni endpoint «e da sloggato?» |
| **Le didascalie restano indietro** | 14 | Un interruttore descritto «funzione in arrivo» per **nove mesi dopo** l'arrivo. Il testo dell'interfaccia è l'unica parte del sistema **che nessun meccanismo tiene onesta** |
| **Token di colore translucidi** | (nuovo/UI) | Un sistema con sole superfici translucide è incompleto: serve un token **opaco** per ciò che galleggia |
| **Due trappole di Tiptap 3** | 4, 8 | `StarterKit` include già `Link`/`Underline` (doppia registrazione, solo un `console.warn`); e `shouldRerenderOnTransaction` **spento di default** → la barra non segue il cursore. Il rimedio istintivo (riaccenderla) è quello sbagliato: si usa `useEditorState` |
| **La baseline lint** | App. C | Metà degli errori **non esistevano** (il linter leggeva un worktree in una dotfolder); e i disable vanno **mirati e motivati**, mai a livello di file |

### C.3 — Suggerimenti strutturali (riguardano la forma del libro, non un capitolo)

1. **Checklist normativa «REQ x.y» a fondo capitolo.** Per fare conformance su un sito vero Simone ha
   dovuto *estrarre* i requisiti dalla prosa. Pubblicarli renderebbe il libro una griglia di audit —
   ed è esattamente quello che è successo: l'audit di SR **ha inventato la numerazione REQ da sé**, e
   ora quella numerazione è citata nei commenti del codice di produzione
   (`sanitize_html.php:13`, `db_maintenance.php:4-5`, `auth_utils.php:95`, `newsletter.php:20`).
   Il libro ha già un'interfaccia pubblica di fatto: non l'ha dichiarata.
2. **Il «dal vivo» è uno snapshot datato.** Da dichiarare esplicitamente. È il nodo del §9.
3. **Ricetta di test d'integrazione locale** per un sito MySQL (Appendice C oggi cita PHPUnit + SQLite
   `:memory:`).
4. **Mappa «una difesa, dove vive»**: statica nel repo *e* ricreata a runtime, client *e* server.

### C.4 — L'incidente che vale un capitolo: nove ore di scarto

Non è negli appunti come voce a sé, ma è la storia più forte del lotto ed è documentata in tre posti
(`docs/INDICE.md:17`, `roadmap.md:27`, e **62 righe di commento** in `api/db.php:22-52`).

DreamHost sta sul Pacifico; `tz.php` mette PHP su Roma; **la sessione MySQL restava sul Pacifico**.
Nove ore di scarto, d'estate. Cos'era rotto senza che nessuno lo sapesse:

- le reazioni a un articolo appena pubblicato → **404 per nove ore**;
- l'antispam da dieci secondi del Muro → **non ha mai fermato nessuno**;
- il freno da due minuti della newsletter → **mai funzionato**;
- le date del pannello, e l'inizio della giornata di analytics alle 9 del mattino.

E il dettaglio che rende la storia da manuale: **`news.php` non era colpito**, perché lega
`date('Y-m-d H:i:s')` come parametro invece di usare `NOW()`. Cioè: il capitolo 9 del libro prescrive
«una sola fonte del presente» e SR aveva un prelude PHP condiviso — *e non bastava*, perché il
presente lo emettono **due** motori. Il libro ha il tema (CAP 9, «i tre fusi») ma non questa forma.

**Corollario di metodo (nota H.3):** la prova falliva anche perché la sessione `mysql` da riga di
comando usava il fuso del sistema. «Chiunque collauda una regola *dopo N minuti* deve allineare la
propria connessione allo stesso fuso dell'applicazione, altrimenti misura sé stesso.» La stessa
assunzione è ora scritta nella CI (`ci.yml`, `TZ: Europe/Rome` sul service container MySQL).

---

## 7. Il filo concettuale nuovo: i requisiti «di seconda battuta»

È la tesi che le note stesse individuano (§G) ed è, secondo me, **il contributo più originale di
tutto il materiale**. Formulata così:

> Le regole del Canone, una volta implementate, **generano requisiti nuovi che il libro non
> dichiara**. Sono conseguenze della regola, non della sua violazione.

Tre casi verificati, tutti in codice:

| La regola madre (nel libro) | Il requisito che genera | Cosa succede se lo ignori |
|---|---|---|
| «Un interceptor unico sul 401» (CAP 6) | **401 diventa un canale riservato**: 401 = non autenticato, 403 = autenticato senza permesso; e `check_auth` deve rispondere **sempre 200** con un flag | Un utente senza permesso vede un falso «sessione scaduta». Bug latente con due ruoli, esplosivo con quattro |
| «Enforcement centralizzato nel connettore DB» (CAP 10, `session_version`) | **Censisci gli endpoint che non connettono** | `check_auth` rispondeva «autenticato» a sessioni già invalidate. Rimedio: `admin.php:143`, forza la connessione |
| «Il ruolo vive in sessione» (CAP 10/14) | **Il cambio ruolo deve incrementare `session_version`** | Un declassamento non ha effetto finché l'utente non si slogga |

Il libro potrebbe dichiararli accanto a ogni regola madre — *«se applichi questa, ora devi anche…»*.

---

## 8. Cosa ho trovato io, che non è negli appunti

1. **La documentazione del sito è andata in deriva, e nel modo esatto che la nota H.6 descrive.**
   `README.md` dichiara «v2.16.0», «Vite 7», «Tailwind CSS 3»; `package.json` dice **v2.21.0, Vite 8,
   Tailwind 4**. `docs/architecture/ARCHITETTURA.md:3` si dichiara aggiornato a v2.15.0 e ripete «Vite 7
   + Tailwind 3» nel titolo del §2. Non è una svista isolata: è la stessa lezione («il testo è l'unica
   parte del sistema che nessun meccanismo tiene onesta») applicata alla documentazione invece che
   all'interfaccia — e rafforza la nota, perché mostra che il problema non riguarda solo le didascalie.
   *(Questo è un rilievo sul sito, da segnalare a Simone; non tocca il libro.)*

2. **Due meccanismi di rate-limit convivono senza che nessuno lo dichiari.** C'è il componente
   condiviso su file (`rate_limit.php`, con un commento che spiega **perché su file e non su DB**:
   «il tetto serve proprio quando qualcuno sta martellando l'endpoint, cioè il momento peggiore per
   aggiungere scritture al database»)… e poi `newsletter.php:95-102` fa il suo rate-limit **con una
   query sul DB**. Funziona, ed è anche difendibile (riusa colonne già presenti). Ma è esattamente il
   tipo di incoerenza che il CAP 13 del libro rimprovera a SR in un altro punto («l'infrastruttura per
   limitare esiste già: semplicemente non è stata riusata qui»). La critica del libro è caduta come
   fatto, ed è **rinata altrove**.

3. **La CI è già una reference implementation per l'Appendice C** e nessuno l'ha proposta come tale.
   `.github/workflows/ci.yml` esegue la suite PHP **due volte, una per dialetto** (SQLite locale,
   MySQL 8 in service container), e i suoi commenti spiegano *perché* — incluso il `TZ: Europe/Rome`
   sul container, che «mette per iscritto l'assunzione su cui il codice si regge già». È il documento
   che l'Appendice C dovrebbe contenere.

4. **La «revisione a due» è un metodo, e le note lo dicono a metà.** Il 11/08 è stata fatta una
   sessione in cui «Claude indicava e Simone guardava», con regole scritte in anticipo (una voce per
   volta, si aspetta la risposta, niente lavoro d'iniziativa). Ha trovato **due difetti che nessuna
   analisi del codice aveva trovato** — la pagina diretta che non si spegne e la didascalia ferma da
   nove mesi. La nota H.6 lo registra («il modo più efficace resta una sessione in cui qualcuno apre
   il pannello e lo legge davvero») ma non come *procedura*. Il piano è riusabile così com'è:
   `docs/archivio/analisi/revisione-11-08-2026.md`.

5. **Le note dichiarano da sole la propria collocazione.** In testa a `NOTE_PER_IL_MANUALE.md`:
   «tutto ciò che sta qui sotto è successivo a quella chiusura e vale quindi come materiale per la
   **quarta edizione** (o come errata/aggiornamento della terza)». La scelta fra le due è la decisione
   che ci resta da prendere.

---

## 9. Il nodo da decidere: cosa fare del «dal vivo»

Questo è il punto che va sciolto prima di qualunque altra cosa, perché **decide la natura del
lavoro**, non solo la sua quantità.

Il libro ha due strati dichiarati: *«dal vivo»* (fotografia del codice reale) e *«Il Canone»* (la
norma). La convenzione è stata una scelta felice — **il Canone è intatto al 100%**, nessuna
prescrizione del libro è stata smentita da un anno di produzione. Ma lo strato «dal vivo» su SR è
scaduto in blocco, e per una ragione onorevole: il sito ha applicato il libro.

Le strade che vedo, senza raccomandarne una qui:

- **(a) Errata/appendice per la terza edizione.** Un documento che dice «SR ha chiuso questi debiti,
  ecco quando e come». Costo minimo. Non tocca il testo stampato, che resta leggibile come fotografia
  datata. Non risolve il problema per chi compra il libro domani.
- **(b) Datare esplicitamente il «dal vivo».** Una riga per capitolo, o una sola in CAP 1: «le sezioni
  *dal vivo* fotografano lo stato al giugno 2026; il Canone è la parte durevole». È il suggerimento
  C.3.2 delle note, costa poco, e **cambia il contratto di lettura** senza riscrivere niente.
- **(c) Quarta edizione.** Aggiornare le fotografie e incorporare il materiale nuovo. È l'unica strada
  che sfrutta davvero le 15 reference implementation e i 14 gotcha, ma è un cantiere, non un ritocco.
- **(d) Il capitolo che oggi manca.** Le note lo indicano esplicitamente in chiusura di Parte II:
  *pattern per hosting condiviso e privacy a costo zero* (piggyback senza cron, rate-limit come
  componente, contatori aggregati + localStorage, hash con sale rotante). È materiale coeso che non ha
  casa in nessuno dei 20 capitoli attuali.

Una cosa la dico, perché è un fatto e non un'opinione: **l'opzione (b) è indipendente dalle altre e
non ha controindicazioni**. Qualunque cosa si decida sul resto, dichiarare che il «dal vivo» è datato
è vero, è a costo quasi zero, ed è ciò che rende il libro onesto rispetto a quello che è appena
successo.

---

## 10. Quello che NON ho verificato

Lo scrivo perché la mappa non sembri più completa di com'è.

- **`admin.php` righe 260-668**: le azioni di migrazione `?action=apply_*` che alimentano la critica
  della «console nascosta» (CAP 14:146). È l'unica riga della tabella A che resta aperta (A13).
- **`index.php`** l'ho letto solo nei punti che riguardano `status` e la sanitizzazione.
- **Live Room** (`live_poll.php`, `live_messages.php`, `live_tournament.php`): sottosistema nato dopo
  il libro, ~670 righe. Il libro non lo copre; andrebbe letto con le lenti del CAP 18/20 se si va
  verso (c) o (d).
- **Gli altri tre siti.** SPW, DIS e FDCA non li ho riaperti: se SR è derivato così tanto in due mesi,
  **non c'è motivo di assumere che gli altri siano fermi**. Le fotografie del libro su SPW v1.21.0 e
  su DIS potrebbero avere lo stesso problema, e nessuno l'ha ancora guardato.
- **La suite di test** (12 file, ~2.000 righe): ho letto solo l'harness.

---

## 11. Inventario, in numeri

| | |
|---|---|
| Versioni di scarto fra libro e sito | v2.9.13 → **v2.21.0** |
| Affermazioni del libro smentite | **11 nette + 2 parziali** (tabella A) |
| Prescrizioni del Canone smentite | **0** |
| Reference implementation disponibili | **15** (tabella C.1) |
| Gotcha nuovi | **14** (tabella C.2) |
| Capitoli toccati dal materiale nuovo | 4, 6, 7, 8, 9, 10, 11, 13, 14, 15, 20, App. C |
| Capitolo nuovo proposto dalle note | 1 (hosting condiviso + privacy a costo zero) |
| Debiti aperti sul sito | 5 (roadmap: dipendenza `live_*`, log del cron, bollino LIVE, incolla markdown, icone admin) |
