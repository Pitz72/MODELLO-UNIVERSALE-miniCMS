# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟨 FASE 2 (SINTESI) in corso. S1-C1 → S1-C8 ✅ COMPLETATE (8/14). S1-C6 ed S1-C7 erano state
> accorpate in una sessione; S1-C8 è stata fatta SOLA. Questa è la NONA scheda di sintesi:
> **S1-C9 Newsletter & Email**. Ordine confermato: S1 → S2 → S3 → S4 (nessuna deviazione).

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md, _cantiere-terza-edizione/LOG.md e
_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md per il contesto.

STATO: FASE 1 (mappatura) CONCLUSA — 4 siti, 34 card, copertura COMPLETA. FASE 2 (SINTESI) in corso:
**8/14 schede S1 completate** (S1-C1 Backend Core ✅, S1-C2 Security & Auth ✅, S1-C3 Frontend Bridge
✅, S1-C4 Content APIs ✅, S1-C5 Media & Upload ✅, S1-C6 Editor ✅, S1-C7 SEO & Prerendering ✅,
S1-C8 RSS & Feed ✅). Metodo: UNA scheda tematica cross-sito per sessione (eccezionalmente DUE se unite
da un filo, come C6+C7). Fonde i 2-3 trattamenti per-sito di un cluster in UNA visione comparata (pattern
comune + varianti per sito in tabella unica + GOLD + mappa→capitoli). Fonti = card di mappatura
(specialmente i §6). NON si rilegge il codice sorgente. Template:
`_cantiere-terza-edizione/sintesi/_TEMPLATE-SCHEDA.md`; modelli già fatti: `S1-C1` … `S1-C8` (seguine
struttura e livello di dettaglio).

UNITÀ DI QUESTA SESSIONE: **S1-C9 — Scheda tematica cross-sito "Newsletter & Email"**.
Fonti primarie: SPW-C9, SR-C9, DIS-C9. Da consolidare (spunti dai §6 e dal LOG già scritti):
- **CHIUDE DEFINITIVAMENTE il "quadro dei 4 emettitori del content"** (DOMPurify render / strip_tags-
  allowlist prerender / feed sottrazione|escape / **newsletter = QUESTA scheda**). La newsletter è
  l'ULTIMO/4° emettitore. Tesi per-sito: **SPW** = la newsletter è il MENO sanitizzato dei 4 (body grezzo
  via buildNewsletterHtml ZERO sanitizzazione) MA NON emette articles.content (solo title/excerpt/cover) e
  i due punti d'iniezione stanno dietro Auth::check, unico input pubblico (name in conferma) escapato →
  ponte chiuso a rischio basso; **SR** = newsletter PIÙ sicura dei 4 (SELECT senza content :306 +
  htmlspecialchars su tutto, sottrazione+escape, speculare-opposto a SPW); **DIS** = newsletter sicura per
  escape (news htmlspecialchars, non emette content) ma il sistema email il PIÙ GREZZO.
- **Scala a 3 gradini "quanto puoi semplificare un sistema di posta":** SPW (double opt-in con
  confirm_token monouso + unsubscribe_token stabile random_bytes(32) + rate-limit per-IP che RICICLA
  login_attempts di C2 anti-mail-bombing) → SR (PHPMailer/SMTP STARTTLS, primo uso reale di lib/ vendored;
  UN SOLO confirmation_token che fa conferma E disiscrizione, mai azzerato, senza TTL; rate-limit ASSENTE
  sulla subscribe = mail-bombing pur avendo .cache/ratelimit) → DIS (mail() NATIVA, NESSUN double opt-in
  = iscrizione di terzi, NESSUN token disiscrizione = forgeable+GET-prefetchabile, invio sincrono nudo,
  email HEADER INJECTION via name nel Subject contact).
