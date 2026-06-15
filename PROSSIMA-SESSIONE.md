# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA sola unità atomica.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.
Leggi anche le card già fatte rilevanti per C12 (contesto indispensabile):
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C1-backend-core.md
  (singleton PDO Database::connect(), timezone Europe/Rome, struttura public/api).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C2-security-auth.md
  (Auth::check gate, CSRF Origin/Referer, session_version fail-closed, cookie HttpOnly/Secure;
   ATTENZIONE C12: ogni endpoint admin/dashboard deve aprire con Auth::check — verifica i gate).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C3-frontend-bridge.md
  (loaders.ts route guard adminAuthLoader→redirect login; AdminLayout; api.ts client unico).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C11-engagement-social.md
  (Dashboard.tsx/AdminLayout.tsx referenziano i conteggi messaggi non letti; analytics.php aggrega
   article_reactions — entrambi pointer ESPLICITI verso C12: chiudere qui).

Unità di QUESTA sessione (atomica, una sola): SPW-C12 — Admin Dashboard & Panels
del sito SimonePizziWebSite
(C:\Users\Utente\Documents\GitHub\SITI-WEB\SimonePizziWebSite).
È l'ULTIMA card di SimonePizziWebSite: alla chiusura il flagship contenuti è mappato per intero.

Ambito C12: il "cervello" lato admin — dashboard, statistiche/analytics, impostazioni, backup,
manutenzione DB, e l'impalcatura UX dell'area riservata. In particolare:
- Endpoint reali (individua i FILE veri in public/api PRIMA con glob/grep):
  analytics.php, stats.php, settings.php, backup.php, optimize_db.php (già intravisti).
  Verifica: ognuno apre con Auth::check? quali dati aggregano? backup espone dump scaricabili
  (rischio se non gated/path-guarded)? optimize_db fa operazioni distruttive (TRUNCATE/OPTIMIZE)?
- analytics.php: cosa misura (incrocia con C11: total_reactions, top_articles_by_reactions,
  reactions_by_type) — è il consumer delle reazioni mappate in C11.
- settings.php: chiavi di configurazione runtime (es. i "TODO settings" del channel RSS visti in C8,
  title/description hardcoded) — esiste una tabella settings? si legge/scrive da qui?
- Lato client/admin (src/pages/admin/): AdminLayout.tsx (shell/nav/guard), Dashboard.tsx (widget,
  conteggi, badge messaggi non letti), pannelli stats/settings/backup. Verifica route guard
  adminAuthLoader (C3) e i falsi positivi come in C8/C9/C11.
Individua prima i file reali con glob/grep.

Fai così:
1. Ispeziona in modo microscopico i file dell'ambito C12 (cita sempre percorso/file:linea).
2. Compila una card seguendo _cantiere-terza-edizione/mappatura/_TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C12-admin-dashboard.md
3. NON sconfinare: backend/db=C1, auth=C2, frontend bridge=C3, contenuti=C4, media=C5,
   editor=C6, SEO=C7, RSS=C8, newsletter=C9, engagement=C11 (tutti già fatti).
   Se trovi roba di altri cluster, annotala solo come puntatore nelle "Note / domande aperte".
   Qui interessa ADMIN/DASHBOARD/STATS/SETTINGS/BACKUP/manutenzione.
4. Follow-up sicurezza: ogni endpoint admin è gated da Auth::check? backup.php espone file
   scaricabili senza gate o con path traversal? optimize_db.php fa operazioni distruttive
   raggiungibili pubblicamente? (parallelo ai gate verificati in C4/C9/C11).
5. NON riportare credenziali/segreti.

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SPW-C12 → ✅)
- aggiungi una riga a _cantiere-terza-edizione/LOG.md (più recente in basso)
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SPW-C12) e lo stato globale
  (segnala: SimonePizziWebSite COMPLETO, prossimo sito = SitoRuntime)
- git add/commit/push e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: SR-C1 — Backend Core & Bootstrap
  del sito SitoRuntime (C:\Users\Utente\Documents\GitHub\SITI-WEB\SitoRuntime; flagship scalabilità).
