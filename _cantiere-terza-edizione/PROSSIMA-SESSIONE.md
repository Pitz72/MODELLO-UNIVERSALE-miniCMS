# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA unità (da 2026-06-15: può essere una COPPIA
> accorpata di cluster accoppiati — vedi ROADMAP §0.1). Questa volta è una card SINGOLA — l'ULTIMA di SitoRuntime.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.

METODO (ROADMAP §0.1): si accorpano nella stessa sessione SOLO coppie di cluster già accoppiati. Per
SitoRuntime le coppie erano C4+C5 (fatta) e C7+C8 (fatta); C9 (fatta), C12 (fatta) e C13 sono DA SOLE.
Questa sessione è SR-C13 (DB Evolution & Incidenti) DA SOLA: UNA sola card. È l'ULTIMA card di SitoRuntime
e ha ALTO VALORE — è il cuore del ruolo del sito nel manuale ("flagship scalabilità + problemi/soluzioni").

Stato: SimonePizziWebSite (flagship contenuti) è COMPLETO. Su SitoRuntime sono fatte SR-C1 (Backend
Core), SR-C2 (Security & Auth + CORS), SR-C3 (Frontend Bridge & State), la coppia SR-C4 (Content APIs)
+ SR-C5 (Media & Upload), la coppia SR-C7 (SEO/seo-cache) + SR-C8 (RSS & Feed), SR-C9 (Newsletter &
Email) e SR-C12 (Admin Dashboard & Panels). Con SR-C13 SitoRuntime SI CHIUDE (10 card) e si passa al 3°
sito DISINTELLIGENZA (base festival).

Per impostare stile e metodo, ricorda l'altissima densità delle card già fatte e il ricco materiale
"incidenti" già emerso lungo tutta la mappatura di SitoRuntime. Leggi in particolare:
- _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C1-backend-core.md (db.php singleton MySQL, init_mysql.php
  schema dedicato, migrate_*/fix_* micro-migrazioni, init_db.php fossile SQLite, incidente fuso/formato-data in
  debug_time.php — molti puntatori "→C13" partono da qui).
- _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C9-newsletter-email.md (i TRE schemi subscribers
  divergenti: init_mysql base 4 col / fix_newsletter_table.php fossile SQLite rotto su MySQL / apply_v293
  self-healing in admin.php — ponte C13 esplicito) e SR-C5 (storia migratoria raster→WebP: optimize_webp/
  fix_image_paths, ponte C13) e SR-C12 (l'ASSENZA di backup/cron: il flagship degli incidenti ha la cura
  emergency_revert_wal ma non la prevenzione — da raccontare in C13).
- (facoltativo) SPW non ha una card C13 equivalente (in SPW gli incidenti erano sparsi); qui SR-C13 è
  un capitolo a sé. Per il §6 il confronto è più "SR vs sé stesso nel tempo" che SR vs SPW.

Unità di QUESTA sessione: SR-C13 (DB Evolution & Incidenti) del sito SitoRuntime
(C:\Users\Utente\Documents\GitHub\SITI-WEB\SitoRuntime). UNA card. ULTIMA di SitoRuntime.

Ambito SR-C13 (DB Evolution & Incidenti):
- migrazione SQLite→MySQL: migrate_to_mysql.php (come copia i dati, COUNT di verifica, gestione errori),
  init_mysql.php (schema di destinazione), init_db.php (il fossile SQLite con seed 24 speaker), fix_users_table.php
  (fossile). Racconta l'evoluzione DB storica.
- INCIDENTI veri: emergency_revert_wal.php (cos'è il WAL, perché un emergency revert, cosa ripristina),
  migrate_status.php, debug_time.php (l'incidente fuso/formato-data separatore 'T' vs spazio già emerso in
  C1/C4), eventuali altri debug_*/test_*.php. Ispeziona ogni file e cita file:linea.
- le micro-migrazioni idempotenti come pattern: apply_v291_status (news.status), apply_v293_newsletter
  (double opt-in), setup_podcasts.php — la filosofia "ALTER TABLE ADD COLUMN con skip su Duplicate column"
  e "self-healing dentro admin.php" vs "script one-shot da cancellare".
- i TRE schemi subscribers divergenti (da SR-C9): consolidali qui come caso-studio "la tabella che nessuno
  crea due volte uguale".
- l'ASSENZA di backup/cron emersa in SR-C12: incidente latente (cura senza prevenzione).
- archeologia: file fossili SQLite rimasti nel repo MySQL (init_db.php, fix_users_table.php,
  fix_newsletter_table.php), gated .htaccess by-prefix (debug_/migrate_/fix_/init_).

Fai così:
1. Ispeziona in modo microscopico i file di C13 (cita sempre percorso/file:linea).
2. Compila UNA card seguendo _TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C13-db-evolution-incidenti.md
3. NON sconfinare: core/DB-bootstrap=C1 (qui solo l'EVOLUZIONE e gli incidenti, non il singleton in sé),
   security/CORS/auth=C2, frontend=C3, content/slug=C4, media/upload=C5, SEO=C7, RSS=C8, newsletter=C9,
   admin UI=C12. Puntatori nelle "Note / domande aperte". Consolida QUI i ponti "→C13" lasciati dalle altre card.
4. §6: qui il confronto è soprattutto storico/interno (SR oggi vs SR nelle migrazioni passate) + nota su
   come SPW gestiva gli incidenti in modo sparso (niente card C13 dedicata) vs SR che li concentra.

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SR-C13 → ✅, segna SitoRuntime COMPLETO)
- aggiungi UNA riga a _cantiere-terza-edizione/LOG.md (più recente IN BASSO — attento all'ordine cronologico)
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SR-C13, segna SitoRuntime COMPLETO, aggiorna stato globale)
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: la PRIMA card di DISINTELLIGENZA
  (festival, SQLite) — verosimilmente DIS-C1 (Backend Core & Bootstrap), DA SOLA. Apri così il 3° sito.
