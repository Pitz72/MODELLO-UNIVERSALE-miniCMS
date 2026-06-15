# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA sola unità atomica.

## Unità da svolgere: **SPW-C5 — SimonePizziWebSite — Media & Upload**

### Prompt (copia/incolla nella nuova sessione)

```
Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.
Leggi anche le card già fatte (contesto indispensabile per C5):
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C1-backend-core.md
  (bootstrap endpoint, singleton PDO, config, timezone, struttura public/api).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C2-security-auth.md
  (gate Auth::check sui rami mutativi; .htaccess con PHP-off sulla cartella uploads).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C3-frontend-bridge.md
  (LATO CLIENT dell'upload: fetch FormData senza Content-Type + XMLHttpRequest con
   xhr.upload.onprogress per la barra; api.ts uploadMedia/getMedia/deleteMedia).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C4-content-apis.md
  (cover_image è solo una stringa URL salvata negli articoli/progetti: la GESTIONE
   del file è C5, qui rimandata. Verificare dove il percorso viene generato/risolto).

Unità di QUESTA sessione (atomica, una sola): SPW-C5 — mappatura di Media & Upload
del sito SimonePizziWebSite (C:\Users\Utente\Documents\GitHub\SITI-WEB\SimonePizziWebSite).

Ambito C5: il LATO SERVER della gestione media (endpoint PHP in public/api/). In particolare:
- upload.php: ricezione file (multipart/FormData), validazione tipo/dimensione/estensione,
  naming/anti-collisione, destinazione su disco, eventuale ottimizzazione/resize immagini,
  risposta col percorso/URL pubblico.
- media.php: lista/CRUD media (libreria), eliminazione file, paginazione/forma risposta
  (chiudere/confermare il pattern Double Read anche qui).
- download.php: download/streaming file, eventuali controlli d'accesso, header.
- Eventuali migrate_media / ottimizzazione immagini / script di manutenzione media.
SOLO LETTURA sul sito sorgente. Individua prima i file reali con glob/grep su public/api/.

Fai così:
1. Ispeziona in modo microscopico gli endpoint dell'ambito C5 (cita sempre percorso/file:linea).
2. Compila una card seguendo _cantiere-terza-edizione/mappatura/_TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C5-media-upload.md
3. NON sconfinare: backend/db=C1, auth/sessioni=C2, frontend bridge=C3, contenuti=C4 (già fatti);
   editor=C6, SEO=C7, RSS=C8, newsletter=C9, engagement=C11, admin=C12.
   Se trovi roba di altri cluster, annotala solo come puntatore nelle "Note / domande aperte".
   Qui interessa il LATO SERVER dei media (upload/storage/ottimizzazione/download).
4. NON riportare credenziali/segreti.

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SPW-C5 → ✅)
- aggiungi una riga a _cantiere-terza-edizione/LOG.md
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SPW-C5) e lo stato globale
- git add/commit/push e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: SPW-C6 — Advanced Editing / Editor
```

### Coda delle unità successive (per orientamento)
SPW-C6 → SPW-C7 → SPW-C8 → SPW-C9 → SPW-C11 → SPW-C12 →
poi SitoRuntime (SR-C1…SR-C13) → DISINTELLIGENZA (DIS-*) → FDCA-DIFF → FASE 2 (Sintesi).
