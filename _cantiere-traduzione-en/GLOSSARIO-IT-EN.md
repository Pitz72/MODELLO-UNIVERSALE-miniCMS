# Glossario IT→EN (proposto) — «The Thin Stack»

Glossario **vivo**: si congela alla sessione pilota (CAP 1) e cresce a ogni capitolo. Le voci marcate
**(DA CONFERMARE)** aspettano la validazione di Simone. Variante: **inglese US**.

## 1. Convenzioni del libro e struttura
| IT | EN proposto | Note |
|---|---|---|
| Convenzione «Due Voci» | **“Two Voices”** | sezione introduttiva nel CAP 1 |
| **Dal vivo** (la voce-autopsia del codice reale) | **In the Wild** ✓ | scelto: oppone «In the Wild» (la realtà non addomesticata) a «The Canon» (la regola sancita); è anche idioma tecnico standard |
| **Il Canone** (box-prescrizione a fine capitolo) | **The Canon** | titolo del box `[!IMPORTANT]` di chiusura |
| Quando NON usarlo / Quando NON usare questo protocollo | **When NOT to Use It / This Protocol** | |
| Il Modello | **The Model** | il protocollo thin-stack |
| Parte I — La Visione | **Part I — The Vision** | |
| Parte II — L'Architettura | **Part II — The Architecture** | |
| Parte III — I Componenti | **Part III — The Components** | |
| Parte IV — Il Flusso Operativo | **Part IV — The Operational Flow** | |
| Parte V — I Casi Reali | **Part V — The Real-World Cases** | |
| Allegati / Appendici | **Appendices** | |
| Prossimo Capitolo (footer) | **Next Chapter** | |
| In sintesi | **In Summary** | |
| Box `[!WARNING]`/`[!NOTE]`/`[!TIP]`/`[!IMPORTANT]` | invariati | si traduce **solo il titolo** in grassetto dentro il box |

