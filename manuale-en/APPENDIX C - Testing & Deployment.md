# APPENDIX C: Testing & Deployment (an Outline)

Two topics the body of the manual touches only in passing deserve at least a starting point: how you test a thin stack without a framework handing you the tools, and how you bring it into production on cheap hosting. These are notes, not a complete guide: they point the direction and the main traps, not every step. But they serve to dispel a misconception, namely that “no framework” means “no tests” and “deploy by feel.”

---

## 1. Testing: No Framework Doesn’t Mean No Tests

The model gives up frameworks, not verification. If anything, its minimal form makes some tests easier, not harder.

**The PHP backend.** Pure logic (slug, validation, sanitization, visibility calculation) is tested with PHPUnit like any code. The endpoints, instead, are better tested *functionally*: a real HTTP request against the endpoint, and a check on the status and the shape of the payload. Here the file-based database becomes an unexpected advantage. Instead of mocking PDO (laborious and not very faithful), you open a throwaway SQLite, in memory or in a temporary file, populate it with known data, and throw it away at the end of the test.

```php
// An endpoint is better tested with a real ephemeral DB than with a PDO mock
$pdo = new PDO('sqlite::memory:');        // a test database, lives as long as the test
$pdo->exec(file_get_contents('schema_test.sql'));   // a known schema
// then: call the endpoint (via HTTP or by including the file with simulated $_GET/$_POST)
// and verify the status code + the JSON structure of the response
```

**The frontend.** Vitest and Testing Library cover the React components. The strong point is the `api` object of Chapter 6: being a single channel over `fetch`, it’s mocked in just one place, and the component tests never touch the real network.

**The tests that pay off most.** In a system like this, two families of test are worth more than a thousand detail assertions:

- **Contract smoke test.** A test that calls every public endpoint and verifies the status plus the shape of the payload catches almost all the regressions of the “unstable contract” discussed in Chapter 6. It’s the net missing exactly where the API has no formal schema.
- **Security non-regression test.** An admin endpoint must answer 401 or 403 without a session; a `.php` file uploaded into the upload folder must not be executable (Chapter 7); a mutation without a CSRF token must fail (Chapter 10). These are the checks that keep an already-closed flaw from silently reopening.

---

## 2. Deploy: From the `dist/` to Five-Euro Hosting

The model is born to run on cheap shared hosting, and the deploy is deliberately simple: no containers, no orchestrators. But “simple” doesn’t mean “improvised.”

**What the build produces.** `npm run build` generates the `dist/` folder with React’s static assets. Two steps of the build process, already seen in Chapters 2 and 11, are defenses, not details: `clean-dist.js` removes the development `.sqlite` files from the distribution (a development database shipped to production is a disaster), and if `index.php` lives in `public/`, the `index.html` has to be renamed `index_react.html`, because the SEO Engine’s PHP entry point has to take precedence.

**What you upload, and what you don’t.** The compiled `dist/` and the `public/api/` folder with the PHP go on the server. The `db_credentials.php` file (for MySQL sites) is uploaded **by hand**, once, and never sits in the repo. You never upload the development `.data/` folder or the test files.

**How you upload.** The three ways, in order of robustness: a `git pull` on the server if the hosting allows it (the cleanest); a scripted SFTP deploy; manual FTP upload (the most fragile, because forgetting a file is easy). Whatever the way, it’s best for the deploy to be *repeatable*: a script in `scripts/` that always does the same steps is worth more than a procedure kept in memory.

**A minimal CI.** Even without complex pipelines, a single GitHub Action that on every push runs the build, the lint, and the tests from the previous section catches regressions before they reach production. The secrets (credentials, keys) live in the CI’s environment variables, never in the repository. A possible automatic deploy step via FTP/SFTP is a handy addition, but it comes later: first the net of tests, then the automation of delivery.

---

## 3. The Limit of These Notes

The above is a map, not the territory. A site with serious availability requirements will want separate environments (staging and production), versioned schema migrations (the debt of Chapter 15), error monitoring, and verified backups, not just executed ones. The thin stack forbids none of this: it simply doesn’t hand it to you, and it’s up to you to decide how much of that discipline your project deserves. The rule is the same as the rest of the book: start from the minimum that keeps you safe, and add only when a concrete need calls for it.

> [!IMPORTANT]
> **The Canon**
> - Test the endpoints with an ephemeral SQLite (`:memory:` or a temporary file), not by mocking PDO.
> - Mock the `api` object in just one place for the React component tests.
> - Keep two nets that pay off: a contract smoke test (status + shape of the payload) and a security non-regression test (gate, upload, CSRF).
> - Build with `clean-dist` (away with the `.sqlite` files); upload `dist/` + `public/api/`, never `db_credentials.php` from the repo or the development `.data/`.
> - A minimal CI (build + lint + test on every push), with the secrets in the environment variables, not in the code.
