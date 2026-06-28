# CHAPTER 12: RSS Feed & Syndication

The RSS feed is the channel a site uses to deliver its content to people who don’t come read it on the site: aggregators, news readers, podcast apps, Telegram bots. In the Model it’s always the same thin-stack gesture: a PHP endpoint that, on every request, queries the database and prints the XML on the fly. No cron, no `.xml` file materialized on disk, no serialization library. A published article shows up in the feed on the first refresh.

But this chapter has a precise lens, and it’s the closing of a thread. In Chapter 8 we opened the picture of the four `content` emitters: the same HTML, saved raw in the database, exits toward the world from four points, each with its own defense. In Chapter 11 we saw the prerender leave the hole open. The feed is the emitter that **closes** it: in all three sites, either it doesn’t emit the `content` at all, or it escapes it in full. It’s the safest point in the chain.

And precisely because the three sites converge on security, it’s interesting how much they diverge on everything else. The geography runs from a single file to a trio of files with opposite roles, all the way to a feed that isn’t even a news feed but a podcast one. And on GUID discipline you see a small story of regression: a good idea solved by one site and forgotten by the other two.

> [!NOTE]
> **Three common misconceptions about these feeds.** Three points, often taken for granted, are actually wrong or misleading. The **podcast feed isn’t SitoRuntime’s but DISINTELLIGENZA’s**: SR doesn’t generate a podcast feed, it *consumes* external ones with a proxy (§4). The **empty catch** is sometimes taught as a virtuous “silent fallback”: it’s an anti-pattern instead, because it serves a truncated feed with HTTP 200 (§7). And **`feed.php` is not an “alias”** of `rss.php`: it’s DIS’s podcast feed, an endpoint with an entirely different purpose (§3).

---

## 1. The Common Anatomy of a Feed

Beneath the differences, the three sites’ feeds share the same skeleton. A single file, a `GET`, the XML printed live from the database. The example is SimonePizziWebSite’s `rss.php`, the most straightforward of the three:

```php
// public/api/rss.php (SPW) — the news feed, real-time from the DB
header('Content-Type: application/rss+xml; charset=utf-8');
$pdo = Database::connect();
date_default_timezone_set('Europe/Rome');                 // timezone forced in the individual file
$ita_now_str = date('Y-m-d H:i:s');
define('RSS_FEED_LIMIT', 50);

echo '<?xml version="1.0" encoding="UTF-8" ?>' . "\n<rss version=\"2.0\">\n<channel>\n";
echo '  <title>' . htmlspecialchars($site_title) . "</title>\n";
echo '  <link>'  . htmlspecialchars($base_url)   . "</link>\n";
echo '  <language>it-IT</language>' . "\n";
```

Three precautions recur in all three sites. Every dynamic field that enters the XML passes through `htmlspecialchars`: title, link, image URL, none of them ends up raw in the feed. The `Europe/Rome` timezone is re-forced inside the file itself, without trusting the timezone set elsewhere, because every file that compares dates against the database has to defend itself against a server in the wrong timezone (the lesson of Chapter 9). And the publication date always comes out in RFC-822 format, the one RSS 2.0 demands, via the `DATE_RSS` constant: never ISO 8601, which many readers reject.

There’s also a small shared asymmetry. While `sitemap.xml` and `robots.txt` are served from clean URLs via a rewrite (we saw it in Chapter 11), the feed is always reached at the raw URL of the PHP file: `/api/rss.php`, `/api/feed_news_rss.php`, `/api/feed.php`. None of the three sites gives it a clean `/feed.xml`. SEO care on the other assets, none here.

---

## 2. The Feed Closes the Thread of the Four Emitters

Let’s pick the table back up from Chapter 8. The same `content`, saved raw, exits from four emitters, and the only defense that really counts is the one each puts up on its own. The render uses DOMPurify (except DIS). The prerender uses `strip_tags` with an allowlist, which lets attributes through: it’s the live flaw of Chapter 11. The feed, the third emitter, closes it.

| # | Emitter | What it emits of the `content` | Defense | Outcome |
|---|---|---|---|---|
| 1 | **React render** (Ch. 8) | full `content` | DOMPurify (SPW, SR) / none (DIS) | real choke point; DIS exposed |
| 2 | **SEO prerender** (Ch. 11) | full `content` | `strip_tags` allowlist (tags only) | **attribute hole** (SPW, SR) |
| 3 | **RSS feed** (this chapter) | nothing (SPW, DIS) / escaped preview (SR) | `htmlspecialchars` / `strip_tags`+`htmlspecialchars` | **safe** |
| 4 | **Newsletter** (Ch. 13) | (the next chapter closes it) | — | — |

