# CHAPTER 13: Newsletter & Email System

An email list is one of the few assets a site truly owns: it doesn’t pass through an algorithm, it doesn’t risk a shadowban, it doesn’t vanish if a platform shuts down. The three sites in the Model all have a homegrown newsletter, with no external services, and they all build it on the same thin-stack skeleton: a PHP endpoint that handles subscription and sending, and the email composed as an HTML string on the fly.

This chapter closes a thread that began five chapters ago. The newsletter is the **fourth and last emitter** of the `content`: after the render (Chapter 8), the prerender (Chapter 11), and the feed (Chapter 12), it’s the last place from which the same raw-saved HTML could exit toward a browser, the mail client’s. The good news, which we’ll see at the end, is that none of the three sites emits the `content` in the email: the thread closes without reopening the XSS hole.

And precisely because the three converge on the XSS risk, the chapter’s real lens becomes another one: **how far you can simplify a mail system** before the simplification becomes dangerous. It runs from a complete system, with double opt-in and anti-abuse protection, all the way to a bare `mail()` that anyone can use to subscribe or unsubscribe anyone. And, as in Chapter 10, the site with the richest backend isn’t the most secure.

> [!NOTE]
> **Three points it’s easy to get wrong.** Three aspects of this system are often misunderstood. The first is **double opt-in**, the cornerstone feature of two sites out of three: omitting it, and showing in its place a subscription that’s active immediately with unsubscribe-by-email-only, means adopting DIS’s model, the weakest. That unsubscribe-by-email-only **isn’t “GDPR-compliant”**: it’s the insecure version (anyone unsubscribes anyone). And a `usleep` **isn’t “rate limiting”**: it’s a different thing (§4).

---

## 1. The Life of a Subscriber

Beneath the differences, the anatomy is shared. The endpoint dispatches by `?action=`, with the public actions served before a central gate and the admin ones after. The email is always validated server-side, without trusting the form, and re-subscription is handled reactively: you attempt the `INSERT` and catch the UNIQUE constraint violation, returning a neutral success that doesn’t reveal who’s already on the list.

```php
// public/api/newsletter.php (DIS) — server-side validation + idempotence by catching the duplicate
$email = filter_var($input['email'] ?? '', FILTER_VALIDATE_EMAIL);
if (!$email) { echo json_encode(['status'=>'error','message'=>'Email non valida']); exit; }
try {
    getDB()->prepare("INSERT INTO subscribers (email) VALUES (?)")->execute([$email]);
    echo json_encode(['status'=>'success','message'=>'Iscrizione completata']);
} catch (PDOException $e) {
    if ($e->getCode() == 23000) {   // UNIQUE violation → already subscribed, but we don't reveal it as an error
        echo json_encode(['status'=>'success','message'=>'Sei già iscritto!']);
    } else { echo json_encode(['status'=>'error','message'=>'Errore database']); }
}
```

The unsubscribe is “soft”: no one deletes the record, the subscriber is flagged `is_active = 0`, which preserves the history and avoids accidental re-subscriptions. And the final email, whatever the site, is built as an HTML string with a table-based layout and inline CSS (mail clients don’t read external stylesheets), with the images made absolute and a placeholder in the unsubscribe link, substituted for each recipient.

> [!NOTE]
> **The minimal schema isn’t the real one.** The four-column `subscribers` table (`id`, `email`, `is_active`, `created_at`) is DIS’s model. The real schema of SPW and SR instead has the double opt-in fields: the status (`pending`/`confirmed`/`unsubscribed`), one or more tokens, the confirmation date. In SR that extended schema coexists with two older versions created by other scripts, one of which is an SQLite fossil that would break on MySQL: the runtime assumes the extended schema and one query fails until the right migration has been run. It’s the same “one table, several truths” story from Chapter 15.

---

## 2. Double Opt-In and the Secret of the Unsubscribe Link

Double opt-in is the guarantee that whoever subscribes an email **owns** that mailbox: instead of activating the address right away, you create a pending record and send an email with a confirmation link; only after the click does the subscription become active. It’s the most important feature of the whole system, and the three sites implement it on three rungs.

SPW does it the textbook way, with **two distinct tokens**: a confirmation one, single-use, cleared after use; an unsubscribe one, random and stable, separate from the first.

