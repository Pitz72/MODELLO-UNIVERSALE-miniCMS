# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA unità (da 2026-06-15: può essere una COPPIA
> accorpata di cluster accoppiati — vedi ROADMAP §0.1). Questa volta è una card SINGOLA — DIS-C2,
> alto valore (auth + anti-frode voto), il 2° passo del 3° sito DISINTELLIGENZA.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.

METODO (ROADMAP §0.1): si accorpano nella stessa sessione SOLO coppie di cluster già accoppiati. Per
DISINTELLIGENZA, dopo aver visto la geografia in DIS-C1, la proposta è: **C2 DA SOLA** (è alto valore
— auth + anti-frode voto), poi valutare la coppia C4+C9 e tenere C10 (festival logic) da sola. Quindi
questa sessione è una card SINGOLA: DIS-C2.

Stato: i PRIMI DUE siti (i due flagship) sono COMPLETI; il 3° è APERTO.
- SimonePizziWebSite (flagship contenuti): COMPLETO (11 card).
- SitoRuntime (flagship scalabilità + incidenti): COMPLETO (10 card).
- DISINTELLIGENZA (base festival, SQLite VIVO): DIS-C1 fatta. 22/~30 card totali.

CONTESTO da DIS-C1 (leggi la card _cantiere-terza-edizione/mappatura/DISINTELLIGENZA/DIS-C1-backend-core.md):
DISINTELLIGENZA gira su SQLite vivo, PHP puro, bootstrap inline minimale (no cors.php, no auth_helper
centralizzato), `session_start()` a mano in ogni endpoint. DIS-C1 ha lasciato APERTI per C2 tre fili
precisi che vanno chiusi qui:
1. DOVE viene creato l'utente admin? init_db.php lo OMETTE (commento "[Admin creation ignored for
   brevity in repl]", :85). Cercare se c'è un hardcoded di default (come SR `runtime2026`) o se è
   creato a mano nel .sqlite.
2. Gli script update_db_* sono per lo più NON protetti (solo security_move=admin, v0.5.4=login) ed
   eseguibili in HTTP; il .htaccess di public/ NON li nega (vs deny by-prefix di SR-C2). Valutare il
   rischio in chiave sicurezza.
3. Schema tab. `votes` (init_db.php:62-70): session_id + ip_address + user_agent → è l'impianto
   anti-doppio-voto. Confrontare con il voter_hash SHA256 di SPW-C11 e con l'anti-frode di SR-C2.

Unità di QUESTA sessione: DIS-C2 (Security & Auth + anti-frode voto) del sito DISINTELLIGENZA
(C:\Users\Utente\Documents\GitHub\SITI-WEB\DISINTELLIGENZA). UNA card.

Ambito DIS-C2 (Security & Auth + anti-frode voto):
- public/api/auth.php (login/logout/check: già visto il login a password_verify + $_SESSION
  user_id/username/role; mappare logout, eventuale recovery/reset, gestione sessione).
- public/api/users.php (gestione utenti admin/editor: CRUD, ruoli, eventuale creazione admin =
  risposta al filo #1 di sopra).
- Meccanica di sessione: session_start() per-endpoint, gate $_SESSION['role'] admin/editor (come
  appare in news.php:17, update_db_security_move.php:8, v0.5.4:8). C'è un cookie config? SameSite/
  Secure/HttpOnly? session_regenerate_id anti-fixation? CSRF (token? Origin/Referer? — in DIS-C1 NON
  ho visto né cors.php né header CSRF)?
- Anti-frode VOTO: la parte di auth/identità del voto (session_id/ip/user_agent in `votes`), rate
  limiting, dedup. NB: la LOGICA festival completa (conteggi, round, master switch) è C10 — qui solo
  l'aspetto sicurezza/identità/anti-abuso del voto.
- .htaccess (public/): già mappato il deny di *.sqlite/*.bak e il routing SEO; qui interessa la
  parte sicurezza (manca HSTS/CSP/redirect HTTPS? manca il deny degli script update_db_*?).
- NON sconfinare: bootstrap/db=C1 (fatto), content/news=C4, media=C5, newsletter/contact=C9, festival
  logic conteggi/round/settings=C10, admin dashboard=C12, feed/podcast=C8.

Fai così:
1. Ispeziona in modo microscopico i file di C2 (cita sempre percorso/file:linea).
2. Compila UNA card seguendo _TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/DISINTELLIGENZA/DIS-C2-security-auth.md
3. §6: confronto a TRE — DIS-C2 vs SPW-C2 e SR-C2 (auth + sessioni + CSRF + rate-limit). Asse chiave:
   quanto si può togliere alla sicurezza quando il sito è piccolo e same-origin (DIS sembra il più
   spoglio: nessun CSRF token visto, cookie di default). Riusa anche SPW-C11 per il confronto
   anti-doppio-voto (voter_hash) e SR-C2 per il rate-limit file-based.
4. Chiudi i 3 fili lasciati aperti da DIS-C1 (admin creation, script non protetti, schema votes).
5. Lascia puntatori nelle "Note / domande aperte" per C4/C5/C9/C10/C12.

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (DIS-C2 → ✅)
- aggiungi UNA riga a _cantiere-terza-edizione/LOG.md (più recente IN BASSO — attento all'ordine cronologico)
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta DIS-C2, aggiorna stato globale)
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: verosimilmente la coppia
  DIS-C4+DIS-C9 (Content/news + Newsletter/contact), oppure DIS-C10 (Festival Logic) da sola se in
  C2 emerge che il voto merita una card dedicata tutta sua.
