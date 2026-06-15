# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA sola unità atomica.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.

Stato: SimonePizziWebSite (flagship contenuti) è COMPLETO. Sul secondo sito SitoRuntime sono già
fatte SR-C1 (Backend Core) e SR-C2 (Security & Auth + CORS). Da questa sessione si prosegue su
SitoRuntime con il cluster C3 — Frontend Bridge & State.

Per impostare stile e metodo, leggi DUE/TRE card di riferimento:
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C3-frontend-bridge.md
  (è il PARALLELO diretto sull'altro sito: client api.ts unico su fetch con credentials:include,
   base URL prod/dev, pattern "Double Read" array vs {data,total}, loaders react-router con route
   guard adminAuthLoader→redirect login, error boundary brandizzati, hook useFetchArticles, upload
   con XHR progress, degradazione graziosa vs errore propagato. Usala per sapere COSA cercare e con
   che dettaglio).
- _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C2-security-auth.md
  (la card APPENA FATTA: ti dà i fatti di sicurezza lato server che il frontend deve rispettare —
   CSRF a TOKEN con header X-CSRF-Token restituito nel body di login/check_auth, gate a ruoli
   admin/editor, CORS allowlist 4 origini SENZA Allow-Credentials, cookie di sessione. In C3 mappa
   COME il frontend gestisce questo token CSRF: dove lo salva, come lo rispedisce su POST/DELETE).
- (facoltativo) SR-C1-backend-core.md per il vocabolario di base di SitoRuntime.

Unità di QUESTA sessione (atomica, una sola): SR-C3 — Frontend Bridge & State del sito
SitoRuntime (C:\Users\Utente\Documents\GitHub\SITI-WEB\SitoRuntime).

Ambito C3: il "ponte" tra React e il backend PHP. Individua i FILE veri PRIMA con glob/grep nel
frontend (probabile src/ con TypeScript). Cerca in particolare:
- il CLIENT API centrale (equivalente di api.ts di SPW): c'è un wrapper unico su fetch? Come
  costruisce la base URL (prod runtimeradio.com vs dev)? Usa credentials:include per le sessioni
  cookie?
- GESTIONE DEL TOKEN CSRF lato client: SR-C2 ha mostrato che il backend RESTITUISCE csrf_token nel
  body di login/check_auth e si aspetta l'header X-CSRF-Token sulle mutazioni. DOVE lo memorizza il
  frontend (state/context/localStorage)? Come lo inietta negli header delle POST/DELETE? Questo è
  il VALORE centrale della card (divergenza da SPW che non ha token CSRF lato client).
- ROUTING e route guard: esiste un equivalente di adminAuthLoader→redirect? Come protegge le rotte
  admin lato client? React Router (loaders) o altro?
- PATTERN di lettura risposte: il backend SR risponde con forme tipo {success, articles, total} /
  {success, article} / {authenticated, user} (visto in admin.php) — c'è un "Double Read" o
  un'asimmetria come in SPW? Mappa come il client estrae i dati.
- hooks/loaders/gestione errori e stato: loading/empty/error, degradazione graziosa, retry.
- upload lato client (solo il bridge: progress/headers; l'ottimizzazione immagini è C5 → puntatore).

Fai così:
1. Ispeziona in modo microscopico i file dell'ambito C3 (cita sempre percorso/file:linea).
2. Compila una card seguendo _cantiere-terza-edizione/mappatura/_TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C3-frontend-bridge.md
3. NON sconfinare: backend core/bootstrap/DB=C1, security/auth/CORS lato SERVER=C2 (già fatti),
   contenuti (news/speakers/podcasts) logica server=C4, media/upload server=C5, SEO+cache=C7,
   RSS=C8, newsletter=C9, admin/dashboard UI=C12, EVOLUZIONE DB & INCIDENTI=C13. Se trovi roba di
   altri cluster, annotala SOLO come puntatore nelle "Note / domande aperte". Qui interessa il
   PONTE FRONTEND↔API: client fetch, base URL, CSRF lato client, routing/guard, data layer, stato,
   gestione errori.
4. Sezione §6 (Differenze rispetto agli altri siti): COMPILALA con cura — il confronto con SPW-C3
   è il vero valore (gestione token CSRF lato client che SPW non ha; eventuale Double Read;
   credentials:include; route guard; CORS multi-dominio lato client).

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SR-C3 → ✅)
- aggiungi una riga a _cantiere-terza-edizione/LOG.md (più recente IN BASSO)
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SR-C3) e lo stato globale
- git add/commit/push e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: SR-C4 — Content APIs
  (news + speakers + podcasts) del sito SitoRuntime.
