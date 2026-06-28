# CHAPTER 19: Festival Logic — Admin Dashboard, Settings & Reporting

This dashboard is the contest’s command board, but it isn’t a console of its own: it’s the **festival specialization** of the general admin area of Chapter 14. The structure that holds it up (the guard that protects the area, the layout, the backup outside the docroot) belongs to that chapter; what stays here is what’s specific to the festival, the phase switches, the contest KPIs, the approval, the ranking, and the report. Reading this chapter as the festival instance of a general pattern, and not as an isolated panel, keeps you from duplicating what Chapter 14 has already explained.

And like the other two chapters of the module, this one too lines the idealized text up against the real code, where two promised functions aren’t what they seem: the final report and the finalists.

## 1. The Master Switches

The `settings` table, a key/value pair, is the festival’s fuse box: `registration_active` opens or closes the sign-up form, `voting_active` the voting session, `current_round` indicates the phase. One switch here opens or closes a whole phase for everyone.

The table is publicly readable (the frontend consults it to know what to show) and writable only by the admin. A detail already met in Chapter 18 comes back here: the reading of the flags accepts both `'1'` and `'true'`, because the write never settled on a single convention. It’s a defensive patch that makes up for an inconsistency upstream, not a design.

## 2. The Contest KPIs

The area shows the indicators in real time: the participants broken down by state (pending, approved), the total volume of votes, an estimate of unique voters. On that last one a caveat is needed, because the module calculates it “by IP and cookie.” The cookie, though, is a cosmetic defense (Chapter 18): it gets deleted, so it counts for little as a measure of uniqueness. The reliable signal is only one, the IP within the twenty-four-hour window; the “unique voter” should be read as “unique IP,” with all the imprecision that entails (the corporate network that collapses many voters onto a single address).

## 3. Approval and Ranking

The admin sees the participants in a table, listens to the track, and decides the outcome; approval is the only action that fires off the official confirmation email. That same action, though, is granted to anyone who’s logged in, not just to administrators: the role-blind gate of Chapter 17 applies from here too.

The ranking is ordered by `vote_count`, and it’s fast precisely because it reads a ready-made counter instead of counting the votes. But it pays for that with fragility: without a periodic reconciliation, that counter can diverge in silence from the real votes (the box in Chapter 18 explains why, and what to add). Then there’s a promise the text makes that the code doesn’t keep.

> [!WARNING]
> **The `finalist` state tells of a plan never carried out**
> The idealized module talks about “selecting the finalists to move into the next round,” as if there were a `finalist` state the admin assigns. In the participants’ enum that state exists, but **no line of code ever sets it**: the contest’s phases are managed by switching on the boolean flag `in_current_round` on groups of participants, not by promoting them to a state. That `finalist` is a schema documenting an abandoned intention, not a function. It’s worth knowing how to spot it: a state that exists in the database but that no one writes is a fossil, and describing it as active confuses the reader about how the contest really runs.

## 4. The Reporting That Was Never Switched On

At the close of voting, the idealized module says, the backend sends the staff a final report email: total votes, the Top 20 most voted, some geographic statistics on the IPs. The function exists, it’s called `sendVotingReport`, and it’s written in full. There’s just one problem.

> [!WARNING]
> **A feature built and disabled: “Phase 2”**
> `sendVotingReport` is fully implemented but **disabled in the code**, commented out with the label “Phase 2.” It’s true that the backend *contains* the report; it’s false that it *sends* it. It’s the twin of the `finalist` state from the previous paragraph: code present, function dormant. Presenting a commented-out capability as operational is one of the easiest ways for documentation to fall out of step with the software: the rule, for anyone writing technical documentation, is to describe what the code *does*, not what it’s *ready to do if someone reactivates it*. As long as “Phase 2” stays commented out, the final report is a promise, not a function.

## In Summary

The festival panel is consistent with the module’s philosophy, simple switches and essential numbers, but it carries the cracks of the “switch-built” approach: a uniqueness estimate that trusts a cosmetic cookie, a ranking that can drift without noticing, a `finalist` state never used, and a report never switched on. These are the points where the real contest diverges from its narrated version, and knowing them is what separates someone who can govern it from someone who only thinks they can. The structure that holds this panel together (guard, layout, backup) stays in Chapter 14, of which this is the festival version.

> [!IMPORTANT]
> **The Canon**
> - It’s the festival instance of the admin area (Chapter 14): structure, guard, and backup live there; what stays here are the contest’s switches and KPIs.
> - The master switches have to be read consistently with how they’re written (no `'1'` versus `'true'`).
> - Show honest KPIs (unique voters by IP, aware of the `vote_count` drift, Chapter 18).
> - Don’t pass off as active the features built but disabled, and remove the vestigial states (a `finalist` state never set).

---
*Next Chapter: Social Interactions & Reactions. The last surface of the CMS, where it’s the anonymous public writing into the database.*