```php
// public/api/subscribers.php (SPW) — two tokens with different purposes
$confirmToken     = $forceConfirm ? null : bin2hex(random_bytes(32));   // single-use
$unsubscribeToken = bin2hex(random_bytes(32));                          // stable, separate
$status           = $forceConfirm ? 'confirmed' : 'pending';
if (!$forceConfirm) { sendConfirmEmail($email, $name ?: 'Amico', $confirmToken); }
```

SR does it with **a single token** that serves both purposes, confirmation and unsubscribe, and that’s never cleared or expired. Two small consequences follow. The confirmation email promises that “the link expires after first use,” but that’s false: the token survives use. And since the same token ends up in the unsubscribe URL of *every* newsletter, anyone who forwards a message hands someone else the power to unsubscribe that user.

```php
// public/api/newsletter.php (SR) — one token, two purposes
// confirm: activates the subscription BUT doesn't clear the token
"UPDATE subscribers SET is_active = 1, confirmed_at = NOW() WHERE confirmation_token = ?"
// send: the unsubscribe URL exposes the same confirmation_token
$unsubUrl = 'https://runtimeradio.com/unsubscribe?token=' . urlencode($sub['confirmation_token']);
```

DIS has neither. The subscription is active immediately, and unsubscribe happens by email alone, with no token:

```php
// public/api/newsletter.php (DIS) — unsubscribe by email alone, via GET, with no token
if ($action === 'unsubscribe') {
    $email = filter_var($_GET['email'] ?? '', FILTER_VALIDATE_EMAIL);
    getDB()->prepare("UPDATE subscribers SET is_active = 0 WHERE email = ?")->execute([$email]);
    echo "<h1>Disiscrizione completata</h1>";   // anyone who knows the email can unsubscribe it
}
```

> [!WARNING]
> **The unsubscribe link needs a secret**
> This unsubscribe-by-email-alone is often passed off as “GDPR-compliant.” It’s the opposite: without a secret token, anyone who knows or guesses a subscriber’s address can unsubscribe them. And since it’s a `GET`, it’s also *prefetchable*: a mail client that preloads links can unsubscribe the user just by hovering over it. The correct version is SPW’s, with a random, stable `unsubscribe_token` (and, ideally, a `POST` confirmation from the landing page). Double opt-in protects the entrance; an unsubscribe token protects the exit. You need both.

---

## 3. Sending: Native `mail()` or Authenticated SMTP

Transport is the point where SR breaks away from the other two. SPW and DIS use PHP’s native `mail()`, which leans on the system sendmail: zero configuration, but fragile deliverability, because without SPF and DKIM the emails easily land in spam (DIS even has a “Fake domain?” comment next to the sender). SR, instead, uses PHPMailer with authenticated SMTP and STARTTLS, reading the credentials from the environment secrets.

```php
// public/api/newsletter.php (SR) — authenticated SMTP via PHPMailer
$mail = new \PHPMailer\PHPMailer\PHPMailer(true);
$mail->isSMTP();
$mail->Host = $cfg['SMTP_HOST']; $mail->SMTPAuth = true;
$mail->Username = $cfg['SMTP_USER']; $mail->Password = $cfg['SMTP_PASS'];
$mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS; $mail->Port = $cfg['SMTP_PORT'];
$mail->setFrom($cfg['SMTP_USER'], $cfg['SMTP_FROM_NAME']);
```

There’s an internal contradiction, though: SR uses authenticated SMTP only for the newsletter. The contact form, `contact.php`, stayed on native `mail()`. The same site thus has two different mail mechanics: it’s easy to think of SMTP as a choice “for the future, at higher volumes,” when in reality in SR it’s already in production, alongside the `mail()` it never retired.

---

## 4. The Form That Fires Emails in Your Name

Here comes the chapter’s most instructive flaw, and it’s born of a common confusion between two defenses that look similar and aren’t.

A **throttle** slows the outgoing send, so as not to overload the mail server and get greylisted: it’s a pause every so many emails. A **rate limit** caps incoming requests, to keep a stranger from abusing an endpoint: it’s a ceiling of attempts per IP. They’re orthogonal defenses, on opposite sides of the system. What often gets called “rate limiting” is really a throttle:

```php
// public/api/newsletter.php (SR) — this is an OUTBOUND THROTTLE, not an inbound rate limit
if ($count % 10 === 0) { usleep(500000); }   // half a second every 10 emails: protects the mail server
```

