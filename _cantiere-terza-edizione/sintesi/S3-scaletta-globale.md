# S3 — Scaletta / Indice Globale della TERZA EDIZIONE

> **Stato:** COMPLETATO (proposta) — **è il documento del GATE S4** (validazione con Simone prima della scrittura)
> **Data:** 2026-06-19 · **Commit:** _(in corso)_
> **Input:** S1 (14 schede) + S2 (inventario: azioni A, nuovi B, scarti C, fili D) + struttura attuale `_master.md` (5 Parti, 19 capitoli + Boilerplate)
> **Output:** struttura a Parti + capitoli (con i nuovi), Indice Generale rinumerato, mappa card/scheda→capitolo, collocazione dei fili trasversali, decisioni aperte per S4.

---

## 0. Cosa cambia rispetto alla struttura attuale (in una pagina)

La Seconda Edizione ha **19 capitoli in 5 Parti + Boilerplate**. La Terza Edizione, sulla base di S1/S2,
propone:

- **+1 capitolo nuovo:** **Admin Dashboard & Panels (generale)** in Parte IV (oggi manca: il CAP 18 è
  solo la dashboard *festival*). → S2/B1.
- **+1 appendice nuova:** **Ciclo di vita di un fork** (FDCA). → S2/B2.
- **2 sezioni nuove dentro capitoli esistenti:** "Misurare senza terze parti" (analytics first-party,
  dentro il nuovo CAP Admin) → S2/B3; **box-ancora "I quattro emettitori del `content`"** dentro CAP
  Editing, richiamato altrove → S2/B4.
- **5 riscritture** (CAP Frontend Bridge, Media, Editing, SEO, Newsletter) + **1 riscrittura grande**
  (Security & Auth, oggi senza CSRF/recovery/session_version) + **molte correzioni** (vedi S2/A).
- **Rinumerazione** della Parte V (le "+1" dovute al nuovo capitolo Admin) — vedi §2.
- **Spostamenti di scope:** cache TTL → Content Lifecycle; SEO da Media → SEO; DDoS-da-bot → SEO.

Risultato: **20 capitoli in 5 Parti + 2 Appendici.**

## 1. Struttura a Parti (confermata, 5 Parti)

L'impianto a 5 Parti regge e va mantenuto; cambia il contenuto, non l'ossatura.

- **Parte I — La Visione** (il perché)
- **Parte II — L'Architettura** (le fondamenta: struttura, DB, dipendenze)
- **Parte III — I Componenti** (i mattoni: backend, bridge, media, editor)
- **Parte IV — Il Flusso Operativo** (i sistemi vivi: contenuti, sicurezza, SEO, feed, email, **admin**)
- **Parte V — I Casi Reali** (le cicatrici: evoluzione DB, portfolio, festival, reactions)
- **Appendici** (Boilerplate + Fork)

## 2. Indice Generale proposto (rinumerato)

