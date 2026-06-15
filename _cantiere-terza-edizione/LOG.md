# LOG LAVORI — Terza Edizione

> Registro cronologico, una riga per step. In coda alla lista (più recente in basso).
> Formato: `AAAA-MM-GG · [FASE/UNITÀ] · cosa fatto · commit`

- 2026-06-15 · [FASE 0] · Recupero corruzione "Seconda Edizione" + integrazione Cap 19 + merge PR #1 remota (restauro locale completo come fonte di verità) · `c75ea67`
- 2026-06-15 · [FASE 0] · Impianto Terza Edizione: cartella `_cantiere-terza-edizione/`, ROADMAP, LOG, template mappatura, indice mappatura, prompt prossima sessione · `e7a5b83`
- 2026-06-15 · [FASE 1 / SPW-C1] · Mappatura Backend Core & Bootstrap di SimonePizziWebSite (db.php singleton PDO, config/config.example, timezone Europe/Rome, schema MySQL via migrate_to_mysql.php, caso init_db.php fossile SQLite). Card COMPLETATO · _(commit in corso)_
- 2026-06-15 · [FASE 1 / SPW-C2] · Mappatura Security & Auth di SimonePizziWebSite (auth.php login/logout/recovery+reset, rate limiting login_attempts riusata, getClientIp anti-spoof; auth_helper.php gate Auth::check con CSRF Origin/Referer + session_version fail-closed; cookie HttpOnly/Secure/SameSite centralizzati v1.19.0; .htaccess HTTPS/HSTS/CSP + PHP-off uploads; password_resets schema sparito con migration cancellate). Card COMPLETATO · _(commit in corso)_
