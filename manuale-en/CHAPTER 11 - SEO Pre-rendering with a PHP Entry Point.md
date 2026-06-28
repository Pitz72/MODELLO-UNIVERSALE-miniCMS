# CHAPTER 11: SEO Pre-rendering with a PHP Entry Point

A Single Page Application has a birth defect when it comes to search engines. Google’s bot, or the Telegram crawler that generates a link preview, receives from the server an almost-empty `index.html`: a `<div id="root"></div>` and a JavaScript bundle. The real content only arrives after that JavaScript runs, and many crawlers don’t execute it. The result is a page that, to the bot, has no sensible title, no description, no preview image, and no text to index.

The Model solves this without an SSR framework, without Next.js, without Node. It puts a PHP file in front of the SPA, has it query the database, and has it inject the correct meta tags in the right places, before the HTML reaches the bot. It’s the thin-stack version of server-side rendering: a few hundred lines of PHP and zero new infrastructure.

But this chapter has three threads to hold together. The first is a story of attempts: the winning pattern isn’t the first one that was tried, and along the way the two flagships discarded a solution that, at first glance, looks the most natural. The second is a three-rung scale: the two flagships do full Dynamic Rendering, DIS stops at a social-preview proxy, and the most capable rung carries three debts with it. The third is the security thread opened in Chapter 8: the prerender is the `content` emitter where the XSS hole of the “four emitters” is **still live**.

> [!NOTE]
> **A temptation to avoid: Static Prerendering (SSG).** For deep indexing you might be tempted to add, on top of meta injection alone, a **Static Prerendering** step at build time (something like `vite-plugin-prerender`). But that’s **exactly the Puppeteer-based SSG that SimonePizziWebSite tried and then abandoned** (§1): today in its repo it’s nothing but dead code, complete with a post-mortem. The solution the flagships actually adopted is **Dynamic Rendering**. Watch out, too, for a detail that misleads: a setup with a `.sqlite` file and a direct connection isn’t SPW’s engine, which runs on MySQL, but DIS’s proxy.

---

## 1. The Problem, and Three Attempts to Solve It

The story of prerendering in SPW is a three-stage path, and telling it explains how the final pattern came to be.

The first stage (v1.7.3) injected only title, description, and Open Graph into the `<head>`. That was enough for social previews, but not for Google: the crawler found the correct meta tags and a still-empty `<body>`, and indexed very few pages.

The second stage was **SSG with Puppeteer**: a Node script that, at build time, prerendered every route into a static HTML file on disk. Technically it worked. But it was conceptually wrong for a CMS, and the post-mortem says so plainly: it broke the “edit online, publish” flow (you needed a local build and an FTP upload for every article), it froze the data at build time, and it dragged a chain of complications behind it (an anti-CORS bridge, a `dist-static` buffer, the render events). It was abandoned.

The third stage, the current one, is **Dynamic Rendering**: no build, no static files. A single `index.php`, in real time, decides what to serve depending on who’s asking.

> [!TIP]
> **The code that’s left after the strategy changes**
> Of the abandoned SSG, what remains in SPW is the fossil imprint: `prerender.php` is deprecated (it only returns a warning), `prerender.js` and `prerender-routes.js` are dead code (the `postbuild` runs `clean-dist.js`, not them), and an `IS_PRERENDERING` constant guards branches that no one defines anymore. SR, which came later, went straight to Dynamic Rendering and has no fossils. It’s a small archaeological reminder: when you change strategy, the code of the old strategy rarely disappears: it sits there, inert, until someone trusts the change enough to delete it.

---

## 2. Dynamic Rendering: Everything in a Single `index.php`

The winning pattern concentrates everything in `public/index.php`, which `.htaccess` places ahead of `index.html` and to which it routes every virtual React Router URL. For each request, in real time, the file does four things: it deduces from the path what type of page it is, queries the database for the real data, and then chooses between two paths depending on who’s asking.

The choice runs through `isCrawler()`, which sniffs the `User-Agent`:

```php
// public/index.php:46-86 (SPW) — the crawler-vs-human fork
function isCrawler(): bool {
    $ua = $_SERVER['HTTP_USER_AGENT'] ?? '';
    if (empty($ua)) return false;
    $crawlers = ['Googlebot', 'Bingbot', 'facebookexternalhit', 'Twitterbot',
                 'TelegramBot', 'WhatsApp', 'Discordbot', /* … */];
    foreach ($crawlers as $bot) { if (stripos($ua, $bot) !== false) return true; }
    return false;
}
$isCrawler = isCrawler();
if ($isCrawler && $pageType !== 'admin') { /* full server-side HTML for the bot */ }
else { /* Vite's index.html + meta injected into the head; React builds the body */ }
```

The real user gets Vite’s `index.html` with the meta tags and JSON-LD injected into the `<head>`, and React builds the `<body>` as always. The crawler, instead, gets already-complete HTML, with the title, the meta tags, and the **article body** written directly into the `<body>`, so the bot indexes without executing a single line of JavaScript. The file explicitly claims this isn’t cloaking: the content served to the bot is the same one the user sees after React hydrates.

For this to work, the PHP has to know the routes as well as React Router knows them, and here lies the method’s first cost:

```php
// public/index.php:133-154 (SPW) — server-side routing that mirrors React Router
if (count($uri_parts) === 0)             $pageType = 'homepage';
elseif ($uri_parts[0] === 'admin')       $pageType = 'admin';      // no SEO for the admin area
elseif ($uri_parts[0] === 'tutti-i-progetti') $pageType = 'projects';
elseif (count($uri_parts) === 2) { $pageType = 'article';  $catSlug = $uri_parts[0]; $slug = $uri_parts[1]; }
elseif (count($uri_parts) === 1) { $pageType = 'category'; $catSlug = $uri_parts[0]; }
```

> [!WARNING]
> **The price of not having an SSR framework: the double truth of the routes**
> The routes now live in two places: in `App.tsx` for React, and in `index.php` for the bots. Adding a public page means touching both. A new route that the PHP doesn’t know about falls into the default branch, and the bot receives the wrong meta tags with no one noticing. It’s the compromise of hand-rolled Dynamic Rendering: no infrastructure, but a map you have to keep aligned by hand in two different languages.

The injection itself is a surgical operation on the HTML compiled by Vite: you remove the `<title>` generated by the build and insert the SEO block before `</head>`.

```php
// public/index.php:576-614 (SPW) — meta injection + removal of Vite's title
$seoInjection = '<title>' . $metaTitle . '</title>'
    . '<meta name="description" content="' . esc($metaDesc) . '" />'
    . '<link rel="canonical" href="' . esc($canonicalUrl) . '" />';   // + OG/Twitter
if ($jsonLd) { $seoInjection .= '<script type="application/ld+json">' . json_encode($jsonLd) . '</script>'; }
$htmlContent = preg_replace('/<title>.*?<\/title>/s', '', $htmlContent, 1);  // avoid the double title
$htmlContent = str_replace('</head>', $seoInjection . '</head>', $htmlContent);
```

Every value coming from the database passes through an `esc()` (that is, `htmlspecialchars`) before it lands in an attribute. Every value, with one exception that is the heart of §4: the article body.

---

## 3. The Three-Rung Scale: Dynamic Rendering or OG-Proxy

The two flagships do the same thing. SR copied SPW’s engine almost to the letter: same `isCrawler()`, same helpers (`esc`, `truncateText`, `absImageUrl`), same injection. The most visible difference is cosmetic (SR derives `baseUrl` from `$_SERVER['HTTP_HOST']`, SPW uses its canonical `SITE_URL`) and the type of structured data: SPW emits `Article` and `CollectionPage`, SR adds a `RadioStation` suited to its domain. But the setup is the same.

DIS sits on a different rung. Its `index.php` isn’t a Dynamic Rendering engine: it’s a social-preview proxy, and it says so. It doesn’t sniff the `User-Agent`, so it serves everyone the same HTML (no cloaking risk) and injects only the meta tags, leaving the body to React. And it writes those meta tags by passing every value through `htmlspecialchars`:

