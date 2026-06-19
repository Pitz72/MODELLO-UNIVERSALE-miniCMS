# PROSSIMA SESSIONE — CONTENUTI FINALIZZATI, PASSAGGIO A COWORK/KDP

> ✅ **La mono-sessione finale dei contenuti è CONCLUSA (19/06/2026).** Tutti e sei i task sono fatti,
> committati e pushati (commit `17da837` → `3858a7d`).

---

## Stato

I **CONTENUTI** del libro sono **FINALIZZATI**. Il manuale «React + PHP: The Thin Stack» (Terza Edizione)
ha **20 capitoli + 2 appendici**:

- **Parte I–V**, CAP 1→20 — riscritture 9/9 ✅ + batch correzioni legacy 10/10 ✅ + CAP 15 ✅.
- **Appendice A** — Boilerplate Checklist (riallineata, con la nuova Fase 7 Sicurezza).
- **Appendice B** — Ciclo di vita di un fork (FDCA).
- Etichetta **«Terza Edizione»** uniforme (README, build-pdf.sh, articolo-blog).
- Tipografia: caporali «», em-dash/virgolette/puntini solo dentro il codice (grep-clean su tutto).

Stato completo in `ROADMAP.md` §7 e `LOG.md`.

---

## Prossimo passo: COWORK/KDP (fuori scope di Claude Code)

La **composizione tipografica / impaginazione per KDP** (font, margini, gabbia, resa PDF/ebook di stampa,
rigenerazione di `_master.md` come artefatto) è un **progetto Claude Cowork separato** (memoria
`scope-claude-code-vs-cowork-kdp`). In Claude Code non si fa: qui i contenuti sono pronti per la consegna.

Prima del passaggio, **Simone farà domande e darà indicazioni**.

## Note / ritocchi puntuali eventualmente da decidere con Simone (NON bloccanti)

1. **Riferimenti «Seconda Edizione» in tre capitoli.** CAP 10 (box correzione), CAP 12 (§7) e CAP 13
   (§4) contengono box «Correzione rispetto alla Seconda Edizione». Sono didattici (spiegano cosa è
   cambiato), ma rompono la quarta parete per il lettore finale della Terza Edizione. Lasciati invariati
   (sono capitoli già chiusi nelle sessioni precedenti): da decidere se neutralizzarli.
2. **Tabella siti nel README** (sezione «I Siti di Riferimento»): versioni e descrizioni datate
   (SitoRuntime v2.6.2 e «Quill Editor» → oggi v2.9.13 e Tiptap; SimonePizziWebSite v1.7.13 → v1.21.0).
   Fuori dallo scope dell'etichetta-edizione (E2): da aggiornare se si vuole un front-matter accurato.
