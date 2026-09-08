# CAPITOLO 1: Architettura Backend e Sanitizzazione Build

FDCA deve passare da un sistema "statico" a uno "dinamico" basato sulla persistenza di SQLite.

## 1. Inizializzazione della Struttura Dati
Eseguire i seguenti comandi nella root di FDCA per preparare il file system:

```bash
mkdir -p public/api/.data
mkdir -p public/api/.cache
mkdir -p public/api/uploads/images
mkdir -p public/api/uploads/audio
```

## 2. Protezione del Database
Creare il file `public/api/.data/.htaccess` con il seguente contenuto:
```apacheconf
Order allow,deny
Deny from all
```

## 3. Sanitizzazione Post-Build (Il sistema Clean-Dist)
Copiare lo script `clean-dist.js` da `DISINTELLIGENZA` nella root di `FDCA`. Questo script garantisce che i dati di produzione (il DB) non vengano mai sovrascritti dai file di build locali.

### 3.1 Aggiornamento Script package.json
Modificare la sezione `scripts` in `package.json`:
```json
"scripts": {
  "build": "tsc -b && vite build && node clean-dist.js"
}
```

## 4. Routing SPA (Single Page Application)
Creare il file `public/.htaccess` (se mancante) per permettere a React Router di gestire le URL amichevoli senza che il server Apache cerchi cartelle fisiche.

---
*Obiettivo: Rendere il database inattaccabile via web e sicuro durante ogni aggiornamento del codice.*
