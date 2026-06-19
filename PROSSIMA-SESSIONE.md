# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟩 **FASE 2 / sotto-fase S1 (Consolidamento) CONCLUSA — 14/14 schede** (S1-C1…C13 + S1-FORK).
> Si passa alla sotto-fase **S2 — Inventario contenuti**. Ordine confermato: S1 ✅ → **S2** → S3 → S4.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md, _cantiere-terza-edizione/LOG.md e
_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md per il contesto.

STATO: FASE 1 (mappatura) CONCLUSA — 4 siti, 34 card. FASE 2 (SINTESI): **sotto-fase S1 CONCLUSA —
14/14 schede tematiche cross-sito** in `_cantiere-terza-edizione/sintesi/` (S1-C1 … S1-C13 + S1-FORK).
Ogni scheda ha: 0 una-frase · 1 pattern comune · 2 tabella varianti · 3 GOLD/box · 4 mappa→capitoli (+
correzioni al testo attuale) · 5 scarti/dedup. Le schede hanno già prodotto, capitolo per capitolo, un
elenco di **azioni e correzioni** verso i 19 capitoli esistenti.

UNITÀ DI QUESTA SESSIONE: **S2 — Inventario contenuti.** Obiettivo: trasformare le 14 schede S1 in un
**inventario operativo** che dica, per ciascun capitolo del libro e per ogni nuovo capitolo proposto,
cosa ENTRA / si AGGIORNA / è NUOVO / si SCARTA. È il ponte tra "abbiamo capito cosa dicono i siti" (S1) e
"ecco la scaletta della Terza Edizione" (S3).

Materiale di partenza (già pronto nelle schede S1, §4 di ciascuna):
- **Mappa scheda→capitolo** già abbozzata in ogni S1-Cx (sezione "Mappa → capitolo/i del libro").
- **Correzioni al testo attuale** già elencate scheda per scheda (CAP 3/6/7/8/9/10/11/12/13/14/16/17/18/19).
- **GAP / capitoli nuovi proposti:** almeno due emersi in S1 — (a) un **CAP "Admin Dashboard & Panels"
  generale** (S1-C12: oggi manca, CAP 18 è solo festival); (b) una **sezione/appendice "ciclo di vita di
  un fork"** (S1-FORK). Valutare anche: un capitolo "Misurare senza terze parti / analytics first-party"
  (S1-C12), e dove collocare il "quadro dei 4 emettitori del content" (filo S1-C6→C7→C8→C9, trasversale a
  CAP 8/11/12/13).

Fai così:
1. Leggi le 14 schede S1 (almeno i §4 "Mappa → capitolo" e le "Correzioni") e l'elenco dei 19 capitoli
   esistenti (sono file `CAPITOLO N - *.md` nella root del repo; c'è anche `_master.md`).
2. Produci `_cantiere-terza-edizione/sintesi/S2-inventario-contenuti.md` con:
   - **A) Tabella capitolo-per-capitolo** (CAP 1→19): per ciascuno → schede S1 che lo toccano · azione
     sintetica (CONFERMA / AGGIORNA / RISCRIVI / CORREGGI) · le correzioni puntuali già raccolte.
   - **B) Capitoli/sezioni NUOVI proposti** (Admin Dashboard generale, sezione Fork, eventuale Analytics
     first-party, box trasversale "4 emettitori") con motivazione e materiale-sorgente (quali schede).
   - **C) Cosa si SCARTA** (materiale per-sito troppo di dettaglio, falsi pattern, doppioni) già segnalato
     nei §5 delle schede.
   - **D) Fili trasversali** che attraversano più capitoli (i 4 emettitori del content; "più
     ingegnerizzato ≠ più sicuro" S1-C2/C5/C9/C12/C13; le due filosofie di sanitizzazione write-time vs
     render-time; il forking che eredita il debito) — dove e come trattarli senza ripetizioni.
3. Aggiorna `_INDICE-SINTESI.md` (S2 → ✅ o 🟨), `ROADMAP.md` (§4 spunta S2, §7 stato), una riga in `LOG.md`.

Criterio di STOP: `S2-inventario-contenuti.md` completo (A+B+C+D), tracking aggiornato, commit+push,
locale = origin/main.

Ciclo di chiusura OBBLIGATORIO a fine sessione: _INDICE-SINTESI + ROADMAP (§4/§7) + LOG (riga in basso) +
git add/commit/push (verifica sync) + riscrivi QUESTO file (root + _cantiere-terza-edizione/) con la
prossima sotto-fase: **S3 — Scaletta/Indice globale** della Terza Edizione (struttura a Parti + capitoli
con mappa card→capitolo), che sarà il GATE prima di S4 (validazione con Simone).

Nota metodo: S2/S3 NON sono "una scheda per cluster" ma documenti unitari di pianificazione — si possono
fare in una o due sessioni. Mantenere la qualità/omogeneità (no ripetizioni, rimandi alle schede S1).
