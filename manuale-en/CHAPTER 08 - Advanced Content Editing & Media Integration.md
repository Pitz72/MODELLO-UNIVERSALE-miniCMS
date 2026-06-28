# CHAPTER 8: Advanced Content Editing

The content editor is where a CMS becomes tangible: it’s where the author writes, formats, pastes, drops in an image or a video. It looks like an interface detail, but it carries two underlying questions this chapter holds together. The first is how much editor you actually need, because it ranges from a library of a dozen packages down to zero dependencies. The second, more serious, is where the defense against XSS lives: the content the author composes is HTML, that HTML ends up in the database, and sooner or later someone prints it to the page. If no one cleans it up, a `<script>` written by whoever has access to the editor becomes code executed in every reader’s browser.

The three sites answer on three rungs. SimonePizziWebSite (SPW) has a hardened Tiptap editor, with insertion guards and sanitization at render. SitoRuntime (SR) uses the same Tiptap engine, with the same defense at render, but with weaker guards and one extra story behind it: a migration from Quill that left scars in the code. DISINTELLIGENZA (DIS) drops to the handcrafted rung, a hand-driven `contentEditable`, and here the XSS defense disappears entirely. The editor scale and the security scale, we’ll see, don’t line up: the real dividing line isn’t which engine you use, but whether you clean up the HTML at the moment of printing it.

> [!NOTE]
> **Two misunderstandings to clear up right away.** It’s easy to think of this editor as “a native-React solution that gives up the heavy external dependencies.” That’s true only for DIS. The two flagships (SPW and SR) use **Tiptap v3** (ProseMirror), that is, a dozen `@tiptap/*` packages: an external dependency that’s anything but light. And the “Paste Protection,” which at first glance looks like a defense capable of removing “scripts and dangerous attributes,” is really just a cosmetic cleanup of the paste. The real XSS defense is elsewhere, at the moment of render, as we’ll see in this chapter.

---

## 1. The Editor: a Three-Rung Scale

The same need, composing rich HTML, is solved at three levels of dependency.

### 1.1 SPW: a “hardened” Tiptap v3

SPW factors out a reusable `RichTextEditor` component around Tiptap v3, with a focused set of extensions: formatted text, images, color, alignment, tables, YouTube embeds in `nocookie` mode. Each extension brings its default Tailwind classes, so the saved HTML is already styled for the public render.

```tsx
// src/components/admin/RichTextEditor.tsx:95-138 (excerpt)
const editor = useEditor({
    shouldRerenderOnTransaction: true,   // v3: needed for the toolbar's active states
    extensions: [
        StarterKit.configure({ heading: { levels: [1, 2, 3, 4] } }),
        Image.configure({ HTMLAttributes: { class: 'max-w-full h-auto rounded-xl my-4 ...' } }),
        TextStyle, Color,
        TextAlign.configure({ types: ['heading', 'paragraph'] }),
        Table.configure({ resizable: true }), TableRow, TableHeader, TableCell,
        Youtube.configure({ nocookie: true }),
    ],
    content: value,
    onUpdate: ({ editor }) => { onChange(editor.getHTML()); updateCounts(editor.getText()); },
});
```

### 1.2 SR: the same Tiptap, but with a migration behind it

SR uses the same engine, but embedded directly inside `ArticleEditor.tsx` (the toolbar and `useEditor` in the same file), and it keeps a second copy in `SpeakerEditor.tsx` for the speakers’ bios. The rich editing isn’t centralized in a single component as in SPW: it’s duplicated per domain, and a change to the configuration has to be replicated in two places.

Its identity, though, lies elsewhere: SR migrated from Quill to Tiptap, and the migration is written into the code. The old articles contain “bare” YouTube `<iframe>`s left by Quill, which Tiptap can no longer edit. A function rewraps them into the format Tiptap recognizes, before handing them to the editor:

```tsx
// src/components/admin/ArticleEditor.tsx:29-36
// Converts Quill's bare iframes into div[data-youtube-video] that Tiptap can edit.
const QUILL_YT_RE = /<iframe\b[^>]*?\bsrc=["'](https?:\/\/(?:www\.)?youtube(?:-nocookie)?\.com\/embed\/[^"'<>]+)["'][^>]*(?:><\/iframe>|\/>)/gi;
function prepareForEditor(html: string): string {
    return html.replace(QUILL_YT_RE, (_m, src) =>
        `<div data-youtube-video=""><iframe src="${src}" allowfullscreen="true" frameborder="0"></iframe></div>`);
}
// usage: setLoadedContent(prepareForEditor(res.article.content || ''));
```

Two other traces of the old library remain: Quill’s `ql-video` CSS class, kept inside the Tiptap configuration, and the `react-quill.d.ts` file still in the repo. Three converging clues of an editor switch never fully cleaned up.

> [!TIP]
> **Changing the editor with content already written: the compatibility shim**
> When you change the editor engine, the old content stays in the previous format. You have two roads: a one-time migration that rewrites every record in the DB, or a shim that converts the old format “on the fly,” every time you open content to edit it. SR chose the second, with `prepareForEditor()`. The upside is that you don’t touch the database and don’t risk a mass migration gone wrong; the price is that the shim stays in the code forever, or at least as long as a single old, never-reopened article exists. It’s a debt you pay in small installments instead of all at once.

### 1.3 DIS: the handcrafted editor

DIS gives up the library entirely. The editor is a `<div contentEditable>` driven by `document.execCommand`, the now-deprecated DOM API. The only external dependency is `showdown`, and it serves only to convert pasted markdown.

```tsx
// src/components/RichTextEditor.tsx:94-102 (excerpt)
const exec = (command: string, value?: string) => {
    document.execCommand(command, false, value);        // deprecated API
    if (editorRef.current) onChange(editorRef.current.innerHTML);
};
// <div ref={editorRef} contentEditable onInput={handleInput} className="prose prose-invert ..." />
```

It works, and in today’s browsers it still runs. But it’s the most fragile option: `contentEditable` produces different HTML from one browser to another, `execCommand` is deprecated, and its future behavior isn’t guaranteed.

> [!NOTE]
> **How much editor you actually need**
> DIS demonstrates the absolute minimum, zero packages for editing, and at the same time shows its price: inconsistent HTML, a deprecated API, and as the “source of truth” the DOM’s raw `innerHTML` instead of the controlled output of a serializer like `getHTML()`. The scale isn’t “more packages means better.” It’s a trade-off choice: SPW and SR pay a dozen dependencies to have a controlled schema and a rich UX; DIS pays nothing and accepts the fragility. What DIS can’t afford to remove, as we’ll see in §3, isn’t the editor: it’s the defense at render.

---

## 2. The HTML Is the Source of Truth, and the Server Saves It Raw

Underneath the three implementations there’s a shared architectural choice. None of the three keeps a JSON state or a proprietary AST to re-serialize: the editor emits HTML (Tiptap’s `getHTML()`, or the `contentEditable`’s `innerHTML`) and that HTML is exactly what ends up in `articles.content` or `news.content`. The content is already in the form it will be shown in.

And the server doesn’t touch it. Consistent with what we saw in Ch. 9 on the content lifecycle, the backend saves the HTML body as-is, with no `strip_tags` or `htmlspecialchars`:

```php
// SPW articles.php:252 — the content goes into the DB raw
$content = $data['content'] ?? '';                     // no strip_tags / htmlspecialchars
$stmt = $pdo->prepare("INSERT INTO articles (title, slug, content, ...) VALUES (?, ?, ?, ...)");
$stmt->execute([$title, $slug, $content, ...]);        // HTML as-is
```

This isn’t an oversight, it’s the model: the rich content is kept faithful and the defense moves to the moment it’s printed. The whole weight of security, then, rests on a single gesture. Let’s see where.

---

## 3. Rich-Content Security: Where the XSS Defense Lives