```php
// public/index.php:93-109 (DIS) — escape-safe meta injection, no prerendered body
function injectTag($html, $tag, $content, $property = null) {
    if (!$content) return $html;
    if ($tag === 'title')
        return preg_replace('/<title>.*?<\/title>/s', "<title>".htmlspecialchars($content)."</title>", $html);
    $attr = $property ? "property" : "name";
    return /* inserts */ '<meta '.$attr.'="'.$tag.'" content="'.htmlspecialchars($content).'" />';
}
```

> [!TIP]
> **Full Dynamic Rendering or a lightweight OG-proxy**
> They’re two different answers to the same question. Dynamic Rendering (SPW, SR) indexes better on crawlers that don’t execute JavaScript, because it serves them the article body too; in exchange it’s more complex, maintains a double route map, and (as we’ll see) reopens a security hole. The OG-proxy (DIS) is simple and honest: no cloaking, no body to re-emit, only escaped meta tags; in exchange its textual SEO for no-JS bots is weak. There’s no absolute winner: a festival site that lives on Telegram social previews does just fine with the lightweight proxy; a content site that wants to rank on Google needs the prerendered body. The choice follows what you have to show, and to whom.

---

## 4. The Prerender Reopens the XSS Hole: the Live Flaw of the Four Emitters

In Chapter 8 we pinned down the picture of the four `content` emitters: the same HTML, saved raw in the database, exits toward the world from four different points, and the sanitization that lives in the React render doesn’t cover the other three. The SEO prerender is the point where that hole is **still open**.

To serve the bot an indexable body, the crawler branch re-emits the article’s `content`. But it doesn’t pass it through DOMPurify (which lives only in the React render): it passes it through `strip_tags` with a tag allowlist.

```php
// public/index.php:403-405 (SPW) — the body for the crawler: strip_tags allowlist, NOT DOMPurify
<div>' . strip_tags($article['content'],
        '<p><br><h2><h3><h4><ul><ol><li><strong><em><a><blockquote><pre><code>') . '</div>
```

The difference isn’t theoretical. `strip_tags` with an allowlist removes dangerous tags at the element level: `<script>`, `<iframe>`, `<svg>` aren’t on the list, so they vanish. But `strip_tags` **doesn’t look at the attributes** of the tags it lets through. An `<a href="javascript:...">` or a `<p onmouseover="...">` survives intact. DOMPurify would have removed those two; `strip_tags` doesn’t.

And the crawler branch is reachable by anyone, because `isCrawler()` trusts only the `User-Agent`. All it takes is showing up with `User-Agent: Googlebot` to receive the body passed through `strip_tags` alone. The surface is narrow (because, as a rule, the victim has to be the one carrying a crawler UA, and bots don’t execute JavaScript), but it’s a second content-render path that doesn’t share the first one’s defense.

> [!WARNING]
> **When you copy a pattern, you copy its flaw too**
> SR-C7 is SPW-C7 almost verbatim: same `isCrawler`, same helpers, **the exact same** `strip_tags` with the same allowlist. In copying the signature Dynamic Rendering pattern, SR copied its hole as well. And in copying it, it lost a piece (the visibility rule, §5) while introducing a new bug. DIS, which doesn’t prerender the body, is the only one immune: not because of a better defense, but because it emits less. It’s the exact flip side of its missing DOMPurify seen in Chapter 8: there, “not defending” hurt; here, “not emitting” saves.
> The lesson closes the thread opened in Chapter 8: when the XSS defense lives in a single render, every other emitter has to re-sanitize on its own, and sooner or later one of them forgets. The right fix isn’t to add `strip_tags` here and DOMPurify there, but **a single server-side sanitization function**, used by every PHP emitter of the `content`. The thread will close in Chapter 12 (the feed, which escapes) and Chapter 13 (the newsletter, which doesn’t emit).

---

## 5. The SEO That Indexes Drafts

There’s a second rule the prerender ought to share with the rest of the system, and that SR and DIS forget. In Chapter 9 the content lifecycle established that a piece of content is public only if `status = 'published'` **and** its publication date is in the past. SPW reuses this rule in the SEO queries and even in the sitemap. SR and DIS filter on the date alone:

