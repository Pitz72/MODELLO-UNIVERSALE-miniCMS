# CHAPTER 1: Manifesto

> *For Valerio Galano: because he’s like Neo, he sees worlds in code, and he taught me to think in a different way. I wonder whether I taught him a little something in return.*
>
> *For Giuseppe Pugliese who, even though he sees the world in his own particular way, takes pride in being a web developer and keeps at his craft with passion.*

---

## Why This Protocol Exists

There’s an unresolved tension at the center of modern web development.

On one side, the frontend has reached an extraordinary maturity, both aesthetic and functional: React, TypeScript, Tailwind. Fluid animations, reusable components, type safety, hot reload. The development experience has become a pleasure, and the finished product, when it’s done well, is visually and functionally better than anything that came before.

On the other side, that revolution brought with it an infrastructural complexity wildly out of proportion to what most sites actually need. Node.js, cloud databases, containers, CI/CD pipelines, microservices, headless CMSs on subscription plans. The technical overhead and the operating cost have become the norm even for sites that would run perfectly well on five-euro-a-month shared hosting.

This protocol grows out of a specific question: **can you have the aesthetic and technical power of React without giving up the simplicity, the control, and the affordability of a PHP backend with SQLite?**

The answer, built on months of real work on real projects, is yes.

---

## The Founding Principle: The Separation of Planes

The Universal Model isn’t a technology. It’s a mental architecture.

It draws a sharp line between two planes that often get confused.

**The Presentation Plane** belongs to React. It’s the place of form, of interaction, of animation, of typography, of the color palette. It’s where aesthetic talent lives, where Tailwind turns visual intent into precise CSS, where framer-motion gives weight and breath to its movements. This plane is compiled, optimized, served as a static asset.

**The Data Plane** belongs to PHP and SQLite (or MySQL when it’s needed). It’s the place of persistence, of business logic, of security, of the content lifecycle. It isn’t “the backend” in the heavy sense of the word: no framework, no ORM, no external dependencies. Just native PHP, PDO, and a file-based database that needs no server configuration.

These two planes talk through a precise contract: the REST API. The frontend knows nothing about the database. The backend knows nothing about React. Their separation is the source of all the scalability and maintainability in the system.

---

## A Scale, Not an Absence

“Thin stack” doesn’t mean “no backend.” It means a backend pared to the bone but real, and above all it means a scale. The same skeleton—native PHP, one PDO singleton per request, one file per endpoint, no framework—plays out at different rungs depending on what you need. At the base rung sits SQLite, a database that is a single file, with no server to configure and no secret to guard. One rung up is essential MySQL, when the data or the traffic calls for it. Higher still is engineered MySQL, with hardened connections, shared preludes, and dedicated scaffolding. These aren’t three different architectures: they’re the same model at three heights.

This book is built on four real sites that sit at different points on that scale, and it reads them exactly that way. When a chapter shows “three ways to do the same thing,” it isn’t listing options at random: it’s measuring how much you can strip away, or add, to the same skeleton before it changes nature. The three-rung scale, from the base rung to the engineered tier, is the lens for the whole book.

---

## What This Protocol Is Not

It’s not a framework. It imposes no rigid code structures, requires no specific dependencies, constrains no stylistic choices.

It’s not a traditional CMS. There’s no visual page builder, no prepackaged themes, no plugin marketplace. Every site built with this protocol is unique, handmade, tailored to its purpose.

It’s not an enterprise solution. It isn’t designed to handle millions of simultaneous users, complex data flows, or distributed architectures. It’s designed for sites that need to be excellent, fast, secure, and maintainable by a small team—or even by a single person.

It’s not for someone who wants a site in ten minutes. It’s for someone who wants to understand what they’re building.

---

## When NOT to Use This Protocol

An honest manifesto has to say where it ends, too. The thin stack trades infrastructural complexity for the discipline of whoever writes it: it removes the framework and puts your attention in its place. When that trade doesn’t pay off, another stack does. Here are the cases where I’d reach for something else without hesitating.

**When the team is large.** The conventions here aren’t enforced by a framework; they’re held together by people. With one or two developers it works; past four or five, the absence of a rigid structure becomes a cost rather than a freedom, and an opinionated framework (Laravel, Next.js with its rules) repays the learning curve.

**When you need real time.** Live chat, instant push notifications, presence, simultaneous collaboration on a single document: these are workloads that want WebSockets and persistent processes, not the request-response model of PHP on shared hosting. You can force them, but it’s an uphill fight.

**When the scale is genuinely high.** Tens of thousands of requests per second, unpredictable spikes, the need to scale horizontally across many nodes: this calls for queues, distributed caches, and managed databases. Chapter 3 puts hard numbers to this, so the threshold doesn’t stay an opinion.

**When the data is complex and heavily relational.** Distributed transactions, heavy analytical reporting, models with dozens of interconnected entities: at a certain point an ORM and an engineered RDBMS aren’t overhead, they’re the right tool.