The `content` is saved raw, and writing is reserved for the authenticated (admin or editor login, as in Ch. 10). So this is a stored XSS from an authenticated author: it isn’t the anonymous visitor injecting the script, but whoever has access to the editor. The risk is still real, because a compromised editor account, or a careless copy-paste from a hostile source, is enough to plant dangerous HTML in the database. The question is: is there a point where that HTML gets cleaned up before reaching the reader’s browser?

### 3.1 The choke point: DOMPurify at render time

In SPW the answer is a single function, called right before the public component’s one `dangerouslySetInnerHTML`. It passes the HTML through DOMPurify and, with a hook, allows only YouTube `<iframe>`s, removing any other:

```tsx
// src/components/SingleArticle.tsx:28-45
const sanitizeArticleHtml = (html: string): string => {
    DOMPurify.addHook('uponSanitizeElement', (node, data) => {
        if (data.tagName === 'iframe') {
            const src = (node as HTMLElement).getAttribute('src') || '';
            if (!src.startsWith('https://www.youtube.com/embed/') &&
                !src.startsWith('https://www.youtube-nocookie.com/embed/')) {
                node.parentNode?.removeChild(node);     // non-YouTube iframe → gone
            }
        }
    });
    try {
        return DOMPurify.sanitize(html, {
            ADD_TAGS: ['iframe'],
            ADD_ATTR: ['style', 'allowfullscreen', 'frameborder', 'allow', 'src'],
        });
    } finally {
        DOMPurify.removeHooks('uponSanitizeElement');    // no leftover global hooks
    }
};
```

Two details deserve attention. The hook is always removed in the `finally`, so it doesn’t stay registered globally between one render and the next. And having granted the `style` attribute widens the surface: it’s needed for the editor’s inline colors, and it’s DOMPurify that cleans up the dangerous CSS, but it’s a trade-off between visual fidelity and security to keep in mind.

SR does the same thing, with DOMPurify, on all the detail pages (article, speaker, podcast). Same philosophy, same choke point at render time.

DIS doesn’t. `NewsDetail.tsx` injects the raw HTML, and `dompurify` isn’t even among the project’s dependencies:

```tsx
// src/pages/NewsDetail.tsx — no sanitization
<div dangerouslySetInnerHTML={{ __html: news.content }} />   // the DB's HTML injected as-is
```

> [!WARNING]
> **Where to sanitize content HTML: the choke point at render time**
> Saving raw and cleaning at render is a legitimate choice, on one condition: that the render really cleans up, and that it’s the only way that content reaches a browser. SPW and SR meet the condition with DOMPurify. DIS doesn’t, and it’s the only one of the three where the stored XSS meets no choke point: raw on write, raw at render. Its only defense is the admin/editor boundary on access to the editor. Zero defense in depth. The dividing line between the two secure sites and the exposed one isn’t the editor (Tiptap vs. `contentEditable`): it’s the presence or absence of this function.

### 3.2 The insertion guards: a second level, not the first

There’s a second defense, more visible to the author but less decisive. When you insert a link from the toolbar, SPW validates its URL on the spot, blocking dangerous schemes:

```tsx
// src/components/admin/RichTextEditor.tsx:36-42
const isSafeLinkUrl = (url: string): boolean => {
    const trimmed = url.trim();
    return /^https?:\/\//i.test(trimmed) || trimmed.startsWith('/')
        || trimmed.startsWith('#') || /^mailto:/i.test(trimmed);   // blocks javascript: and data:
};
```

SR and DIS don’t have this filter. SR does a bare `setLink({ href: url })`; DIS takes the URL from a `prompt()` and passes it to `createLink` without looking at it, so a typed `javascript:alert(1)` ends up in the HTML exactly as-is:

```tsx
// DIS RichTextEditor.tsx:104-107
const promptLink = () => {
    const url = prompt('Inserisci URL:');
    if (url) exec('createLink', url);     // no filter: 'javascript:...' would be inserted as-is
};
```

