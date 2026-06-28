# CHAPTER 14: Admin Dashboard & Panels

Every system seen so far has a back office. The content of Chapter 9, the media of Chapter 7, the newsletter of Chapter 13, the reactions of Chapter 20, the festival of the chapters that follow: all of them open, sooner or later, onto a panel from which an administrator watches and governs them. The admin area is the fabric that ties the other clusters together, the point where they become numbers to read and actions to take. It’s a surface the festival makes easy to underestimate: the only “dashboard” people usually think of is the contest’s, which is instead a special case (we meet it again in Chapter 19). Here we deal with the general administrative area, of which the festival’s is only a specialization.

The three sites build their console on two independent questions. The first is *how it’s built*: a route structure with a declarative guard, a single mega-component, or something in between. The second is *how much it measures*: an analytical dashboard with charts, a menu that counts nothing, or real numbers written in text. The two questions don’t go hand in hand, and their combination yields three very different admins.

There’s a reversal worth flagging up front, because it’s the through-line. SitoRuntime is the site of the scalability scars, the one that lived through the nighttime crash and the emergency migration of Chapter 15. And yet it’s the one with the least-equipped admin: it measures nothing and has no backup. That is, it has neither the eye to notice a problem nor the net to survive it. It’s confirmation, once again, that more engineered doesn’t mean more protected.

---

## 1. The Admin Is an Aggregator, Not an Application

Before the differences, four traits the three sites share.

The restricted area isn’t a separate application: it’s a frame that mounts the other clusters’ panels inside itself. The editor of Chapter 8, the media library of Chapter 7, the newsletter composer of Chapter 13, the festival management live as pages of a shared console. What’s the admin’s own are the frame, the guard, and a few surfaces of its own: the dashboard, the settings, user management.

The guard, precisely, covers the whole area in a single place, not page by page. It’s the reverse of the backend, where every endpoint calls its own `Auth::check()` (Chapter 10): here the frontend protects the entire restricted subtree with a single barrier, and all the child pages inherit its protection. It’s the “one guard, N pages” principle.

Each panel degrades gracefully on its own: if a data source goes down (the metrics absent, a table not yet migrated), that panel hides itself or shows zero, but the rest of the console stays usable. The dashboard is never a blank page. And in all three the admin password change lives inside the settings, often the only truly “configuration” item present.

---

## 2. How It’s Built: Three Guard Architectures

On this axis, the scale runs from declarative to imperative.

SPW uses a declarative *route guard*: the route that mounts the admin layout has a loader, and all the children inherit its redirect. The session is verified before the page mounts; if it’s missing, the user doesn’t even see a flash of restricted content.

```tsx
// SPW App.tsx:239-258 + loaders.ts:10-20 — one guard, N pages
{ element: <AdminLayout />, loader: adminAuthLoader, children: [ /* dashboard, settings, … */ ] }

export const adminAuthLoader = async () => {
    const session = await api.checkSession();
    if (!session || !session.user) return redirect('/admin/login');   // never an admin datum served without a session
    return session;
};
```

SR sits at the opposite extreme: a single component, `Admin.tsx`, nearly six hundred lines, that switches “section” in memory instead of navigating between routes. The guard is a check inside the component, run on mount. DIS takes a middle road that’s almost a curious hybrid: it has SPW’s structure (an `AdminLayout` with a sidebar and child routes via `Outlet`), it even runs on the data-router infrastructure that would allow loaders, but then it protects the area with a check inside the component, like SR.

```tsx
// DIS AdminLayout.tsx:13-25 — structure like SPW, guard like SR
useEffect(() => {
    api.checkAuth().then(u => {
        if (!u) navigate('/admin/login');        // client-side protection, no loader
        else setUser(u);
    });
}, [navigate]);
if (!user) return null;                          // NB: no role === 'admin' check (see below)
```

The full comparison between loader guard and component guard, with its trade-offs, is in Chapter 6. Here what counts is a security consequence that shows up precisely in DIS.

> [!WARNING]
> **Protecting the area isn’t enough: you need the role**
> DIS’s guard verifies that there’s a logged-in user, not that they’re an administrator. An *editor*, therefore, sees the entire console: subscriptions, voting, reset, user management. It’s the backend that has to reject the actions the editor can’t perform, but it does so inconsistently (Chapter 10): some endpoints are reserved for admins, others accept any logged-in user. The result is that an editor can really approve participants and change the rounds from the UI. It’s the whole-area version of the “the gate hides the content but not the button” problem that also shows up in SR. The rule: hiding a page is user experience; preventing an action is security, and it has to be done on the role, both on the client and (above all) on the server.

---

## 3. How Much It Measures: Analytical, Console, Textual

The other axis is orthogonal to the first, and it separates the three sites cleanly.

