# React + PHP: The Thin Stack
## Il protocollo miniCMS per Web App moderne
### A cura di Simone Pizzi — Prima Edizione

---

Questo repository raccoglie le migliori pratiche, le architetture e le logiche software sviluppate e affinate attraverso quattro progetti reali: **SitoRuntime**, **DISINTELLIGENZA**, **FDCA** e **SimonePizziWebSite**.

L'obiettivo è uno standard di sviluppo per Web App moderne leggere che sia:
1. **Sicuro**: Protezione dei dati sensibili e prevenzione degli attacchi comuni.
2. **Performante**: Caching intelligente e database ottimizzati.
3. **Scalabile**: Passaggio documentato e testato da SQLite a MySQL.
4. **Professionale**: Gestione avanzata del ciclo di vita dei contenuti, SEO reale, feed RSS.

## I Siti di Riferimento

| Sito | Stack DB | Versione | Caratteristica Distintiva |
| :--- | :--- | :--- | :--- |
| **SitoRuntime** (Runtime Radio) | MySQL (migrato da SQLite) | v2.6.2 | Radio web, Speakers, Podcast, Quill Editor, CORS |
| **DISINTELLIGENZA** | SQLite | v0.5.4 | Festival con votazioni e iscrizioni (base originale) |
| **FDCA** | SQLite | fork di DISINTELLIGENZA | Festival concorso musicale (fork identico) |
| **SimonePizziWebSite** | MySQL (migrato) | v1.7.13 | Portfolio personale, Projects, Dynamic Tags, Pagination, RSS URN, SEO Engine |

---

## Struttura del Manuale

### Parte I — La Visione
*Il perché. La filosofia che guida ogni decisione tecnica.*

- [Capitolo 1: Manifesto](./CAPITOLO%201%20-%20Manifesto.md)

### Parte II — L'Architettura
*Le fondamenta. Struttura del progetto, database, stack tecnologico.*

- [Capitolo 2: Architettura e Struttura Progetto](./CAPITOLO%202%20-%20Architettura%20e%20Struttura%20Progetto.md)
- [Capitolo 3: Database Strategy](./CAPITOLO%203%20-%20Database%20Strategy.md)
- [Capitolo 4: Frontend Dependencies](./CAPITOLO%204%20-%20Frontend%20Dependencies.md)

### Parte III — I Componenti
*I mattoni. Backend, frontend, media, editor: i building block del sistema.*

- [Capitolo 5: Backend Logic (PHP)](./CAPITOLO%205%20-%20Backend%20Logic%20(PHP).md)
- [Capitolo 6: Frontend Bridge (API.ts)](./CAPITOLO%206%20-%20Frontend%20Bridge%20(API.ts).md)
- [Capitolo 7: Media & Optimization](./CAPITOLO%207%20-%20Media%20%26%20Optimization.md)
- [Capitolo 8: Advanced Content Editing & Media Integration](./CAPITOLO%208%20-%20Advanced%20Content%20Editing%20%26%20Media%20Integration.md)

### Parte IV — Il Flusso Operativo
*Come i contenuti vivono. Dal ciclo di vita alla distribuzione, passando per sicurezza e SEO.*

- [Capitolo 9: Content Lifecycle](./CAPITOLO%209%20-%20Content%20Lifecycle.md)
- [Capitolo 10: Security & Auth](./CAPITOLO%2010%20-%20Security%20%26%20Auth.md)
- [Capitolo 11: SEO Pre-rendering con PHP Entry-Point](./CAPITOLO%2011%20-%20SEO%20Pre-rendering%20con%20PHP%20Entry-Point.md)
- [Capitolo 12: RSS Feed & Syndication](./CAPITOLO%2012%20-%20RSS%20Feed%20%26%20Syndication.md)
- [Capitolo 13: Newsletter & Email System](./CAPITOLO%2013%20-%20Newsletter%20%26%20Email%20System.md)

### Parte V — I Casi Reali
*Dove la teoria incontra la produzione. Pattern estratti da progetti reali, con le loro cicatrici.*

- [Capitolo 14: Database Evolution - Da SQLite a MySQL](./CAPITOLO%2014%20-%20Database%20Evolution%20-%20Da%20SQLite%20a%20MySQL.md)
- [Capitolo 15: Portfolio & Projects Module](./CAPITOLO%2015%20-%20Portfolio%20%26%20Projects%20Module.md)
- [Capitolo 16: Festival Logic - Iscrizioni e Workflow Approvazione](./CAPITOLO%2016%20-%20Festival%20Logic%20-%20Iscrizioni%20e%20Workflow%20Approvazione.md)
- [Capitolo 17: Festival Logic - Votazioni e Protezione Anti-Frode](./CAPITOLO%2017%20-%20Festival%20Logic%20-%20Votazioni%20e%20Protezione%20Anti-Frode.md)
- [Capitolo 18: Festival Logic - Dashboard Admin, Settings e Reporting](./CAPITOLO%2018%20-%20Festival%20Logic%20-%20Dashboard%20Admin%2C%20Settings%20e%20Reporting.md)

### Allegati
*Strumenti pratici per iniziare.*

- [Boilerplate Checklist](./BOILERPLATE-CHECKLIST.md)

---
*Prima Edizione — Marzo 2026*
