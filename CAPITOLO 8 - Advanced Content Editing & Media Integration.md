# CAPITOLO 8: Advanced Content Editing & Media Integration (v1.1 - ADVANCED)

Il Modello Universale (miniCMS) eleva l'esperienza di editing trasformandola in un centro di controllo multimediale integrato. Questa sezione definisce gli standard per la gestione degli asset, l'editing del testo e l'integrazione fluida tra i due mondi.

## 1. Il Media Center Centralizzato
L'architettura dei media non è un semplice file browser, ma un gestore di stato con logiche di anteprima e azioni di massa.

### 1.1 Filtraggio Contestuale (Tab Strategy)
I media vengono organizzati in base alla loro natura e destinazione, filtrati dinamicamente tramite i percorsi del file system:
- **Immagini**: Filtrate per mime-type `image/*`.
- **Audio Partecipanti**: Isolati nella sottocartella `/participants/`.
- **Audio Podcast**: Riservati alla cartella `/podcasts/` con permessi di scrittura limitati agli Admin.

### 1.2 Gestione Asset Avanzata
Il sistema deve implementare funzioni di manutenzione proattiva:
- **Bulk Delete**: Selezione multipla e cancellazione atomica per la pulizia del server.
- **Audio Engine**: Player integrato (`Audio API`) per il pre-ascolto istantaneo direttamente dalla griglia media.
- **Visual Feedback**: Visualizzazione del peso dei file (`formatBytes`) per sensibilizzare l'editor sull'occupazione del disco.

## 2. Il Componente MediaPicker (Integration Layer)
Il `MediaPicker` è il ponte tra l'editor di news e la libreria media.
- **Modal Logic**: Deve aprirsi in sovrapposizione (Overlay) senza perdere lo stato del form sottostante.
- **Search & Filter**: Ricerca testuale in tempo reale sulla lista dei file e filtraggio automatico per il tipo di dato richiesto dal form (es. solo immagini per la cover, solo audio per il podcast).
- **Selection Callback**: Restituzione dell'URL relativo al componente genitore, con chiusura automatica del modale.

## 3. Rich Text Editor & Formattazione (UX Avanzata)
L'editor di testo è il cuore dell'interfaccia. Pur rinunciando a pesanti dipendenze esterne in favore di soluzioni native-React, le evoluzioni architetturali (v1.7.9) prevedono l'implementazione obbligatoria dei seguenti pattern UX:
- **Sticky Actions**: La toolbar di formattazione deve utilizzare `sticky top-0 z-30` (o simili) affinché non scompaia mai dallo schermo durante la scrittura di articoli molto lunghi.
- **Keyboard Shortcuts**: L'intercettazione nativa degli eventi tastiera (es. `Ctrl+K`) per innescare modali specifici (es. inserimento link) senza costringere l'uso del mouse.
- **Metriche in Real-Time**: Il rendering di una status bar a piè di pagina con contatori istantanei di parole e caratteri, fornendo metriche vitali per il targeting SEO.
- **Interoperabilità Tabelle**: Funzioni native per l'inserimento di griglie di dati compatibili con i plugin di Typography del frontend pubblico.
- **State Reset (Key Strategy)**: L'uso rigido di `key={id}` nel componente genitore React per garantire la pulizia istantanea dei buffer interni al caricamento di un nuovo articolo.
- **Paste Protection**: Intercettazione pro-attiva dell'evento `paste` con rimozione di stili inline, script e attributi pericolosi (generati tipicamente incollando da Word o Wikipedia).
- **Markdown Paster**: Conversione silenziosa "in volo" se il testo intercettato segue notazioni Markdown verso l'HTML semantico compatibile.

## 4. Gestione degli URL e Portabilità
- **Relative Path Strategy**: Nel database vengono salvati solo percorsi relativi (es. `/api/uploads/file.jpg`).
- **Absolute Resolver**: In fase di condivisione o copia (pulsante "Copia URL"), il sistema trasforma il percorso in URL assoluto (`window.location.origin + path`) per garantire che i link funzionino anche al di fuori dell'applicazione.

## 5. UX e Feedback Visivo
- **Miniature (Lazy Loading)**: Caricamento differito delle miniature nella griglia media per non appesantire il browser in librerie con centinaia di file.
- **Transizioni**: Uso di animazioni CSS (`animate-in`, `fade-in`) per rendere fluida l'apertura dei modali e il caricamento delle liste.

---
*Conclusione: Il Modello Universale miniCMS è ora un sistema completo, sicuro e scalabile, pronto per essere impiegato come standard universale.*

---
*Prossimo Capitolo: Content Lifecycle - Il ciclo di vita dei contenuti, dalla bozza alla pubblicazione programmata, con il pattern di bypass admin.*
