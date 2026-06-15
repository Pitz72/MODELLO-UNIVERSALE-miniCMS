# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA sola unità atomica.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.

Stato: SimonePizziWebSite (flagship contenuti) è COMPLETO. Sul secondo sito SitoRuntime sono già
fatte SR-C1 (Backend Core), SR-C2 (Security & Auth + CORS) e SR-C3 (Frontend Bridge & State). Da
questa sessione si prosegue su SitoRuntime con il cluster C4 — Content APIs (news + speakers + podcasts).

Per impostare stile e metodo, leggi DUE/TRE card di riferimento:
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C4-content-apis.md
  (è il PARALLELO diretto sull'altro sito: endpoint-router su REQUEST_METHOD con Auth::check sui rami
   mutativi, paginazione backend-driven COUNT+LIMIT/OFFSET con PARAM_INT, filtro categoria gerarchico,
   tag M:N + cache CSV, slug con normalizzazione accenti, visibilità pubblico/admin come AND
   condizionale, post programmati published_at futuro, ricerca LIKE. GOLD: il "Double Read" CHIUSO —
   solo articles lista ritorna {data,total}, il resto array nudo. Usala per sapere COSA cercare).
- _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C3-frontend-bridge.md
  (la card APPENA FATTA: ti dà la mappa CLIENT delle buste di payload che ora devi mappare lato
   SERVER — news.php={success,data,meta}, admin.php?action=list={success,articles,total},
   speakers.php=array NUDO, podcasts.php=array NUDO, feed_config.php={success,feed_url}. In C4
   mappa CHI produce queste forme e PERCHÉ sono asimmetriche: è il lato server del "non-Double-Read"
   eterogeneo osservato in C3).
- (facoltativo) SR-C1-backend-core.md per il vocabolario (getDB() lazy, schema init_mysql.php con
   news/speakers[col JSON]/podcasts, incidente fuso/formato-data debug_time.php — il confronto
   stringa published_at<=NOW con separatore 'T', che è LOGICA C4 di visibilità).

Unità di QUESTA sessione (atomica, una sola): SR-C4 — Content APIs (news + speakers + podcasts) del
sito SitoRuntime (C:\Users\Utente\Documents\GitHub\SITI-WEB\SitoRuntime).

Ambito C4: la LOGICA SERVER dei contenuti. Individua i FILE veri PRIMA con glob/grep nel backend
(public/api/). Cerca in particolare:
- news.php: come costruisce la lista pubblica paginata {success,data,meta} (COUNT + LIMIT/OFFSET?),
  il lookup per slug, e SOPRATTUTTO la regola di VISIBILITÀ (status=published AND published_at<=NOW):
  com'è scritto il confronto data/ora? È il confronto-stringa con separatore 'T' dell'incidente
  documentato in SR-C1 (debug_time.php)? Mappa il post programmato (published_at futuro).
- admin.php rami contenuto (action=list/get/save/delete): la forma {success,articles,total}, la
  generazione dello slug (normalizzazione accenti?), il campo author (SR-C2/C3 hanno notato che
  $_SESSION['username'] non è salvato → author='Admin'), draft vs published, gating isLoggedIn/CSRF.
- speakers.php: la colonna JSON (programs/social?), il flag founder, la forma ARRAY NUDO in lettura
  vs {success,...} in errore (il perché della guardia Array.isArray lato client), GET/POST/DELETE.
- podcasts.php: forma array nudo, struttura feed/episodi (solo la lettura/scrittura DB; il feed RSS
  syndication vero è C8 → puntatore).
- categorie/tag/ricerca/navigazione: ci sono? (SPW sì) o SitoRuntime è più piatto (category come
  stringa libera su news)? Mappa quello che c'è, marca N/A il resto.

Fai così:
1. Ispeziona in modo microscopico i file dell'ambito C4 (cita sempre percorso/file:linea).
2. Compila una card seguendo _cantiere-terza-edizione/mappatura/_TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C4-content-apis.md
3. NON sconfinare: backend core/bootstrap/DB=C1, security/auth/CORS=C2 (fatti), frontend bridge/
   client=C3 (fatto), media/upload server=C5, editor/sanitizzazione=C6, SEO+seo-cache=C7, RSS/feed
   syndication=C8, newsletter=C9, admin/dashboard UI=C12, EVOLUZIONE DB & INCIDENTI=C13. Se trovi
   roba di altri cluster, annotala SOLO come puntatore nelle "Note / domande aperte". Qui interessa
   la LOGICA SERVER dei contenuti: query, paginazione, slug, visibilità/scheduling, forma delle
   risposte, colonna JSON speaker.
4. Sezione §6 (Differenze rispetto agli altri siti): COMPILALA con cura — il confronto con SPW-C4 è
   il vero valore (Double Read di SPW vs buste eterogenee di SR; categoria gerarchica + tag M:N di
   SPW vs eventuale category-stringa piatta di SR; published_at<=NOW e l'incidente fuso/'T' di SR;
   author='Admin' di SR).

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SR-C4 → ✅)
- aggiungi una riga a _cantiere-terza-edizione/LOG.md (più recente IN BASSO)
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SR-C4) e lo stato globale
- git add/commit/push e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: SR-C5 — Media & Upload del sito
  SitoRuntime.