The throttle protects *your* mail server. It doesn’t protect against someone hammering the subscription form. And here’s SR’s hole: its `subscribe` has no rate limit at all. The requester’s IP is even recorded, but only stored, never used as a limit, and on top of that read from raw `X-Forwarded-For` (forgeable, as in Chapter 10). Anyone can therefore send subscription requests with arbitrary emails, and each one fires a real confirmation email via SMTP toward a third party who asked for nothing. It’s a mail-bombing vector that burns the domain’s reputation and consumes the SMTP quota.

SPW, instead, closes the vector, reusing for the newsletter the same `login_attempts` table as the login (with a different key prefix, so as not to mix the counters):

```php
// public/api/subscribers.php (SPW) — anti-mail-bombing rate limit that recycles login_attempts
$rl_key = 'sub:' . substr(hash('sha256', $_SERVER['REMOTE_ADDR'] ?? 'unknown'), 0, 40);
$stmtRl = $pdo->prepare("SELECT COUNT(*) FROM login_attempts WHERE ip_address = ?");
$stmtRl->execute([$rl_key]);
if ((int)$stmtRl->fetchColumn() >= 3) { http_response_code(429); exit; }   // max 3 subscriptions / 15 min
```

> [!WARNING]
> **Inbound rate limit ≠ outbound throttle**
> SR has the throttle but not the rate limit; SPW has the rate limit but not the throttle. They have opposite defenses, and the one SR lacks is the one that matters most for security: without an inbound ceiling, the subscription form becomes a weapon that fires emails in your name toward anyone. It’s the reversal already seen in Chapter 10: SR, the most engineered site, leaves open exactly the hole that SPW, simpler, had closed. And the irony is that the infrastructure to limit (the same `.cache/ratelimit/` as the login) already exists in SR: it simply wasn’t reused here.

There’s then a problem common to all three, on a descending scale of crudeness: sending is a blocking `foreach` inside the HTTP request. On a large list, the request hits `max_execution_time` and delivery cuts off halfway, without anyone knowing. SR is the least bad (it has the throttle and a per-recipient `try/catch` that counts errors); SPW counts only `mail()`’s return value; DIS ignores it entirely, and the campaign counter records the *attempts*, not the successes. None of the three has a queue or a cron: it’s the same “heavy work inside the request” anti-pattern seen with image conversion in Chapter 7.

---

## 5. Header Injection from the Name Field

One last trap, and it’s in DIS, in the contact form. The name entered by the user is cleaned with `strip_tags` before landing in the database, and that’s fine for the database. But that same name is also placed in the subject of the notification email to the admin, and there `strip_tags` isn’t enough:

```php
// public/api/contact.php (DIS) — strip_tags removes tags, NOT line breaks
$name    = strip_tags($input['name'] ?? '');                       // sanitization for the DB
$subject = "Nuovo Messaggio da $name - Disintelligenza";           // ...but $name ends up in the Subject header
$headers = "From: no-reply@...\r\nReply-To: $email\r\n";
mail('runtimeradio@gmail.com', $subject, $body, $headers);
```

`strip_tags` removes HTML tags, but not the line-break characters `\r\n`. A name that contains them can inject additional headers into the email, for example a `Cc` or a `Bcc` toward addresses chosen by the attacker. The sender’s email, which ends up in the `Reply-To`, is instead safe because it’s passed through `FILTER_VALIDATE_EMAIL`: the vector is the name, the only free text field that enters a header.

> [!WARNING]
> **Sanitizing for the database isn’t sanitizing for email headers**
> Sanitization always has a context. `strip_tags` neutralizes HTML, which is the danger when the data will be shown on a page; but when the same data enters a mail header, the danger changes shape, and it’s the `\r\n` that count. The rule: for an email header, remove or reject control characters, and never put user input in the headers if you can avoid it. SR, not by chance, builds the `From` from a fixed value, not from input.

---

## 6. The Thread of the Four Emitters Closes

Let’s go back one last time to the table from Chapter 8. The newsletter is the fourth box, and in all three sites the send query selects title, summary, image, and link, **never the `content`**. The email links back to the article with a “Read more,” and the raw HTML field defended only at render-time is never touched.

