# CAPITOLO 6: Ottimizzazioni Finali e Deploy

Per garantire performance e visibilità, FDCA deve implementare i meccanismi di ottimizzazione avanzati del Modello Universale.

## 1. Implementazione Cache Endpoint (api/.cache)
Aggiornare `news.php` e gli altri endpoint GET per supportare la cache su file JSON.
- Impostare un TTL di 300 secondi per le liste pubbliche.
- Assicurarsi che ogni operazione di scrittura (POST) distrugga la cartella `.cache/` per mantenere i dati aggiornati.

## 2. Implementazione SEO Dynamics
Creare il file `public/api/rebuild_seo_cache.php` e configurarlo per generare i file JSON minimi (`seo_news_hash.json`).
- Integrare l'entry-point PHP del sito per leggere questi file e iniettare i meta tag `og:title`, `og:description`, `og:image`.

## 3. Test Finale della Programmazione Reale
Creare una news di prova in FDCA impostando:
- Stato: `published`
- Data di Pubblicazione: 10 minuti nel futuro.
Verificare che la news NON appaia sul sito pubblico finché non sono passati i 10 minuti (confrontando con l'orario del server).

## 4. Deploy Sicuro
Eseguire `npm run build` e verificare che lo script `clean-dist.js` rimuova effettivamente eventuali file di test `.sqlite` dalla cartella `dist/`.

---
*Obiettivo: Consegnare un prodotto veloce, sicuro e pronto per i motori di ricerca.*
