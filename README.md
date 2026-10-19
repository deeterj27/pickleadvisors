# Pickle Advisors website

A static site with shared Python templates, plain HTML, and small browser scripts. No client-side framework is required.

## Edit once

- `content/site.json`: navigation, social destinations, contact, analytics ID, existing audit receiver.
- `content/advisory.json`: service fit, audit expectations, implementation scope, boundaries.
- `content/newsletter.json`: last validated newsletter snapshot. The local scheduled task refreshes the three newest public RSS stories and optimized images.
- `content/social.json`: the latest three verified Instagram posts used on Home and Media. The daily task reads the public profile in the browser, orders posts by actual publication date (ignoring pinned position), and imports observed cover assets using `scripts/update_instagram.py <local-manifest.json>`. It never uses private APIs or stores Instagram credentials.
- `content/podcast.json`: the latest verified Unpackaged Goods interview, shared by Home and Media. The official Spotify player is lazy-loaded with a direct episode link as a fallback.
- `content/audit.json`: backend-compatible selections.
- `templates/pages/`: page-specific content and metadata.
- `templates/partials/`: shared navigation, footer, workflow demonstration, and audit form.
- `assets/site.css`, `assets/audit.css`: current visual styles. `assets/fonts/brand.css` serves the licensed local fonts.

Run `python scripts/build_site.py` after editing. Commit both sources and generated pages. Do not edit generated HTML directly.

## Local checks

Python 3.12 and Node 24:

```sh
python -m pip install -r requirements.txt
python scripts/build_site.py
python -m unittest discover -p 'test_*.py'
node --test tests/*.test.cjs
python scripts/build_site.py --check
python scripts/preview_site.py --port 8882
```

The local preview uses a fake audit receiver; it never sends test leads to production. Open `/audit/?test=confirmed` or `/audit/?test=error` to exercise response states.

The checks cover links and anchors, structured data, sharing metadata, common navigation, form naming, permitted content, validation, receiver payload compatibility, and submission failure states. They do not submit test leads to production. Check responsive layout and keyboard interaction in a browser before visual releases.

## Publishing and freshness

GitHub Pages uses `.github/workflows/site.yml`. Pushes, pull requests, and manual runs execute the checks; only non-PR runs deploy after the checks succeed.

A Codex task on the owner's Mac refreshes the public RSS selection and checks the public Instagram grid daily at 8:17 AM America/New_York, validates changes, and commits only the newsletter and Instagram snapshots, artwork, generated pages, and sitemap. The Mac and Codex must be available for that task. The refresh was moved out of GitHub Actions because Substack returns HTTP 403 from GitHub's hosted runner; the approved local feed fetch works. On failure, the last valid published selection remains in place. The task does not overwrite a dirty working tree and reports actionable failures. To run a refresh manually, use `python scripts/refresh_newsletter.py`, then the build and checks above before committing and pushing.


`python scripts/package_site.py` produces `_site/` with only public assets and pages, retaining legacy redirects and verification files. The custom domain and existing sitemap/robots settings are preserved. Revert a problematic change in Git and publish through the same checked workflow.

## Inquiry analytics

Every page uses the same analytics configuration. Events contain only category/step/error codes, never form answers, email addresses, or receipt IDs:

- `inquiry_click` with `audit`, `contact`, or `media` category; a click is not an inquiry received.
- `audit_start`, `audit_step_view`, `audit_validation_error`, `audit_submit_attempt`, `audit_submit_error`.
- `generate_lead` only when the receiver returns readable JSON `{ "saved": true, "receiptId": "..." }` after durable storage.

GA4 reporting/admin settings were not changed by this repository. Build a funnel using these events once collection is verified in that account.

## Audit receiver boundary

The existing Apps Script endpoint and sheet are retained. `backend/Code.gs` contains the versioned receiver source, with the private sheet ID replaced by a deployment placeholder. Deploy updates through the existing AI Audit project, replacing that placeholder with its existing ID. Keep execution identity and access unchanged.

The receiver validates inputs, escapes spreadsheet formulas, and saves new submissions to `Audit Intake v2` in the existing spreadsheet. It checks the exact header schema before writing; Phone is column I, Tools J, and Request ID U. Historical `Sheet1` headers and lead values remain untouched because earlier rows may follow different layouts. Existing request IDs in Sheet1 are recognized to avoid duplicate rollout retries. Do not relabel historical columns without a separate row-level reconciliation.

A script lock, request ID, and payload hash deduplicate retries. The browser retains the original payload after an uncertain submission and disables editing; Retry resends that same request. Starting a new form or reloading generates a new ID, so the error copy asks visitors to keep the page open or contact Jonathan with their reference. Only a saved response with a matching receipt ID records `generate_lead`; there is no automatic network retry.

