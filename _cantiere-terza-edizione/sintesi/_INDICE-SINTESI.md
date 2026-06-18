# INDICE SINTESI — FASE 2, stato delle schede

> Legenda: ⬜ da fare · 🟨 in corso · ✅ completato
> Metodo: UNA scheda tematica cross-sito per sessione. Fonti = card di mappatura (specialmente i §6).
> Ordine confermato della FASE 2: **S1 → S2 → S3 → S4** (vedi ROADMAP §4).

## S1 — Consolidamento (card per-sito → schede tematiche cross-sito)

Un cluster per scheda. Fonde i 2-3 trattamenti per-sito in una visione comparata
(pattern comune + varianti per sito + GOLD + mappa capitolo).

- ✅ **S1-C1 Backend Core & Bootstrap** — fonti SPW-C1, SR-C1, DIS-C1 (+ FDCA §3). → CAP 3/5/14.
  Scala a 3 gradini (SQLite grado-zero DIS / MySQL essenziale SPW / MySQL ingegnerizzato SR);
  GOLD init-fossile, credenziali-default, errore-connessione. Corregge 2 sviste in CAP 3.
- ✅ **S1-C2 Security & Auth** — fonti SPW-C2, SR-C2, DIS-C2 (+ SPW-C11 voter_hash, DIS-C10 contesto voto). → CAP 10 (princ.) + ponti CAP 13/11/17.
  Scala a 3 gradini RIBALTATA (SPW maturo / SR parziale / DIS grado-zero) — più ingegnerizzato ≠ più sicuro;
  CSRF a 3 gradini, flag cookie, IP grezzo-come-pregio (DIS), anti-frode voto + voter_hash, reset-a-un-clic.
  Corregge/amplia 4 punti in CAP 10 (§1.1 cookie Strict≠Lax, §1.2 username, §3 brute-force, §6 DDoS→CAP 11).
- ⬜ S1-C3 Frontend Bridge & State — fonti SPW-C3, SR-C3, DIS-C3
- ⬜ S1-C4 Content APIs — fonti SPW-C4, SR-C4, DIS-C4
- ⬜ S1-C5 Media & Upload — fonti SPW-C5, SR-C5, DIS-C5
- ⬜ S1-C6 Advanced Editing / Editor — fonti SPW-C6, SR-C6, DIS-C6
- ⬜ S1-C7 SEO & Prerendering — fonti SPW-C7, SR-C7, DIS-C7
- ⬜ S1-C8 RSS & Feed — fonti SPW-C8, SR-C8, DIS-C8
- ⬜ S1-C9 Newsletter & Email — fonti SPW-C9, SR-C9, DIS-C9
- ⬜ S1-C10 Festival Logic — fonte DIS-C10 (solo DIS; FDCA eredita)
- ⬜ S1-C11 Engagement & Reactions — fonte SPW-C11 (solo SPW)
- ⬜ S1-C12 Admin Dashboard & Panels — fonti SPW-C12, SR-C12, DIS-C12
- ⬜ S1-C13 DB Evolution & Incidenti — fonti SR-C13, DIS-C1 (meccanismo update_db_*), SPW-C1 (init fossile)
- ⬜ S1-FORK FDCA come caso "fork/evoluzione" — fonte FDCA-DIFF (non aggiunge pattern: backend = DIS)

## S2 — Inventario contenuti
- ⬜ Cosa entra / aggiorna / è nuovo / si scarta vs i 19 capitoli esistenti.

## S3 — Scaletta / indice globale
- ⬜ Struttura a Parti + capitoli, con mappa card→capitolo.

## S4 — Validazione indice con Simone
- ⬜ GATE prima della scrittura (FASE 3).

---

### Stato globale FASE 2
- **2 / 14 schede S1 completate** (S1-C1 ✅, S1-C2 ✅). Prossima: **S1-C3 Frontend Bridge & State**.
