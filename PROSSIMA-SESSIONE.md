# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟨 **FASE 3 — SCRITTURA in corso.** Riscritture CHIRURGICHE. Target: 20 capitoli + 2 appendici.
> ✅ CAP 10 Security · ✅ CAP 8 Editing · ✅ CAP 11 SEO · ✅ CAP 12 RSS · ✅ CAP 13 Newsletter · ✅ CAP 14 Admin (NUOVO) · ✅ CAP 6 Bridge · ✅ CAP 7 Media
> 🟢 Filo 4 emettitori COMPLETO · 🟢 Rinumerazione Parte V eseguita (20 capitoli fisici).
> 🟦 Questa sessione: **9ª card — CAP 20 — Social Interactions & Reactions.**

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
`_cantiere-terza-edizione/ROADMAP.md`, `LOG.md`, `sintesi/_INDICE-SINTESI.md` e — per la scrittura —
`sintesi/S2-inventario-contenuti.md` (azioni/correzioni per capitolo) e `sintesi/S3-scaletta-globale.md`
(indice a 20 capitoli §2, mappa card→capitolo §3, decisioni gate §8).

STATO: FASE 1 ✅, FASE 2 ✅, FASE 3 in corso — **CAP 10 ✅ · 8 ✅ · 11 ✅ · 12 ✅ · 13 ✅ · 14 ✅ · 6 ✅ · 7 ✅** (8/9).
Ordine (S3 §8): … → **(9) CAP 20 Reactions ← QUESTA SESSIONE** → (10) correzioni CAP 1/2/3/4/5/9/16/17/18/19 →
(11) App. B Fork → (12) FASE 4.

UNITÀ DI QUESTA SESSIONE: **FASE 3 / CAP 20 — Social Interactions & Reactions** (riscrittura chirurgica).

Metodo (riscrittura CHIRURGICA — NON da zero):
1. Leggi il **CAP 20 attuale** (`CAPITOLO 20 - Social Interactions & Reactions.md`) e la scheda **S1-C11**
   (`sintesi/S1-C11-engagement-reactions.md`) per intero (pattern §1, tabella §2, GOLD §3, mappa+correzioni §4).
   Per gli stralci di codice reali usa la card di mappatura `mappatura/SimonePizziWebSite/SPW-C11-*.md` con riferimento `path:linea`.
