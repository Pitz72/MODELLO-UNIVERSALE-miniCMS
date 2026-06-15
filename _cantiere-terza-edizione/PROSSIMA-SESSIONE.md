# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA sola unità atomica.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.

Stato: SimonePizziWebSite (flagship contenuti) è COMPLETO. Sul secondo sito SitoRuntime è già
fatta SR-C1 (Backend Core). Da questa sessione si prosegue su SitoRuntime con il cluster C2.

Per impostare stile e metodo, leggi DUE card di riferimento:
- _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C1-backend-core.md
  (la card APPENA FATTA sullo stesso sito: ti dà il vocabolario reale di SitoRuntime —
   prelude di bootstrap centralizzato in cors.php, getDB() lazy, auth_utils.php, .env, ecc.
   In SR-C1 cors.php e auth_utils.php sono stati lasciati come PUNTATORI a C2: ora vai a fondo).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C2-security-auth.md
  (è il PARALLELO diretto sull'altro sito: login/logout/recovery+reset, rate limiting su
   login_attempts, getClientIp anti-spoof, gate Auth::check con CSRF Origin/Referer +
   session_version fail-closed, cookie HttpOnly/Secure/SameSite, .htaccess HTTPS/HSTS/CSP).
   Usala per sapere COSA cercare e con che dettaglio, MA ricorda: SitoRuntime è un altro
   codebase, non dare nulla per scontato — leggi i file veri.

Unità di QUESTA sessione (atomica, una sola): SR-C2 — Security & Auth (+ CORS) del sito
SitoRuntime (C:\Users\Utente\Documents\GitHub\SITI-WEB\SitoRuntime).

Ambito C2: autenticazione, sessioni/cookie, CSRF, CORS, hardening HTTP. Individua i FILE veri
in public/api PRIMA con glob/grep. Già intravisti in SR-C1 (verifica e ispeziona a fondo):
- cors.php (allowlist origini https://runtimeradio.com/.it + www, header Access-Control-*,
  X-CSRF-Token, short-circuit OPTIONS 204): è il PRELUDE di bootstrap comune — qui mappane la
  LOGICA di sicurezza CORS per intero.
- auth_utils.php (in SR-C1 visto solo come puntatore: contiene generateCsrfToken() e
  presumibilmente il gate di auth — VERIFICA: come fa login/logout? sessioni PHP native o token?
  c'è un equivalente di Auth::check? CSRF come è validato — header X-CSRF-Token vs Origin/Referer
  di SPW?).
- admin.php (in SR-C1 visto che chiama generateCsrfToken() e auth_utils: è probabilmente l'endpoint
  di login/gestione admin — mappane i rami di autenticazione, NON la logica contenuti/upload che è
  C4/C5/C12 → solo puntatori).
- fix_users_table.php (tocca lo schema users/auth: in C2 interessa SE aggiunge colonne di
  sicurezza tipo rate-limit/lockout; la storia migratoria pura → C13, qui solo il meccanismo auth).
In particolare verifica e confronta con SPW-C2:
- Sessioni: PHP native (session_start) o token? Cookie con HttpOnly/Secure/SameSite? Esiste un
  meccanismo session_version fail-closed come in SPW?
- CSRF: SitoRuntime usa un TOKEN esplicito (generateCsrfToken + header X-CSRF-Token, visto in
  cors.php Access-Control-Allow-Headers) — questa è una DIVERGENZA forte da SPW che usa il
  controllo Origin/Referer. Mappa il ciclo completo: generazione, dove viene memorizzato,
  dove viene validato.
- Rate limiting / brute force: esiste una tabella login_attempts o equivalente? (in SR-C1 lo
  schema init_mysql.php NON aveva login_attempts — verifica se l'auth ha protezione anti-brute-force
  o se è un BUCO da segnalare come GOLD).
- Password admin di default 'runtime2026' hardcoded (già emersa in SR-C1 §4): aggancia qui il
  ponte di sicurezza — è cambiata? c'è un flusso di recovery/reset password come in SPW?
- .htaccess: cerca regole HTTPS/HSTS/CSP/header di sicurezza (in public/ e public/api/). C'è il
  PHP-off sugli upload? (l'hardening HTTP è C2; il PHP-off sugli upload è anche C5 → annota).

Fai così:
1. Ispeziona in modo microscopico i file dell'ambito C2 (cita sempre percorso/file:linea).
2. Compila una card seguendo _cantiere-terza-edizione/mappatura/_TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C2-security-auth.md
3. NON sconfinare: backend core/bootstrap/DB=C1 (già fatto), frontend bridge=C3, contenuti
   (news/speakers/podcasts)=C4, media/upload=C5, SEO+cache=C7, RSS=C8, newsletter=C9,
   admin/dashboard UI=C12, EVOLUZIONE DB & INCIDENTI=C13. Se trovi roba di altri cluster,
   annotala SOLO come puntatore nelle "Note / domande aperte".
   Qui interessa AUTH / SESSIONI / COOKIE / CSRF / CORS / HARDENING HTTP.
4. Sezione §6 (Differenze rispetto agli altri siti): COMPILALA con cura — il confronto con
   SPW-C2 è il vero valore (CSRF a token vs Origin/Referer; presenza/assenza di rate limiting;
   session_version; recovery password; password di default hardcoded).
5. NON riportare credenziali/segreti reali (il .env è gitignorato — non leggerne i valori).

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SR-C2 → ✅)
- aggiungi una riga a _cantiere-terza-edizione/LOG.md (più recente IN BASSO)
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SR-C2) e lo stato globale
- git add/commit/push e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: SR-C3 — Frontend Bridge &
  State del sito SitoRuntime.
