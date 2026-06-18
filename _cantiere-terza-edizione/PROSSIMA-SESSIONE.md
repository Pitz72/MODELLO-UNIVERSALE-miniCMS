# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟨 FASE 2 (SINTESI) avviata. S1-C1 (Backend Core) ✅ COMPLETATA. Questa è la SECONDA scheda di
> sintesi: **S1-C2 Security & Auth**. Ordine confermato: S1 → S2 → S3 → S4 (nessuna deviazione).

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md, _cantiere-terza-edizione/LOG.md e
_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md per il contesto.

STATO: FASE 1 (mappatura) CONCLUSA — 4 siti, 34 card, copertura COMPLETA. FASE 2 (SINTESI) in corso:
**1/14 schede S1 completate** (S1-C1 Backend Core ✅). Metodo: UNA scheda tematica cross-sito per
sessione, che fonde i 2-3 trattamenti per-sito di un cluster in UNA visione comparata (pattern comune
+ varianti per sito in tabella unica + GOLD + mappa→capitoli). Le fonti sono le card di mappatura
(specialmente i loro §6, già a confronto). NON si rilegge il codice sorgente: si consolida ciò che è
già mappato. Il template è `_cantiere-terza-edizione/sintesi/_TEMPLATE-SCHEDA.md`; il modello già
fatto è `S1-C1-backend-core.md` (seguine struttura e livello di dettaglio).

UNITÀ DI QUESTA SESSIONE: **S1-C2 — Scheda tematica cross-sito "Security & Auth"**.
Fonti primarie: SPW-C2, SR-C2, DIS-C2. Fonti di supporto: SPW-C11 (voter_hash SHA256, rate-limit a
due strati), DIS-C2/DIS-C10 (anti-frode voto). Da consolidare (spunti dai §6 già scritti):
- **Sessione & cookie:** hardening centralizzato HttpOnly/Secure/SameSite (SPW) · HttpOnly+SameSite
  Strict ma SENZA Secure (SR) · cookie php.ini DEFAULT, zero hardening (DIS). session_version
  fail-closed (SPW) vs assente (SR/DIS).
- **CSRF:** Origin/Referer check (SPW) · token sincronizzato X-CSRF-Token + hash_equals (SR) ·
  NESSUN CSRF (DIS) → la scala "tre gradini di difesa CSRF".
- **Rate-limit login / brute-force:** tabella `login_attempts` riusata (SPW) · file-based
  `.cache/ratelimit/<md5(ip)>.json` 5/15min + sleep (SR) · NIENTE (DIS).
- **Anti-spoofing IP:** getClientIp anti-XFF (SPW) vs X-Forwarded-For grezzo bypassabile (SR) vs
  REMOTE_ADDR grezzo — che in DIS-C2 è un PREGIO per l'anti-frode voto (non spoofabile).
- **Recovery/reset password:** presente (SPW, password_resets) vs assente (SR/DIS).
- **`.htaccess`:** HTTPS/HSTS/CSP + PHP-off uploads (SPW) · HSTS/CSP/X-Frame DENY + deny by-prefix
  script manutenzione, ma NO redirect 301 HTTPS (SR) · deny solo *.sqlite/*.bak, script update_db_*
  NON protetti (DIS).
- **Gate componibile:** Auth::check per-endpoint (SPW) · isLoggedIn()/isAdmin() (SR) · gate
  $_SESSION['role'] a mano, spesso solo isset(user_id) non isAdmin (DIS, incoerente → editor può
  agire).
- **GOLD anti-frode voto (DIS):** master switch difensivo '1'||'true', barriera IP/24h reale,
  IP+UA in chiaro (privacy ≠ voter_hash di SPW-C11), CSRF assente su reset_* = catastrofe a un clic.
- **Credenziali default** (ponte da S1-C1): random / hardcoded runtime2026 / omessa — qui si chiude
  il box iniziato in S1-C1.
- **FDCA:** backend byte-identico a DIS → eredita auth grado-zero immutata (caso forking).

Fai così:
1. Scrivi la scheda in `_cantiere-terza-edizione/sintesi/S1-C2-security-auth.md` seguendo
   `_TEMPLATE-SCHEDA.md` (0 una-frase · 1 pattern comune · 2 tabella varianti UNICA e deduplicata · 3
   GOLD/box · 4 mappa→capitoli · 5 scarti/dedup). La tabella comparativa va scritta UNA volta, pulita.
2. Mappa esplicitamente → capitoli esistenti: soprattutto **CAP 10 (Security & Auth)**, con ponti a
   CAP 13 (Newsletter, rate-limit/mail), CAP 11 (SEO, .htaccess), CAP 17 (Votazioni & anti-frode).
   Segnala eventuali CORREZIONI al testo attuale (come fatto per CAP 3 in S1-C1).
3. Aggiorna `_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md` (S1-C2 → ✅, contatore 2/14).

Criterio di STOP: scheda S1-C2 in stato COMPLETATO (pattern + varianti + GOLD + mappa capitolo).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna `_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md` (S1-C2 → ✅)
- aggiorna `_cantiere-terza-edizione/ROADMAP.md` (spunta S1-C2 in §4, aggiorna §7 stato globale)
- aggiungi UNA riga a `_cantiere-terza-edizione/LOG.md` (più recente IN BASSO)
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md, sia root sia in _cantiere-terza-edizione/) con la
  prossima scheda: **S1-C3 (Frontend Bridge & State)** — fonti SPW-C3, SR-C3, DIS-C3 (pattern api.ts:
  Double Read SPW / token-CSRF in-memory SR / codemod fix_api DIS).
