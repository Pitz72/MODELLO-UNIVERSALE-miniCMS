# PROSSIMA SESSIONE — il libro è pubblicato; prossimo lavoro: traduzione EN

> ✅ **Contenuti FINALIZZATI** (20 capitoli + 3 appendici A/B/C, Terza Edizione).
> ✅ **Impaginazione fatta** (interno Typst 7×10" B/N + EPUB + copertina integrale).
> ✅ **Pubblicato su KDP**, poi **ristampa urgente** con 3 correzioni tecniche del revisore.

---

## Stato al 27/06/2026 (ultima sessione)
Un revisore ha segnalato errori tecnici; ne ho corretti **3** nei sorgenti `.md` (commit `0968314`):
- **CAP 16** — nota di dialetto sullo schema `projects` (mostrato in SQLite ma SPW è MySQL).
- **CAP 11 §7** — i crawler social ricevono **HTML generato dai file JSON di cache**, non JSON.
- **CAP 20 §3** — commento inline sul `substr(…,0,40)`.

Le pagine restano **160** (multiplo di 4) → **copertina/dorso invariati**, ristampa del solo interno.
La build print-ready finale (DeviceGray) l'ha fatta **Cowork** (su Windows `gs` segfaulta — vedi
`_cowork-impaginazione/ISTRUZIONI-COWORK-BUILD.md` e la memoria `impaginazione-build-delivery`).
Deliverable in `…\Claude\Projects\Progetto di Impaginazione Libri\Libri Archiviati\Pubblicati\The Thin Stack\`.

## Se serve un'altra ristampa / correzione
1. Correggi i `.md` in `manuale/` (regola: skill `prosa-italiana` + `humanizer`, tipografia «», niente `—` in prosa).
2. Commit + push su `main`.
3. Passa a Cowork il file `_cowork-impaginazione/ISTRUZIONI-COWORK-BUILD.md` (ha tutto: build interno DeviceGray + EPUB, verifiche, consegna).
4. Se le pagine cambiano (≠160 o non multiplo di 4) → **va rigenerata anche la copertina** (dorso diverso).

## ➡️ PROSSIMO LAVORO PREVISTO: traduzione integrale in inglese
Progetto a sé (ramo o cartella `/en`), **un capitolo per volta**, partendo dal testo italiano congelato:
- glossario tecnico IT→EN coerente; **codice lasciato intatto**;
- revisione di stile da madrelingua tecnico; tipografia inglese (virgolette dritte/curve, **non** caporali «»);
- stesso impianto a 20 capitoli + 3 appendici.

Quando riapri: dimmi se partiamo con la **traduzione EN** (e da quale capitolo) o se c'è altro da ritoccare.
