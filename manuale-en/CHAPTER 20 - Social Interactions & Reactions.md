# CHAPTER 20: Social Interactions & Reactions

Almost everything in the CMS is restricted writing. Publishing an article, uploading a file, composing a newsletter: each of these actions lives behind `Auth::check()`. There are two exceptions, and this chapter is about them. The **reactions** to articles and the **messages** from the contact form are the only two surfaces where an unauthenticated visitor really writes into the database. They’re the most exposed front of the site, and that’s exactly why they concentrate the most sophisticated defenses SimonePizziWebSite has built.

A necessary premise: the reactions exist **only** in SimonePizziWebSite. SitoRuntime and DISINTELLIGENZA don’t have them; the messages surface, on the other hand, returns elsewhere as a contact form. So the chapter is largely single-site, but its lens, *how the thin stack handles anonymous public writing*, touches threads that run through the whole book: the hashed identity and the anti-abuse (Ch. 10), the sanitization (Ch. 8), best-effort email (Ch. 13), the festival vote (Ch. 18).

And there’s a standout worth the read: in the same codebase **two opposite philosophies** of sanitization live side by side. The content of the articles, written by an admin you trust, is saved raw and cleaned at the moment it’s shown; the text of the messages, written by anyone who passes through, is cleaned at the moment it’s saved. It isn’t a contradiction: it’s the right choice for each context, and the two look each other in the face right here.

---

## 1. Two Surfaces, One Principle: Defend at the Entrance

Beneath the differences, the two surfaces share five traits.

Both are endpoint-routers on `REQUEST_METHOD` with a **selective gate**: in `messages.php` the `POST` is public (anyone sends a message), while `GET`, `PUT`, and `DELETE` (list, mark-read, delete) go through `Auth::check()`; the reactions are entirely public, and have no admin branch at all. The identity of whoever writes is a **derived pseudonym**, not an account and not a cookie. Integrity is entrusted to the **database**, not just to an application-level `if`. Public input is cleaned **at write-time**. And everything degrades gracefully: the reactions fall to a zero count on any error (the article page never breaks), and the notification email is best-effort, because the truth is in the saved record, not in the email that went out.

The next sections take these five traits one at a time, starting with the one the module describes a little too generously: anonymity.

---

## 2. The Anonymous Identity, and Why a Hash Isn’t Anonymity

The voter has no account. They’re identified by a pseudonym computed on the fly from the two pieces of data the server sees on every request: the IP address and the User-Agent.

```php
// SPW reactions.php:25-29 — an anonymous pseudonym, no personal data persisted in cleartext
$voter_hash = hash('sha256',
    ($_SERVER['REMOTE_ADDR'] ?? 'unknown') .
    ($_SERVER['HTTP_USER_AGENT'] ?? 'unknown')
);
```

It’s a good idea: what ends up in the database isn’t an IP address in cleartext, but a string that means nothing to whoever reads it. It’s better than what the festival vote does, which saves the IPs in cleartext (Ch. 18). But here an honest clarification is needed, because it’s easy to tell it better than it is. This hash **isn’t salted**, and the IPv4 address space is small: a little over four billion values, which a computer tries all of in a ridiculous amount of time. Combined with a plausible User-Agent, an unsalted `SHA256(IP+UA)` **inverts by brute force**. It doesn’t protect the IP, it only obfuscates it.

> [!WARNING]
> **A hash isn’t anonymity: it’s pseudonymization, and it has limits**
> “We hash it, so it’s anonymous and compliant” is a sentence you hear often, and it’s almost always false. A hash is a deterministic function: the same input always gives the same output, and if the input space is small (IPs are) anyone can build the reverse table for themselves. What you get is pseudonymization, useful for not having the IP in cleartext in the database, not irreversible anonymity. To make it genuinely hard to invert you need a **secret salt** kept on the server and never exposed: without that, the hash is a padlock with the key hanging right beside it. It’s still a step up from saving the bare IP; the only problem is claiming it’s more than it is.

A minor detail in the same direction: both the reactions and the messages read the raw `REMOTE_ADDR`, not the anti-spoofing helper `getClientIp()` used elsewhere on the site (Ch. 10). Behind a proxy or a CDN this can collapse many visitors onto a single address, and make the rate limit of the next section stricter than it should be.

---

## 3. The Two-Layer Rate Limit: Why One Isn’t Enough

To keep a script from inflating the counts, the reactions have a rate limit. The first layer counts the recent actions by `voter_hash`: above twenty a minute, the request is rejected. It seems enough, but there’s a crack, and it’s the heart of this chapter: the `voter_hash` includes the User-Agent, which is a header **chosen by the client**. Just change it on every request to get a different hash each time, and the first layer never sees two actions from the “same” voter.