```php
// public/index.php:130-135 (SR) — the status filter is missing
$stmt = $pdo->prepare(
    "SELECT id, title, slug, summary, content, cover_image, published_at
     FROM news WHERE slug = ? AND published_at <= ? LIMIT 1");   // ← no "AND status = 'published'"
```

The consequence is a crack between two ideas of “public.” A draft article with a past date is invisible in the API and in the public list, but it leaks into the meta tags, into the HTML served to the crawler, into the “latest news” block on the homepage and, in SR, even into the sitemap, which hands it to Google.

> [!WARNING]
> **Two ideas of “public” in the same site**
> “Public for the user” and “public for the bot” ought to be the same thing, but when the visibility rule is written by hand in every query, it’s easy for one path to apply it and another not to. SPW keeps it aligned across three files (API, prerender, sitemap); SR loses it in the very file that feeds it to the search engines. Here too the root is the same as the XSS hole: a domain rule that doesn’t live in one single place ends up diverging among its consumers.

---

## 6. The SEO Cache That Outlives Its Reader

SR, unlike SPW, has an SEO cache: on every save it writes a `.cache/seo_news_<md5(slug)>.json` file, regenerates it in bulk with a dedicated script, and deletes it when you delete the content. All perfectly maintained, except for one detail: **no one reads it**.

A search across the entire codebase doesn’t turn up a single place that opens those files. The v3.0 engine queries the database directly. And the smoking gun is written in the code itself: the banner in `index.php` declares it has replaced “the v2 cache-file proxy,” and a regeneration script contains a comment that gives away the vanished reader:

```php
// public/api/rebuild_seo_cache.php:67-79 (SR)
$seoData = [
    'title' => $speaker['name'],
    'description' => $speaker['role'] . ' - ' . substr($speaker['bio'] ?? '', 0, 150) . '...',
    'name' => $speaker['name'], // Injected for consistency with index.php reader  ← the reader no longer exists
];
file_put_contents($cacheDir . '/seo_speaker_' . md5($speaker['id']) . '.json', json_encode($seoData));
```

Version 2 was a proxy that read those JSON files; v3.0 rewrote the engine with the direct query and removed the reader without shutting down the writers. Every save still pays the cost of writing a file no one will open. It’s the opposite of SPW, which never had an SEO cache, by choice.

> [!TIP]
> **The cache that outlives its reader**
> It’s a specific way code rots: you rewrite the consumer of something and forget to shut down its producers. The cache stays, gets updated, invalidated, regenerated, and serves no purpose. It also stands as a correction to a point in Chapter 7, which cited the `rebuild_seo_cache` script as useful for migrations: today it regenerates a dead cache. The next section gives this cache a less innocent twist than that.

---

## 7. When the Entry Point Becomes a Target

There’s a reason a cache that serves bots without touching the database isn’t just an optimization. Runtime Radio learned it, and the lesson is important enough to have a home in this chapter: the attack vector is exactly the SEO entry point we’ve just described.

Between February 23 and 27, 2026, the site went through two overlapping crises. The first was the collapse of the SQLite database under a load that had been growing for months, resolved with an emergency migration to MySQL in under a day (Chapter 15 tells it). The second arrived while the infrastructure was still unstable: a wave of requests returning 503 and 500 errors, with near-vertical traffic spikes that organic growth couldn’t explain.

The vector was elegant. Thousands of hostile bots **impersonated the social crawlers**, sending a Telegram or Facebook `User-Agent`. And every request with that UA hit `index.php`, which by design queried the database to extract the meta tags. The SEO engine, designed to make shared links look good, had become a lever: a near-zero-cost request for the attacker forced a query on the just-migrated, still-fragile database.

```
Hostile bot → User-Agent: TelegramBot → request to /news/a-slug
→ index.php → DB query for the meta tags → response
→ the bot discards it and repeats, a thousand times a second
→ the DB gives out → 503/500
```

The response separated the bots’ path from the users’. The HTML for social crawlers was **generated from precompiled static JSON files**, written to disk at the moment an article is published: the bot gets its page with the meta tags in a few milliseconds, read from the cache instead of from the database, which is therefore never queried. Only real users, with a browser that runs JavaScript, take the normal path. And the core service, audio streaming, stayed up behind a static maintenance page even while the rest was offline.

