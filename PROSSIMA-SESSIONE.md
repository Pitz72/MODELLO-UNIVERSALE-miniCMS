# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA unità (da 2026-06-15: può essere una COPPIA
> accorpata di cluster accoppiati — vedi ROADMAP §0.1). Questa volta è una card SINGOLA.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.

METODO (ROADMAP §0.1): si accorpano nella stessa sessione SOLO coppie di cluster già accoppiati. Per
SitoRuntime le coppie erano C4+C5 (fatta) e C7+C8 (fatta); C9 (fatta), C12, C13 restano DA SOLE. Questa
sessione è SR-C12 (Admin Dashboard & Panels) DA SOLA: UNA sola card.

Stato: SimonePizziWebSite (flagship contenuti) è COMPLETO. Su SitoRuntime sono fatte SR-C1 (Backend
Core), SR-C2 (Security & Auth + CORS), SR-C3 (Frontend Bridge & State), la coppia SR-C4 (Content APIs)
+ SR-C5 (Media & Upload), la coppia SR-C7 (SEO/seo-cache) + SR-C8 (RSS & Feed) e SR-C9 (Newsletter &
Email). Da questa sessione si prosegue con SR-C12 — Admin Dashboard & Panels. Resta poi SR-C13 (DB
Evolution & Incidenti), da sola → SitoRuntime si chiude in 2 sessioni / 2 card.

Per impostare stile e metodo, leggi le card di riferimento:
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C12-admin.md (parallelo C12: stats.php
  contatori "cifre tonde" con fallback-0 try/catch; analytics.php motore a DOPPIA PERSONALITÀ — POST
  tracking pubblico anonimo (view dedup IP-giorno, click rate-limit) vs GET gated con ~20 aggregazioni,
  CONSUMER delle reazioni di C11; settings.php gated-al-top tabella chiave/valore app_settings +
  cambio password PUT con session_version++; backup.php router ?action= con backup FUORI docroot +
  nome random_bytes + chmod 0600 + rotazione + pseudo-cron timing-safe hash_equals; route guard UNICO
  adminAuthLoader su AdminLayout copre tutte le rotte figlie; Dashboard 3 livelli densità con Chart.js +
  degradazione graziosa; GOLD: backup automatico fuori docroot perché clean-dist strippa .data/).
- _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C9-newsletter-email.md (la card appena fatta:
  EMERSO che admin.php è il MEGA-ROUTER del sito — un solo file con login/logout/check_auth/
  change_password (C2), CRUD news list/get/save/delete (C4), helper WebP + optimize_webp/fix_image_paths
  (C5), apply_v293_newsletter + test_smtp (C9). In SR-C12 va mappato admin.php COME PANNELLO/DASHBOARD:
  quali action sono PROPRIE di C12 — stats/contatori, settings, eventuale backup/export, analytics/tracking.
  ATTENZIONE a NON rimappare ciò che è già C2/C4/C5/C9: qui solo la UX admin, le dashboard, gli
  aggregati/statistiche, il backup, le impostazioni).
- (facoltativo) SR-C2 per il gate isLoggedIn/isAdmin/role e la meccanica CSRF; SR-C4 §8 per i puntatori
  ad admin.php già annotati; SR-C3 per Admin.tsx come guard-COMPONENTE (checkAuth on mount, NO loader).

Unità di QUESTA sessione: SR-C12 (Admin Dashboard & Panels) del sito SitoRuntime
(C:\Users\Utente\Documents\GitHub\SITI-WEB\SitoRuntime). UNA card.

Ambito SR-C12 (Admin Dashboard & Panels):
- admin.php COME hub admin: quali action sono PROPRIE di C12 (stats/contatori, dashboard, settings/
  impostazioni, backup/export, analytics/tracking)? Marca cosa è C12 e cosa è puntatore (auth=C2,
  news CRUD=C4, upload/WebP=C5, newsletter/test_smtp=C9).
- esiste un stats.php / analytics.php / settings.php / backup.php SEPARATO come in SPW, oppure tutto è
  dentro admin.php?action= (filosofia "mega-router" di SR)? Verifica con grep.
- Admin.tsx (src/pages/Admin.tsx): guard-COMPONENTE (checkAuth on mount → LoginForm se !user, SR-C3) +
  dashboard. Quali pannelli/tab monta? (news, speakers, podcasts, media, newsletter, feed, settings?)
  Layout, densità, UX, degradazione graziosa, eventuale Chart.js o equivalente.
- c'è tracking analytics (view/click) o statistiche di traffico? backup del DB? export? impostazioni
  sito (chiave/valore)? cambio password admin (meccanica già C2, qui come UX del pannello)?
- pseudo-cron / manutenzione schedulata (in SPW backup.php aveva un cron gated)? In SR esiste?

Fai così:
1. Ispeziona in modo microscopico i file/azioni di C12 (cita sempre percorso/file:linea).
2. Compila UNA card seguendo _TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C12-admin.md
3. NON sconfinare: core/DB=C1, security/CORS/rate-limit-meccanica/auth=C2, frontend/client=C3,
   content/slug=C4, media/upload=C5, editor/sanitizzazione-render=C6, SEO/seo-cache=C7, RSS/feed=C8,
   newsletter/email=C9 (fatto), EVOLUZIONE DB & INCIDENTI=C13. Puntatori nelle "Note / domande aperte".
4. §6: confronto con SPW-C12 (route guard unico adminAuthLoader vs guard-COMPONENTE; stats/analytics/
   settings/backup in file SEPARATI vs tutto in admin.php?action=; backup fuori-docroot + pseudo-cron di
   SPW — esistono in SR?; settings chiave/valore; Chart.js / densità dashboard). Evidenzia la filosofia
   "mega-router admin.php" di SR vs i file separati di SPW.

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SR-C12 → ✅)
- aggiungi UNA riga a _cantiere-terza-edizione/LOG.md (più recente IN BASSO — attento all'ordine cronologico)
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SR-C12) e lo stato globale
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: SR-C13 (DB Evolution & Incidenti)
  del sito SitoRuntime, DA SOLA — è l'ULTIMA card di SitoRuntime, alto valore (incidenti MySQL/WAL/
  emergency revert, migrazioni storiche, i TRE schemi subscribers divergenti emersi in C9).