SPW has a real analytical dashboard: seven total cards, a dozen mini-stats with a percentage trend, six charts (with a period selector at 7, 30, or 90 days). SR measures nothing: its dashboard is made of cards that are navigation buttons, not counters. It’s a menu disguised as a dashboard. DIS is in the middle, and it’s the most useful lesson of the three: it really measures, but in text. Counters of subscribers and votes, disk space broken down by folder, the provisional ranking, the latest arrivals. No charts, no tracking engine, just the right `COUNT`s.

> [!TIP]
> **How much dashboard you really need**
> DIS’s dashboard proves you can give informational value to an administrator without Chart.js and without an analytics engine: the right queries and a page that writes them out plainly are enough. SPW’s analytical dashboard is richer, but it costs a whole tracking system to maintain; SR’s “menu” is the rung below the minimum, because it doesn’t even answer the simplest question (“how many subscribers do I have today?”). Between too much and nothing, the text-based dashboard is often the right point: it measures what you need to decide, and nothing else.

---

## 4. Measuring Without Third Parties

When a site wants to know how many visits it gets without handing its readers’ data to Google Analytics, it has to build its own in-house analytics. SPW does it with `analytics.php`, a dual-personality file: the branch that *records* an event is public (the live site calls it on every visit), the branch that *reads* the reports is reserved for the admin.

```php
// SPW analytics.php:16-77 — one file, two audiences
if ($method === 'POST') {
    // 'view'/'click' tracking from the live site, anonymous: no Auth
    // 'view' deduplicated by IP-hash + article + day; 'click' rate-limited
}
elseif ($method === 'GET') {
    Auth::check();        // only the reporting is private
    // ~20 aggregations for the dashboard
}
```

Two precautions make this tracking sound. Views are deduplicated by IP and day, so a reader who reloads ten times counts only once: the numbers don’t inflate. And clicks, beyond the frequency threshold, get a neutral response instead of an error:

```php
// SPW analytics.php:62 — beyond the limit, a neutral response: the client can't tell "recorded" from "discarded"
echo json_encode(['status' => 'ok']);   // not a 429
```

It’s the same `analytics.php` that consumes the reactions of Chapter 20, turning them into “most-loved articles” and “reactions by type.” A site that counts its own readers keeps the data in-house (a concrete privacy advantage) and decides for itself what counts as a real visit. The price is one more public endpoint to defend from abuse, and it’s the reason for the deduplication and the rate limit.

---

## 5. The Safety Net: the Backup, and SitoRuntime’s Paradox

Here the three sites part ways in the most instructive manner. SPW has the gold pattern: the automatic backup is written **outside the document root**, where no web request can reach it. And there’s a detail born of a real scar.

```php
// SPW backup.php:192-213 — the backup goes outside the docroot; the fallback defends itself at runtime
$outside = dirname(realpath(__DIR__ . '/..')) . '/db_backups_simonepizzi';
if (!is_dir($outside)) @mkdir($outside, 0700, true);
if (is_dir($outside) && is_writable($outside)) {
    $backup_dir = $outside;
} else {
    // Fallback inside the docroot: but clean-dist.js (postbuild) removes .data/ from the dist,
    // so the deny .htaccess committed in the repo does NOT reach the server → recreate it at runtime
    $backup_dir = __DIR__ . '/.data/backups';
    if (!is_dir($backup_dir)) mkdir($backup_dir, 0700, true);
    @file_put_contents($backup_dir . '/.htaccess', "Require all denied\n");
}
$filename = "auto_backup_" . date('Y-m-d_H-i-s') . '_' . bin2hex(random_bytes(8)) . ".sql";  // unguessable name
@chmod($backup_dir . '/' . $filename, 0600);
```

> [!WARNING]
> **The build can betray your static defense: defend yourself at runtime**
> The `.htaccess` with `Require all denied` that protects the backups folder is committed in the repo. But the build script (`clean-dist.js`) removes the `.data/` folder from the distribution, so as not to ship development databases to production. Side effect: the deny file never reaches the server. SPW recreates it at runtime, the first time it writes a backup. The lesson is general: a defense that lives in a static file is worth something only if that file gets to where it’s needed; if your build pipeline touches it, the defense has to be reestablished at runtime. It always pays to ask what the build *removes*, not just what it adds.

SPW’s backup is also schedulable from an external cron without login, but protected by a secret compared in a timing-safe way, and *fail-closed*: if the secret isn’t configured, the cron branch is reachable only by a logged-in admin.

```php
// SPW backup.php:156-166 — cron without login, but protected; denies if the secret isn't defined
if (!$is_admin && (empty($configured_secret) || !hash_equals($configured_secret, $secret))) {
    http_response_code(403); die("Accesso negato.");
}
```

SR has none of this. No backup, no export, no cron, and, as we saw in §3, no metrics.

