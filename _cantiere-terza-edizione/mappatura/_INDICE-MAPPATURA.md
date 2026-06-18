# INDICE MAPPATURA — stato delle card

> Legenda: ⬜ da fare · 🟨 in corso · ✅ completato

## SimonePizziWebSite
- ✅ SPW-C1 Backend Core · ✅ SPW-C2 Security · ✅ SPW-C3 Frontend Bridge · ✅ SPW-C4 Content APIs
- ✅ SPW-C5 Media · ✅ SPW-C6 Editor · ✅ SPW-C7 SEO · ✅ SPW-C8 RSS · ✅ SPW-C9 Newsletter
- ✅ SPW-C11 Engagement · ✅ SPW-C12 Admin · **(SimonePizziWebSite COMPLETO)**

## SitoRuntime
- ✅ SR-C1 Backend Core · ✅ SR-C2 Security+CORS · ✅ SR-C3 Frontend Bridge · ✅ SR-C4 Content (news/speakers/podcasts)
- ✅ SR-C5 Media · ✅ SR-C6 Editor (Tiptap v3 + shim Quill→Tiptap) · ✅ SR-C7 SEO+cache · ✅ SR-C8 RSS · ✅ SR-C9 Newsletter
- ✅ SR-C12 Admin · ✅ SR-C13 DB Evolution & Incidenti · **(SitoRuntime COMPLETO, 11 card)**

## DISINTELLIGENZA
- ✅ DIS-C1 Backend Core (SQLite vivo) · ✅ DIS-C2 Security+anti-frode voto · ✅ DIS-C3 Frontend Bridge (codemod fix_api) · ✅ DIS-C4 Content · ✅ DIS-C5 Media (upload pubblico/RCE)
- ✅ DIS-C6 Editor (contentEditable custom, no DOMPurify) · ✅ DIS-C7 SEO (OG-proxy leggero) · ✅ DIS-C8 RSS (feed podcast iTunes) · ✅ DIS-C9 Newsletter (no double opt-in/no token)
- ✅ DIS-C10 Festival Logic (cuore: stati/round/voto/settings) · ✅ DIS-C12 Admin (dashboard che misura; contacts write-only; guard role-blind) · **(DISINTELLIGENZA COMPLETO, 11 card)**

## FDCA
- ✅ FDCA-DIFF (vs DISINTELLIGENZA) — backend PHP byte-identico (tutti i GOLD ereditati, RCE inclusa); frontend riscritto/ridotto/scollegato (no admin, no api.ts, no fetch); re-brand "Canzone Artificiale" via Google AI Studio; v0.0.1 + ROADMAP-EVOLUZIONE-miniCMS · **(FDCA COMPLETO)**

---

## ✅ FASE 1 — MAPPATURA CONCLUSA + colmatura gap (4 siti, 34 card)
SimonePizziWebSite 11 · SitoRuntime 11 · DISINTELLIGENZA 11 · FDCA 1 (diff). → Prossima: FASE 2 (Sintesi).

## Matrice di copertura `(sito × cluster)`
> Legenda: ✅ mappato · — N/A (giustificato) · ◐ rinviato (coperto altrove) · *(FDCA: backend = DIS, solo DIFF)*

| Cluster | SPW | SR | DIS |
|---|:--:|:--:|:--:|
| C1 Backend Core | ✅ | ✅ | ✅ |
| C2 Security & Auth | ✅ | ✅ | ✅ |
| C3 Frontend Bridge | ✅ | ✅ | ✅ |
| C4 Content APIs | ✅ | ✅ | ✅ |
| C5 Media & Upload | ✅ | ✅ | ✅ |
| C6 Editor | ✅ | ✅ | ✅ |
| C7 SEO & Prerendering | ✅ | ✅ | ✅ |
| C8 RSS & Feed | ✅ | ✅ | ✅ |
| C9 Newsletter & Email | ✅ | ✅ | ✅ |
| C10 Festival Logic | — *(no festival)* | — *(no festival)* | ✅ |
| C11 Engagement/Reactions | ✅ | — *(no reactions)* | — *(no reactions)* |
| C12 Admin Dashboard | ✅ | ✅ | ✅ |
| C13 DB Evolution & Incidenti | — *(MySQL migrato pulito, previene)* | ✅ | ◐ *(meccanismo update_db_* in DIS-C1)* |

**Gap colmati il 18/06/2026 (FASE 1-bis):** SR-C6, DIS-C3, DIS-C6, DIS-C7, DIS-C8 — riequilibrio
verso la metà React/SEO della mission "thin stack". Copertura ora **completa** (tutti i cluster reali
mappati; N/A giustificati; C13-DIS rinviato perché il meccanismo è in DIS-C1).