> [!TIP]
> **Two levels, one real choke point**
> The insertion guard (`isSafeLinkUrl`) and the render sanitization (DOMPurify) aren’t interchangeable. The first covers only what comes through the toolbar, and it doesn’t touch HTML that’s pasted or built some other way: it’s defense in depth and good UX, because it warns the author right away instead of letting the URL through to the public page. But the real barrier, the one that intercepts any HTML however it got into the DB, is the render. If you have to pick one, pick the choke point at render. Having both is better; having only the first is an illusion of security.

### 3.3 Cleaning the paste isn’t defending against XSS

That leaves the old “Paste Protection” misunderstanding to clear up. DIS, when it intercepts a paste, does two things: if it recognizes markdown it converts it with `showdown`, otherwise it cleans the HTML of inline styles and the `class`es from Word or Wikipedia. Useful for not importing unwanted fonts and backgrounds. But it isn’t security:

```tsx
// DIS RichTextEditor.tsx:63-85 (excerpt) — COSMETIC cleanup
const doc = new DOMParser().parseFromString(htmlText, 'text/html');
doc.querySelectorAll('[style]').forEach(el => { el.style.backgroundColor=''; el.style.color=''; });
doc.querySelectorAll('*').forEach(el => el.removeAttribute('class'));   // removes styles/classes, NOT script/handlers
document.execCommand('insertHTML', false, doc.body.innerHTML);
```

It removes `style` and `class`, but it lets `<script>`, the `on*` attributes, and `javascript:` URLs through. The comment in the code talks about “enemy classes,” not XSS, and it’s honest: it’s cosmetics. It has to be told apart, clearly, from a real sanitization. Removing Word’s formatting improves how the text looks; it protects no one.

---

## 4. Anchor Box: the Four `content` Emitters

Here a thread opens that runs through four chapters, and that’s worth pinning down once. The starting point is what we’ve just seen: the `content` is saved raw in the database, and the sanitization lives only in the React render. But the React render isn’t the only place that content leaves for the world. The same `articles.content` is reread and re-emitted by at least four different “emitters,” and each has to defend itself on its own. The defense that lives in a single component doesn’t cover the other three.

| Emitter | Where | What it does with the `content` | Anti-XSS defense | Outcome |
|---|---|---|---|---|
| **React render** | public page (this chapter) | injects it via `dangerouslySetInnerHTML` | DOMPurify (SPW, SR) / **nothing** (DIS) | real choke point; **DIS exposed** |
| **SEO prerender** | `index.php` for bots (Ch. 11) | re-emits its HTML body | `strip_tags` with an allowlist (SPW, SR) / doesn’t emit the body (DIS) | **attribute hole** alive in SPW and SR; DIS immune by subtraction |
| **RSS feed** | `rss.php`/`feed_*` (Ch. 12) | emits the article | doesn’t emit the `content` (SPW uses the excerpt; DIS does podcasts only) / escapes it (SR: `strip_tags` + `htmlspecialchars`) | closed |
| **Newsletter** | email send (Ch. 13) | sends the article | no one emits the `content` | closed |

Here’s the read. The feed and the newsletter close the problem, because they either don’t emit the body or escape it entirely. The render closes it where there’s DOMPurify and leaves it open in DIS. The only flaw still alive in the flagships is the SEO prerender: to serve bots an indexable body, SPW and SR re-emit the `content` passing it through `strip_tags` with a tag allowlist, which isn’t DOMPurify. `strip_tags` removes the disallowed tags but doesn’t touch the attributes: an `onerror` or a `javascript:` inside an allowed tag survives. And since SR copied SPW’s SEO engine to the letter, it copied the flaw too.

> [!IMPORTANT]
> **The lesson of the picture: a shared server-side sanitization**
> When you save the content raw and entrust the cleanup to whoever prints it, you’re betting that *every* print point remembers to clean up. Four emitters are enough, and it only takes one to forget: in DIS the render forgets, in the flagships the prerender forgets. The conclusion that runs through the next three chapters is that the sanitization should live once, on the server, where the content is produced or reread, instead of being reinvented by every consumer. The thread reopens in Ch. 11 (where the prerender hole is alive), closes again in Ch. 12 (the feed that escapes), and closes fully in Ch. 13 (the newsletter that doesn’t emit).