| # | Capitolo | Parte | vs 2ª ed. | Azione (da S2) |
|---|---|---|---|---|
| 1 | Manifesto | I | =1 | AGGIORNA (tesi-filo D2/D5) |
| 2 | Architettura e Struttura Progetto | II | =2 | AGGIORNA (config/segreti 3-factor) |
| 3 | Database Strategy | II | =3 | CORREGGI (.data=DIS; PRAGMA prescrittivo≠reale) |
| 4 | Frontend Dependencies | II | =4 | AGGIORNA/CORREGGI (Tiptap; **SR non è più Quill**; no-fetch-libs) |
| 5 | Backend Logic (PHP) | III | =5 | AGGIORNA (3 stili bootstrap, errore-connessione) |
| 6 | Frontend Bridge (API.ts) | III | =6 | **RISCRIVI** (Double Read corretto, CSRF client, guard, msg perso) |
| 7 | Media & Optimization — Upload & Sicurezza | III | =7 | **RISCRIVI** (sicurezza upload 3/1/0, RCE, PHP-off; cache→9, SEO→11) |
| 8 | Advanced Content Editing | III | =8 | **RISCRIVI** (Tiptap scala, DOMPurify render-time) + **box-ancora 4 emettitori** |
| 9 | Content Lifecycle | IV | =9 | CORREGGI (3 strategie fuso, M:N non-universale, matrice stati) + cache-contenuto da CAP 7 |
| 10 | Security & Auth | IV | =10 | **RISCRIVI grande** (CSRF 3 gradini, cookie, brute-force, recovery, role-blind) + box-ancora IP |
| 11 | SEO Pre-rendering con PHP Entry-Point | IV | =11 | **RISCRIVI** (Dynamic Rendering vs SSG-scartato; buco XSS; bozze; seo-cache morta) + DDoS-bot da ex-CAP10§6 |
| 12 | RSS Feed & Syndication | IV | =12 | **RISCRIVI/CORREGGI** (feed-podcast=DIS; proxy CORS; security-theater; catch) |
| 13 | Newsletter & Email System | IV | =13 | **RISCRIVI** (double opt-in; rate-limit≠throttle; SMTP; header-injection) + **chiude i 4 emettitori** |
| **14** | **Admin Dashboard & Panels (generale)** | **IV** | **NUOVO (B1)** | tre-modelli + tre-architetture + backup-fuori-docroot + write-only + sez. "Misurare senza terze parti" (B3) |
| 15 | Database Evolution (SQLite→MySQL) | V | era 14 | AGGIORNA/CORREGGI (fossili, 3-schemi, WAL-incidente, cura-senza-prevenzione, DIS-SQLite-vivo) |
| 16 | Portfolio & Projects Module | V | era 15 | CONFERMA (+ ricerca unificata da CAP 9) |
| 17 | Festival — Iscrizioni & Approvazione | V | era 16 | AGGIORNA/CORREGGI (consenso-GDPR; upload-pubblico-RCE) |
| 18 | Festival — Votazioni & Anti-Frode | V | era 17 | AGGIORNA/CORREGGI (cookie-cosmetico; voter_hash; reset-CSRF; drift) |
| 19 | Festival — Dashboard Admin | V | era 18 | AGGIORNA (report-disabilitato; finalist-vestigiale) — **specializzazione del CAP 14** |
| 20 | Social Interactions & Reactions | V | era 19 | **RISCRIVI** (2-strati rate-limit; hash-non-salato; messages.php; 2-filosofie) |
| App. A | Boilerplate Checklist | App. | =All. | AGGIORNA (voci rinumerate + checklist-sicurezza) |
| App. B | **Ciclo di vita di un fork (FDCA)** | App. | **NUOVO (B2)** | fork-eredita-il-debito; guscio-scollegato; v0.0.1; roadmap-AI |

**Nota rinumerazione:** l'unico inserimento "in mezzo" è il **CAP 14 Admin** (Parte IV); tutta la Parte V
scala di +1 (ex 14→15 … ex 19→20). È una rinumerazione meccanica (rename file + header + cross-ref +
README + Boilerplate), da eseguire in FASE 3/4 con cura — già fatta una volta (memoria progetto).

## 3. Mappa card di mappatura / schede S1 → capitolo

Quale materiale-sorgente alimenta ciascun capitolo (per la scrittura in FASE 3).

