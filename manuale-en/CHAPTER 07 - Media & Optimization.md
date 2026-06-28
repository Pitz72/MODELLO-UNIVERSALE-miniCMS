# CHAPTER 7: Media & Optimization

This chapter follows a file from the disk of whoever uploads it to the disk of the server: how it arrives, how it’s checked, how it’s slimmed down, where it ends up, and how it’s served back. It’s a short path, and that’s exactly what makes it dangerous. In the three sites the skeleton is the same (an `upload.php` that receives a `multipart`, validates it, optimizes it with GD, and puts it on disk), but it’s the cluster where security scales **the opposite way from common sense**.

The defense against code execution from an upload runs from **three independent barriers** (SimonePizziWebSite) to **a single one** (SitoRuntime) to **almost zero on a public upload** (DISINTELLIGENZA), where the chain that leads from the image to a shell is verified. And two details flip your intuition: the “most minimal” naming (SR, which throws the file name away) is the **most secure**, while the “most polite” one (DIS, which keeps the name and the extension) is what opens the door. The question that runs through the chapter is a single one: *how much can you take away from an upload system before it becomes insecure*. And DIS shows what lies one step past that line, because an upload open to the public changes all the rules.

A note from the field: this is about **media**, not cache or SEO. The cache of the content lists lives in the content lifecycle (Ch. 9); the prerendering of metadata for bots is the PHP entry-point chapter (Ch. 11). This chapter stays on the file: uploading it, validating it, optimizing it, serving it.

---

## 1. The Shared Skeleton

Before the divergences, the traits the three sites share.

An `upload.php` receives **one file at a time**: `POST` only, `multipart/FormData` (sent by the client of Ch. 6), `$_FILES['file']`. No media-management library, no external service; the file arrives in the same request that processes it. The image optimization happens **synchronously, inside the endpoint**, via GD, behind an `extension_loaded('gd')` guard that degrades gracefully if GD is missing: no queue, no worker, no cron. The name is made collision-proof with `uniqid()`. The “library” and the “deletion” live in a separate file (`media.php`), distinct from the upload itself. And the reference to the file, inside the content, is always a **URL string** (`cover_image`, `audio_file`), not a foreign-key relation.

That last trait has a shared consequence, **dangling media**: deleting a file doesn’t notify whatever cited it, and none of the three keeps a count of references. An image used as a cover, once deleted, leaves a broken `<img>` and no one notices until the page is opened.

```php
// SPW upload.php — the canonical flow: gate, validate, optimize, record, respond
Auth::check();                                  // only the admin uploads (SPW/SR; DIS does NOT, see §5)
// 1) validate extension + real bytes  2) choose subfolder  3) collision-proof name
// 4) resize/WebP via GD  5) INSERT into `media`  6) echo { status, url, id, name }
```

---

## 2. Validating a File: the Extension Isn’t Enough, and Neither Is the Content-Type

The endpoint’s first job is to decide whether the file is really what it claims to be. SPW and SR do it in **two layers**: first the extension against a whitelist, then the **real bytes** read with `finfo`/`mime_content_type` against a whitelist of MIME types. It’s the “don’t trust the file name” principle: a `shell.php.jpg` passes the first filter but is stopped by the second, because its bytes aren’t those of an image. That same real MIME also decides the subfolder, so the classification never trusts the declared extension.

```php
// SPW upload.php:25-54 — two layers: extension, then the real bytes
$allowedExts = ['jpg','jpeg','png','webp','gif','pdf','zip','rar','mp3'];
if (!in_array($fileExt, $allowedExts)) { /* 400 */ }

$realMime = mime_content_type($file['tmp_name']);   // reads the bytes, not the extension
$allowedMimes = ['image/jpeg','image/png','image/webp','image/gif','application/pdf','application/zip', /* … */];
if (!in_array($realMime, $allowedMimes)) { /* 400: disguised content blocked */ }
```

DIS makes a different choice, and here the chapter’s security story begins: it trusts `$_FILES['type']`, that is, the Content-Type **the browser declares**. No `finfo`, no extension whitelist, only the value that whoever sends the request controls entirely.

```php
// DIS upload.php:100 — the "validation" looks at the client-declared MIME (spoofable)
if (!in_array($file['type'], $allowed)) {           // $file['type'] = browser header
    http_response_code(400); die(json_encode(['status'=>'error','message'=>'Invalid file format']));
}
```

> [!WARNING]
> **`$_FILES['type']` is not validation**
> The Content-Type inside `$_FILES` isn’t computed by the server: the client writes it into the `multipart` request, and it’s faked with one line of `curl`. Validating against that value means asking the attacker whether their file is allowed. The real defense is to read the file’s opening bytes (`finfo_file` / `mime_content_type`) and compare them against a whitelist of MIME types, using the *real* type to decide where to save it too. SPW and SR do this; DIS doesn’t, and that “doesn’t” is the first link in a chain we’ll see in §5.

