# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟨 **FASE 3 — SCRITTURA in corso.** Riscritture CHIRURGICHE. Target: 20 capitoli + 2 appendici.
> ✅ CAP 10 Security · ✅ CAP 8 Editing · ✅ CAP 11 SEO · ✅ CAP 12 RSS · ✅ CAP 13 Newsletter · ✅ CAP 14 Admin (NUOVO) · ✅ CAP 6 Bridge
> 🟢 Filo 4 emettitori COMPLETO · 🟢 Rinumerazione Parte V eseguita (20 capitoli fisici).
> 🟦 Questa sessione: **8ª card — CAP 7 — Media & Optimization (Upload & Sicurezza).**

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
`_cantiere-terza-edizione/ROADMAP.md`, `LOG.md`, `sintesi/_INDICE-SINTESI.md` e — per la scrittura —
`sintesi/S2-inventario-contenuti.md` (azioni/correzioni per capitolo) e `sintesi/S3-scaletta-globale.md`
(indice a 20 capitoli §2, mappa card→capitolo §3, decisioni gate §8).

STATO: FASE 1 ✅, FASE 2 ✅, FASE 3 in corso — **CAP 10 ✅ · 8 ✅ · 11 ✅ · 12 ✅ · 13 ✅ · 14 ✅ · 6 ✅** (7/9).
Ordine (S3 §8): … → **(8) CAP 7 Media ← QUESTA SESSIONE** → (9) CAP 20 Reactions →
(10) correzioni CAP 1/2/3/4/5/9/16/17/18/19 → (11) App. B Fork → (12) FASE 4.

UNITÀ DI QUESTA SESSIONE: **FASE 3 / CAP 7 — Media & Optimization — Upload & Sicurezza** (riscrittura chirurgica).

Metodo (riscrittura CHIRURGICA — NON da zero):
1. Leggi il **CAP 7 attuale** (`CAPITOLO 7 - Media & Optimization.md`) e la scheda **S1-C5**
   (`sintesi/S1-C5-media-upload.md`) per intero (pattern §1, tabella §2, GOLD §3, mappa+correzioni §4).
   Per gli stralci di codice reali usa le card di mappatura `mappatura/*/(*-C5).md` con riferimento `path:linea`.
2. **Preserva** ciò che è corretto; **sostituisci** le parti smentite; **aggiungi** le sezioni mancanti.
   Tesi portante (S1-C5): stesso scheletro `upload.php`+GD nei tre siti, ma la **SICUREZZA scala
   all'inverso del naming** — 3 barriere SPW / 1 SR / ≈0 + upload PUBBLICO DIS = **catena RCE verificata**;
   il più minimale (SR) non è il più insicuro, il più "gentile" (DIS, che accetta upload dai partecipanti)
   abilita la RCE. Correzioni note (da S1-C5 §4): **il CAP 7 attuale OMETTE del tutto la sicurezza upload**;
   §3.3 — l'`.htaccess` su uploads è **PHP-off** (esecuzione spenta), non solo cache; §3.1 — **WebP non è
   universale** (GIF animata preservata/esclusa, fallback). Tesi D2 dove pertinente («più ingegnerizzato ≠ più sicuro»).
3. Materiale da coprire (GOLD S1-C5): **difesa a 3 livelli** SPW (estensione + magic-bytes finfo + naming
   uniqid-senza-punti + sottocartelle su MIME-reale + `.htaccess` PHP-off) vs **1 livello** SR (solo
   validazione applicativa, NESSUN `uploads/.htaccess`, PHP non spento) vs **≈0 + upload pubblico** DIS
   (`participants.php` accetta audio dai partecipanti, MIME client spoofabile, no PHP-off = **catena RCE**);
   **`$_FILES['type']` non è validazione** (è dichiarato dal client); **path-guard** realpath/basename/strpos
   + **delete senza CSRF** (media.php SR non include auth_utils, solo basename); **disco-come-DB-media**
   (SR scandir, niente tabella media) vs tabella `media` SPW; **WebP non universale**; **script one-shot
   non-gated** (optimize/fix). NB scope già spostato: cache TTL → CAP 9, SEO/prerender → CAP 11.
