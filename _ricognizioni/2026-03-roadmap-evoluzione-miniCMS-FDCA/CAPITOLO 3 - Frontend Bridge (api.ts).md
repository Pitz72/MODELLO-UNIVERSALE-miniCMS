# CAPITOLO 3: Frontend Bridge (api.ts)

FDCA deve centralizzare le chiamate API in un unico punto per garantire stabilità e facilità di debug.

## 1. Creazione del Bridge (src/api.ts)
Copiare il file `api.ts` da `DISINTELLIGENZA` adattando solo gli endpoint se necessario.
- Implementare il pattern **Double Read** (`res.clone().json()`) per estrarre gli errori del server.
- Definire le interfacce TypeScript per le entità di FDCA (News, Podcast, Iscritti).

## 2. Configurazione Base API
Il file `api.ts` deve definire l'URL base:
```typescript
const API_BASE = '/api';
```
In questo modo, in fase di build, il percorso sarà relativo alla root del sito, rendendo il deploy istantaneo su qualsiasi dominio.

## 3. Metodi Critici da Implementare:
- `checkAuth()`: Per la protezione delle rotte.
- `login()` e `logout()`: Per la gestione delle sessioni.
- `getNews()`: Con supporto alla paginazione.
- `uploadFile()`: Con gestione multipart per immagini e audio.

---
*Obiettivo: Separare la logica delle chiamate dai componenti UI.*