---

## 3. The File Name Is a Vector

The name the file ends up with on disk is a security decision too, and the three sites make it in three ways that map exactly onto three levels of risk. SPW prepends a `uniqid()` to a base stripped of dots, so a `shell.php.jpg` executable via `mod_mime` can never be born. SR makes the most radical move: it discards the original name entirely and uses a pure `uniqid()`, so no user string enters the final name. DIS keeps the name **and** the extension, and dots stay in the set of allowed characters.

```php
// SPW upload.php:73-75 — base with NO internal dots, then uniqid: no double extension
$safeBase = preg_replace('/[^A-Za-z0-9\-_]/', '', pathinfo($fileName, PATHINFO_FILENAME));
$newFileName = uniqid() . '-' . $safeBase . '.' . $fileExt;
```

```php
// SR upload.php:62 — total erasure: the user name is thrown out, only uniqid + technical extension remain
$baseId = uniqid('', true);                     // no user input in the file name
```

```php
// DIS upload.php:110-111 — keeps name and extension (dots allowed): the weakest
$filename = uniqid() . '_' . basename($file['name']);
$filename = preg_replace('/[^a-zA-Z0-9_.-]/', '', $filename);   // the "." stays -> extension preserved
```

> [!TIP]
> **The less you trust the name, the safer you are: the scale of erasure**
> This is the most counterintuitive point in the chapter. The “most polite” choice, keeping the name the user gave the file, is the riskiest, because it leaves the attacker in control of the final extension. The “most brutal” choice, deleting the name and replacing it with a server-generated identifier, is the safest, because it removes every foothold. SR sits at the protective extreme not because it added a defense, but because it removed a surface: the file name isn’t data to preserve, it’s input to neutralize.

---

## 4. Defense in Depth: Three Barriers, One, Zero

Validation and naming are application defenses, and they live inside `upload.php`. But what happens if that point is bypassed, or if tomorrow a second way to write into the folder gets added? Here comes the barrier that doesn’t depend on the PHP code: the `.htaccess` of the `uploads/` folder that **turns the PHP engine off**. If Apache no longer interprets `.php` in there, a malicious file that gets uploaded stays an inert file, whatever happened before.

```apacheconf
# SPW public/uploads/.htaccess — the FIRST anti-RCE barrier: no PHP execution in here
php_flag engine off
<FilesMatch "\.(php|phtml|phar|cgi|pl)$">
    Require all denied
</FilesMatch>
```

It’s easy to look at the `uploads/` `.htaccess` as a matter of **cache control** (`Expires`, `max-age`), a performance detail, and stop there. Its critical use is another: it’s the shutdown of PHP, and it’s the first of SPW’s three independent barriers. We’ve already seen the other two: the naming that doesn’t generate executable names (§3) and the validation on the real bytes (§2). Three nets for the same risk, and each covers the other’s gap: if the `.htaccess` weren’t read, the naming saves you; if the naming failed, the `.htaccess` saves you; disguised content is stopped by the MIME check.

SR has only one of these nets, the application validation: there’s no `uploads/.htaccess` (the folder is created at runtime and isn’t in the repository), and the global `.htaccess` doesn’t turn PHP off. As long as `upload.php` stays the only write path, it holds; but there’s no second net. DIS has practically none of the three.

> [!WARNING]
> **A single barrier is not defense in depth**
> “Validate the upload well” is necessary, not sufficient. Defense in depth means every single barrier can fail without the system falling, because there’s another one behind it. Turning PHP off in the upload folder costs two lines of `.htaccess` and turns a possible flaw in the validation from “code execution” into “a useless file on disk.” It’s the barrier with the best cost-to-protection ratio in the whole chapter, and it’s also the one SR and DIS don’t have.

---

## 5. The Perfect Storm: the RCE Chain from a Public Upload

The conditions seen so far, taken one at a time, would be manageable. In DIS they add up, and on a front the other two sites don’t have: the **public upload**. Being a festival site, DIS accepts the audio tracks participants upload during sign-up, and to lower the friction that upload doesn’t require a login. The gate is decided by type, and for two types it’s simply absent.