## 2. Termini coniati / firma del libro (consistenza obbligatoria)
| IT | EN | Note |
|---|---|---|
| thin stack | **thin stack** | invariato (è il titolo/marchio del libro) |
| i quattro emettitori del content | **the four content emitters** | filo CAP 8→11→12→13 |
| scala a tre gradini | **the three-rung scale** | alt: *three-tier scale* — scegliere e tenere fisso |
| cicatrici (del codice) | **scars** | «pattern with their scars» |
| dal vivo (autopsia) | **In the Wild** (vedi §1) | |
| choke-point | **choke point** | già inglese nel testo |
| Double Read | **Double Read** | pattern nominato, invariato |
| cura senza prevenzione | **treatment without prevention** | paradosso di SR |
| più ingegnerizzato ≠ più sicuro | **more engineered ≠ more secure** | tesi D2 |
| teatro della sicurezza / security-theater | **security theater** | |
| guscio scollegato (fork) | **a disconnected shell** | App. B |
| il fix non segue il fork | **the fix doesn’t follow the fork** | App. B |
| i (sei) fossili | **the (six) fossils** | residui SQLite in repo MySQL |
| falla viva / buco (XSS) | **the live flaw / the open hole** | |
| write-time / render-time | **write-time / render-time** | invariati |
| role-blind (guardia) | **role-blind** | invariato |
| OG-proxy / Dynamic Rendering | invariati | |
| ponte (verso CAP X) | **bridge (to Ch. X)** | raccordi narrativi |
| Il Modello Universale / Il Modello | **The Universal Model / The Model** | fissato dal pilota CAP 1 |
| Il Piano della Presentazione / dei Dati | **The Presentation Plane / The Data Plane** | «separazione dei piani» → *separation of planes* |
| grado-zero | **base rung** | metafora della scala |
| MySQL essenziale / ingegnerizzato | **essential MySQL / engineered MySQL** | nomi dei gradini della scala |
| ridotto all'osso | **pared to the bone** | |
| in chiaro (password) | **in cleartext** | |
| senza sconti | **without flinching** | |
| Il codice non mente. Le cicatrici nemmeno. | **Code doesn’t lie. Neither do scars.** | chiusura ricorrente |
| database-a-file | **file-based database** | fissato dal CAP 2 |
| un file per endpoint / endpoint autonomo | **one file per endpoint / standalone PHP file** | architettura miniCMS |
| seconda rete (difesa) | **a second net** | tiene la metafora «rete» |
| Il Pattern Fork | **The Fork Pattern** | rimanda all'App. B |
| fuori dalla docroot | **outside the docroot** | |
| crescente paranoia (opzioni PDO) | **escalating paranoia** | fissato dal CAP 3 |
| finché regge | **as long as it holds** | CAP 3, soglia SQLite→MySQL |
| la riga che porta una cicatrice | **the line that carries a scar** | CAP 3, tiene la metafora «scars» |
| a prevalenza/dominante di lettura | **read-heavy / read-dominant** | CAP 3, profilo di carico |
| contesa in scrittura | **write contention** | CAP 3 |
| ciclo di vita delle migrazioni | **the migration lifecycle** | CAP 3 |
| debito di sicurezza / debito da non ereditare | **security debt / a debt not to inherit** | CAP 3 |
| busta (forma del payload) / busta zero | **envelope / zero envelope** | CAP 6, contratti API |
| contratti elastici | **elastic contracts** | CAP 6, box Double Read/type guard/zero envelope |
| guardia di tipo | **type guard** | CAP 6, `Array.isArray` |
| codemod / rattoppo per-metodo | **codemod / per-method patch** | CAP 6, `fix_api.cjs` |
| i metodi «sfuggiti» | **the “slipped-through” methods** | CAP 6 |
| impronte / tracce (del codemod) | **fingerprints** | CAP 6 |
| a macchia di leopardo | **in patches** | CAP 6 |
| prelude inline / prelude condiviso | **inline prelude / shared prelude** | CAP 5, i tre stili di bootstrap |
| gate selettivo sul ramo | **a gate selective per branch** | CAP 5 |
| information disclosure gratuita | **information disclosure for free** | CAP 5 |
| l'assenza che conta | **the absence that counts** | CAP 4, niente data-fetching lib |
| si guadagna il posto | **earns its place** | CAP 4, costo delle dipendenze |
| viaggiano in coppia | **travel as a pair** | CAP 4, showdown + DOMPurify |
| difesa in profondità | **defense in depth** | CAP 7/8 |
| catena RCE | **RCE chain** | CAP 7, upload pubblico DIS |
| magic-bytes / byte reali | **magic bytes / real bytes** | CAP 7, validazione upload |
| dangling media | **dangling media** | invariato (già inglese), CAP 7 |
| la scala dell'elisione | **the scale of erasure** | CAP 7, naming file |
| la tempesta perfetta | **the perfect storm** | CAP 7, §5 |
| path-guard / containment | **path guard / containment** | CAP 7, delete media |
| pulizia cosmetica | **cosmetic cleanup** | CAP 8, Paste Protection |
| emettitore (del content) | **emitter** | CAP 8, «the four content emitters» |
| guardie all'inserimento | **insertion guards** | CAP 8, `isSafeLinkUrl` |
| buco attributi | **attribute hole** | CAP 8, `strip_tags` non tocca gli attributi |
| stored-XSS da autore autenticato | **stored XSS from an authenticated author** | CAP 8 |
| compatibility shim | **compatibility shim** | invariato, CAP 8 (migrazione Quill→Tiptap) |
| choke-point | **choke point** | CAP 8 (già in §2) |
| stati dinamici / persistenti | **dynamic states / persistent states** | CAP 9, `status` DB vs stato calcolato a runtime |
| programmato (stato) | **scheduled** | CAP 9, terza riga della matrice di visibilità (`published` nel futuro) |
| la fonte del presente | **the source of the present** | CAP 9, «adesso» = una sola fonte (PHP o DB), mai mescolarle |
| il 404 deliberato | **the deliberate 404** | CAP 9, non confermare l'esistenza di una bozza (404, non 403) |
| estendere un contratto invece di versionarlo | **extending a contract instead of versioning it** | CAP 9, busta per-endpoint |
| doppia scrittura (M:N + CSV legacy) | **double write** | CAP 9, `syncArticleTags` + campo CSV in parallelo |
| cache di retrocompatibilità | **backward-compatibility cache** | CAP 9, `articles.tags` CSV tenuto vivo |
| cache su file con TTL | **file cache with a TTL** | CAP 9, `.cache/` JSON, header `X-Cache: HIT/MISS` |
| scala di sottrazione | **scale of subtraction** | CAP 10, leggere ogni difesa per cosa si rompe togliendola |
| gate unico / componibile / inline | **single gate / composable gate / inline gate** | CAP 10, le tre architetture di protezione endpoint |
| il gate che si dimentica | **the gate you forget** | CAP 10, rischio del gate componibile/inline |
| anti session-fixation | **anti session-fixation** | invariato, CAP 10 (`session_regenerate_id`) |
| fail-closed / fail-open | **fail-closed / fail-open** | invariati, CAP 10 (ramo `catch` di `session_version`) |
| backup giusto-in-tempo | **just-in-time backup** | CAP 10, `copy()` del `.sqlite` prima del `DELETE` |
| contatore brute-force | **brute-force counter** | CAP 10, file/DB/assenza |
| credenziali di default | **default credentials** | CAP 10, random/hardcoded/omesse |
| il seeding dell'admin | **seeding the admin** | CAP 10, primo amministratore |
| enumeration-safe / password-reset poisoning | **enumeration-safe / password-reset poisoning** | invariati, CAP 10 (recovery) |
| debito di tracciabilità | **traceability debt** | CAP 10, schema non ricostruibile (`password_resets`) |
| Dynamic Rendering / front controller | **Dynamic Rendering / front controller** | invariati, CAP 11 (entry-point PHP davanti alla SPA) |
| OG-proxy / proxy di anteprime social | **OG-proxy / social-preview proxy** | CAP 11, il gradino leggero (DIS): solo meta escaped, niente corpo |
| la doppia verità delle rotte | **the double truth of the routes** | CAP 11, rotte duplicate in `App.tsx` + `index.php` |
| iniezione sicura per escape | **escape-safe (meta) injection** | CAP 11, DIS passa ogni valore per `htmlspecialchars` |
| quando copi un pattern, copi anche la sua falla | **when you copy a pattern, you copy its flaw too** | CAP 11, SR eredita il buco `strip_tags` di SPW |
| la SEO che indicizza le bozze | **the SEO that indexes drafts** | CAP 11, manca `AND status = 'published'` nel ramo crawler |
| due idee di «pubblico» | **two ideas of “public”** | CAP 11, pubblico-per-utente ≠ pubblico-per-bot |
| la cache che sopravvive al suo lettore | **the cache that outlives its reader** | CAP 11, scrittori vivi, lettore rimosso nella v3.0 |
| impronta fossile | **fossil imprint** | CAP 11, codice morto della SSG abbandonata (estende «the fossils») |
| simulare i crawler dei social | **impersonate the social crawlers** | CAP 11, vettore DDoS feb 2026 (UA falsificato) |
| scudo anti-DDoS / cache orfanata | **anti-DDoS shield / orphaned cache** | CAP 11, la seo-cache nata come difesa, poi orfanata |
| lo User-Agent non è un gatekeeper | **the User-Agent is not a gatekeeper** | CAP 11, UA per ottimizzare, mai come barriera d'accesso |
| syndication / aggregatori | **syndication / aggregators** | CAP 12, il feed consegna i contenuti fuori dal sito |
| sicuro per sottrazione / per escape | **safe by subtraction / safe by escaping** | CAP 12, le due strade del feed (SPW non emette, SR escapa tutto) |
| proxy inbound (CORS) | **inbound (CORS) proxy** | CAP 12, SR scarica feed altrui same-origin; difese allowlist+https-only |
| open proxy / fallback stale | **open proxy / stale fallback** | CAP 12, anti-SSRF + cache scaduta meglio di niente |
| il lucchetto sulla porta accanto | **the lock on the door next to it** | CAP 12, gate sul dispenser di un URL, endpoint pubblico |
| sicurezza per oscurità | **security through obscurity** | CAP 12, `feed_config.php` (l'oscurità non c'è: nome prevedibile) |
| il GUID che ripubblica | **the GUID that republishes** | CAP 12, GUID = permalink/URL audio → ripubblicazione al cambio |
| GUID stabile (URN), non il permalink | **stable GUID (a URN), not the permalink** | CAP 12, `urn:...:article:<id>`, disaccoppiato dall'URL |
| il catch vuoto | **the empty catch** | CAP 12, anti-pattern: feed troncato con HTTP 200 |
| fallback silenzioso / guasto silenziato | **silent fallback / silenced failure** | CAP 12, un errore mascherato da risposta valida |
| cicatrici minori | **minor scars** | CAP 12, configurabilità annunciata, MIME enclosure errato, bozze nel feed |
| configurabilità annunciata | **announced configurability** | CAP 12, commento «dai settings» mai cablato |
| quando il codice racconta i suoi dubbi | **when the code narrates its doubts** | CAP 12, monologhi LLM lasciati in produzione (DIS) |
| double opt-in | **double opt-in** | invariato, CAP 13 (record pending + link di conferma) |
| due token distinti / un solo token | **two distinct tokens / a single token** | CAP 13, conferma monouso + disiscrizione stabile (SPW) vs token unico (SR) |
| disiscrizione morbida | **a “soft” unsubscribe** | CAP 13, `is_active = 0`, niente DELETE |
| il link di disiscrizione ha bisogno di un segreto | **the unsubscribe link needs a secret** | CAP 13, no token = chiunque disiscrive chiunque (anche prefetch) |
| il form che spara email a nome tuo | **the form that fires emails in your name** | CAP 13, subscribe senza rate-limit = mail-bombing |
| throttle in uscita ≠ rate-limit in ingresso | **outbound throttle ≠ inbound rate limit** | CAP 13, `usleep` non è rate-limit |
| header injection dal campo nome | **header injection from the name field** | CAP 13, `strip_tags` non tocca i `\r\n` |
| sanitizzare per il DB ≠ per gli header email | **sanitizing for the DB isn't sanitizing for email headers** | CAP 13, il contesto della sanitizzazione |
| il consenso come effetto collaterale | **consent as a side effect** | CAP 13, iscrizione da approvazione festival senza consenso specifico |
| una sanitizzazione, quattro render-path | **one sanitization, four render paths** | CAP 13, chiusura del filo dei quattro emettitori |
| l'admin è un aggregatore, non un'applicazione | **the admin is an aggregator, not an application** | CAP 14, telaio che monta i pannelli degli altri cluster |
| una guardia, N pagine | **one guard, N pages** | CAP 14, route-guard che protegge l'intero sotto-albero |
| route-guard / guardia al montaggio | **route guard / check on mount** | CAP 14, dichiarativo (SPW) vs imperativo (SR/DIS) |
| nascondere una pagina è UX; impedire un'azione è sicurezza | **hiding a page is UX; preventing an action is security** | CAP 14, va fatto sul ruolo, client+server |
| cruscotto testuale | **text-based dashboard** | CAP 14, DIS misura in testo, senza grafici (i `COUNT` giusti) |
| misurare senza terze parti | **measuring without third parties** | CAP 14, analytics in casa (`analytics.php`), niente Google Analytics |
| il build può tradire la tua difesa statica | **the build can betray your static defense** | CAP 14, `.htaccess` di deny strippato dal build → ricrealo a runtime |
| console nascosta | **hidden console** | CAP 14, azioni potenti via `GET` senza UI né ruolo (SR `admin.php`) |
| il `confirm()` non è una difesa di sicurezza | **`confirm()` is not a security defense** | CAP 14, conferma = UX, non ferma una richiesta forgiata (serve CSRF) |
| raccogliere e dimenticare / tabella di sola scrittura | **collect and forget / a write-only table** | CAP 14, `contacts` salvata e mai letta (debito, non archivio) |
| quando l'ottimizzazione è il disastro | **when the optimization is the disaster** | CAP 15, il WAL su hosting condiviso = crash notturno |
| il trasloco di motore / pattern a tre script | **the engine move / the three-script pattern** | CAP 15, ETL a mano (credenziali + connettore + `init_mysql`) |
| due PDO e un COUNT | **two PDOs and a COUNT** | CAP 15, l'ETL minimale (`ON DUPLICATE KEY UPDATE` + verifica conteggi) |
| debito schema-as-code | **schema-as-code debt** | CAP 15, niente registro migrazioni → la verità vive nel DB |
| una tabella, tre `CREATE` / dove vive la verità di una tabella | **one table, three CREATEs / where a table's truth lives** | CAP 15, `subscribers` con 3 definizioni divergenti |
| il bug della data come stringa | **the date-as-string bug** | CAP 15, `published_at` confrontato come testo (fuso/formato) |
| avere il defibrillatore ma non l'allarme antincendio | **having the defibrillator but not the fire alarm** | CAP 15, cura reattiva senza prevenzione (backup) |
| i sei fossili (igiene del repo) | **the six fossils (repo hygiene)** | CAP 15, codice SQLite in repo MySQL: inerte o rotto (estende «the fossils») |
| URL su id numerico, non slug | **URLs on a numeric id, not a slug** | CAP 16, i progetti non generano slug (la logica accenti vive una volta al CAP 5) |
| creazione con auto-sort | **creation with auto-sort** | CAP 16, `MAX(sort_order)+1` nella categoria → il nuovo progetto va in fondo |
| lo switch Web/Email | **the Web / Email switch** | CAP 16, toggle «tipo di link» che antepone `mailto:` da solo (UX distraction-proof) |
| ricerca unificata / campo `type` | **unified search / the `type` field** | CAP 16, un `LIKE` su articoli+progetti, marcati con `type`, smistati lato client |
| categorie da statiche a DB-driven | **categories from static to DB-driven** | CAP 16, da `PROJECT_CATEGORIES` in React a tabella interrogata a runtime (niente rebuild Vite) |
| modificabili a caldo | **editable on the fly** | CAP 16, spostare le categorie dal codice al DB |
| la fonte di verità della classifica | **the source of truth for the ranking** | CAP 18, ordinamento per `vote_count` denormalizzato, non `COUNT(votes)` |
| tre difese, una sola conta | **three defenses, only one counts** | CAP 18, IP-window regge / cookie cosmetico / User-Agent solo registro |
| per il voto pubblico l'IP grezzo è un pregio | **for a public vote the raw IP is a strength** | CAP 18, `REMOTE_ADDR` non falsificabile vs `X-Forwarded-For` (rovescia l'auth-dietro-proxy del CAP 10) |
| la classifica che può derivare | **the ranking that can drift** | CAP 18, contatore denormalizzato senza **reconciliation** = drift silenzioso |
| i round a interruttore | **the on/off rounds** | CAP 18, le fasi del concorso = il flag `in_current_round`, non entità con storia |
| quando il lettore deve indovinare come ha scritto lo scrittore | **when the reader has to guess how the writer wrote** | CAP 18, `'1'` vs `'true'`: lettura difensiva che compensa una convenzione mancante a monte |

