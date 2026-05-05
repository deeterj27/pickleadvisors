# Claude Design Brief — Pickle Advisors Website Revamp

## Context
Pickle Advisors has shifted from being framed narrowly as food & beverage / CPG advisory to a broader consumer brand operating-systems advisory. The site copy has been updated to say **consumer brands**, while preserving the existing strengths: ops, AI infrastructure, dashboards, workflows, pricing/margin visibility, retail/ecommerce/channel planning, and Deets Eats media distribution.

Current repo/site structure is static HTML/CSS:
- Homepage: `index.html`
- Audit page: `audit/index.html`
- Resources page: `resources/index.html`
- Tests: `test_site_content.py`

Primary CTA: `Book a Strategy Call`
Secondary CTA: `Get the AI Audit`

Booking URL: `https://cal.com/jonathan-deeter-vlslzl/ai-audit-pickle-advisors`

## Goal
Improve the design so Pickle Advisors feels like a premium AI/ops advisory for founder-led consumer brands — not just a food blog, not generic SaaS, not a local consultant page.

The site should make Jonathan look like the person who can install the operational layer behind a growing consumer brand: finance visibility, pricing, dashboards, AI workflows, planning cadence, and media/distribution support.

## Audience
Founder-led consumer brands across:
- food & beverage
- wellness
- beauty / personal care
- home / lifestyle
- specialty retail
- ecommerce-native brands

They are likely running too much through spreadsheets, founder memory, scattered docs, and manual reporting. They need practical operating infrastructure, not theoretical AI strategy.

## Current Positioning
Headline:
> Fix the operational bottlenecks slowing your consumer brand down.

Support:
> Pickle Advisors builds the workflows, dashboards, pricing tools, forecasting systems, and AI automation that turn scattered spreadsheets into an AI-ready operating system.

Offer pillars:
1. Operating systems
2. AI infrastructure
3. Media & distribution

Proof points:
- $1B+ in fund systems experience
- 10+ years across startups, finance, ops
- Consumer-native retail + media network

## Design Direction
Keep:
- Green/black/cream Pickle brand palette
- Premium, operational, slightly editorial feel
- Clear CTA hierarchy
- Deets Eats media credibility as a distribution engine

Improve:
- Make it feel more expensive and more conversion-focused
- Reduce any “template landing page” feel
- Build stronger distinction between advisory, AI infrastructure, and media engine
- Better section rhythm: problem → installed system → services → founder credibility → media distribution → CTA
- Make the proof and offer feel more concrete
- Improve mobile polish without bloating the page

Avoid:
- Generic SaaS glassmorphism
- Fake dashboards with fake metrics
- Overly tech-bro AI visuals
- Food-only imagery/language
- Too many icons or generic feature cards
- Making the site feel like a newsletter/media brand first; advisory should lead

## Desired Deliverable
Create 2–3 design directions for the homepage, preferably as self-contained HTML mockups or a branchable implementation plan:
1. **Conservative upgrade** — keeps current structure, improves polish and hierarchy.
2. **Strong-fit direction** — best premium advisory interpretation.
3. **Divergent direction** — more editorial / media-commerce / consumer-intelligence feel.

Each direction should include:
- Desktop hero
- Mobile hero
- Services section treatment
- Media/distribution section treatment
- CTA section
- Notes on typography, color, spacing, and interaction posture

## Implementation Constraints
- Current site is static HTML/CSS, so avoid frameworks unless recommending a larger rebuild.
- Must preserve SEO/meta basics.
- Must keep booking and audit CTAs.
- Must be responsive at 390px and 430px widths.
- Must be easy for Gherkin/OpenClaw to implement in the existing repo.

## Design QA Requirements
Before presenting:
- Desktop screenshot
- Mobile screenshots at 390px and 430px
- No horizontal overflow
- CTA visible and obvious
- Copy readable and not cramped
- The result must feel stronger than the current production site