| # | Emitter | What it emits of the `content` | Defense | Outcome |
|---|---|---|---|---|
| 1 | **React render** (Ch. 8) | full `content` | DOMPurify (SPW, SR) / none (DIS) | real choke point; DIS exposed |
| 2 | **SEO prerender** (Ch. 11) | full `content` | `strip_tags` allowlist (tags only) | **attribute hole** (SPW, SR) |
| 3 | **RSS feed** (Ch. 12) | nothing / escaped preview | `htmlspecialchars` / `strip_tags`+escape | safe |
| 4 | **Newsletter** (this chapter) | **nothing** (title, summary, intro only) | `htmlspecialchars` (SR, DIS) / raw behind Auth (SPW) | **safe** |

You could read the query-without-`content` as a simple “payload optimization,” to keep the emails light. That’s true, but above all it’s the closing of the thread: not emitting the raw field is what keeps the email from becoming a fifth XSS vector.

There’s a curious symmetry between the two flagships. In SR the newsletter is the *most* secure of the four emitters: it doesn’t touch the `content` and on top of that escapes every other field. In SPW it’s instead the *least* sanitized, because the introductory text written by the admin is emitted raw, with no `htmlspecialchars`: it’s safe only because whoever writes it is authenticated, not because there’s a defense. Two opposite positions on the same scale.

> [!IMPORTANT]
> **The full picture: one sanitization, four render paths**
> With the newsletter, the thread of the four emitters closes. Feed and newsletter don’t reopen the hole, because they either don’t emit the `content` or they escape it. The only flaw still live in the whole picture is the prerender of Chapter 11, with its allowlist `strip_tags` that lets attributes through. The conclusion, repeated for five chapters, is always the same: content sanitization should live once, server-side, shared by every emitter, instead of being reinvented (or forgotten) by each one. That the hole stayed open in only one point out of four isn’t to the architecture’s credit: it’s luck, plus the discipline of whoever wrote the other three.

---

## 7. Consent, and Where It Disappears

What remains is the GDPR side of subscription, which isn’t only a matter of tokens but of consent. On the form, SPW asks for double explicit agreement (data processing and a declaration of legal age); SR asks for only one, and has a “minimal” variant of the form, meant for the footer, that has no checkbox at all. DIS, on the form, just validates and that’s it.

But the most interesting case is in DIS, and it doesn’t even go through the form. An email can enter the list from a second door too: when a festival participant is approved, their address is added to the subscribers with an `INSERT OR IGNORE`, **with no explicit consent to the newsletter**. The comments in the code show the same developer wondering whether it’s correct.

> [!WARNING]
> **Consent as a side effect**
> Subscribing someone to a list because they did *something else* (applying to a festival) is a collection of consent that the GDPR doesn’t consider valid: consent has to be specific to that purpose. It’s an easy trap, because the code that does it looks harmless: a line of `INSERT` tacked onto the approval. The rule: every entry door to an email list must have its own consent, explicit and separate. The full treatment of the festival workflow is in the chapters that cover it; here the lesson is enough.

---

## In Summary

The newsletter shows a scale of simplification that’s also a scale of risk. SPW is the complete rung: double opt-in with two distinct tokens, a rate limit against mail-bombing, an unsubscribe link with a secret, double consent. SR adds the more serious transport, authenticated SMTP, but removes the rate limit (and opens the mail-bombing vector) and merges the two tokens into one. DIS removes the double opt-in and every token too, and leaves a header injection in the contact form’s name field, while keeping two good hygiene habits (email validation everywhere and cleanup on write). On the `content`, though, all three do the right thing: they don’t emit it, and the thread of the four emitters closes. The defense that’s missing most often isn’t the one against XSS, which here is solved by discipline: it’s the one against abuse of your own form.

> [!IMPORTANT]
> **The Canon**
> - Double opt-in with two distinct tokens (single-use confirmation + stable unsubscribe): the unsubscribe link needs a secret, the cleartext email isn’t enough.
> - A rate limit (per-IP ceiling) on subscription against mail-bombing; don’t confuse it with the throttle, which only regulates send cadence.
> - Sanitize for the email headers (the `\r\n`), not only for the DB: the name is a header-injection vector.
> - Explicit GDPR consent; mass sending, better if asynchronous or queued.

---
*Next Chapter: Admin Dashboard & Panels. The control panel that ties together the systems seen so far, and the three very different ways the sites decide what an administrator can see and do.*