> [!WARNING]
> **Treatment without prevention: the site that doesn’t back itself up**
> It’s the paradox at the heart of this chapter. SitoRuntime lived through a nighttime database crash and an emergency migration (Chapter 15), and carries around a WAL “emergency revert” script: it has the *treatment*. But it doesn’t have the *prevention*: no automatic backup, no metric to warn it before things get worse. The site mapped precisely for its incidents is the one least equipped to see them coming and to recover. Having the emergency script but not the backup is like keeping the fire extinguisher and not the smoke alarm.

---

## 6. The Powerful Actions, and How They’re (Not) Protected

An admin area contains the site’s most dangerous levers, and the three sites protect them unequally.

SR has what you could call a **hidden console**: inside its `admin.php` live powerful actions, like an `ALTER TABLE` or the reconversion of all the images, reachable via `GET` by typing the URL. They’re protected by login alone, not by role, they have no CSRF protection (they’re GETs), and above all no button in the UI invokes them: whoever doesn’t know the action’s name doesn’t even know they exist. It’s maintenance done by hand, with no interface and no role boundary (the mechanics of those migrations are in Chapter 15).

DIS exposes the destructive resets in a panel, and surrounds them with confirmations. But the confirmations are only user experience:

```tsx
// DIS Settings.tsx:155-163 — double CLIENT confirm, POST fetch WITHOUT a CSRF token
if (confirm('⚠️ RESET EDIZIONE: cancellerà TUTTI i partecipanti/voti/audio…')) {
  if (confirm('ULTIMA CONFERMA: i dati saranno persi per sempre. Procedere?')) {
    await fetch('/api/reset_system.php', { method: 'POST',
      body: new URLSearchParams({ action: 'confirm_reset' }) });   // no CSRF
  }
}
```

> [!WARNING]
> **`confirm()` is not a security defense**
> A double `window.confirm` reduces human error: it’s useful against the careless click. But it doesn’t stop a request forged by another site while the admin is logged in, because that request doesn’t go through the browser’s dialog. The defense against that vector is the CSRF token (Chapter 10), which is missing here. Confusing the confirmation with the protection is a common mistake: the first speaks to the honest user, the second to the attacker. You need both, and they do different things.

SPW is the most disciplined here too, but not free of blemishes. Its password change increments the `session_version` server-side, invalidating the other open sessions (Chapter 10); but the settings save accepts any key, without a list of the allowed ones. It’s a low risk, because everything is behind the admin guard, but it’s the kind of door worth closing before someone leans something sensitive against it.

---

## 7. Data Without a Consumer: the Table No One Reads

A subtler flaw, and all DIS’s, concerns the contact form messages. They’re saved in the `contacts` table, and then no one reads them: there’s no panel that shows them, nor an endpoint that retrieves them. The only way the admin “sees” a message is the notification email that goes out at the moment of sending; the copy in the database stays there, written and never consulted.

> [!WARNING]
> **Collect and forget**
> Persisting a piece of data without having a place to read it is a hidden cost, and for personal data it’s also a risk. That table accumulates names, emails, and messages (with the IP address) with no application purpose and, above all, with no place to delete them when they ought to be deleted. The rule is simple and often ignored: if you save a piece of data, you must have a consumer that uses it and a way to dispose of it. A write-only table isn’t an archive, it’s a debt.

---

## 8. The Festival Is a Special Case of This Chapter

Everything we’ve seen (the frame with the guard, the dashboard, the settings as switches, the evaluation of applications) has a specialization in the festival module, which has panels of its own (listening to the participants’ tracks, the master switches for registration and voting, the ranking). That dashboard is Chapter 19, and it should be read as the festival instance of the general pattern described here: the structure, the guard, and the backup belong to this chapter; the master switches and the contest KPIs stay there.

---

## In Summary

The admin area is measured on two independent axes, and the three sites occupy them revealingly. SPW is high on both: an analytical dashboard and a declarative architecture, with the out-of-docroot backup acting as a net. SR is low on both: a mega-component that measures nothing and saves nothing, the paradox of the site that suffered the most without having equipped itself to see it coming. DIS is in the middle in an instructive way: the first one’s structure, the second one’s guard (and holes), and a text-based dashboard that proves how much you can measure with little. The chapter’s lesson isn’t “add more charts”: it’s that a good admin lets you *see* the state of the system and gives you the *net* for when something goes wrong. The apparatus matters less than the question it answers.

> [!IMPORTANT]
> **The Canon**
> - A single guard for the entire restricted area (route guard or check on mount), with a **role** verification, not just login.
> - An automatic backup outside the docroot, with a cron protected by a timing-safe secret and fail-closed; recreate at runtime the defenses the build strips.
> - Powerful actions go through POST + a CSRF token, not hidden GETs; no write-only table (saved data has a consumer and a way to delete it).
> - Measure what you need to decide: even a text-based dashboard is enough.

---
*Next Chapter: Database Evolution, from SQLite to MySQL. The February night a database went down, and the emergency migration told hour by hour.*
