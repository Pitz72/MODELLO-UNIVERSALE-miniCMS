# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA unità. Questa volta è la PENULTIMA card del 3°
> sito: DIS-C12 (Admin Dashboard & Panels) di DISINTELLIGENZA.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.

METODO (ROADMAP §0.1): C12 è il pannello admin, va DA SOLA. Questa sessione = card SINGOLA: DIS-C12.
Dopo resta solo FDCA-DIFF (l'ultima unità, che chiude la FASE 1 di mappatura).

Stato: i PRIMI DUE siti (flagship) COMPLETI; il 3° quasi completo.
- SimonePizziWebSite: COMPLETO (11). SitoRuntime: COMPLETO (10).
- DISINTELLIGENZA (festival, SQLite VIVO): DIS-C1, C2, C4, C5, C9, C10 fatte. 27/~30 card totali.
- Resta: DIS-C12 (questa), poi FDCA-DIFF.

CONTESTO IMPORTANTE: a differenza degli altri cluster di DIS, il LATO SERVER dell'admin è GIÀ stato
mappato sparso nelle altre card (stats.php=DIS-C10, settings.php=DIS-C10, users.php=DIS-C2,
participants.php update_status/update_round=DIS-C10, newsletter.php?send=DIS-C9). Quindi DIS-C12 è
soprattutto il LATO FRONTEND: come la SPA React mette insieme questi endpoint in una dashboard admin.
Bisogna quindi guardare src/ (NON solo public/api/). Confronto chiave: SR-C12 ("la dashboard che non
misura niente", guard-componente, niente AdminLayout/loader) e SPW-C12 (AdminLayout + adminAuthLoader,
dashboard a 3 livelli con Chart.js, backup/analytics).

Unità di QUESTA sessione: DIS-C12 (Admin Dashboard & Panels) del sito DISINTELLIGENZA
(C:\Users\Utente\Documents\GitHub\SITI-WEB\DISINTELLIGENZA). UNA card.

Ambito DIS-C12 (Admin Dashboard & Panels):
- src/ — trovare il componente Admin/Dashboard e i pannelli: come si fa il guard (componente che
  controlla check_auth on mount, come SR? o loader/route guard, come SPW? o niente?). Cercare in
  src/pages, src/components, App routing (vite + react-router?).
- La DASHBOARD: cosa mostra? stats.php fornisce participants_count/votes_count/top_voted/
  latest_participants/storage_breakdown → c'è un cruscotto con grafici? contatori? o solo navigazione
  (come SR)? È "una dashboard che misura" (≠ SR) grazie a stats.php?
- I PANNELLI admin del festival: gestione partecipanti (lista, approva/rifiuta, toggle round),
  master switch (settings: voting/registration active+period), compositore newsletter (send + selezione
  articoli), inbox contatti (lettura tabella contacts — c'è un endpoint GET per leggerli? verificare:
  in DIS-C9 contact.php fa solo POST, manca un read!), gestione utenti.
- COERENZA col backend già mappato: collegare ogni pannello UI al suo endpoint (participants.php,
  settings.php, newsletter.php, users.php, stats.php).
- NON sconfinare: logica festival=C10 (fatto), auth=C2 (fatto), email=C9 (fatto), upload=C5, content=C4.
  Qui si mappa la PRESENTAZIONE/orchestrazione admin, non la logica di dominio.

Fai così:
1. Ispeziona src/ in modo microscopico (cita sempre percorso/file:linea). Parti da App/routing e dal
   componente admin.
2. Compila UNA card in
   _cantiere-terza-edizione/mappatura/DISINTELLIGENZA/DIS-C12-admin-dashboard.md
3. §6: confronto a TRE — DIS-C12 vs SR-C12 (console CRUD senza metriche, guard-componente) e SPW-C12
   (cruscotto analitico, AdminLayout+loader, backup). Dove sta DIS? Ha stats.php → forse una via di
   mezzo (qualche metrica ma niente Chart.js/analytics/backup-cron?).
4. Verifica il buco emerso in DIS-C9: i `contacts` si possono LEGGERE da admin? (contact.php è
   solo-POST). Se non c'è un read, è un dato raccolto e mai mostrato → GOLD.
5. Puntatori per FDCA-DIFF.

Criterio di STOP: card in stato COMPLETATO.

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (DIS-C12 → ✅, DISINTELLIGENZA COMPLETO)
- aggiungi UNA riga a _cantiere-terza-edizione/LOG.md (più recente IN BASSO)
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta DIS-C12, aggiorna stato globale)
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con l'ULTIMA unità: FDCA-DIFF (differenze del fork FDCA
  vs DISINTELLIGENZA: cosa è cambiato), che chiude la FASE 1 di mappatura.
