# CAPITOLO 6: Frontend Bridge (API.ts) (v1.1 - ADVANCED)

Il "Bridge" tra React e PHP è il punto di snodo critico per la stabilità dell'applicazione. Questa sezione definisce gli standard per la gestione delle chiamate asincrone, la cattura degli errori parlanti e la sincronizzazione dello stato.

## 1. Architettura del Wrapper Universale
Invece di chiamate `fetch` isolate, il sistema utilizza un oggetto `api` centralizzato che incapsula la logica di base degli URL e degli header.

### 1.1 Il Pattern "Double Read" (Response Cloning)
Per estrarre messaggi di errore dal server senza perdere la possibilità di gestire lo stato HTTP, il Modello Universale impone il clonaggio della risposta:

```typescript
async function handleResponse(res: Response) {
    if (!res.ok) {
        let errorMessage = 'Errore imprevisto dal server';
        try {
            const json = await res.clone().json(); // Clona lo stream
            errorMessage = json.message || errorMessage;
        } catch (e) { /* Ignora errori di parsing */ }
        throw new Error(errorMessage);
    }
    return await res.json();
}
```

## 2. Polimorfismo delle Chiamate
Il Bridge deve adattarsi al tipo di dato inviato, distinguendo tra payload JSON e flussi binari (multipart).

- **JSON Standard**: Utilizzato per configurazioni, news e login. Richiede `JSON.stringify(body)`.
- **FormData**: Obbligatorio per upload di file o form complessi (es. iscrizioni con allegati). Non deve essere stringhizzato; va passato direttamente alla fetch.

## 3. Sincronizzazione dello Stato Globale
### 3.1 Silent Auth Check
L'operazione di `checkAuth` deve essere "silenziosa": non deve lanciare eccezioni in caso di fallimento, ma restituire `null`. Questo permette all'applicazione di decidere se reindirizzare l'utente o permettere la navigazione pubblica senza interrompere il flusso di rendering.

### 3.2 Hard Logout
Per garantire che nessun dato sensibile rimanga negli stati di React (Context, Redux, etc.), l'azione di logout deve concludersi con un `window.location.reload()`, resettando l'intero ambiente di esecuzione del browser.

## 4. Validazione Incrociata (HTTP vs Logic)
Alcune risposte del backend potrebbero essere tecnicamente corrette (HTTP 200) ma contenere fallimenti logici. Il Bridge deve validare entrambi i livelli:

```typescript
const data = await res.json();
if (data.status === 'error') throw new Error(data.message);
return data;
```

## 5. TypeScript Integration (Type Safety)
Ogni metodo dell'oggetto API deve (dove possibile) essere tipizzato. Questo garantisce che il frontend conosca esattamente la struttura dei dati (es. `NewsArticle[]`, `UserRole`, `StatsResponse`) riducendo errori di runtime dovuti a proprietà mancanti o rinominate.

## 6. Scalabilità e Paginazione Backend-driven
Nei primi stadi di vita di un portfolio o blog, fetching globali (es. estrattore massivo di tutti gli articoli array-based) sono tollerabili. Tuttavia, l'esperienza operativa di SimonePizziWebSite (giunto alla v1.7.12) manifesta come tale ingenuità causi degradazione prestazionale e memory issues (rallentamento del Time to Interactive React).

Lo standard del Modello Universale eleva l'approccio alla **paginazione nativa server-side**:
- **Parametrizzazione Query**: Le API GET di liste (articoli, log, item) devono accettare query params tipizzati `?page=N&limit=10`. Le query backend devono forzare stringhe di `LIMIT :limit OFFSET :offs`.
- **Custom React Hooks**: Il bridge usa hook specializzati (come `useFetchArticles`) che conservano lo step matematico e lo stato `hasMore`. La logica "Carica altro" non sostituisce lo scope del JS, ma *appensa* linearmente i nuovi frame JSON ricevuti.
- **Strategie Pre-Fetch Limitizzate**: Sezioni UI ad alta densità (come vetrine e griglie Home Page) limitizzano *at runtime* la chiamata (es. `slice(0, 7)`) garantendo un mounting fulmineo.

---
*Prossimo Capitolo: Media & Optimization - Caching, ridimensionamento e SEO.*