| Capitolo (nuova num.) | Schede S1 | Card di mappatura principali |
|---|---|---|
| 1 Manifesto | (fili D) | — (sintesi trasversale) |
| 2 Architettura | S1-C1 | SPW/SR/DIS-C1 |
| 3 Database Strategy | S1-C1, S1-C13 | *-C1, SR-C13 |
| 4 Frontend Dependencies | S1-C3, S1-C6 | *-C3, SPW/SR/DIS-C6 |
| 5 Backend Logic | S1-C1, S1-C4 | *-C1, *-C4 |
| 6 Frontend Bridge | S1-C3, S1-C4 | *-C3 (FDCA: bridge assente) |
| 7 Media & Upload | S1-C5 | SPW/SR/DIS-C5 |
| 8 Advanced Editing | S1-C6 (+ B4: C7/C8/C9) | *-C6 |
| 9 Content Lifecycle | S1-C4, S1-C3 | *-C4 |
| 10 Security & Auth | S1-C2, S1-C3, S1-C5, S1-C11, S1-C12 | *-C2 |
| 11 SEO Pre-rendering | S1-C7, S1-C2(§6) | SPW/SR/DIS-C7 |
| 12 RSS Feed | S1-C8 | SPW/SR/DIS-C8 |
| 13 Newsletter | S1-C9, S1-C2 | SPW/SR/DIS-C9 |
| 14 Admin Dashboard (NEW) | S1-C12, S1-C11(analytics) | SPW/SR/DIS-C12 |
| 15 Database Evolution | S1-C13, S1-C1, S1-C5, S1-C9 | SR-C13, *-C1 |
| 16 Portfolio & Projects | S1-C4 | SPW-C4 (projects) |
| 17 Festival Iscrizioni | S1-C10, S1-C5, S1-C9 | DIS-C10, DIS-C5 |
| 18 Festival Votazioni | S1-C10, S1-C2 | DIS-C10, DIS-C2 |
| 19 Festival Dashboard | S1-C10, S1-C12 | DIS-C10, DIS-C12 |
| 20 Social Reactions | S1-C11 | SPW-C11 |
| App. A Boilerplate | (tutte) | — |
| App. B Fork | S1-FORK | FDCA-DIFF |

**Copertura:** tutte le 14 schede S1 hanno una casa; tutte le 34 card di mappatura confluiscono in almeno
un capitolo. Nessun cluster resta orfano.

## 4. Collocazione degli 8 fili trasversali (S2/D) — una casa + rimandi

| Filo (D) | Casa (capitolo dove si spiega) | Rimandi (dove si richiama) |
|---|---|---|
| D1 — I 4 emettitori del `content` | **CAP 8** (box-ancora) + tabella completa in CAP 13 | CAP 11 (buco vivo), CAP 12 (il feed lo chiude) |
| D2 — "Più ingegnerizzato ≠ più sicuro" | **CAP 1** (tesi) | CAP 3/5/7/10/13/15 (dove emerge) |
| D3 — Write-time vs render-time | **CAP 20** (li mette a confronto) | CAP 8 (render-time), CAP 10 |
| D4 — Il fork eredita il debito | **App. B** | CAP 10 ("il fix non segue il fork") |
| D5 — La scala a 3 gradini come forma | **CAP 1** (chiave di lettura) | CAP 3/7/8/10/11/14 (forma ricorrente) |
| D6 — "L'init mente" + versionamento | **CAP 15** | CAP 3 (anticipo) |
| D7 — IP grezzo: buco o pregio | **CAP 10** (box anti-spoof) | CAP 18 (voto: pregio), CAP 20 (reazioni) |
| D8 — Cura senza prevenzione (backup) | **CAP 15** | CAP 14 (backup-placement), CAP 18 |

## 5. Spostamenti di contenuto (scope) decisi in S2/C

- **Cache TTL su file JSON**: da CAP 7 (Media) → **CAP 9 (Content Lifecycle)** [cache di *contenuto*] e
  CAP 11 [cache *SEO*, dove si racconta che in SR è morta].
- **SEO pre-rendering**: da CAP 7 §2 → **CAP 11** (è già il suo capitolo).
- **DDoS da bot social**: dall'attuale CAP 10 §6 → **CAP 11** (il vettore è l'entry-point PHP / UA).
- **CAP 7 ribattezzato** "Media & Optimization — Upload & Sicurezza" per riflettere il baricentro reale
  (la sicurezza upload, oggi assente).

## 6. Etichetta edizione (decisione da prendere)

Oggi incoerente (memoria progetto + ROADMAP E2): `_master.md`/README dicono **"Prima Edizione — Marzo
2026"**, `build-pdf.sh`/articolo dicono **"Seconda Edizione"**. Proposta: uniformare a **"Terza
Edizione"** in `_master.md`, README, `build-pdf.sh`, articolo-blog, e aggiornare "diciotto/diciannove
capitoli" → **"venti capitoli + due appendici"**. (Esecuzione in FASE 4/E2; qui si fissa la decisione.)

## 7. DECISIONI APERTE per il GATE S4 (servono a Simone)

