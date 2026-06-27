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
