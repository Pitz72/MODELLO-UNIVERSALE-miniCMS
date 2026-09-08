# CAPITOLO 4: Architettura Admin e Protected Routes

FDCA deve creare un'area riservata inaccessibile al pubblico per gestire i contenuti del miniCMS.

## 1. Struttura delle Pagine Admin
Creare la cartella `src/pages/admin/` e includere le seguenti schermate (copiabili da `DISINTELLIGENZA` e adattabili nello stile):
- `Login.tsx`: Pagina di accesso.
- `Dashboard.tsx`: Riepilogo statistiche.
- `NewsManager.tsx`: Gestione CRUD news (Bozze/Programmate/Pubblicate).
- `MediaCenter.tsx`: Gestione centralizzata degli asset.

## 2. Layout Protettivo (AdminLayout.tsx)
Creare `src/components/admin/AdminLayout.tsx` che implementi la logica di protezione:
- Se l'utente non è loggato, reindirizza istantaneamente a `/admin/login`.
- Mostra un caricamento ("Verifying...") durante il `checkAuth`.
- Implementa la sidebar con i link alle sezioni gestionali.

## 3. Configurazione delle Rotte (Routes.tsx)
Aggiornare il Router di FDCA per includere le rotte admin sotto il layout protetto:
```typescript
{
  path: '/admin',
  element: <AdminLayout />,
  children: [
    { path: 'dashboard', element: <Dashboard /> },
    { path: 'news', element: <NewsManager /> },
    { path: 'media', element: <MediaCenter /> },
  ]
}
```

---
*Obiettivo: Separare l'esperienza pubblica da quella gestionale in modo sicuro.*