Version 1.19.0 plugged the crack with a second barrier, anchored to a key the client doesn’t control: **the IP alone**.

```php
// SPW reactions.php:92-119 — two layers, because the first can be bypassed
// Layer 1: by voter_hash (IP + UA), max 20/min — but the UA is chosen by the client
$stmtRate = $pdo->prepare("SELECT COUNT(*) FROM article_reactions
    WHERE voter_hash = ? AND created_at >= DATE_SUB(NOW(), INTERVAL 1 MINUTE)");   // >= 20 -> 429

// [v1.19.0] Layer 2: by IP ONLY, max 30/min — reuses login_attempts with the 'rea:' namespace
$rl_key = 'rea:' . substr(hash('sha256', $ip), 0, 40);   // truncated to fit the reused ip_address column
$stmtIpRate = $pdo->prepare("SELECT COUNT(*) FROM login_attempts
    WHERE ip_address = ? AND attempt_time >= DATE_SUB(NOW(), INTERVAL 1 MINUTE)");  // >= 30 -> 429
```

The second layer reuses the `login_attempts` table, the same one that defends the login from brute force (Ch. 10) and the newsletter from mail-bombing (Ch. 13), distinguishing the uses with a namespace prefix (`rea:`). One table, three jobs.

> [!TIP]
> **If the rate-limit key includes client input, you need a second layer**
> It’s an easy and common mistake: you pick a “strong” key for the rate limit (here IP plus User-Agent, more specific than the IP alone) without noticing that part of it is under the control of the very person you want to limit. The User-Agent is decided by the browser, and an attacker changes it on every request with a single line of code: the key becomes new each time and the limit never trips. The defense is to pair a second layer on a key the client can’t forge at will, like the IP. The two layers work together: the first is precise on the normal cases, the second holds when the first gets bypassed.

---

## 4. Integrity Lives in the Schema, Not in the Code

A reaction works like a toggle: if you haven’t given it yet, a click adds it; if you already have it, another click removes it. This logic lives in the code, but that isn’t where the anti-duplicate guarantee lives. That lives in the table’s schema.

```sql
-- SPW migrate_reactions.php:19-27 — the UNIQUE KEY is the real anti-duplicate barrier
CREATE TABLE IF NOT EXISTS article_reactions (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    article_id  INT NOT NULL,
    reaction    VARCHAR(20) NOT NULL,
    voter_hash  VARCHAR(64) NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_vote (article_id, voter_hash, reaction)   -- a double vote impossible by construction
);
```

```php
// SPW reactions.php:129-145 — the toggle in the code; the INSERT IGNORE leans on the UNIQUE KEY
if ($existing) { /* DELETE: remove */ }
else { $pdo->prepare("INSERT IGNORE INTO article_reactions (article_id, reaction, voter_hash)
    VALUES (?, ?, ?)")->execute([$article_id, $reaction, $voter_hash]); }
```

The difference is subtle but decisive. An application-level check of the kind “read whether it exists, then insert” can be overtaken by a race condition: two near-simultaneous requests both read “it doesn’t exist” and both insert. The `UNIQUE KEY`, instead, refuses the duplicate regardless of what the code does, even under a double click or racing requests. It’s the principle of the database as the guardian of integrity, and it’s exactly what the festival’s denormalized vote counter lacks (Ch. 18), where the absence of an equivalent constraint leaves room for the mismatch.

> [!NOTE]
> **Let the database guarantee integrity**
> When a rule says “this combination can exist only once,” the right place to enforce it is a constraint in the schema, not an `if` in the application code. The constraint holds under concurrency, survives the bugs of the code running around it, and applies to every write path, present and future. The code can take care of the experience (the toggle, the message to the user); leave integrity to the engine that really knows how to defend it.

---

## 5. The Second Surface: Messages, and the Two Philosophies of Sanitization

The reactions are half the cluster. The other half is `messages.php`, the contact form. The table creates itself on the first call (the schema travels with the code, with a `CREATE TABLE IF NOT EXISTS` and a defensive `ALTER`), the `POST` is public with its own rate limit (three messages per IP every fifteen minutes, counted on its own table), and the notification to the administrator is a native fire-and-forget `mail()`: if the send fails, the visitor still sees “message sent,” because the record is already saved and the email is only a secondary channel (Ch. 13).

But the point that matters is how the text coming from outside is handled. It’s cleaned **before** touching the database.

```php
// SPW messages.php:86-90 — public input cleaned at WRITE-TIME: what enters the DB is already harmless
$name    = trim(strip_tags($data['name']    ?? ''));
$email   = trim(filter_var($data['email']   ?? '', FILTER_SANITIZE_EMAIL));
$subject = trim(strip_tags($data['subject'] ?? ''));
$message = trim(strip_tags($data['message'] ?? ''));
```

