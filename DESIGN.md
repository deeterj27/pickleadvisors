# Pickle Ecosystem Editorial Design System

## Concept

**The Operator's Newsroom**

A working editorial desk for companies being built, backed, and published. The system borrows the authority of a financial briefing, the speed of a newsroom, and the precision of an operator's dashboard without becoming a newspaper costume or a generic SaaS interface.

## Reference translation

### Fitt Insider: adopt

- Clear category thesis before the content grid
- Editorial metadata, rules, and disciplined modular rhythm
- Media and platform/services in one navigation system
- Publication as proof of domain intelligence
- Repeated but restrained newsletter/conversion modules

### Fitt Insider: reject

- A homepage dominated by a large article archive
- Media-first hierarchy that buries high-intent advisory conversion
- Generic publication thumbnails without a strong Pickle point of view

### Feed Me: adopt

- Founder voice as a core product feature
- One-line publication promise
- Visible social proof and personality
- Commercial/community links that feel native to the editorial identity

### Feed Me: reject

- Substack-native modal dependence
- Personal-brand whimsy that weakens implementation and capital credibility
- Newsletter subscription as the only meaningful conversion

### Counter Service and Breaking News Desk: adopt

- Strong mastheads and compact utility labels
- High-contrast headlines
- Rules, rails, issue codes, timestamps, and section markers
- A repeatable system that makes every artifact recognizable

### Deet's Eats editorial system: adopt

- Warm paper, ink, deep green, and acid-lime palette
- Serif display type paired with utilitarian sans
- Dot-grid paper texture
- Left rail / desk label concept
- Crisp bordered modules and one black inversion module
- Confident CTA band and visible footer metadata

### Public sell sheets: reject

- A literal one-page print layout on the web
- Dense pricing-card rhythm on the homepage
- Full-height decorative rail on mobile
- Public exact advisory pricing

## Color tokens

- `--paper: #E8DED0`
- `--paper-light: #F6F0E7`
- `--ink: #10110F`
- `--rule: #282A25`
- `--pickle: #087B36`
- `--pickle-bright: #00C851`
- `--lime: #B8FF38`
- `--muted: #625F57`
- `--white: #FFFDF8`
- `--danger: #B23A2E`

### Color rules

- Warm paper is the default editorial canvas.
- Ink is the primary type and dark-surface color.
- Deep green identifies Pickle and structural rails.
- Acid lime is reserved for active signals, underlines, small data labels, and one primary CTA at a time.
- Bright legacy green may appear in Deet's D bug but should not flood large surfaces.
- Pink/coral is removed from the core website system. It may appear only inside an original media artifact that already uses it.

## Typography

### Display

`Georgia, 'Times New Roman', serif`

Use for editorial hero statements, major section theses, and selected pull quotes. Large, high-contrast, tight line-height. Do not use for body copy or every card title.

### Body and UI

`Archivo, Arial, sans-serif`

Use local Archivo 400, 700, and 900 files. This is the primary body, navigation, card, and CTA face.

### Utility and numbers

`'Space Grotesk', Arial, sans-serif`

Use for prices if ever approved, issue codes, data values, CTA labels, and compact system readouts.

### Metadata

Use Archivo or Space Grotesk at small sizes with generous letter spacing. Monospace may be used sparingly for dates, route-like labels, or system status, but not as a default AI cliché.

### Punctuation

Do not use em dashes anywhere on the website. Use a period, comma, colon, or rewrite the sentence.

## Layout

### Desktop

- Max content width: 1320px
- Outer gutters: 40 to 64px
- Twelve-column editorial grid
- Major sections separated by full-width rules, not floating rounded containers
- Alternating dense editorial bands and quieter reading space
- Asymmetry is intentional: 7/5, 8/4, and 5/7 splits are preferred over repeated thirds

### Mobile

