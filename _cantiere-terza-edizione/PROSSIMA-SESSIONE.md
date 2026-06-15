# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA sola unità atomica.

## Unità da svolgere: **SPW-C4 — SimonePizziWebSite — Content APIs**

### Prompt (copia/incolla nella nuova sessione)

```
Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.
Leggi anche le card già fatte (contesto indispensabile per C4):
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C1-backend-core.md
  (bootstrap endpoint, singleton PDO, schema MySQL in migrate_to_mysql.php: tabelle
   articles/categories/article_views/projects/tags già viste lì).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C2-security-auth.md
  (gate Auth::check sui rami mutativi: GET pubblici vs POST/PUT/DELETE/PATCH protetti).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C3-frontend-bridge.md
  (LATO CLIENT del bridge: pattern "Double Read" array vs {data,total}, firme di api.ts.
   IMPORTANTE per C4: completare la mappa di QUALI endpoint tornano array nudo e quali
   {data,total}; il contratto si decide lato server, ed è qui che va verificato).

Unità di QUESTA sessione (atomica, una sola): SPW-C4 — mappatura delle Content APIs
del sito SimonePizziWebSite (C:\Users\Utente\Documents\GitHub\SITI-WEB\SimonePizziWebSite).

Ambito C4: il LATO SERVER delle API di contenuto (gli endpoint PHP in public/api/). In particolare:
- articles.php: CRUD articoli, paginazione (page/limit + total), filtri (category/tag/date),
  ricerca full-text (param q), slug, is_featured/is_category_pinned, status draft/published.
- categories.php + navigation.php: gerarchia categorie (parent_id, sort_order), menu navigazione.
- tags.php: CRUD tag, relazione con articoli, slug.
- projects.php: CRUD progetti (se non già abbastanza coperto; è "contenuto" anche lui).
- Logica di paginazione/ricerca/ordinamento e la FORMA delle risposte (array nudo vs {data,total}):
  chiudere la mappa del "Double Read" aperta in C3.
SOLO LETTURA sul sito sorgente. Individua prima i file reali con glob/grep su public/api/.

Fai così:
1. Ispeziona in modo microscopico gli endpoint dell'ambito C4 (cita sempre percorso/file:linea).
2. Compila una card seguendo _cantiere-terza-edizione/mappatura/_TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C4-content-apis.md
3. NON sconfinare: backend/db=C1, auth/sessioni=C2, frontend bridge=C3 (già fatti);
   media/upload=C5, editor=C6, SEO=C7, RSS=C8, newsletter=C9, engagement=C11, admin=C12.
   Se trovi roba di altri cluster, annotala solo come puntatore nelle "Note / domande aperte".
   Qui interessa il LATO SERVER dei contenuti (articoli/categorie/tag/navigazione/progetti).
4. NON riportare credenziali/segreti.

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SPW-C4 → ✅)
- aggiungi una riga a _cantiere-terza-edizione/LOG.md
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SPW-C4) e lo stato globale
- git add/commit/push e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: SPW-C5 — Media & Upload
```

### Coda delle unità successive (per orientamento)
SPW-C5 → SPW-C6 → SPW-C7 → SPW-C8 → SPW-C9 → SPW-C11 → SPW-C12 →
poi SitoRuntime (SR-C1…SR-C13) → DISINTELLIGENZA (DIS-*) → FDCA-DIFF → FASE 2 (Sintesi).
