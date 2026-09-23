# Pickle Advisors website

A static site with shared Python templates, plain HTML, and small browser scripts. No client-side framework is required.

## Edit once

- `content/site.json`: navigation, social destinations, contact, analytics ID, existing audit receiver.
- `content/advisory.json`: service fit, audit expectations, implementation scope, boundaries.
- `content/newsletter.json`: last validated newsletter snapshot. The local scheduled task refreshes the three newest public RSS stories and optimized images.
- `content/social.json`: the curated Instagram selection used on Home and Media. Edit title, destination, date, image, and dimensions here; these posts are deliberately curated, not scraped automatically.
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

A Codex task on the owner's Mac refreshes the public RSS selection daily at 8:17 AM America/New_York, validates changes, and commits only the newsletter snapshot, artwork, generated pages, and sitemap. The Mac and Codex must be available for that task. The refresh was moved out of GitHub Actions because Substack returns HTTP 403 from GitHub's hosted runner; the approved local feed fetch works. On failure, the last valid published selection remains in place. The task does not overwrite a dirty working tree and reports actionable failures. To run a refresh manually, use `python scripts/refresh_newsletter.py`, then the build and checks above before committing and pushing.


`python scripts/package_site.py` produces `_site/` with only public assets and pages, retaining legacy redirects and verification files. The custom domain and existing sitemap/robots settings are preserved. Revert a problematic change in Git and publish through the same checked workflow.

## Inquiry analytics

Every page uses the same analytics configuration. Events contain only category/step/error codes, never form answers, email addresses, or receipt IDs:

- `inquiry_click` with `audit`, `contact`, or `media` category; a click is not an inquiry received.
- `audit_start`, `audit_step_view`, `audit_validation_error`, `audit_submit_attempt`, `audit_submit_error`.
- `generate_lead` only when the receiver returns readable JSON `{ "saved": true, "receiptId": "..." }` after durable storage.

GA4 reporting/admin settings were not changed by this repository. Build a funnel using these events once collection is verified in that account.

## Audit receiver boundary

The existing Apps Script endpoint and sheet are retained. `backend/Code.gs` contains the versioned receiver source, with the private sheet ID replaced by a deployment placeholder. Deploy updates through the existing AI Audit project, replacing that placeholder with its existing ID. Keep execution identity and access unchanged.

The receiver stores written answers alongside their selected categories, validates required inputs, escapes spreadsheet formulas, and uses a script lock plus a request ID column to deduplicate retries. The browser sends answers in a POST body, follows Google's ContentService response redirect, and requires a saved receipt before recording `generate_lead`. It keeps one random request ID for the form session and never retries automatically. A timeout is still uncertain; visitors are asked to email before retrying. Existing GET clients continue working during rollout. The receiver does not send automated emails or book appointments; Jonathan reviews the lead sheet and replies.

Tests use a mock sheet and a local form receiver. The deployed endpoint's health check is read-only and returns the receiver version without accessing lead data. No test leads are inserted into the live sheet.

The workflow demonstration is labeled illustrative. Do not replace it with client claims or measured outcomes without supporting evidence and permission.
