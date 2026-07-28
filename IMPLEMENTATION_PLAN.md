# Pickle Ecosystem Website Implementation Plan

## 2026-07-28 revision lane

- Preserve `97548e05e633554d05d0dbd1285c51f0d8e60159` and its screenshot set as the prior-candidate baseline.
- Tighten the homepage first viewport at 1440px, 390px, and 430px.
- Replace generic AI/service language with named CPG workflows and human-controlled exceptions.
- Consolidate Deet's Eats to permanent Instagram, TikTok, Unpackaged Goods, and The Deeter Digest destination links without issue artwork or provider embeds.
- Explain Pickle VC as a future selective vehicle built on combined operating and market intelligence.
- Measure word count and page height against the prior candidate, then capture production vs prior candidate vs revised candidate proof.
- No merge or publish before a new exact-head packet receives Jonathan's renewed approval.

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

Retain static HTML/CSS/JavaScript and GitHub Pages. Use one continuous homepage for the three businesses instead of separate page designs:

- `index.html` contains full `#advisory`, `#media`, and `#capital` sections
- `assets/site.css` provides one shared visual system
- `assets/site.js` provides smooth in-page navigation and the mobile menu
- `advisory/index.html`, `media/index.html`, and `capital/index.html` are noindex compatibility redirects to homepage anchors
- `resources/` legacy routes redirect to `/#media`
- `audit/index.html` remains the functional conversion workflow

A single-page static architecture creates one coherent buyer journey, keeps every business in the same visual language, preserves inbound URLs, and avoids framework or hosting risk.

## Route map

### `/`

Primary company and conversion surface. Scroll order: hero, Pickle Advisors, Deet's Eats, Pickle VC, founder proof, and one ecosystem close with the final AI Audit CTA.

### `/#advisory`

AI advisory and implementation method, systems, boundaries, and primary AI Audit action.

### `/#media`

Deet's Eats source directory for Instagram, TikTok, Unpackaged Goods, and The Deeter Digest, plus a compact brand or agency inquiry.

### `/#capital`

Pickle VC coming-soon perspective, operating lens, private conversation, and legal boundaries.

### `/advisory/`, `/media/`, `/capital/`

Noindex compatibility routes that immediately return visitors to the correct homepage section.

### `/resources/`

Retired resource URLs redirect to the Deet's Eats homepage section.

### `/audit/`

Preserve the current AI Audit flow as the dedicated functional conversion step, using the shared Pickle palette and brand system.

## Delivery phases

### Phase 1: foundations

- Complete `STRATEGY.md`
- Complete `DESIGN.md`
- Verify baseline screenshots and tests
- Copy approved local fonts and canonical media assets
- Define shared tokens/components in `assets/site.css`
- Define mobile navigation and minimal JS

### Phase 2: single-page build

- Outcome-first hero
- Full Pickle Advisors section
- Full Deet's Eats section with live providers
- Full Pickle VC section with maturity and legal boundaries
- Founder proof and cohesive ecosystem conversion close
- Compatibility redirects for retired business pages

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
- Build / Cover / Back are full scroll destinations on the homepage
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
