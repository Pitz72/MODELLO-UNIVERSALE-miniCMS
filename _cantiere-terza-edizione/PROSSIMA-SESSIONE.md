# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA sola unità atomica.

## Unità da svolgere: **SPW-C2 — SimonePizziWebSite — Security & Auth**

### Prompt (copia/incolla nella nuova sessione)

```
Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.
Leggi anche la card già fatta _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C1-backend-core.md
(contiene puntatori verso C2: auth_helper.php, auth.php, tabella login_attempts).

Unità di QUESTA sessione (atomica, una sola): SPW-C2 — mappatura di Security & Auth
del sito SimonePizziWebSite (C:\Users\Utente\Documents\GitHub\SITI-WEB\SimonePizziWebSite).

Ambito C2: public/api/auth.php, public/api/auth_helper.php, sessioni, cookie, login/logout,
hashing password, rate limiting (tabella login_attempts), recupero password, .htaccess,
CORS, eventuali protezioni anti-frode/anti-abuso. SOLO LETTURA sul sito sorgente.

Fai così:
1. Ispeziona in modo microscopico i file dell'ambito C2 (cita sempre percorso/file:linea).
2. Compila una card seguendo _cantiere-terza-edizione/mappatura/_TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C2-security-auth.md
3. NON sconfinare in altri cluster (db/bootstrap=C1 già fatto, content api=C4, newsletter=C9,
   admin=C12): se trovi roba di altri cluster, annotala solo come puntatore nelle
   "Note / domande aperte".
4. NON riportare credenziali reali da config.php (sono segrete): redigerle come in SPW-C1.

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SPW-C2 → ✅)
- aggiungi una riga a _cantiere-terza-edizione/LOG.md
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SPW-C2) e lo stato globale
- git add/commit/push e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: SPW-C3 — Frontend Bridge & State
```

### Coda delle unità successive (per orientamento)
SPW-C3 → SPW-C4 → SPW-C5 → SPW-C6 → SPW-C7 → SPW-C8 → SPW-C9 → SPW-C11 → SPW-C12 →
poi SitoRuntime (SR-C1…SR-C13) → DISINTELLIGENZA (DIS-*) → FDCA-DIFF → FASE 2 (Sintesi).