The feed is safe, but by two different roads. SPW is safe **by subtraction**: its `rss.php` loads the `content` column in the query but never prints it; the item’s `<description>` uses only the `excerpt`, escaped.

```php
// public/api/rss.php (SPW) — content SELECTed but NEVER emitted; description = escaped excerpt only
echo '    <description>' . htmlspecialchars($article['excerpt']) . "</description>\n";  // ← excerpt, not content
// (the content column is in the SELECT but there isn't a single echo of $article['content'])
```

SR, instead, **breaks the subtraction**: when the summary is missing, it falls back to the first 500 characters of the `content`. But it neutralizes them with a `strip_tags` without an allowlist, which removes *all* tags, followed by `htmlspecialchars`:

```php
// public/api/feed_news_rss.php (SR) — emits a preview of the content, but fully escaped
$descriptionText = $article['summary'] ?: $article['content_preview'] . '...';   // uses content if summary is missing
$description = htmlspecialchars(strip_tags($descriptionText));                    // strip_tags WITHOUT allowlist + escape
```

The difference from Chapter 11’s prerender is all here: there, `strip_tags` had an allowlist and left the tags (and their dangerous attributes); here it has no allowlist, so no tag survives, and that bit of text also gets turned into entities. DIS, for its part, doesn’t emit a news feed: its feed is a podcast one, and the news `content` is touched by no one.

> [!IMPORTANT]
> **Two ways to make a feed safe: don’t emit, or escape**
> The feed proves, in the positive, the thesis that runs through Chapters 8, 11, and 13: when the XSS defense lives in a single render, every other emitter has to fend for itself, and the feed manages it. SPW doesn’t emit the dangerous field (safe by subtraction: robust, but it loses information, no full article in the feed). SR emits it but escapes it in full (safe by escaping: more informative, but more fragile, because it would only take adding an allowlist back to `strip_tags` to reopen the hole, as happened in the prerender). Same outcomes, opposite philosophies. The conclusion is still the one from the thread: sanitization should live once, server-side, not be reinvented by every emitter. The picture closes completely in Chapter 13, where no one emits the `content`.

---

## 3. The Geography: One File, a Trio, a Podcast Feed

On form, the three sites couldn’t be more different.

SPW is a single file, `rss.php`: a news feed, minimal and rigorous. SR is a trio, and here lies its complexity: `feed_news_rss.php` generates the site’s news feed, `rss.php` (same name as SPW’s, opposite role) is a proxy that *consumes* external feeds, and `feed_config.php` is a dispenser that serves the admin the feed address. DIS is a case of its own: no news feed, only `feed.php`, a **podcast** feed in RSS 2.0 with the iTunes namespace, subscribable from an app like Apple Podcasts.

> [!NOTE]
> **Producing a podcast feed, or consuming one: not the same thing**
> It’s an easy point to confuse. The site that *generates* a podcast feed is DIS, with `feed.php`: it reads the `podcasts` table and emits the episodes with an audio `<enclosure>` and the `<itunes:*>` tags. SR does the opposite: it generates no podcast feed, but with `rss.php` it *downloads* other people’s podcast feeds (Spreaker, its own AzuraCast) to show them on the site. Producing and consuming a feed are two mirror operations, and it’s precisely the contrast between these two sites that makes it plain. We see it in the next section.

---

## 4. The Inbound CORS Proxy: Consuming Other People’s Feeds

A browser can’t read a feed hosted on another domain if that domain doesn’t send CORS headers, and external podcast feeds usually don’t. SR solves this with a server-side proxy: `rss.php` downloads the other feed and returns it same-origin. The interesting part is the defense, because a proxy that downloads whatever URL you hand it is an *open proxy*, a door flung wide to SSRF attacks.

```php
// public/api/rss.php (SR) — inbound proxy: allowlist + https-only + stale fallback
$allowedHosts = ['www.spreaker.com', 'spreaker.com', 'player.runtimeradio.com'];
if ($scheme !== 'https' || !in_array($host, $allowedHosts, true)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Feed URL not allowed']); exit;   // no open proxy
}
// ... disk cache rss_<md5>.xml, TTL 30 min ...
if ($xml === false || $httpCode !== 200) {
    if (file_exists($cacheFile)) { header('X-Cache: STALE'); readfile($cacheFile); exit; }  // a stale cache beats nothing
}
```

