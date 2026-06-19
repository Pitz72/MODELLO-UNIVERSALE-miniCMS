# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟨 **FASE 3 — SCRITTURA in corso.** Riscritture CHIRURGICHE. Target: 20 capitoli + 2 appendici.
> ✅ **CAP 10 — Security & Auth** concluso (2026-06-19): CSRF a 3 gradini, `session_version`, recovery/reset,
> credenziali default, box-ancora D7 "Fidarsi dell'IP", reset-senza-CSRF + backup; DDoS spostato a CAP 11.
> 🟦 Questa sessione: **2ª card di scrittura — CAP 8 — Advanced Content Editing.**

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
`_cantiere-terza-edizione/ROADMAP.md`, `LOG.md`, `sintesi/_INDICE-SINTESI.md` e — per la scrittura —
`sintesi/S2-inventario-contenuti.md` (azioni/correzioni per capitolo) e `sintesi/S3-scaletta-globale.md`
(indice a 20 capitoli, mappa card→capitolo §3, fili trasversali §4, decisioni del gate §8).

STATO: FASE 1 (mappatura) ✅, FASE 2 (sintesi) ✅, FASE 3 (scrittura) in corso — **CAP 10 ✅** (1/9 riscritture).
Decisioni del gate (S3 §8): riscritture **CHIRURGICHE**; ordine FASE 3: (1) CAP 10 Security ✅ →
**(2) CAP 8 Editing [box-ancora 4 emettitori] ← QUESTA SESSIONE** → (3) CAP 11 SEO → (4) CAP 12 RSS →
(5) CAP 13 Newsletter → (6) CAP 14 Admin → (7) CAP 6 Bridge → (8) CAP 7 Media → (9) CAP 20 Reactions →
(10) correzioni → (11) App. B Fork → (12) FASE 4.

UNITÀ DI QUESTA SESSIONE: **FASE 3 / scrittura del CAP 8 — Advanced Content Editing** (riscrittura chirurgica).
Motivo della priorità (S3 §8): il CAP 8 ospita il **box-ancora "I quattro emettitori del `content`"** (filo D1),
che apre il filo portante della sicurezza dei contenuti CAP 8→11→12→13. Va scritto prima dei tre capitoli
che lo richiamano.

Metodo (riscrittura CHIRURGICA — NON da zero):
1. Leggi il **CAP 8 attuale** (`CAPITOLO 8 - Advanced Content Editing & Media Integration.md`) e la scheda
   **S1-C6** (`sintesi/S1-C6-advanced-editing.md`) per intero (pattern §1, tabella §2, GOLD §3, mappa+correzioni §4).
   Per il box-ancora "4 emettitori" attingi anche a **S1-C7** (prerender = il buco vivo `strip_tags`-allowlist ≠
   DOMPurify), **S1-C8** (il feed che chiude per escape/sottrazione) e **S1-C9** (la newsletter che non emette
   content). Per gli stralci di codice reali usa le **card di mappatura** (`mappatura/*/(*-C6).md` + `*-C7/C8/C9`
   per il box) con riferimento `path:linea`.
2. **Preserva** ciò che è corretto; **sostituisci** le parti smentite; **aggiungi** le sezioni mancanti.
   Correzioni note (da S1-C6 §4): l'editor **NON** è "native-React senza dipendenze" ma **Tiptap** (SPW blindato /
   SR Tiptap + **shim migrazione Quill→Tiptap** / DIS `contentEditable`+`execCommand` custom, niente Tiptap);
   la **"Paste Protection" è sovradichiarata** (è cosmetica, NON sicurezza — non rimuove `<script>`); manca del
   tutto la difesa XSS-stored = **DOMPurify SOLO al render-time** è il choke-point reale, e **DIS è l'UNICO senza**
   DOMPurify (stored-XSS scoperto, salda con DIS-C6 link via `prompt` senza guardia).
3. **Tesi-filo da innestare:** la scala a 3 gradini (D5) applicata all'editor (Tiptap-blindato / Tiptap+shim /
   contentEditable-grezzo); D2 "più ingegnerizzato ≠ più sicuro" dove pertinente.
4. **BOX-ANCORA OBBLIGATORIO da scrivere qui (D1): "I quattro emettitori del `content`".** Lo stesso `content`
   grezzo riemesso da: **render** (DOMPurify = choke-point) / **prerender** (`strip_tags`-allowlist = **buco
   attributi**, vive in CAP 11) / **feed** (sottrazione|escape, CAP 12) / **newsletter** (non emette, CAP 13).
   Tesi: serve **una sanitizzazione server-side condivisa**. Qui va la **tabella completa** + apertura del filo;
   gli altri 3 capitoli lo **richiamano** (non ripetere). Rimando (NON ripetere) ai box di sicurezza che vivono
   in CAP 10 (CSRF, render-time vs write-time D3 → casa in CAP 20).
5. Mantieni il **tono narrativo** del libro + blocchi di codice reali con origine `path:linea` + box
   `[!WARNING]`/`[!NOTE]`/`[!TIP]` (stile casa) + footer "Prossimo Capitolo".

Criterio di STOP: CAP 8 riscritto (chirurgico) e coerente, con la scala editor a 3 gradini + DOMPurify-render-time
come choke-point + Paste-Protection ridimensionata + **box-ancora "4 emettitori" presente con tabella completa**;
correzioni applicate. **NB:** la rinumerazione fisica (il nuovo CAP 14 Admin + rinumerazione Parte V) si applica
quando si scrive il CAP 14 / in FASE 4 — qui il CAP resta numerato 8.

Ciclo di chiusura OBBLIGATORIO: aggiorna `ROADMAP.md` (§5: spunta CAP 8, indica CAP 11 come prossimo) +
una riga `LOG.md` + git add/commit/push (verifica sync) + riscrivi QUESTO file (root +
`_cantiere-terza-edizione/`) con la prossima unità: **FASE 3 / CAP 11 — SEO Pre-rendering** (riscrittura
chirurgica: Dynamic Rendering vs SSG-scartato; il **buco XSS-attributi** del prerender = qui il filo dei 4
emettitori mostra la falla viva; SEO indicizza le bozze; seo-cache morta in SR; **accogliere il caso DDoS-da-bot**
spostato qui dal vecchio CAP 10 §6; fonti S1-C7 + S1-C2 §6).

Nota metodo: un capitolo per sessione (materiale corposo). Se resta margine di contesto si può iniziare il CAP 11,
ma scrivere/committare un capitolo alla volta.