1. **Nuovo CAP 14 "Admin Dashboard generale":** confermi l'inserimento in Parte IV con la conseguente
   rinumerazione della Parte V (+1)? *(Raccomandato: sì — oggi è un buco reale.)*
2. **Appendice B "Fork":** appendice a sé (raccomandato) oppure sezione in coda al CAP 15 (DB Evolution)?
3. **Analytics first-party:** sezione dentro il CAP 14 Admin (raccomandato) o capitolo a sé?
4. **CAP 7 ribilanciamento:** ok spostare cache→9 e SEO→11 e rinominarlo "Upload & Sicurezza"?
5. **Etichetta edizione:** confermi "Terza Edizione" ovunque (chiusura E2)?
6. **Profondità delle riscritture:** per i 5+1 capitoli "RISCRIVI", riscrittura integrale o riscrittura
   chirurgica per sezioni? *(Raccomandato: chirurgica — preservare ciò che è corretto, sostituire le parti
   smentite, aggiungere le sezioni mancanti.)*
7. **Ordine di scrittura (FASE 3):** proposta di partire dai capitoli a più alto valore/più rotti —
   **CAP 10 Security** (gap CSRF), **CAP 8+11+12+13** (il filo dei 4 emettitori, da scrivere insieme per
   coerenza), poi il nuovo **CAP 14 Admin**, infine correzioni minori. Confermi questa priorità?

> Una volta che Simone valida (S4), la FASE 2 è chiusa e si passa alla FASE 3 (scrittura, un capitolo/
> micro-step per sessione, generati da questa scaletta).

---

## 8. ✅ DECISIONI DEL GATE S4 — prese da Simone il 2026-06-19

1. **Nuovo CAP 14 "Admin Dashboard generale" + rinumerazione Parte V (+1): SÌ.** Si adotta l'Indice a
   **20 capitoli + 2 appendici** del §2. CAP 19 (festival dashboard) → specializzazione del nuovo CAP 14.
2. **Appendice B "Fork": SÌ, appendice a sé** (non sezione del CAP DB Evolution).
3. **Analytics first-party: SÌ, sezione dentro il CAP 14 Admin** ("Misurare senza terze parti").
4. **CAP 7 ribilanciato: SÌ** — cache→CAP 9, SEO→CAP 11, rinominato "Media & Optimization — Upload & Sicurezza".
5. **Etichetta "Terza Edizione": SÌ** ovunque (chiude E2) — esecuzione in FASE 4.
6. **Profondità riscritture: CHIRURGICA** — preservare il corretto, sostituire le parti smentite,
   aggiungere le sezioni mancanti (vale per CAP 6/7/8/10/11/12/13/20).
7. **Ordine FASE 3: deciso da Claude "secondo logica".** Sequenza adottata:
   - **(1) CAP 10 Security & Auth** — fondamenta referenziate ovunque (CSRF, `session_version`, IP-box,
     role-blind); oggi il capitolo più lacunoso. Stabilisce il vocabolario di sicurezza usato dagli altri.
   - **(2) CAP 8 Advanced Editing** — ospita il **box-ancora "4 emettitori"** (D1), apre il filo.
   - **(3) CAP 11 SEO → (4) CAP 12 RSS → (5) CAP 13 Newsletter** — completano il filo dei 4 emettitori in
     ordine (il buco vivo → il feed che lo chiude per escape/sottrazione → la newsletter che lo chiude del tutto).
   - **(6) CAP 14 Admin (nuovo)** — sintetizza e referenzia Security/analytics/backup: dopo il CAP 10.
   - **(7) CAP 6 Frontend Bridge → (8) CAP 7 Media/Upload → (9) CAP 20 Reactions** — le altre riscritture.
   - **(10) Correzioni** ai capitoli AGGIORNA/CORREGGI (CAP 3, 9, 15, 16, 17, 18, 19, + 1/2/4/5).
   - **(11) App. B Fork** + **(12) FASE 4**: rinumerazione fisica, etichetta edizione, Boilerplate, build.

**→ FASE 2 CHIUSA. Prossima unità operativa: FASE 3 / scrittura CAP 10 Security & Auth (riscrittura chirurgica).**
