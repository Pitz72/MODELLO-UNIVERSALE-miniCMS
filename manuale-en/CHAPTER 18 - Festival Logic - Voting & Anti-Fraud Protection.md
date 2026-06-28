# CHAPTER 18: Festival Logic — Voting & Anti-Fraud Protection

The vote is the heart of the contest, and it’s also the point where a seemingly robust module reveals which of its defenses truly count and which are only decoration. This chapter tells them apart, and makes plain two fragilities the idealized text kept quiet about: the ranking can drift in silence, and the reset isn’t protected.

## 1. The Voting Session

A visitor can cast one to three preferences in a single call. The backend validates that every participant voted for is really in the running (`status = 'approved'` and `in_current_round = 1`), then records the vote in a transaction that does two things at once: it inserts the row in `votes` and increments the counter on the participant.

```php
// every vote is a transaction: INSERT + increment of the denormalized counter
$pdo->beginTransaction();
$pdo->prepare("INSERT INTO votes (participant_id, ip, user_agent) VALUES (?, ?, ?)")
    ->execute([$pid, $ip, $ua]);
$pdo->prepare("UPDATE participants SET vote_count = vote_count + 1 WHERE id = ?")->execute([$pid]);
$pdo->commit();
```

That `vote_count` isn’t a convenience: it’s the **source of truth for the ranking**. The participants are ordered by `vote_count`, not by counting the rows in `votes`. It’s a reasonable performance choice (the ranking becomes a `SELECT ... ORDER BY vote_count`), but it comes at a price that §5 brings into focus.

## 2. The Anti-Abuse Defenses, in Order of Real Effectiveness

The module presents three defenses against multiple voting. The point, though, is that they’re not equivalent at all: one holds, one is cosmetic, one defends nothing. Telling them apart matters, because confusing them gives a false sense of security.

- **The real barrier: IP for twenty-four hours.** The backend records the voter’s IP address and refuses new votes from the same IP for the next twenty-four hours. It’s the only server-side defense an attacker can’t bypass from their own browser.
- **The cosmetic defense: the cookie.** After the vote, a cookie (`dis_voted`) is set with a thirty-day expiry. It lives on the client, so anyone can delete it, open a private window or switch browsers, and vote again. It improves the honest user’s experience (it reminds them they’ve already voted); it doesn’t stop someone bent on cheating.
- **No defense, just a record: the User-Agent.** Every vote stores the `User-Agent`, but it isn’t used to block anything: it serves only for possible after-the-fact analysis.

> [!WARNING]
> **Three defenses, only one counts**
> Listing cookie, IP, and User-Agent as if they were three equivalent locks is a common and dangerous mistake, because the reader believes they have a three-layer defense when they have only one. The cookie and the User-Agent are under the client’s control: the first gets deleted, the second gets spoofed. The only barrier that lives on the server, and that can therefore really limit abuse, is the IP-based one. Knowing which defense actually holds is what keeps you from leaving a contest defenseless while believing it’s armored.

On the IP there’s a counterintuitive observation (Chapter 10): the module uses the raw `REMOTE_ADDR`, not a helper that reads the forwarding headers. For authentication behind a proxy that would be a flaw, but for a public vote it’s a **strength**: the `X-Forwarded-For` header is written by the client and gets spoofed, while `REMOTE_ADDR` doesn’t. The flip side is NAT collision: behind a single corporate or university network, many legitimate voters share an IP and block one another.

> [!NOTE]
> **The privacy counterpoint: the hashed identity of the reactions**
> The festival vote saves the IP and User-Agent **in cleartext** in the `votes` table: personal data persisted without obfuscation. The article reactions (Chapter 20) face the same problem more carefully, deriving a `SHA256(IP+UA)` pseudonym instead of saving the bare IP. Neither one is perfect anonymity (that hash is reversible, see Chapter 20), but it’s the difference between “I obfuscated the data” and “I kept every voter’s address in cleartext.” For a module that collects votes from the public, saving the raw IP is a choice to weigh on the GDPR plane too, not just the anti-fraud one.

## 3. The On/Off Rounds

A participant shows up on the voting page only if they’re `approved` **and** `in_current_round = 1`. The phases of the contest (heats, semifinals, final) aren’t entities with a history: they’re this flag, switched on or off by the admin on groups of participants. It’s the module’s simplicity, and also its limit.

> [!WARNING]
> **`reset_votes` erases the round’s history**
> Advancing the contest means zeroing out the round’s votes and switching the flag back on for the next group. But `reset_votes` **deletes** the previous round’s votes and resets the counter to zero: there’s no per-round archiving, so the results of the heats vanish, except for the `.bak` copy the system makes before destructive operations (Chapter 10). Managing the phases with a single boolean flag is convenient, but if you want to keep each round’s results you have to archive them before the reset: the module, on its own, doesn’t.

## 4. The Voting Master Switch

The ability to vote is governed by a global switch (`voting_active`) in the `settings` table: if it’s off, the backend refuses every vote with a `403`. The `settings` table is publicly readable (the frontend consults it to show or hide the form) and writable only by the admin.

One detail reveals a small internal inconsistency: the reading of the flag accepts both `'1'` and `'true'`, because one spot in the code saves booleans as `'1'` and another as the string `'true'`. The defensive read (`=== '1' || === 'true'`) makes up for the fact that the write never settled on a convention. It works, but it’s the symptom to recognize: when the reader has to guess how the writer wrote, there’s an agreement missing upstream.

## 5. The Ranking That Can Drift

The subtlest fragility remains, and the most important one for the fairness of the contest. Because the ranking is ordered by `vote_count` (the denormalized counter from §1) and not by the real count of the rows in `votes`, the two values can diverge. The transaction keeps them aligned in normal operation, and the reset zeroes them together, but there’s no **reconciliation**: no periodic check verifies that `vote_count` really matches the number of votes recorded.

> [!WARNING]
> **Denormalizing a counter: speed against truth**
> Keeping the vote total in a column makes the ranking instant, but it also makes it fragile: a transaction interrupted halfway, a manual import, a correction made by hand on the database, and the counter no longer matches the real votes. The trouble is that the divergence is **silent**: the ranking shows an order that looks right, and no one notices it’s wrong until someone counts the votes by hand. When a denormalized number decides an outcome (a ranking, a prize), you need a reconciliation query that periodically compares the counter against `COUNT(votes)` and flags the gaps. The module doesn’t have one, and it’s the first thing to add before entrusting it with a real contest.

There’s the reset itself, finally: the actions that zero out votes and counters (`reset_votes`, `reset_system`) are powerful and destructive, but they have **no CSRF protection** (Chapter 10). All that surrounds them is a browser confirmation, which stops the careless click but not a request forged by another site while the admin is logged in. The pre-destruction `.bak` copy is the safety net that softens the damage; the defense that’s missing is the token.

> [!IMPORTANT]
> **The Canon**
> - The real anti-fraud is the IP constraint plus a time window (24h); the cookie is cosmetic, the User-Agent only a hint.
> - For a public vote the raw IP is a strength against spoofing (unlike auth behind a proxy, Chapter 10).
> - If you denormalize a counter (`vote_count`), plan for periodic reconciliation against `COUNT(votes)`, or you accept the silent drift.
> - Destructive resets go through a CSRF token plus the `.bak` copy; the browser confirmation isn’t enough.

---
*Next Chapter: Festival Logic — Admin Dashboard, Settings & Reporting. The contest’s control panel, and the final report that was never switched on.*