- **Trasporto:** SPW mail() nativa · SR PHPMailer/SMTP (ma contact.php usa mail() → DUE trasporti
  coesistono) · DIS mail() nativa duplicata per file. Deliverability (no SPF/DKIM con mail(), From "Fake
  domain?" DIS).
- **GOLD trasversali:** (1) invio SINCRONO foreach mail()/SMTP senza coda/throttle in tutti e tre
  (gemello del WebP sincrono S1-C5) — SPW nessun throttle, SR usleep ogni 10+try/catch per-destinatario
  (il migliore), DIS nudo (recipients_count = tentativi non successi); (2) rate-limit anti-mail-bombing
  (SPW ricicla login_attempts / SR assente / DIS assente); (3) double opt-in a 3 gradini (SPW pieno / SR
  un-token-per-tutto / DIS assente); (4) unsubscribe (token stabile SPW / stesso token SR / sola-email
  forgeable DIS) + GET prefetch-able senza conferma in tutti; (5) confirm_token senza TTL nonostante
  claim "il link scade" (SPW E SR = stesso fossile di promessa); (6) header injection via name (DIS);
  (7) storicizzazione campagne (newsletter_campaigns solo DIS); (8) consenso/GDPR (doppio checkbox SPW /
  singolo SR / implicito all'approvazione festival DIS, ponte C10).
- **Ponte Telegram (da S1-C1/C8):** in SR il TELEGRAM_BOT_TOKEN è fossile e il feed_config.php di S1-C8
  ne era il relitto; in C9 verificare se Telegram entra davvero nell'invio (probabilmente no — bot manuale
  via copia-URL). Chiude il filo Telegram-fossile.

Fai così:
1. Scrivi la scheda in `_cantiere-terza-edizione/sintesi/S1-C9-newsletter-email.md` seguendo
   `_TEMPLATE-SCHEDA.md` (0 una-frase · 1 pattern comune · 2 tabella varianti UNICA e deduplicata · 3
   GOLD/box · 4 mappa→capitoli · 5 scarti/dedup). COMPLETA esplicitamente la "mappa dei 4 emettitori del
   content" come tabella/box riassuntivo, marcando che con la newsletter il quadro è CHIUSO (riprendi la
   tabella del §3 di S1-C8 e riempi la riga 4 per ciascun sito) — è il valore trasversale di questa scheda.
2. Mappa esplicitamente → capitoli esistenti: soprattutto **CAP 13 (Newsletter & Email System)**, con
   ponti a CAP 8/11/12 (gli altri 3 emettitori del content), CAP 10 (rate-limit/header-injection/CSRF,
   il riciclo di login_attempts), CAP 9 (consenso/GDPR), CAP 16-18 (consenso implicito festival DIS).
   Segnala eventuali CORREZIONI al testo attuale (come fatto per CAP 3/10/6/9/7/8/11/12 nelle schede
   precedenti).
3. Aggiorna `_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md` (S1-C9 → ✅, contatore 9/14).

Criterio di STOP: scheda S1-C9 in stato COMPLETATO (pattern + varianti + GOLD + mappa capitolo + quadro
4 emettitori CHIUSO).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna `_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md` (S1-C9 → ✅)
- aggiorna `_cantiere-terza-edizione/ROADMAP.md` (spunta S1-C9 in §4, aggiorna §7 stato globale)
- aggiungi UNA riga a `_cantiere-terza-edizione/LOG.md` (più recente IN BASSO)
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md, sia root sia in _cantiere-terza-edizione/) con la
  prossima scheda: **S1-C10 (Festival Logic)** — fonte DIS-C10 (solo DIS; FDCA eredita). Scheda
  particolare (un solo sito): macchina a stati iscrizione→selezione→voto→reset, round manuali via flag
  in_current_round, vote_count denormalizzato, master switch pubblici, anti-frode voto (già in S1-C2,
  qui il contesto festival), report finale disabilitato, stato finalist vestigiale. Valuta il taglio:
  cluster mono-sito → scheda più corta, focalizzata sul pattern "concorso a voto pubblico" come modulo
  opzionale del miniCMS, con FDCA come eredità.

Nota: scheda S1-C9 = valuta se accorparla con C13 (DB Evolution) — probabilmente NO (C13 è alto valore e
corposo, merita sola; C9 è autonoma e chiude il quadro emettitori). Default: S1-C9 SOLA. L'accorpamento
resta eccezionale e solo quando due cluster sono genuinamente uniti da un filo tematico.