## 3. Mappa titoli (file `manuale-en/`)
| # | IT | EN |
|---|---|---|
| 1 | Manifesto | **Manifesto** |
| 2 | Architettura e Struttura Progetto | **Architecture & Project Structure** |
| 3 | Database Strategy | **Database Strategy** |
| 4 | Frontend Dependencies | **Frontend Dependencies** |
| 5 | Backend Logic (PHP) | **Backend Logic (PHP)** |
| 6 | Frontend Bridge (API.ts) | **Frontend Bridge (API.ts)** |
| 7 | Media & Optimization | **Media & Optimization** |
| 8 | Advanced Content Editing & Media Integration | **Advanced Content Editing & Media Integration** |
| 9 | Content Lifecycle | **Content Lifecycle** |
| 10 | Security & Auth | **Security & Auth** |
| 11 | SEO Pre-rendering con PHP Entry-Point | **SEO Pre-rendering with a PHP Entry Point** |
| 12 | RSS Feed & Syndication | **RSS Feed & Syndication** |
| 13 | Newsletter & Email System | **Newsletter & Email System** |
| 14 | Admin Dashboard & Panels | **Admin Dashboard & Panels** |
| 15 | Database Evolution - Da SQLite a MySQL | **Database Evolution — From SQLite to MySQL** |
| 16 | Portfolio & Projects Module | **Portfolio & Projects Module** |
| 17 | Festival Logic - Iscrizioni e Workflow Approvazione | **Festival Logic — Submissions & Approval Workflow** |
| 18 | Festival Logic - Votazioni e Protezione Anti-Frode | **Festival Logic — Voting & Anti-Fraud Protection** |
| 19 | Festival Logic - Dashboard Admin, Settings e Reporting | **Festival Logic — Admin Dashboard, Settings & Reporting** |
| 20 | Social Interactions & Reactions | **Social Interactions & Reactions** |
| A | Boilerplate Checklist | **Appendix A — Boilerplate Checklist** |
| B | Ciclo di vita di un fork | **Appendix B — The Life of a Fork** |
| C | Testing e Deploy | **Appendix C — Testing & Deployment** |