2. **Preserva** ciò che è corretto; **sostituisci** le parti smentite; **aggiungi** le sezioni mancanti.
   Lente vera (S1-C11): è il capitolo della **scrittura PUBBLICA non autenticata** — l'unico fronte in cui un
   visitatore scrive nel DB (reazioni + messaggi). **Reactions = SOLO SPW** (gli altri siti non le hanno).
   Correzioni note (da S1-C11 §4): §4 il rate-limit NON è "un solo strato per IP" → sono **DUE strati**
   (voter_hash 20/min, bypassabile via UA-rotation, + secondo argine solo-IP 30/min riusando login_attempts
   namespaced 'rea:'); §3 il `voter_hash=SHA256(IP+UA)` **NON è salato né irreversibile** → NON è anonimato
   (rimando CAP 10 «fidarsi dell'IP»); il capitolo **omette `messages.php`** e **le DUE filosofie** di
   sanitizzazione; versione SPW è **v1.21** non «v2.0».
3. Materiale da coprire (GOLD S1-C11): **le due filosofie ANTITETICHE nello stesso codebase** —
   sanitizzazione **write-time** per i messaggi (`strip_tags` all'INSERT, stored-XSS neutralizzato all'origine)
   vs **render-time** per gli articoli (DOMPurify a video, CAP 8) = polarità inversa; **rate-limit a due strati**
   (perché lo UA è bypassabile dal client → secondo argine solo-IP); **hash ≠ anonimato** (SHA256(IP+UA) non
   salato = reversibile/correlabile); **integrità nello schema** (UNIQUE KEY + INSERT IGNORE anti-doppio-voto
   a livello DB, contrasto col drift di `vote_count` del festival CAP 18/S1-C10); **REMOTE_ADDR grezzo** invece
   di getClientIp anti-spoof (CAP 10); **email fire-and-forget** verso indirizzo hardcoded (ponte CAP 13);
   consenso GDPR solo client-side. Engagement leggero (reazioni) vs voto competitivo (festival CAP 18).
4. Tono narrativo + blocchi di codice reali con origine `path:linea` + box `[!WARNING]`/`[!NOTE]`/`[!TIP]`/`[!IMPORTANT]`
   (stile casa) + footer "Prossimo Capitolo". NB: CAP 20 è l'ULTIMO capitolo del libro (chiude la Parte V):
   il footer può rimandare alle Appendici / chiudere l'arco, non a un CAP 21 inesistente.

5. ⚠️ **REVISIONE STILISTICA OBBLIGATORIA — REGOLA FISSA (memoria `feedback-revisione-stilistica-capitoli`).**
   A capitolo scritto, PRIMA del commit, passalo per le skill **`prosa-italiana`** e **`humanizer`**, poi fai
   il pass finale «cosa rende ancora questo testo ovviamente LLM?» e correggi. Il libro è tecnico ma deve
   essere semplice, narrativo, piacevole — senza appiattire la tesi. Checklist concreta (già applicata a CAP 6/7/8/10/11/12/13/14):
   - **TIPOGRAFIA ITALIANA:** virgolette **caporali «»** per termini/citazioni/etichette (NON le `"..."` dritte
     fuori dal codice); puntini di sospensione `…` unici (NON `...`) fuori dal codice; apostrofo dritto `'`
     (coerenza col libro esistente); accenti corretti (è/é, perché, sé, né); i numeri da uno a dieci in lettere.
   - **ANTIPATTERN LLM (humanizer):** il **trattino lungo `—` NON va usato in prosa** (convertilo in virgola,
     punto o parentesi) — è ammesso SOLO nei commenti dei blocchi di codice (etichette d'origine) e come cella
     «non applicabile» nelle tabelle; niente **tricolon** non guadagnati (gruppi di tre meccanici); niente
     **signposting/filler** («vale la pena», «conviene», «è importante notare», «approfondiamo», «in conclusione»);
     niente **boldface meccanico** a raffica; niente conclusioni genericamente positive; varia il ritmo
     delle frasi; preserva voce e posizione (la tesi NON va annacquata); **non rompere la quarta parete**
     (niente riferimenti alla «versione precedente del capitolo» né alla «Seconda Edizione»).
   - **VERIFICA GREP prima del commit:** `grep "—"` → solo commenti-codice/celle-tabella; `grep '\.\.\.'` e
     `grep '"'` → solo dentro blocchi di codice; conta caporali e filler. (Vedi i comandi usati nei LOG di CAP 6/7/11/12/13/14.)

Criterio di STOP: CAP 20 riscritto (chirurgico) e coerente, con rate-limit-a-DUE-strati + hash≠anonimato
+ le-due-filosofie-write/render + integrità-nello-schema + messages.php; correzioni applicate (DUE strati non uno,
hash non salato, versione v1.21); **revisione stilistica eseguita.**

Ciclo di chiusura OBBLIGATORIO: aggiorna `ROADMAP.md` (§5: spunta CAP 20; FASE 3 scrittura 9/9 capitoli-da-riscrivere
COMPLETA, restano le correzioni dei capitoli legacy CAP 1/2/3/4/5/9/16/17/18/19 + App. B Fork) + una riga `LOG.md`
+ git add/commit/push (verifica sync) + riscrivi QUESTO file (root + `_cantiere-terza-edizione/`) con la prossima
unità: **FASE 3 / batch correzioni capitoli legacy** (CAP 1/2/3/4/5/9/16/17/18/19 — riscritture/correzioni minori
da S2 + allineamento tipografico «» dei capitoli vecchi con `"..."` dritte; oppure App. B Fork). Vedi `sintesi/S3-scaletta-globale.md`
§8 per l'ordine. **Ricorda di rimettere le REGOLE TIPOGRAFICHE/PROSA/ANTIPATTERN come qui sopra.**

Nota metodo: un capitolo per sessione. Scrivere/committare un capitolo alla volta.
