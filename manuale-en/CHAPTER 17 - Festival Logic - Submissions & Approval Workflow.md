# CHAPTER 17: Festival Logic — Submissions & Approval Workflow

A word of honesty before the module. The “festival” isn’t part of the miniCMS core: it’s an **optional module**, present in **one site out of four** (DISINTELLIGENZA), which FDCA inherits unchanged because it’s a fork with a byte-identical backend. The three chapters that follow (this one, the voting, the dashboard) describe a real public-vote contest, with its strengths and its cracks, not a standard component to take for granted.

This first chapter covers the front door: how an entrant signs up, how the admin evaluates them, and the two points where the idealized module diverges from the code (the newsletter sign-up and the public upload of the tracks).

## 1. The Participant Workflow

A submission follows a three-state pipeline, run not by a state machine but by a `status` column that the admin moves forward.

- **`pending`**: the initial state. The entrant has sent their data and their track, but isn’t visible on the site.
- **`approved`**: validated. They get the confirmation email, enter the contest, and (see §4) get signed up to the newsletter.
- **`rejected`**: discarded, with a courtesy notice.

There’s a security detail the “clean” workflow hides, though: the action that changes the state (`update_status`) is protected only by a session check, not a role check. It means that **an editor too**, not just an administrator, can approve or reject entrants.

> [!WARNING]
> **The gate that confuses “logged in” with “admin”**
> Approving an entrant is a weighty decision: it lets them into the contest, sends them an email in your name, signs them up to the newsletter. And yet the backend grants it to anyone who’s logged in, without checking that they’re an administrator. It’s the same “role-blind gate” that runs through several points of the site (Chapter 10): hiding a menu item from an editor is user experience, but stopping them from taking an action is security, and that has to be done on the role, server-side. Here it isn’t.

## 2. The Transactional Emails

On every state change the backend sends an email with an HTML template consistent with the festival’s branding: a technical confirmation on receipt, and a formal message (positive or negative) on the outcome. The transport is native `mail()`, *fire-and-forget*: the record in the database is the source of truth, the email is a best-effort channel (the full mechanics, with its limits, are in Chapter 13).

## 3. Participant Assets: The Public Upload That Opens a Door

The audio tracks uploaded by the entrants land in an isolated folder (`uploads/audio/participants/`) with a unique name, and the admin pre-listens to them in the Media Center before deciding. So much for the convenient version. The real version is that this upload, to lower the friction of signing up, **requires no login**, and it’s the front from which the RCE chain described in Chapter 7 starts.

> [!WARNING]
> **The public upload of the tracks changes all the rules**
> A submission form that accepts files without authentication is an attack surface open to the internet. In DISINTELLIGENZA four weaknesses add up: the upload is public, the validation trusts the Content-Type the browser declares, the file name keeps its extension, and the folder doesn’t turn off PHP. The result, verified, is remote code execution (the full chain, link by link, is in Chapter 7). The lesson for anyone building a frictionless sign-up: opening to the public is a legitimate product choice, but it has to be paid for with the defenses that opening demands (validate the real bytes, neutralize the name, turn off PHP in the folder), not with their absence. FDCA, being a fork, inherited the same open door intact.

## 4. Newsletter Sign-Up on Approval

On approval, the entrant’s address is inserted into the newsletter table with an `INSERT OR IGNORE`. The idealized module presents it as a “growth strategy” for the marketing database, one that would guarantee a list of only real, validated users. That’s the framing to flip.

> [!WARNING]
> **Signing up for a contest isn’t consenting to marketing**
> Whoever submits their track consents to taking part in the festival, not to receiving a newsletter: these are two different legal bases (Chapter 13). Signing approved entrants up to the mailing list by default, without explicit and separate consent, is a GDPR compliance problem, not a product strength. The comments in the source give away the developer’s own doubt. The fix is simple and points in the opposite direction from the “convenient” one: a distinct marketing consent, opt-in, collected at the moment of sign-up and recorded; approval for the contest must not drag the newsletter sign-up along with it as a side effect.

> [!IMPORTANT]
> **The Canon**
> - A `pending → approved/rejected` workflow with a `registration_active` master switch.
> - The public upload of the tracks is the front of the RCE chain: gate it and validate it like every upload (Chapter 7).
> - Approval is an admin action: gate by **role**, not just by login (no role-blind gate).
> - Signing up for a contest isn’t consent to marketing: no newsletter sync without explicit, separate opt-in.

---
*Next Chapter: Festival Logic — Voting & Anti-Fraud Protection. The public vote, the defenses that truly count, and the merely cosmetic ones.*
