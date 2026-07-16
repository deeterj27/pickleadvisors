# Pickle Ecosystem Website Implementation Plan

## Production baseline

- Repository: `deeterj27/pickleadvisors`
- Working directory: `/Users/jonathandeeter/.openclaw/workspace/projects/pickleadvisors-site-redesign`
- Baseline commit: `6da45ea`
- Hosting: GitHub Pages
- Canonical domain: `pickleadvisors.com`
- Current stack: static HTML/CSS/JavaScript
- Existing routes: `/`, `/audit/`, `/resources/`, `/resources/geo-checklist.html`
- Existing analytics: `G-2X2CE22ZED`
- Current founder image: `jonathan.jpeg`
- Baseline tests: `python3 -m unittest -v test_site_content.py`
- Baseline screenshots: `qa/baseline/desktop.png`, `qa/baseline/mobile-390.png`, `qa/baseline/mobile-430.png`

## Architecture decision

Retain static HTML/CSS/JavaScript and GitHub Pages. Add shared assets instead of introducing a framework:

- `assets/site.css`
- `assets/site.js`
- `assets/fonts/`
- `assets/media/`
- `index.html`
- `advisory/index.html`
- `capital/index.html`
- `media/index.html`
- `resources/index.html`
- Preserve `audit/index.html`

A static architecture is the lowest-risk option, keeps deployment trivial, and is fully capable of the required editorial system.

## Route map

### `/`

Ecosystem homepage and primary conversion surface.

### `/advisory/`

AI advisory and implementation. Primary CTA to `/audit/` and strategy call.

### `/capital/`

Pickle VC / capital perspective and private conversation.

### `/media/`

Deet's Eats Media, programs, real editorial artifacts, and brand/agency inquiries.

### `/resources/`

Editorial resources and high-intent lead magnets.

### `/audit/`

Preserve current secure AI Audit flow, then restyle to the shared system after functionality is verified.

## Delivery phases

### Phase 1: foundations

- Complete `STRATEGY.md`
- Complete `DESIGN.md`
- Verify baseline screenshots and tests
- Copy approved local fonts and canonical media assets
- Define shared tokens/components in `assets/site.css`
- Define mobile navigation and minimal JS

### Phase 2: parallel page builds

- Homepage
- Advisory + capital
- Media + resources

Each lane writes unique files and may only read shared assets after the foundation commit.

### Phase 3: integration

- Founder bio/photo
- Audit and CTA integration
- Real artifacts and link validation
- SEO, OG, sitemap, robots, analytics
- Content tests

### Phase 4: independent QA

- Serve locally
- Run automated tests
- Capture 1440px, 390px, and 430px screenshots
- Check scroll width, navigation, CTAs, routes, focus, contrast, reduced motion, image loading, and metadata
- Compare candidate screenshots against `qa/baseline/`

### Phase 5: production

- Settled-tree review
- Credential and placeholder scan
- Commit and push
- Wait for GitHub Pages propagation
- Capture live 1440px, 390px, and 430px screenshots
- Verify live routes, CTAs, analytics script, OG metadata, sitemap, robots, CNAME, and HTTPS
- Record rollback commit

## Build acceptance

- No horizontal overflow at 390px or 430px
- Visible, operable mobile menu
- Hero names the ecosystem and primary revenue action
- Build / Back / Publish are all visible above or immediately after the fold
- Current Jonathan photo remains
- Biography supports advisory, capital, and media
- No public exact advisory pricing
- No unsupported metrics, client logos, or testimonials
- Deet's Eats uses real artifacts and canonical marks
- Audit and resource routes remain functional
- Google Analytics ID remains present
- Candidate materially outperforms the production baseline

## Rollback

The pre-redesign production baseline is commit `6da45ea`. If the launch fails live QA, revert the deployment commit or reset the GitHub Pages branch to that commit, then verify `https://pickleadvisors.com` again.