Sottotitolo libro: «Il protocollo miniCMS per Web App moderne» → **“The miniCMS protocol for modern web apps.”**

## 4. Idiomi da transcreare (lista seme, cresce dal testo)
| IT | EN proposto |
|---|---|
| il lucchetto con la chiave appesa accanto | a padlock with the key hanging right beside it |
| ragionamento ad alta voce (commenti) | thinking out loud |
| alle tre di notte / database corrotto alle tre di notte | a corrupted database at 3 a.m. |
| la prova del delitto | the smoking gun |
| usa e getta (script) | throwaway / one-shot |
| a prova di distrazione | distraction-proof |
| fidarsi dell'IP | trusting the IP |
| niente scaramanzia | not out of superstition |
| cura le proporzioni (tabella) | minds its proportions |
| un'ora prima del previsto | an hour ahead of schedule |
| compare o sparisce con uno scarto | appears or disappears off by (an hour) |
| un attrezzo dimenticato in un angolo | a tool forgotten in a corner |
| lo scudo non è più imbracciato da nessuno | no one carries the shield anymore |
| il vettore era elegante | the vector was elegant |

## 5. Restano INVARIATI (non tradurre)
Nomi siti/marchi (SitoRuntime, DISINTELLIGENZA, FDCA, SimonePizziWebSite, Runtime Radio, Runtime
Edizioni); keyword e API (PHP, PDO, `strip_tags`, DOMPurify, `htmlspecialchars`, Tiptap, Quill, Vite,
React, TypeScript, Puppeteer, `index.php`, `.htaccess`, WAL, `PRAGMA`, `INSERT IGNORE`, `UNIQUE KEY`…);
termini di sicurezza già inglesi (stored-XSS, CSRF, header injection, mail-bombing, tabnapping, rate-limit,
brute-force, SSRF, cloaking); annotazioni `path:linea`; numeri di versione.

## Decisioni prese (27/06/2026)
- **«Dal vivo» → In the Wild.** La coppia *In the Wild ↔ The Canon* è l'opposizione voluta:
  la realtà non addomesticata contro la regola sancita.
- **D2 → SÌ:** i commenti dentro i blocchi codice si traducono in EN (sono prosa didattica);
  restano intatti identificatori, keyword, stringhe, `path:linea`, numeri di versione.
- **D3 → titolo italiano + glossa EN in corsivo:** es. *L'Albero dei Racconti* (The Tree of Tales),
  *Frequenza di Servizio* (Service Frequency). In inglese i titoli vanno in **corsivo**, mai tra «».