After the storage flush, the receiver can send a submitter receipt and Jonathan an owner alert using MailApp. `AUDIT_MAIL_ENABLED` defaults to false until the deployment approval and controlled test. The audit is free; implementation is scoped and priced separately; no appointment is booked automatically. Mail failures do not undo a saved lead. Columns W/X track `pending`, `sending`, `sent`, or `review`. Quota or pre-send authorization failures leave messages pending. `retryPendingAuditNotifications()` processes at most 20 pending rows and can be run by the owner; it is not exposed through HTTP. No trigger is created by this change.

MailApp does not provide a transactional idempotency key or delivery receipt. Before sending, the script flushes `sending`; uncertain sends remain `sending` or `review` and are not automatically retried. The owner must inspect their Sent mailbox before resetting such a status to `pending`. `sent` means MailApp accepted the send, not verified inbox delivery. This deliberately avoids promising exactly-once email delivery. Do not bulk-reset notification statuses or replay historical leads.

Deployment approval is required before modifying the existing Apps Script project, enabling mail, merging the frontend, or running a live submission. The existing project was inspected on October 12: Version 6, execute as `jonathan@pickleadvisors.com`, access Anyone, one requested OAuth scope (`spreadsheets`). MailApp adds `https://www.googleapis.com/auth/script.send_mail`, which must be approved at action time. Preserve the current execution identity/access. No new credentials or Gmail inbox-reading scope are needed. Intended controlled test: one clearly labeled QA request using `jonathan@pickleadvisors.com` as submitter and owner, yielding two distinct emails to that same inbox. Repeat the exact request ID once and verify one lead row and no extra emails. Keep the test row labeled, and check real inbox receipt before promotion.

Deploy the backend first, restore the existing private sheet ID only in Apps Script, approve send-mail, and enable mail only for the approved live test/rollout. Update the existing deployment to a new version, retaining its URL. Then merge the draft frontend PR after checks pass. Run the read-only health check, the approved live test, and check notification status cells. On rollback, revert the web-app version and frontend commit while preserving both sheet tabs and all lead rows. Storage under the old receiver returns to Sheet1, so inspect both tabs during reconciliation.

Tests use mock Sheets and MailApp services and a local receiver; no automated check sends a live email or stores a production lead. Browser QA uses `/audit/?test=confirmed` and `/audit/?test=error`. The deployed health check is read-only and returns the version without opening lead data.

The workflow demonstration is labeled illustrative. Do not replace it with client claims or measured outcomes without supporting evidence and permission.

Instagram manifests contain exactly three objects with `url`, `title`, `date` (ISO), `format` (REEL / WATCH, CAROUSEL / READ, or POST / READ), `alt`, and `source_image` (absolute local cover path). Verify titles against visible captions or artwork; do not invent captions. When no newer post exists, retain the existing snapshot and artwork. If Instagram blocks the public grid or dates/artwork cannot be verified, retain the last valid Instagram snapshot and report the problem; independent newsletter updates can still proceed.

## Latest podcast interview

The current episode is published. Recurring podcast refresh is not enabled; the existing daily task covers the newsletter and Instagram.

Inspect the public [Unpackaged Goods show](https://open.spotify.com/show/6moZEYjORSb5XZ7LVu8b3f) in the supported browser. Choose the newest published guest interview; skip solo news episodes. Verify the guest, title, and episode link in the public description, and obtain the official player using Share > Embed episode. Update `content/podcast.json` only when a newer interview is verified. `episode_id` is the 22-character ID in its episode URL; `video` reflects whether the official embed uses `/video`; `title` and `summary` are factual, emoji-free text. `interview_start` is a confirmed timestamp from the description (or an empty string when none is given). `verified_on` is the ISO date of verification, not a guessed publication date. Keep existing metadata when the episode has not changed. Never embed arbitrary supplied HTML or URLs. No Spotify credentials or private APIs are required.

Build, test, and check reproducibility before publishing. Confirm the iframe loads the selected interview on both Home and Media, including a narrow mobile viewport. If Spotify cannot be verified, retain the last valid podcast snapshot and allow independent newsletter/Instagram updates. The player does not autoplay; Spotify controls playback availability. The visible episode title, summary, and direct link remain available if a visitor blocks the embed.

The shared podcast block also uses verified `youtube_id` and `apple_episode_id` values for direct links to the same interview. The show cover at `assets/podcast/unpackaged-goods-cover.webp` was sourced from the public Apple Podcasts listing on September 24, 2026; preserve the original artwork. YouTube and Apple show links in `content/site.json` remain stable footer destinations. Keep episode links synchronized when manually refreshing the podcast.

## Optional isolated browser regression

When Python Playwright and its Chromium browser are already installed, run `python3 scripts/qa_audit_browser.py`. It starts a temporary localhost preview, blocks all external browser requests, and uses fresh browser contexts at 1280px and 390px. It deliberately populates the trap to reproduce the October 12 client failure, then tests keyboard recovery using real inputs/FormData, fake receiver success, and identical-payload retry after a fake failure. Screenshots and results are written beside the checkout in `audit-browser-qa/`. This is not native autofill reproduction or production storage/email validation. The ordinary Node DOM test is a simulation and is named accordingly.
