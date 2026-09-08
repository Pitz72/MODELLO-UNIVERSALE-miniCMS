# CAPITOLO 5: Advanced Components Integration

FDCA deve arricchire l'area admin con componenti evoluti per permettere una gestione dei contenuti semplice e potente.

## 1. Rich Text Editor (src/components/RichTextEditor.tsx)
Copiare il componente `RichTextEditor.tsx` da `DISINTELLIGENZA`.
- Assicurarsi che gestisca correttamente la sanitizzazione del paste da Word/Wikipedia.
- Integrare la logica di inserimento link e colori.
- (Avanzato) Aggiungere un pulsante per l'apertura del Media Picker per inserire immagini direttamente nel corpo del testo.

## 2. Media Picker (src/components/admin/MediaPicker.tsx)
Copiare il componente `MediaPicker.tsx`. Questo componente è cruciale per poter scegliere immagini già caricate o caricarne di nuove senza uscire dal form di creazione della news.
- Deve supportare il filtraggio per tipo (`image` o `audio`).
- Deve implementare la logica di selezione con restituzione dell'URL relativo.

## 3. Gestione Preview
In FDCA, i form di creazione devono sempre mostrare un'anteprima dell'immagine di copertina caricata per fornire feedback immediato all'editor.

---
*Obiettivo: Fornire all'editor strumenti potenti senza sacrificare la pulizia dell'HTML generato.*