- 20px outer gutters at 390px and 430px
- No horizontal overflow
- Navigation control remains visible and operable
- Hero display type uses controlled line breaks and `overflow-wrap`
- Rails collapse into top labels, not left-side vertical strips
- Primary CTA remains visible without forcing two full-width buttons above the first proof point
- Editorial modules reorder by argument, not by desktop source order alone

## Surfaces and rules

- Square or 2 to 8px corner radii; avoid pill-card saturation
- One-pixel ink rules are the primary divider
- Three-pixel green rule may be used for mastheads or active desk labels
- Dot-grid texture: 7px repeat, `#50493F` at approximately 0.12 to 0.14 opacity
- Shadows are rare. Use border, contrast, and whitespace first.
- Dark modules invert to ink background with paper type and lime details

## Core components

### Masthead

Text-led Pickle Advisors wordmark, ecosystem navigation, one primary CTA, and a visible mobile menu control. The retired arrow-P mark is not used in the masthead or public assets.

### Signal rail

A horizontal or wrapping strip of short operating signals such as `AI IMPLEMENTATION`, `CAPITAL PERSPECTIVE`, `MEDIA INTELLIGENCE`, and `BROOKLYN / NYC`. It should feel like metadata, not a stock ticker.

### Desk module

Each pillar receives:

- Issue-style number
- Verb: Build, Back, Publish
- One-line job
- Three concrete outputs
- One relevant proof artifact
- One CTA

The three modules should not be identical cards. Each gets a distinct composition while sharing the same type and rule system.

### Artifact frame

Use real work: audit pages, reports, content cards, podcast covers, editorial graphics, or genuine workflow screenshots. Include source/category/date metadata. Never invent metrics or UI. Do not publish sell sheets as website content.

### Founder block

Use the current `jonathan.jpeg`. Crop deliberately with `object-position` tuned at desktop, 430px, and 390px. Pair the portrait with a concise ecosystem biography and verified proof. Avoid a large generic rounded photo card.

### CTA band

One strong sentence, one primary action, one secondary text link, and utility metadata. Use deep green or ink with lime details. Do not return to a disconnected pink section.

## Page signatures

### Homepage

Editorial overview with ecosystem thesis and high-intent conversion.

### Advisory

System diagrams, operating artifacts, audit flow, and installed outcomes. Dark ink plus paper.

### Capital

More restrained and institutional: ink, paper, lime signal, sparse copy, explicit private-conversation boundary.

### Media

Most expressive page. Use real Deet's cards, stronger image density, content taxonomy, an official Substack signup embed, and the latest verified Spotify episode embed.

### Retired resource routes

There is no Resources section in the public information architecture. Legacy Resources and GEO checklist URLs redirect to Deet's Eats Media and remain `noindex` so old links do not break.

## Motion

- Small hover shifts on arrows, rules, and underlines only
- Respect `prefers-reduced-motion`
- No scroll-jacking, floating gradient blobs, or continuous marquees that impede reading
- If a signal rail moves, it must pause on hover/focus and remain readable without animation

## Accessibility

- Body text contrast must meet WCAG AA
- Lime must not carry body text on paper without a dark container
- Visible focus states use ink + lime outline
- All navigation and menu controls are keyboard accessible
- Semantic headings remain sequential
- Images require meaningful alt text or empty alt when decorative
- Minimum 44px touch targets on mobile

## Anti-patterns

- Generic SaaS three-card service grid
- AI gradients, glowing orbs, circuit patterns, robot icons
- Fake dashboards or invented client metrics
- Excessive pills and rounded rectangles
- Newspaper cosplay: fake paper tears, random stamps, or overused typewriter effects
- Making every section green
- Treating Deet's Eats as a logo row instead of a media product

## Quality gate

The redesigned site must:

1. Be visibly stronger than the current production baseline at 1440px.
2. Have no horizontal overflow at 390px or 430px.
3. Preserve a readable hero, visible navigation, primary CTA, and first ecosystem proof at mobile sizes.
4. Use real artifacts and current Jonathan photography.
5. Keep advisory conversion primary while making capital and media first-class pillars.
