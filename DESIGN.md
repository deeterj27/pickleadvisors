# Pickle Advisors clean editorial design system

## Concept

**Three businesses. One clear front door.**

Pickle should be understood before it is admired. The website explains three distinct businesses in plain language, then proves them with real work. Editorial character comes from typography, photography, and judgment. It does not come from newsroom decoration.

## Reference translation

### Fitt Insider: primary structural reference

Adopt:

- One sentence that explains the product
- Restrained navigation with actual destination names
- One clear conversion near the top
- Real content visible in the first viewport
- Simple section labels, rules, and repeatable image cards
- Wide whitespace and a mostly neutral canvas
- Media integrations that feel native to the page

Do not copy:

- Fitt's logo, typeface, green-yellow, health taxonomy, or article archive
- A publication-first hierarchy that hides Pickle's advisory conversion
- Sticky newsletter overlays

### The New Consumer: supporting editorial reference

Adopt:

- Founder point of view
- Real consumer-market artifacts
- Clear value to operators, founders, and investors

Reject:

- Long introductory copy
- Membership pricing and gated research structure
- Personal publication identity as the entire company

### Forerunner: supporting capital reference

Adopt:

- Sparse capital language
- Confidence through restraint
- Simple navigation and low visual noise

Reject:

- Minimalism so extreme that the three businesses become unclear
- Venture language that implies Pickle VC is already operating

## Information architecture

Primary navigation uses business names:

1. **Advisory**: Pickle Advisors
2. **Pickle VC**: coming soon
3. **Deet's Eats**: media
4. **AI Audit**: primary conversion

Build, Back, and Publish are supporting verbs. They are not the navigation labels or the only explanation of the company.

## Homepage flow

1. One plain-language company statement and one primary CTA
2. Three clearly separated business blocks
3. One consolidated Deet's Eats proof section with direct signup
4. One compact founder and AI Audit conversion section
5. Simple footer with boundaries

Remove repeated ecosystem thesis sections, decorative signal rails, duplicated media sections, and artifact grids that restate the same idea.

## Media page flow

1. Clear Deet's Eats promise
2. Three uniform format cards using real assets
3. Compact latest-episode player
4. Direct Deeter Digest signup
5. Simple partnership explanation and CTA

The Spotify player should use the compact 152px format. The official Substack embed remains the subscription system.

## Copy rules

- Name the business before describing its philosophy
- Use concrete nouns: workflows, dashboards, podcast, newsletter, video, investment platform
- Keep paragraphs to two or three sentences
- Do not use em dashes
- Do not use “ecosystem” when “company,” “business,” or a specific brand name is clearer
- Do not imply Pickle VC is active before launch
- Do not imply advisory guarantees media coverage or capital

## Color tokens

- `--canvas: #FAF8F3` for the primary page background
- `--surface: #FFFFFF` for cards and embeds
- `--surface-soft: #F1EDE5` for secondary bands
- `--ink: #11120F` for primary type
- `--muted: #66665F` for supporting type
- `--rule: #D6D1C7` for quiet borders
- `--green: #087B36` for brand and links
- `--green-dark: #075C2A` for hover and dark sections
- `--lime: #DDF77A` for the single primary action highlight

### Color rules

- The canvas is mostly neutral and untextured
- Green is an accent, not a full-page costume
- Lime appears on one primary action at a time
- Black inversion is limited to the final CTA or a compact capital module
- Original Deet's Eats assets keep their own colors inside image frames

## Typography

### Primary display and body

Use Archivo for navigation, body, hero statements, and clean interface hierarchy.

### Editorial accent

Use Georgia for business names, selected section headings, and Deet's Eats titles. Do not use oversized serif type for every major statement.

### Utility

Use Space Grotesk for small labels, status, and compact metadata.

### Scale

- Homepage H1: 64 to 78px desktop, 42 to 52px mobile
- Page H1: 58 to 72px desktop, 42 to 50px mobile
- Section title: 38 to 54px desktop, 32 to 40px mobile
- Card title: 24 to 32px
- Body: 16 to 19px

## Layout

- Maximum width: 1240px
- Desktop gutters: 48 to 64px
- Mobile gutters: 20px
- Header height: 72px desktop, 68px mobile
- Section padding: 80 to 96px desktop, 52 to 64px mobile
- Use two or three columns only when the content genuinely benefits
- First proof should appear within the first mobile viewport or immediately after it

## Components

### Masthead

Text-led PICKLE ADVISORS wordmark. Navigation uses Advisory, Pickle VC, Deet's Eats, and AI Audit. No signal rail below the header.

### Primary button

Solid lime or green, 4 to 8px radius, no shadow, no transform-heavy interaction.

### Business block

Each business receives:

- supporting verb and number
- actual business name
- one plain-language sentence
- launch status when relevant
- one destination link

All three use the same calm surface. Pickle VC does not become a dramatic black card.

### Media card

Uniform image ratio, simple format label, title, one sentence, and destination link. No oversized vertical card paired with tiny horizontal cards.

### Provider embed

Bordered white surface with no decorative shadow. Spotify uses 152px compact height. Substack remains large enough to show its complete form and terms.

### Founder proof

Use the current Jonathan photo at a restrained size. The copy explains why one operator can credibly connect the three businesses. It does not repeat the entire career history.

## Mobile rules

- No horizontal signal rail
- No giant multi-line serif headline
- One primary CTA in the hero
- Business blocks stack with visible names and boundaries
- Media cards use consistent image proportions
- Spotify and Substack embeds fill the available width
- Navigation remains a simple full-screen menu
- No horizontal overflow at 390px or 430px

## Anti-patterns

- Newsroom costume
- Dot-grid texture across large sections
- Giant highlighted serif headlines
- Repeated explanations of the ecosystem
- Dark card inserted only for visual drama
- Multiple media grids showing the same assets
- Decorative metadata that does not help a decision
- Large blank provider iframe areas
- Generic three-card SaaS services with icons
- Public sell sheets or Resources navigation

## Quality gate

The redesign must:

1. Explain all three businesses in one viewport on desktop
2. Reach the first business proof faster than the current mobile baseline
3. Keep AI Audit as the primary revenue CTA
4. Show real Deet's Eats assets without duplicate sections
5. Keep Pickle VC visibly marked Coming Soon
6. Keep editorial, advisory, and capital boundaries intact
7. Pass desktop, 390px, and 430px visual QA with no overflow
8. Be visibly quieter and easier to scan than the current candidate
