# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA sola unità atomica.

## Unità da svolgere: **SPW-C3 — SimonePizziWebSite — Frontend Bridge & State**

### Prompt (copia/incolla nella nuova sessione)

```
Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.
Leggi anche le card già fatte:
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C1-backend-core.md
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C2-security-auth.md
  (C2 ha mappato il gate Auth::check, le sessioni, gli stati HTTP 401/403/429 che il
  frontend deve saper gestire, e la CORS same-origin: utile per capire il bridge).

Unità di QUESTA sessione (atomica, una sola): SPW-C3 — mappatura di Frontend Bridge & State
del sito SimonePizziWebSite (C:\Users\Utente\Documents\GitHub\SITI-WEB\SimonePizziWebSite).

Ambito C3: il "ponte" React↔PHP lato client. In particolare:
- src/services/api.ts (o equivalente): client HTTP, pattern "Double Read", base URL, fetch wrapper.
- hooks di data-fetching, loaders, gestione stato (context/store), caching lato client.
- routing (react-router): rotte pubbliche vs /admin, route guard/redirect su 401.
- gestione errori e stati di loading; come il frontend reagisce a 401/403/429/500 (vedi C2).
SOLO LETTURA sul sito sorgente. Individua prima i file reali con glob/grep (struttura src/).

Fai così:
1. Ispeziona in modo microscopico i file dell'ambito C3 (cita sempre percorso/file:linea).
2. Compila una card seguendo _cantiere-terza-edizione/mappatura/_TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C3-frontend-bridge.md
3. NON sconfinare in altri cluster (backend/db=C1, auth/sessioni=C2 già fatti, content api=C4,
   media=C5, editor=C6, admin/dashboard=C12): se trovi roba di altri cluster, annotala solo
   come puntatore nelle "Note / domande aperte". Qui interessa il LATO CLIENT del bridge.
4. NON riportare credenziali/segreti.

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SPW-C3 → ✅)
- aggiungi una riga a _cantiere-terza-edizione/LOG.md
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SPW-C3) e lo stato globale
- git add/commit/push e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: SPW-C4 — Content APIs
```

### Coda delle unità successive (per orientamento)
SPW-C4 → SPW-C5 → SPW-C6 → SPW-C7 → SPW-C8 → SPW-C9 → SPW-C11 → SPW-C12 →
poi SitoRuntime (SR-C1…SR-C13) → DISINTELLIGENZA (DIS-*) → FDCA-DIFF → FASE 2 (Sintesi).