Two sound choices: an allowlist of hosts (the proxy downloads only from those domains) and the HTTPS requirement close the SSRF door; a disk cache with a “stale” fallback means that, if the upstream is down, the last good copy is served instead of failing. There is, though, a less sound detail on the client side: if the site’s proxy doesn’t respond, the frontend code falls back to public third-party proxies (CodeTabs, AllOrigins), which don’t know the allowlist. Resilience is bought with an undeclared dependency on third parties.

> [!WARNING]
> **A proxy that downloads URLs is an SSRF target**
> Any endpoint that, on request, downloads a URL supplied from outside has to be treated as a potential lever to reach internal resources (cloud metadata, services on `localhost`, private IPs). The two defenses in `rss.php` are the correct minimum: an explicit allowlist of trusted hosts and the rejection of anything that isn’t HTTPS. The rule is the same as Chapter 10’s on the IP: don’t trust a value that arrives from the client, in this case the URL to download. And watch the fallbacks: the client’s fall-through to public proxies sidesteps the allowlist and is worth knowing about.

---

## 5. `feed_config.php`: The Lock on the Door Next to It

In SR’s trio there’s a third file that’s worth a box of its own, because it’s a textbook case of apparent security. `feed_config.php` is protected by `isAdmin()` and its comment promises a lot: “Returns the private RSS feed URL only to authenticated admins. The token is never exposed in the public JavaScript bundle.”

```php
// public/api/feed_config.php (SR) — gates the URL, but the endpoint is public
require_once 'auth_utils.php';
if (!isAdmin()) { http_response_code(403); echo json_encode(['success'=>false,'error'=>'Forbidden']); exit; }
$origin = (/* https */ . '://' . $_SERVER['HTTP_HOST']);
echo json_encode(['success' => true, 'feed_url' => $origin . '/api/feed_news_rss.php']);
```

Two things don’t add up. There is no token: the returned URL is bare. And above all the feed that URL reaches, `feed_news_rss.php`, is **completely public**: it doesn’t include `auth_utils.php`, doesn’t call `isAdmin()`, anyone can read it without logging in. The `isAdmin()` gate protects the act of *discovering* an address that’s public and guessable anyway.

> [!WARNING]
> **The lock on the door next to it**
> Putting a gate on the dispenser of a URL doesn’t make the endpoint that URL reaches private. It’s security through obscurity, and the obscurity here isn’t even there, because the file name is predictable. Almost certainly it’s the fossil of an intention never realized: an authenticated news feed with a token for the Telegram bot (consistent with the `TELEGRAM_BOT_TOKEN` that lives in the secrets, Chapter 10), designed and never built. The lesson: if an endpoint has to be private, the authentication goes on *that endpoint*, not on the slip of paper that carries its address.

---

## 6. The GUID That Republishes

Every `<item>` in a feed has a `<guid>`, the identifier consumers use to recognize whether a piece of content is new or already seen. Getting it wrong has a concrete, annoying consequence: if an article’s GUID changes, aggregators and bots treat it as a new article and republish it. On a Telegram integration, that means spamming every subscriber all over again.

SPW solved the problem cleanly: the GUID is a URN built on the database ID, decoupled from the URL.

```php
// public/api/rss.php (SPW) — stable GUID, independent of the URL
$stable_guid = 'urn:simonepizzi:article:' . (int)$article['id'];
echo '    <guid isPermaLink="false">' . $stable_guid . "</guid>\n";
```

This way a change of slug or category doesn’t touch the article’s identity: to consumers it stays the same content. It’s the same concern that, on the URL side, justifies 301 redirects: keeping a page’s identity stable even when its address changes.

The other two sites lost this idea. SR uses the permalink as the GUID, with `isPermaLink="true"`: at the first slug change, the article republishes (and SR doesn’t even have 301s to act as a safety net). DIS goes lower still and uses the audio file’s URL: all it takes is for `migrate_media` to move the audio and every episode is “new” again in the podcast apps.

> [!TIP]
> **An article’s stable identity: a URN, not the permalink**
> The URN GUID is the correct recommendation. What needs adding is that it’s a best practice two sites out of three **don’t** follow: SPW applies it, SR regressed to the permalink, DIS to the audio URL (the least stable of all). The rule, in one line: a feed item’s identity has to depend on something that never changes (the database ID), never on the address, which changes plenty.

---

## 7. The Empty Catch That Hides a Database Down

There’s a point often mistaken for a virtue, and wrongly so. Both SPW and DIS wrap the query in a `try/catch` with an **empty** `catch`:

```php
// public/api/rss.php (SPW) — the empty catch: the header and <channel> have already gone out with HTTP 200
} catch (Exception $e) {
    // silent fallback: no log, no 5xx
}
echo "</channel></rss>";
```