```php
// DIS upload.php:64-98 — the gate is per-type and INCONSISTENT: audio_participant is public
if ($type === 'image') {
    if (!isset($_SESSION['user_id'])) { http_response_code(401); die(...); }   // GATED
    $uploadDir = __DIR__ . '/../uploads/images/';
} elseif ($type === 'audio_participant') {
    $uploadDir = __DIR__ . '/../uploads/audio/participants/';                   // NO auth gate
} elseif ($type === 'audio_podcast') {
    if (!isset($_SESSION['user_id'])) { http_response_code(401); die(...); }    // GATED
    $uploadDir = __DIR__ . '/../uploads/audio/podcasts/';
}
```

Now line up the four links. First: `type=audio_participant` doesn’t ask for a login. Second: the validation looks only at `$_FILES['type']`, the MIME the browser declares (§2), which is fakeable. Third: the naming keeps the name and the extension (§3). Fourth: there’s no `uploads/.htaccess` and the global `.htaccess` doesn’t turn PHP off (§4), it only denies `.sqlite` and `.bak` files. The result is a single request.

```bash
# The chain: a public POST drops an executable PHP script
curl -F 'type=audio_participant' -F 'file=@shell.php;type=audio/mpeg' https://site/api/upload.php
#  -> no login required  ->  the declared "audio/mpeg" MIME passes the whitelist
#  -> saved as /uploads/audio/participants/<uniqid>_shell.php  ->  Apache executes it
```

> [!WARNING]
> **A public upload changes all the rules**
> An upload behind a login is a hygiene problem; a public upload is an attack surface open to the internet, and it has to be treated with the utmost suspicion. DIS’s four weaknesses, on their own, would be minor findings. Together, on an endpoint with no authentication, they produce remote code execution: the worst case. The defense isn’t one countermeasure but their sum: authenticate where you can, validate on the real bytes, neutralize the name, and above all turn PHP off in the folder, so that even if everything else gives way the file stays inert (Ch. 10). When the upload is public (the festival sign-ups, Ch. 17), these aren’t recommendations: they’re the minimum.

There’s an unpleasant corollary. FDCA, the fork of DIS, has a byte-identical `upload.php`: it inherits the chain intact, the public upload, the weak naming, and the absence of PHP-off, unchanged. A security flaw copied with a `git clone` multiplies without anyone rewriting it. And note the reversal of the usual refrain “more engineered means more fragile”: here the leanest site (SR, which removed everything removable) is more secure than the most “welcoming” one (DIS, which added the opening to the public without adding the defenses that opening requires).

---

## 6. Optimizing the Image: WebP, Resize, and What the Book Promised Too Much Of

Past the validation, the image gets slimmed down. Here the choices diverge, and it’s easy to flatten them into a single rule the real code doesn’t follow.

SPW and SR **convert** raster images to WebP via GD (quality 82, resizing if the width exceeds 1920px), then delete the original. DIS **doesn’t convert**: it only resizes, keeping the starting format (a PNG stays a PNG, smaller). The “mandatory WebP transcoding, the official standard” is therefore the pattern of two sites out of three, not all of them.

```php
// SPW upload.php:83-119 — WebP conversion + resize, synchronous in the endpoint, behind a GD guard
if (in_array($realMime, ['image/jpeg','image/png','image/gif']) && extension_loaded('gd') && function_exists('imagewebp')) {
    if ($origW > 1920) { /* imagecopyresampled to 1920px, alpha preserved */ }
    if (@imagewebp($img, $webpDestination, 82)) { unlink($destination); /* the original goes away */ }
}
```

Three details deserve a sharp clarification. The GIF is a choice, not an automatism: SPW flattens it into a single frame (the animation is lost), SR **keeps it animated** by excluding it from the conversion. The GD re-encode, as a side effect, **strips the EXIF**: the geolocation and the device model disappear without anyone asking, a small privacy defense gained for free (SR notes it, the others don’t). And the size constraint touches only the **width** above 1920px: there’s no height limit, so a very tall, narrow image stays huge.

> [!NOTE]
> **WebP+resize in the thin stack: the variants, and its limits**
> The optimization is synchronous: it happens inside the upload request, with no queue or worker. On a large image the user waits for GD before seeing the response, but for a low-traffic site (with the client’s progress bar, Ch. 6) it’s a reasonable trade-off. The real variants are three: convert to WebP flattening the GIF (SPW), convert preserving the animated GIF (SR), only resize leaving the format as it is (DIS). None is “the right one” in absolute terms; the wrong one is declaring universal a rule that two lines of code contradict.

---

## 7. The Library and the Deletion: When the Disk Is the Database

Once the file is uploaded, you need to list it and be able to delete it. On this axis SPW parts ways with the other two. SPW keeps a `media` table with two name columns: `file_path`, the technical URL the browser loads, and `filename`, the original human name. That second name serves a courtesy: `download.php`, a public proxy that streams the file with `readfile`, gives the user back `relazione.pdf` instead of `64f1a2-relazione.pdf`.

