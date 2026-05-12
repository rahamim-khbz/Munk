# Architecture Design: PWA & Community Feedback Loop

## 1. Constraints
- [x] **Scale:** Static site hosted on GitHub Pages. Expected hundreds to low thousands of readers.
- [x] **Consistency:** Readers must receive updates (new pages or edited text) reliably without getting stuck on a stale cache.
- [x] **Latency:** Instant load times for reading. Sub-second transitions between chapters.
- [x] **Team:** Solo maintainer. Static HTML generation pipeline. No existing backend servers.
- [x] **Cost:** Free tier only (GitHub Pages).

## 2. Core Trade-offs
- **Caching vs. Freshness:** Aggressive caching gives the best mobile experience but risks serving outdated HTML if the corpus is updated. We must prioritize cache invalidation.
- **Feedback Friction vs. System Complexity:** A frictionless feedback form requires a server or third-party service, while a GitHub link is free but adds friction for non-technical users.

## 3. Options

### Caching Strategy (For Updates)
**Option A: Cache-First with Hard Versioning**
Every time you run the build script, it generates a new `VERSION` hash in the Service Worker. The browser checks the version, wipes the old cache, and downloads the new files.
* Pros: Guarantees users see the exact new version.
* Cons: Requires users to redownload all cached files even if only one typo was fixed.

**Option B: Stale-While-Revalidate (SWR)**
The Service Worker instantly serves the cached chapter, but simultaneously checks GitHub Pages for a newer version in the background. If a newer version exists, it updates the cache so the *next* time the user opens it, they see the update.
* Pros: Instant loading; bandwidth efficient.
* Cons: Users might read a stale version for one session before seeing the update.

### Feedback Mechanism
**Option A: GitHub Issue Link ("Propose an Edit")**
A button at the bottom of every chapter: "Found an error? Open an issue." It pre-fills the GitHub Issue title with the current chapter name.
* Pros: Zero cost, zero infrastructure. Keeps edits tracked natively where the code lives.
* Cons: Requires the reader to have a GitHub account.

**Option B: Formspree / Google Form Modal**
A "Suggest Edit" button opens a lightweight modal with a form that submits directly to your email via Formspree (free tier) or a Google Form.
* Pros: No login required for readers. Very low friction.
* Cons: You receive emails instead of tracked Git issues. Requires a 3rd party free account.

## 4. Recommendation

**For Caching:** I recommend **Option B (Stale-While-Revalidate)**. It provides the absolute fastest mobile experience. To address the freshness issue, we will add a small JavaScript check: if the Service Worker detects a new version in the background, it shows a subtle "Update available - click to refresh" toast notification.

**For Feedback:** I recommend **Option A (GitHub Issue Link)** if your audience is primarily scholars/developers who are comfortable with GitHub. However, if you expect general readers, I recommend **Option B (Formspree)** because it removes the login barrier, ensuring you actually receive the correction suggestions.

## 5. Decision Record
* **Decided:** Lazy-load runtime caching (PWA without aggressive upfront download).
* **Decided:** SWR caching strategy with version invalidation to allow seamless corpus updates.
* **Decided:** Option A (GitHub Issues link) for reader feedback mechanism.

## 6. Open Questions
* None remaining. Design fully approved.