The problem is the sequence. By the time the exception fires, the `Content-Type` header and the opening of the `<channel>` have already been printed, with response code 200. The empty `catch` swallows the error, and the closing `</channel></rss>` comes out anyway: the client receives a perfectly well-formed and **empty** feed, indistinguishable from “no news.” No log, no 500, no signal. A database down becomes invisible.

SR does better, though not perfectly: it intercepts the exception and responds with a real HTTP error.

```php
// public/api/feed_news_rss.php (SR) — at least it signals the failure
} catch (PDOException $e) {
    http_response_code(500);
    echo "<error>Database Error</error>";   // (covers only PDOException: a non-PDO error would slip through)
}
```

> [!WARNING]
> **The silent fallback that hides a failure**
> An error disguised as a valid response is worse than a visible error: no one notices it until a user complains that the feed “hasn’t updated in a week.” The rule is not to open the response (header and first output) before running the part that can fail, or to handle the failure with an honest HTTP code, as SR tries to do. The empty `catch` isn’t a fallback: it’s a silenced failure.

---

## 8. Minor Scars

Some smaller details, but real ones. The visibility filter from Chapter 9 (`status = 'published'`) is forgotten here too: SR’s news feed filters on the date alone, so a draft with a past date leaks into the feed, the third file after `index.php` and the sitemap to forget the same rule. The image’s `<enclosure>` declares `type="image/jpeg"` hardcoded, but the upload converts covers to WebP (Chapter 7): the pickier readers discard a thumbnail whose MIME doesn’t match. And in both flagships the channel configuration (title, description) is hardcoded, with a comment that promises to read it “from the settings”: an announced configurability never wired up, of which DIS is the extreme version (it reads `podcast_*` keys that no one populates, so it always runs on the defaults).

On DIS there’s also a detail that’s almost an artifact. The `feed.php` contains comments where the code reasons out loud with itself:

```php
// public/api/feed.php (DIS) — the code debating its own doubts, in production
// During init_db.php step I created a 'podcasts' table? Let's check init_db.php if I can.
// Fallback: ... create it via SQL here? No, bad practice on GET.
// I'll assume it exists or use NEWS with a category.
```

> [!NOTE]
> **When the code narrates its doubts**
> It isn’t a bug, but it’s a process scar: the portrait of a codebase generated in conversation with an assistant, and never reread before deploy. The same tone shows up in other DIS files (the `init_db.php`, the `api.ts`). In production the code should assert, not question itself: these monologues should be removed in the rewrite, because they reveal, to anyone who opens the source, exactly what the author hadn’t verified.

---

## 9. Announcing and Delivering the Feed

A feed is of little use if no one finds it. It has to be announced in the HTML’s `<head>`, so browsers and RSS readers discover it on their own:

```html
<link rel="alternate" type="application/rss+xml" title="Feed Notizie" href="/api/rss.php" />
```

And it has to be delivered to the distributors. SPW has a “Copy RSS” button in the admin area, which puts the address on the clipboard with a click; SR shows the URL in the dashboard (that’s what `feed_config.php` is really for, once the pretense of privacy is stripped away). A small editorial UX touch: giving whoever publishes a way to hand the feed to an aggregator or a bot without transcribing it by hand.

---

## In Summary

The feed is the quietest part of the content’s journey: the emitter that closes the XSS hole, by subtraction or by escaping. But around this quiet the three sites tell three different stories: SPW is minimal and disciplined (stable GUID, visibility rule respected, errors aside); SR is richer and more fragmented, with a well-defended inbound proxy, a dispenser that feigns a privacy that isn’t there, and a few regressions (the drafts in the feed, the GUID that republishes); DIS does only podcasts, on the defaults, with the author’s doubts still written in the code. The thread of the four emitters, meanwhile, has one last box to fill: the newsletter.

> [!IMPORTANT]
> **The Canon**
> - A valid RSS 2.0 feed: correct header, RFC-822 dates, absolute URLs, `content` escaped (or not emitted at all).
> - The feed is a `content` emitter: either you escape it fully or you don’t put it in.
> - A stable GUID with `isPermaLink="false"` (a URN), not the mutable permalink.
> - No empty `catch` that masks a failure: better an explicit 5xx. An inbound proxy has to be protected with a host allowlist + https-only (anti-SSRF).

---
*Next Chapter: Newsletter & Email System. The last emitter of the content, the one that closes the thread completely, and a scale of how far you can simplify a mail system before it becomes dangerous.*
