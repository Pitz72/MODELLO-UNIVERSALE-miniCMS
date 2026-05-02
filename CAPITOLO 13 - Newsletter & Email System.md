# CAPITOLO 13: Newsletter & Email System (v2.0)

La newsletter è uno degli strumenti di fidelizzazione più diretti e indipendenti dalle piattaforme. Il Modello Universale implementa un sistema professionale completo basato su **SimonePizziWebSite (v1.7.4)**, con supporto a Double Opt-in, gestione template dark-mode e tracking degli invii.

## 1. Schema del Database (Evoluto)

Rispetto alla v1.0, lo schema include token di sicurezza univoci per ogni utente, necessari per la conformità GDPR e la protezione contro le iscrizioni bot.

`sql
CREATE TABLE IF NOT EXISTS subscribers (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    email             VARCHAR(255) UNIQUE NOT NULL,
    name              VARCHAR(100) NULL,
    status            ENUM('pending', 'confirmed', 'unsubscribed') DEFAULT 'pending',
    confirm_token     VARCHAR(64) NULL,
    unsubscribe_token VARCHAR(64) NOT NULL,
    confirmed_at      DATETIME NULL,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabella Storico Invii
CREATE TABLE IF NOT EXISTS newsletter_sends (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    subject         VARCHAR(255) NOT NULL,
    body            TEXT NOT NULL,
    sent_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    recipient_count INT DEFAULT 0
);
`

## 2. Architettura Double Opt-in

Per garantire la qualità della lista e la conformità normativa, il sistema segue il flusso Double Opt-in:

1.  **Iscrizione:** L'utente inserisce l'email. Lo stato è pending. Viene generato un confirm_token.
2.  **Verifica:** Viene inviata un'email transazionale con un link di conferma unico.
3.  **Conferma:** Solo al click sul link, lo stato passa a confirmed e viene registrata la data confirmed_at.

### Generazione Token Sicuri
`php
     = bin2hex(random_bytes(32));
 = bin2hex(random_bytes(32));
`

## 3. Invio Newsletter e Composizione (v2.0)

### 3.1 Template HTML Professionale (Dark Theme)
Le newsletter moderne devono essere leggibili su client che supportano la dark mode. Il template di riferimento usa un design "Cyber-Dark" coerente con l'estetica del Modello Universale:

- **Sfondo:** #0a0a0a con container #111.
- **Tipografia:** Font di sistema puliti (Segoe UI, Arial).
- **Accent Color:** #22c55e (Verde Cyber).
- **Responsive:** Layout table-based a 600px per massima compatibilità (Outlook/Gmail).

### 3.2 Gestione Unsubscribe (GDPR)
Ogni email include un link di disiscrizione univoco in fondo. La disiscrizione è immediata (one-click) tramite l'unsubscribe_token, senza richiedere login all'utente.

`php
 = "https://tuosito.it/newsletter/disiscritto?token=" . urlencode();
`

## 4. Tracking e Storico (Admin)

L'interfaccia admin permette di:
- Visualizzare le statistiche (Totali, Confermati, In attesa, Disiscritti).
- Consultare lo storico degli invii effettuati (
ewsletter_sends).
- Approvare manualmente un iscritto se necessario (es. assistenza clienti).

## 5. Protezione Anti-Spam e Rate Limiting

- **Mailing Limit:** L'invio cicla sugli iscritti con un piccolo delay (es. usleep(100000)) per evitare di essere contrassegnati come spam dai provider.
- **Header SMTP:** Utilizzo di Reply-To reale per permettere all'utente di rispondere alla newsletter, mantenendo il From tecnico per i server di posta.

---
*Prossimo Capitolo: Social Interactions & Reactions - Come gestire l'engagement anonimo e sicuro.*