4. Tono narrativo + blocchi di codice reali con origine `path:linea` + box `[!WARNING]`/`[!NOTE]`/`[!TIP]`/`[!IMPORTANT]`
   (stile casa) + footer "Prossimo Capitolo" (→ CAP 20 Social Interactions & Reactions, prossima riscrittura
   dell'ordine FASE 3; in ordine-libro il successivo CAP 8 è già fatto, quindi punta a CAP 20).

5. ⚠️ **REVISIONE STILISTICA OBBLIGATORIA — REGOLA FISSA (memoria `feedback-revisione-stilistica-capitoli`).**
   A capitolo scritto, PRIMA del commit, passalo per le skill **`prosa-italiana`** e **`humanizer`**, poi fai
   il pass finale «cosa rende ancora questo testo ovviamente LLM?» e correggi. Il libro è tecnico ma deve
   essere semplice, narrativo, piacevole — senza appiattire la tesi. Checklist concreta (già applicata a CAP 6/8/10/11/12/13/14):
   - **TIPOGRAFIA ITALIANA:** virgolette **caporali «»** per termini/citazioni/etichette (NON le `"..."` dritte
     fuori dal codice); puntini di sospensione `…` unici (NON `...`) fuori dal codice; apostrofo dritto `'`
     (coerenza col libro esistente); accenti corretti (è/é, perché, sé, né); i numeri da uno a dieci in lettere.
   - **ANTIPATTERN LLM (humanizer):** il **trattino lungo `—` NON va usato in prosa** (convertilo in virgola,
     punto o parentesi) — è ammesso SOLO nei commenti dei blocchi di codice (etichette d'origine) e come cella
     «non applicabile» nelle tabelle; niente **tricolon** non guadagnati (gruppi di tre meccanici); niente
     **signposting/filler** («vale la pena», «conviene», «è importante notare», «approfondiamo», «in conclusione»);
     niente **boldface meccanico** a raffica; niente conclusioni genericamente positive; varia il ritmo
     delle frasi; preserva voce e posizione (la tesi NON va annacquata); **non rompere la quarta parete**
     (niente riferimenti alla «versione precedente del capitolo»).
   - **VERIFICA GREP prima del commit:** `grep "—"` → solo commenti-codice/celle-tabella; `grep '\.\.\.'` e
     `grep '"'` → solo dentro blocchi di codice; conta caporali e filler. (Vedi i comandi usati nei LOG di CAP 6/11/12/13/14.)

Criterio di STOP: CAP 7 riscritto (chirurgico) e coerente, con difesa-upload 3/1/0 + catena RCE pubblica DIS
+ `$_FILES['type']`-non-è-validazione + PHP-off `.htaccess` + path-guard + delete-senza-CSRF + WebP-non-universale;
correzioni applicate (sicurezza upload aggiunta, `.htaccess`=PHP-off, WebP non universale); **revisione stilistica eseguita.**

Ciclo di chiusura OBBLIGATORIO: aggiorna `ROADMAP.md` (§5: spunta CAP 7, indica CAP 20 come prossimo) +
una riga `LOG.md` + git add/commit/push (verifica sync) + riscrivi QUESTO file (root +
`_cantiere-terza-edizione/`) con la prossima unità: **FASE 3 / CAP 20 — Social Interactions & Reactions**
(riscrittura chirurgica: reazioni anonime toggle, `voter_hash=SHA256(IP+UA)` NON salato/reversibile ≠ anonimato,
rate-limit a DUE strati voter_hash 20/min bypassabile-via-UA + secondo argine solo-IP 30/min, integrità nello
schema UNIQUE+INSERT-IGNORE, le DUE filosofie write-time-messaggi vs render-time-articoli; reactions SOLO SPW.
Fonti S1-C11. Correzioni: un-solo-strato-mislabeled→sono-DUE, hash-NON-salato-né-irreversibile, omessi messages.php
+ le-due-filosofie, versione v1.21 non v2.0). **Ricorda di rimettere le REGOLE TIPOGRAFICHE/PROSA/ANTIPATTERN come qui sopra.**

Nota metodo: un capitolo per sessione. Scrivere/committare un capitolo alla volta.
