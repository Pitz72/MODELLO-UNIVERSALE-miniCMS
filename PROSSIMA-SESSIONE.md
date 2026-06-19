# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟨 **FASE 3 — SCRITTURA in corso.** Riscritture CHIRURGICHE. Target: 20 capitoli + 2 appendici.
> ✅ **CAP 10 — Security & Auth** (2026-06-19) · ✅ **CAP 8 — Advanced Content Editing** (2026-06-19, con box-ancora "4 emettitori").
> 🟦 Questa sessione: **3ª card di scrittura — CAP 11 — SEO Pre-rendering con PHP Entry-Point.**

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
`_cantiere-terza-edizione/ROADMAP.md`, `LOG.md`, `sintesi/_INDICE-SINTESI.md` e — per la scrittura —
`sintesi/S2-inventario-contenuti.md` (azioni/correzioni per capitolo) e `sintesi/S3-scaletta-globale.md`
(indice a 20 capitoli, mappa card→capitolo §3, fili trasversali §4, decisioni del gate §8).

STATO: FASE 1 ✅, FASE 2 ✅, FASE 3 in corso — **CAP 10 ✅ · CAP 8 ✅** (2/9 riscritture).
Decisioni del gate (S3 §8): riscritture **CHIRURGICHE**; ordine FASE 3: (1) CAP 10 Security ✅ →
(2) CAP 8 Editing ✅ → **(3) CAP 11 SEO ← QUESTA SESSIONE** → (4) CAP 12 RSS → (5) CAP 13 Newsletter →
(6) CAP 14 Admin → (7) CAP 6 Bridge → (8) CAP 7 Media → (9) CAP 20 Reactions → (10) correzioni →
(11) App. B Fork → (12) FASE 4.

UNITÀ DI QUESTA SESSIONE: **FASE 3 / scrittura del CAP 11 — SEO Pre-rendering con PHP Entry-Point**
(riscrittura chirurgica). È il **secondo capitolo del filo dei 4 emettitori** (aperto in CAP 8): qui il
`content` grezzo riemesso dal prerender mostra la **falla XSS-attributi ancora viva**.

Metodo (riscrittura CHIRURGICA — NON da zero):
1. Leggi il **CAP 11 attuale** (`CAPITOLO 11 - SEO Pre-rendering con PHP Entry-Point.md`) e la scheda
   **S1-C7** (`sintesi/S1-C7-seo-prerendering.md`) per intero (pattern §1, tabella §2, GOLD §3, mappa+correzioni §4).
   Attingi anche a **S1-C2 §6** (il caso DDoS-da-bot, che si SPOSTA qui dal vecchio CAP 10 §6) e al
   **box-ancora "4 emettitori" già scritto in CAP 8 §4** (qui si RICHIAMA, non si riscrive: è il punto in
   cui la falla del prerender è viva). Per gli stralci di codice reali usa le **card di mappatura**
   (`mappatura/*/(*-C7).md`) con riferimento `path:linea`.
2. **Preserva** ciò che è corretto; **sostituisci** le parti smentite; **aggiungi** le sezioni mancanti.
   Correzioni note (da S1-C7 §4): il capitolo **raccomanda l'SSG (Puppeteer/`vite-plugin-prerender`) che SPW
   ha PROVATO e SCARTATO** — la soluzione reale è il **Dynamic Rendering** (UA-sniff + HTML del corpo per i
   bot), non descritto; l'esempio SQLite è attribuito a SPW-MySQL (correggere). Aggiungere: **buco
   XSS-attributi** del prerender (`strip_tags`-allowlist ≠ DOMPurify, copiato identico da SPW a SR),
   **SEO indicizza le bozze** (SR riusa solo `published_at`, non `status`), **seo-cache morta** in SR
   (scritta da tutti, letta da nessuno), sitemap/robots dinamici, JSON-LD divergente.
3. **Scala a 3 gradini (D5):** Dynamic Rendering completo SPW≡SR (UA-sniff + body) / OG-proxy leggero
   solo-meta DIS (immune al buco per sottrazione). Tesi D2 dove pertinente (SR copia il motore di SPW + la falla).
4. **Accogliere il caso DDoS-da-bot** (dal vecchio CAP 10 §6): i bot che simulano i crawler social
   bombardano l'entry-point PHP che interroga il DB a ogni richiesta → 503/500. Soluzione: cache statica
   precompilata, percorso bot separato dall'umano. Qui è la **casa** del caso (il vettore è l'entry-point SEO);
   in CAP 10 è rimasta solo la massima "l'UA non è un gatekeeper".
5. Mantieni tono narrativo + blocchi di codice reali con origine `path:linea` + box
   `[!WARNING]`/`[!NOTE]`/`[!TIP]`/`[!IMPORTANT]` (stile casa) + footer "Prossimo Capitolo".
6. **REVISIONE STILISTICA OBBLIGATORIA (regola fissa, memoria `feedback-revisione-stilistica-capitoli`):**
   a capitolo scritto, passalo per la skill **`prosa-italiana`** (tipografia — caporali «», puntini `…`;
   prosa/narrativa — ritmo, lessico, niente filler) **e** per **`humanizer`** (antipattern LLM — trattini
   lunghi abusati, tricolon, signposting, boldface meccanico). Pass finale «cosa rende ancora LLM?» + correzione.
   Verifica via grep che non restino `—` in prosa (solo nei commenti codice è OK) né `...`/`"..."` fuori dal codice.

Criterio di STOP: CAP 11 riscritto (chirurgico) e coerente, con Dynamic Rendering vs SSG-scartato + buco
XSS-attributi (richiamo al box-ancora 4 emettitori) + bozze indicizzate + seo-cache morta + caso DDoS-da-bot
accolto; correzioni applicate; **revisione stilistica eseguita.** NB: il CAP resta numerato 11.

Ciclo di chiusura OBBLIGATORIO: aggiorna `ROADMAP.md` (§5: spunta CAP 11, indica CAP 12 come prossimo) +
una riga `LOG.md` + git add/commit/push (verifica sync) + riscrivi QUESTO file (root +
`_cantiere-terza-edizione/`) con la prossima unità: **FASE 3 / CAP 12 — RSS Feed & Syndication**
(riscrittura chirurgica: il feed è l'emettitore PIÙ sicuro del content — non lo emette o lo escapa, **chiude
il filo dei 4 emettitori**; feed-podcast = DIS non SR; proxy CORS inbound; `feed_config` security-theater;
catch-vuoto = anti-pattern non pattern; GUID URN. Fonti S1-C8).

Nota metodo: un capitolo per sessione (materiale corposo). Scrivere/committare un capitolo alla volta.