**When compliance is an explicit requirement.** Formal audits, certifications, regulated environments that demand frameworks and libraries with commercial support and a documented chain of responsibility: here, disciplined do-it-yourself is a risk not worth taking.

The rule that ties these cases together is simple: the thin stack is excellent as long as the complexity of the problem stays below the complexity a framework would impose. When it goes past that, the framework stops being a weight and becomes a safety net. Recognizing that crossover point is part of the same technical honesty that runs through the rest of the book.

---

## The Values That Guide Every Decision

**Total control.** Whoever builds a site with this protocol owns every line of their stack. No vendor lock-in, no forced update that breaks production, no dependency on an external service for the site’s survival.

**Lightness as a principle, not a compromise.** SQLite isn’t the “cheap” choice next to MySQL: it’s the right choice for 90% of use cases. Simplicity isn’t a limitation to overcome, it’s a goal to reach and defend.

**Security as architecture, not as a patch.** The security decisions are built into the design of the system: the database outside the public root, a build script that never leaves the database in the deploy, PHP sessions with HttpOnly cookies, passwords never in cleartext. These aren’t measures bolted on afterward, they’re the structure itself.

**More engineered doesn’t mean more secure.** It’s the most uncomfortable lesson these sites teach, and it comes back in almost every chapter. The technically richest site, with the most hardened connections and the most carefully tended infrastructure, is often the one with the most fragile fundamentals: a default password written into the code, no automatic backup, an anti-abuse barrier missing exactly where it’s needed. Adding complexity doesn’t pay security interest on its own, and sometimes it distracts from the two lines that actually matter. Distrusting the equation “more layers equals more secure” is one of the threads that hold this book together.

**Documentation as part of the code.** A system you can’t understand is a system you can’t maintain. This protocol is documented with the same care it’s built with, because knowledge has to stay accessible even when the context changes.

**Real experience as the only validator.** Every pattern documented in this book was pulled from code running in production. The most important lessons come from real incidents, not hypothetical scenarios: the nighttime WAL crash that forced Runtime Radio into an emergency migration to MySQL, the wave of bots that swamped its entry point. Theory without the scar doesn’t teach enough.

---

## Who It’s For

For anyone who wants to build a website that’s a living thing: not a template, not a customized WordPress, not a site spat out by a builder.

For the developer who knows React and wants a backend without having to learn a whole framework.

For the freelancer who has to deliver a fast, maintainable, secure site to a client with no budget for cloud infrastructure.

For the author, the musician, the festival, the radio station that wants a digital presence of its own: controlled, independent of the whims of the platforms.

For anyone who believes the web can still be a place made by people, for people, with no middlemen.

---

## Two Voices: “In the Wild” and “The Canon”

This book does something most technical texts avoid: it shows real code as it is, not as it should be. That’s its strength, but it can confuse, because two different things live on the same page, and they have to be kept apart.

The first voice is **“in the wild”**: the snapshot of what the four sites actually do. Here are the good choices and also the scars, the anti-patterns, the holes left open. When the text recounts that a site saves raw HTML without sanitizing it, or exposes a migration script, it isn’t recommending that: it’s documenting it. This is the body of every chapter, and it’s written without flinching precisely because the scar teaches more than theory.

The second voice is **“the Canon”**: the rule to follow, distilled. Every chapter closes with a box titled **The Canon**, which cleanly separates the prescription from the snapshot. There you’ll find what to do in a new project, cleaned of the imperfections of the real cases. If you have ten seconds and just want the rule, read that box; if you want to understand *why* the rule is what it is, read the chapter that comes before it.

> [!NOTE]
> **The reading rule, in one line**
> The body of the chapter says what the code *does* (“in the wild”); the box at the end says what you *should* do (“the Canon”). When the two diverge, the Canon is always right: the divergence is the point, not a typo.

---

## How to Use This Book

The book is organized into independent thematic chapters. You don’t have to read it from start to finish: every chapter is a self-contained reference.

To start a new project from scratch, the **Boilerplate Checklist** (Appendix A) is the practical place to begin.

To improve an existing project, the specific chapters (Database Strategy, Security & Auth, SEO Pre-rendering) offer patterns you can apply surgically.

To learn from history, the chapters with the experiential voice (the WAL crash, the bot attack on Runtime Radio, the migration to MySQL) are the most honest reading this book has to offer.

Code doesn’t lie. Neither do scars.

---

> [!IMPORTANT]
> **The Canon**
> - Separate the two planes: compiled React for presentation, native PHP with PDO for data, a REST contract between them.
> - Pick the right rung of the scale (SQLite base rung → essential MySQL → engineered MySQL), never more than you need.
> - Treat security as architecture, not as a patch, and distrust the equation “more layers equals more secure.”
> - Document the code as it is, not as it looks: the scar teaches more than theory.
> - Use the thin stack as long as the problem’s complexity stays below what a framework would impose; past that point, choose the framework.

---

*“Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away.”*
*Antoine de Saint-Exupéry*

---
*Next Chapter: Architecture & Project Structure. Where ideas become folders.*