Those precompiled JSON files have a familiar name: `.cache/seo_*.json`. They’re the same SEO cache from the previous section. It’s hard not to read the two facts together: the cache was born as an anti-DDoS shield, a path for the bots that didn’t touch the database; then the v3.0 rewrite of the engine returned to the direct query and removed the reader, leaving the cache written-but-never-read. The shield is still there, it’s still polished on every save, but no one carries it anymore.

> [!WARNING]
> **Every public endpoint that queries the DB is a target; the User-Agent is not a gatekeeper**
> Three things to take home. First: any unauthenticated endpoint that, to respond, queries the database is a lever for a volumetric attack. If the response to a repetitive request can come from a static cache, that cache isn’t just performance, it’s a security layer. Second, already met in Chapter 10: social bots are recognized by their `User-Agent`, and the `User-Agent` can be spoofed. You can use it to *optimize* (serving a cache to recognized bots), never as an access barrier. Third, the most uncomfortable: a defense that works can be dismantled without meaning to, in a rewrite that looks only at features. Runtime Radio’s SEO cache wasn’t “removed”: it was orphaned, and with it the protection it gave.

---

## 8. Sitemap, robots, and Structured Data

What remains is the surrounding SEO infrastructure, which is easy to dismiss as “already handled by the `.htaccess`.” In reality there’s a precise pattern: `sitemap.xml` and `robots.txt` aren’t physical files, but rewrites toward `sitemap.php` and `robots.php`, generated in real time.

```apache
# public/.htaccess (SPW) — no physical files: sitemap and robots are PHP
DirectoryIndex index.php index.html                 # the SEO Engine before index.html
RewriteRule ^sitemap\.xml$ sitemap.php [L,NC]
RewriteRule ^robots\.txt$  robots.php  [L,NC]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_URI} !^/api/ [NC]
RewriteRule ^(.*)$ /index.php [L,QSA]                # every virtual React URL → SEO Engine
```

This way the sitemap is always fresh without prerendering, and its `baseUrl` is derived from the request host, so the same file works on production and staging. SR’s `robots.php` adds a small editorial personality: it blocks commercial SEO crawlers (Ahrefs, Semrush, DotBot) and imposes a `Crawl-delay`, so as not to waste bandwidth on tools that bring no readers.

On structured data, both flagships build the JSON-LD as a PHP array, choosing the type based on the page: `Article` or `NewsArticle` for articles, `CollectionPage` for listings, and on the homepage an `@graph` that describes the site and the author (or, for Runtime Radio, a `RadioStation`). DIS, faithful to its rung, doesn’t emit JSON-LD: it stops at the meta tags.

---

## In Summary

Indexing a SPA without an SSR framework is possible, with a PHP that acts as a front controller, sniffs the bot, and serves it complete HTML. But Dynamic Rendering isn’t free: it duplicates the route map, and above all it reopens the XSS hole in the content, because it re-emits the `content` with a tool (`strip_tags`) weaker than the render’s DOMPurify. SPW does it well, SR copied its defects too and added some of its own (the indexed drafts, the orphaned cache), DIS sidesteps the problems by doing less. And the story of February’s DDoS closes the circle: the entry point that makes the site visible is the same one that, under strain, brings it down, and the cache that saved it is today a tool forgotten in a corner.

> [!IMPORTANT]
> **The Canon**
> - Index the SPA with Dynamic Rendering from a PHP entry point (UA-sniffing), not with a fragile SSG.
> - The prerender re-emits the `content`: sanitize it with the **same** defense as the render, because `strip_tags` with an allowlist lets attributes through (`onerror`, `href="javascript:"`).
> - Respect the `status` in the crawler branch too: don’t index drafts.
> - Dynamic `sitemap`/`robots`; the User-Agent is not a security gatekeeper.

---
*Next Chapter: RSS Feed & Syndication. The feed is the safest emitter of the content, the one that closes the thread of the four emitters, and at the same time the place where a CORS proxy and a bit of security theater lurk.*
