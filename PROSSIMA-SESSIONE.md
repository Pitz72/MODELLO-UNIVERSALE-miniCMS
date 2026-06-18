# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA unità. Questa è l'ULTIMA card della FASE 1:
> FDCA-DIFF, che chiude la mappatura.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.

METODO (ROADMAP §3.4): FDCA è un FORK di DISINTELLIGENZA. NON si rifà la mappatura da zero: si fa UN
SOLO documento di DIFF che cattura SOLO ciò che è cambiato nel fork rispetto a DISINTELLIGENZA (già
mappata in 7 card: C1, C2, C4, C5, C9, C10, C12). Questa è l'ULTIMA unità: chiude la FASE 1.

Stato: TRE siti mappati a fondo, manca solo il diff del fork.
- SimonePizziWebSite: COMPLETO (11 card). SitoRuntime: COMPLETO (10). DISINTELLIGENZA: COMPLETO (7).
- 28/~30 card. Resta SOLO FDCA-DIFF. Dopo → FASE 2 (Sintesi).

Unità di QUESTA sessione: FDCA-DIFF (differenze del fork) del sito FDCA
(C:\Users\Utente\Documents\GitHub\SITI-WEB\FDCA). UNA card di DIFF.

Metodo consigliato per il DIFF (efficiente):
1. Prima capire COSA è FDCA: leggere README.md, package.json (nome/versione), e la struttura cartelle.
   Capire se è "Festival della Canzone d'Autore" o simile (acronimo FDCA) — un altro festival.
2. DIFF STRUTTURALE veloce: confrontare l'elenco di public/api/*.php e src/pages|components di FDCA
   con quelli di DISINTELLIGENZA (usare find/ls e un grep mirato). Identificare: file aggiunti, file
   rimossi, file rinominati. Questo dà la mappa del "cosa è cambiato".
3. DIFF MIRATO sui file chiave già analizzati in DIS (db.php, init_db.php, auth.php, votes.php,
   participants.php, settings.php, upload.php, newsletter.php, AdminLayout.tsx, Dashboard.tsx): per
   ognuno, è IDENTICO o MODIFICATO? Citare le differenze concrete (file:linea). NON ri-descrivere ciò
   che è identico — solo i delta. Se un GOLD di DIS (es. RCE upload pubblico, auth grado-zero, contacts
   write-only, vote_count denormalizzato, anti-frode IP/24h) è CAMBIATO o RISOLTO nel fork, è il valore
   principale della card.
4. Branding/contenuti: FDCA avrà testi/tema diversi (altro festival). Annotare il livello di
   personalizzazione (solo branding? o anche logica?).

Ambito FDCA-DIFF: TUTTI i cluster, ma SOLO in termini di differenza vs DIS. Organizzare la card per
cluster (C1/C2/C4/C5/C9/C10/C12) con una riga "IDENTICO" o l'elenco dei delta per ciascuno.

Fai così:
1. Ispeziona FDCA in modo mirato (diff vs DIS, cita file:linea).
2. Compila UNA card in
   _cantiere-terza-edizione/mappatura/FDCA/FDCA-DIFF.md (crea la cartella FDCA/)
   Struttura suggerita: §1 cos'è FDCA · §2 diff strutturale (file aggiunti/rimossi) · §3 diff per
   cluster · §4 GOLD: cosa il fork ha cambiato/risolto/peggiorato · §5 cosa resta identico (sintetico).
3. Verifica in particolare se il fork ha RISOLTO qualcuno dei GOLD di sicurezza di DIS (RCE upload,
   CSRF, double opt-in, ecc.) — sarebbe il dato più prezioso.

Criterio di STOP: card di DIFF in stato COMPLETATO; con essa la FASE 1 (MAPPATURA) è CONCLUSA.

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (FDCA-DIFF → ✅, FASE 1 COMPLETA)
- aggiungi UNA riga a _cantiere-terza-edizione/LOG.md (più recente IN BASSO)
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta FDCA-DIFF; segnare FASE 1 CONCLUSA, passare a FASE 2)
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la PRIMA unità della FASE 2 — SINTESI: verosimilmente
  S1 (consolidamento card per-sito → schede tematiche cross-sito) oppure S3 (scaletta/indice globale
  della Terza Edizione). Proporre il punto di partenza della sintesi.