Here the thread of public input closes, and it does so with a polarity reversed from the articles. The content of an article (Ch. 8) is written by an admin you trust, is saved raw so as not to lose its rich formatting, and is cleaned with DOMPurify only **at the moment of showing it** (render-time). The text of a message comes from a stranger, and is cleaned with `strip_tags` **at the moment of saving it** (write-time): what ends up in the database is already free of tags, and stored XSS is neutralized at the source. There’s even a second safety net: the admin panel shows the message as a React text node, which rewrites the special characters on its own, and never uses `dangerouslySetInnerHTML`.

> [!IMPORTANT]
> **Write-time or render-time: where to clean input depends on who sends it to you**
> In the same codebase two opposite strategies live side by side, and neither one is wrong. Public, untrusted input has to be neutralized as early as possible, at the write: the fewer dangerous things you keep in the database, the better you sleep. Rich, trusted content (a formatted article), on the other hand, has to be preserved as it is and cleaned where fidelity matters, at the read, because cleaning it at the write would destroy the legitimate formatting. The question isn’t “write-time or render-time” in the abstract, but “who do I trust for this data”: the answer decides the moment. Getting the direction wrong isn’t elegant: saving public input raw opens stored XSS, cleaning editorial content at the write mutilates it.

A couple of side notes, for honesty. The public `POST` has no CSRF protection, and that’s correct: there’s no privileged action to forge, the only sensible barrier is the rate limit. And the form’s double GDPR-consent checkbox is verified **only on the client side**: whoever submits directly to the endpoint skips it. It’s consistent with the idea that consent is user experience and not a technical barrier, but it’s worth knowing.

---

## 6. Reaction vs. Vote: Tuning the Anti-Abuse to What’s at Stake

SimonePizziWebSite’s reactions and DISINTELLIGENZA’s festival vote (Ch. 18) are, technically, the same gesture: anonymous public writing defended by a hashed identity and an anti-duplicate barrier. But they serve two different purposes, and the rigidity is tuned accordingly. The reaction is free and plural: you can give more than one to the same article, remove them, put them back, and the anti-abuse is light because the stakes are low. The festival vote is single and watched: one expression per participant, an IP barrier on a twenty-four-hour window, a master switch that closes it off entirely, because there a ranking is being decided and the incentive to cheat is real.

> [!NOTE]
> **Same mechanics, two tunings: weigh the anti-abuse against what’s at stake**
> It’s pointless to police a “like” as if it were a ballot box, and dangerous to treat a vote that awards a prize with the lightness of a like. The same toolbox (derived identity, uniqueness constraint, rate limit) is tuned to two levels of rigidity depending on how much the abuse costs. Understanding where the stakes lie, before writing the anti-fraud code, is what avoids both needless friction and insufficient defense.

---

## 7. The Micro-Interaction: Optimistic, but with a Net

On the client the reaction bar updates the count and the button state **before** the server answers: the click feels instant. If the request fails, the update is rolled back and the UI returns to the real state. It’s the optimistic UI of the social platforms, with the rollback that makes it honest. Together with the degradation to a zero count seen in §1 (if the reactions don’t load, the article reads all the same), it’s how a “side” module never becomes a breaking point for the page.

---

## In Summary

Anonymous public writing is the most exposed point of the CMS, and SimonePizziWebSite defends it with care: a derived identity instead of the IP in cleartext, integrity enforced by the schema instead of by the code, a two-layer rate limit instead of one that can be bypassed, and input cleaned at the entrance instead of trusted. The lesson that ties it all together is the one about the two philosophies of sanitization: there’s no absolutely right place to clean input, there’s the question “who do I trust,” and the answer changes the direction of the defense. What’s left to remember is also what the module *isn’t*: the hash makes no one anonymous, it obfuscates them; the form’s consent is a courtesy, not a barrier. Knowing that, and not telling yourself the padlock is sturdier than it is, is part of the same technical honesty that runs through the whole book. Here the tour inside the CMS ends: from the foundations of the backend to the last click of a visitor we’ll never know the identity of.

> [!IMPORTANT]
> **The Canon**
> - For unauthenticated public writing, derive a pseudonym with a **salted** hash: an IP+UA hash without salt isn’t anonymity, it’s reversible.
> - If the rate-limit key includes client input (the User-Agent), you need a second layer anchored to the IP; leave integrity to the schema (`UNIQUE` + `INSERT IGNORE`).
> - Sanitize public input **at write-time** (`strip_tags`) and trusted content **at the render** (DOMPurify): it depends on who sends it to you.
> - Tune the anti-abuse to the stakes: a light reaction isn’t defended like a watched vote.

---
*End of Part V. The appendices gather the service materials: the checklist for starting from scratch, and the case of the fork (FDCA), the project that inherits an entire CMS, security debts included.*