SR and DIS have no table: the library is the filesystem, read with `scandir` (flat in SR, recursive in DIS). The disk **is** the media database. Simple, but with a cost: no original name, no saved MIME, ordering by the file’s physical date. And the dangling media, common to all, here becomes outright impossible to track, because there isn’t even a starting point from which to count the references. In DIS the orphans are competition records: data that gets lost.

The deletion is the most delicate point, because it’s a mutation that touches the disk, and it has to be protected on two fronts: the path and the request. On the path, the three sites scale again. SPW resolves the path with `realpath` and checks that it really sits inside `/uploads/`, not even trusting its own database. SR uses only `basename()`. DIS just rejects `..` with a `strpos`, then attempts the `unlink` on several candidate paths.

```php
// SPW media.php:31-39 — path guard with realpath: doesn't even trust the DB
$physicalPath = realpath(__DIR__ . '/..' . $filePath);
$uploadsBase  = realpath(__DIR__ . '/../uploads');
if ($physicalPath && $uploadsBase && str_starts_with($physicalPath, $uploadsBase)) {
    unlink($physicalPath);                       // only if REALLY contained in /uploads
}
```

```php
// SR media.php — no auth_utils, a bare session, and NO validateCsrf on the delete
session_start();
if (!isset($_SESSION['user_id'])) { http_response_code(401); exit; }   // no CSRF, no role check
$filename = basename($input['filename'] ?? '');   // the only traversal defense
if (file_exists($uploadDir.$filename)) unlink($uploadDir.$filename);
```

> [!WARNING]
> **The media delete: the path guard and the missing token**
> On the second front, the request, SR and DIS have the same hole: the deletion **has no CSRF protection**. In SR `media.php` doesn’t even include the authentication prelude of the rest of the site, it runs on a bare session and doesn’t check the role; in DIS the CSRF protection doesn’t exist at all. It means a malicious site can make the logged-in admin delete files with a forged request, mitigated only by the cookie’s `SameSite` (Ch. 10). It’s the typical inconsistency: the upload demands the token, the delete doesn’t, and yet deleting is as destructive as uploading. An endpoint that changes state has to be protected as such, always, even when it lives in a “utility” file that gets less attention.

---

## 8. Evolving the Storage Without Stopping the Site

Every site carries the scars of a storage migration: from raster to WebP, from a flat folder to subfolders. You read them in the one-shot scripts, and they tell the same sequence: first the flat uploads, then a batch conversion of what was already there, then the sorting into subfolders, finally the realignment of the references still pointed at the old path.

The difference that matters is how much protection these powerful scripts have, the ones that move files and rewrite the database. SPW’s follow the “upload via FTP, run from the browser, delete right away” pattern, with dry-run active by default (you look before you touch). SR’s live inside `admin.php`, behind the login. DIS’s, `migrate_media.php`, **has no gate at all**: anyone, from the internet, can trigger the mass relocation of the files and the updating of the rows. The full mechanics of these migrations, and the discipline they require, is the chapter on database evolution (Ch. 15); here the symptom is enough, along with the warning that powerful maintenance exposed over HTTP is a back door as much as the upload is a front one.

---

## In Summary

The media side of the three sites starts from the same skeleton and diverges on a single axis that truly matters: how many independent defenses stand between an uploaded file and code execution. SPW has three (PHP off in the folder, naming that doesn’t generate executables, validation on the real bytes), and each covers the other’s failure. SR has one, the application validation, robust as long as it stays the only write path. DIS has almost none, and on a public upload at that: the sum of an absent gate, a MIME trusted from the client, a preserved name, and PHP not turned off is the RCE chain that the FDCA fork inherited intact too. The optimization choices (WebP or resize only, flattened or animated GIF) and the storage ones (a `media` table or a bare filesystem) matter for performance and maintainability, but they don’t move the risk. The risk is in the file name, in the bytes you don’t check, and in the engine you didn’t turn off. The chapter’s rule is that an upload shouldn’t be made “richer”: it should be made redundant, because the first barrier, sooner or later, gives way.

> [!IMPORTANT]
> **The Canon**
> - Validate files by magic bytes (`finfo`), never by the client-declared MIME.
> - Rename with `uniqid()` and discard the original name; rebuild the extension from an allowlist.
> - Defense in depth: an `.htaccess` with PHP-off in the upload folders (the first anti-RCE barrier), plus validation and naming. A single barrier is not defense in depth.
> - Never an ungated public upload into an executable folder; the media delete goes through a path guard (`realpath`/containment) and a CSRF token.

---
*Next Chapter: Advanced Content Editing & Media Integration. The content editor, and how the HTML it produces is kept safe at the moment of showing it.*