---

## 5. Inserting Media into the Content

Managing the media library (upload, optimization, formats: that’s Ch. 7) is one thing; embedding an image *inside* the article’s text is another. Here it’s the second that matters, and it’s another point where the three sites diverge.

SPW opens a modal gallery, `MediaSelectorModal`, which reuses the same upload bridge from Ch. 7: the author picks an already-uploaded image or uploads a new one with a progress bar, and the URL comes back to the editor.

```tsx
// src/components/admin/MediaSelectorModal.tsx:65-71 (excerpt)
const result = await api.uploadMediaWithProgress(file, (p) => setUploadProgress(p));
if (result.url) onSelect(result.url);     // the URL becomes an <img src> in the editor
// gallery: onClick={() => onSelect(item.file_path)}
```

SR skips the gallery: an `<input type="file">` created on the fly, a direct upload, and done. Simpler, but no reuse of images already present. DIS doesn’t allow images in the article body at all: the editor covers only formatted text and links, and the cover is handled elsewhere.

On the portability side, all three save **only relative paths** in the database (for example `/api/uploads/file.jpg`), so the content isn’t tied to a domain. When an absolute URL is needed, at the moment of copying or sharing a link, it’s the client that rebuilds it from `window.location.origin`. The thing saved stays portable; the thing shown adapts to the context.

---

## 6. The Editorial Micro-Touches

Under the differences, the writing experience shares a few small attentions worth gathering, because they’re the kind of detail that tells a usable editor apart from one that frustrates.

All three show the word count and a reading-time estimate in real time. All have a toolbar that stays visible while you scroll a long article (`sticky`), with buttons that don’t lose the text selection (`onMouseDown` with `preventDefault`). And all have to solve the same subtle problem: when the content changes “from outside” (because you open an existing article), updating the editor without making the cursor jump or marking the form as modified. Tiptap does it with `setContent(value, { emitUpdate: false })`, and the comment in SPW’s code explains why:

```tsx
// SPW RichTextEditor.tsx:157-165 — the Tiptap v3 gotcha
// In v3 setContent emits onUpdate by default, marking the form "dirty"
// and creating phantom drafts in localStorage. emitUpdate:false avoids it.
editor.commands.setContent(value, { emitUpdate: false });
```

DIS gets the same result by hand, updating the `innerHTML` only when the editor isn’t in focus.

Where the sites really diverge is in the safety net against losing work. SPW saves a draft to `localStorage` every couple of seconds and, on reopening, offers a banner to restore the interrupted session; the “modified” state also feeds a block on navigation. SR stops at `beforeunload`, the browser’s warning when you close the tab with unsaved changes. DIS has neither.

> [!TIP]
> **Not losing the editor’s work without a backend**
> In the thin stack there’s no autosave endpoint: the draft lives in the browser. SPW’s solution (`localStorage` plus a restore banner) is the most robust at zero backend cost, and it turns a browser crash into an explicit choice (“restore” or “ignore”) instead of lost work. The limit remains: if you switch devices or clear the cache, the unsaved draft is gone anyway. But between DIS’s nothing and SR’s warning alone, a local draft is the difference between losing half an hour of writing and getting it back.

---

> [!IMPORTANT]
> **The Canon**
> - A Tiptap editor, HTML as the source of truth saved raw.
> - The defense against XSS is sanitization **at render** (DOMPurify), a single choke point; the paste cleanup is cosmetic, not security.
> - Guards on link insertion (`isSafeLinkUrl`): no `javascript:` and no unvalidated URLs.
> - The four `content` emitters (render, SEO prerender, feed, newsletter) share the same server-side sanitization: if one forgets it, the XSS hole reopens.

*Next Chapter: Content Lifecycle. The lifecycle of content, from draft to scheduled publication, and the three visibility rules that decide what the public really sees.*
