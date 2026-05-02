# CAPITOLO 19: Social Interactions & Reactions (v1.0)

L'engagement degli utenti è fondamentale per un blog moderno. Il Modello Universale integra un sistema di **Reazioni Social** anonime, sicure e totalmente GDPR-compliant, ispirato alla logica di **SimonePizziWebSite (v2.0)**.

## 1. Filosofia del Modulo
A differenza dei commenti, che richiedono moderazione e gestione di dati personali (email, nomi), le reazioni permettono un'interazione istantanea senza frizioni.

- **Anonimato:** L'utente non deve registrarsi.
- **Sicurezza:** Protezione contro il voto multiplo (Spam) tramite hashing dell'identità.
- **Leggerezza:** Icone SVG native cross-platform (Emoji style).

## 2. Il Sistema delle 5 Reazioni
Il set standard include 5 tipi di feedback emotivo:
1.  **Thumb** (Apprezzamento standard)
2.  **Heart** (Amore/Passione)
3.  **Fire** (Contenuto "caldo" o di tendenza)
4.  **Think** (Contenuto riflessivo o complesso)
5.  **Game** (Contenuto ludico o interattivo)

## 3. Sicurezza e GDPR: Il Voter Hash
Per impedire a un utente di cliccare 100 volte la stessa reazione senza memorizzare il suo indirizzo IP (dato personale sensibile), usiamo un **Hash SHA256** salato e anonimo.

`php
// Hash anonimo del visitatore
 = hash('sha256',
    (['REMOTE_ADDR'] ?? 'unknown') .
    (['HTTP_USER_AGENT'] ?? 'unknown')
);
`
Questo hash identifica univocamente la "sessione/dispositivo" ma non permette di risalire all'IP originale, garantendo la conformità GDPR.

## 4. Rate Limiting (Protezione Anti-Frode)
Oltre alla chiave univoca sul database, il sistema implementa un limite temporale per IP: **max 20 azioni al minuto**. Questo blocca script automatizzati che tenterebbero di falsare le statistiche di engagement.

## 5. Schema Database (MySQL)

`sql
CREATE TABLE IF NOT EXISTS article_reactions (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    article_id  INT NOT NULL,
    reaction    VARCHAR(20) NOT NULL,
    voter_hash  VARCHAR(64) NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (article_id, voter_hash, reaction) -- Impedisce voti doppi
);
`

## 6. Logica API (Toggle Pattern)
L'endpoint eactions.php non si limita ad aggiungere voti, ma implementa la logica **Toggle**:
- Se l'utente clicca su una reazione che ha già dato, questa viene **rimossa**.
- Se clicca su una nuova, viene **aggiunta**.

Questo permette un'esperienza fluida simile ai "Like" dei social media moderni (Instagram/Facebook).

---
*Prossimo Capitolo: [Capitolo successivo previsto in roadmap]*