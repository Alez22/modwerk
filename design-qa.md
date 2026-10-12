# Audio preview prototype QA

Final result: passed

The selected direction is the waveform dock, refined to preserve Modwerk's current cards, support optional recordings, and add a detail-page carousel and submission form. Existing cards and artwork take precedence over the generated concept's larger cards, typography, invented counts and illustrations, as requested by the owner.

## Evidence and normalization

- Source visual truth: `artifacts/audio-design-qa/source-refined.png` (1487 × 1058 pixels; desktop, mobile and dialog concepts share a composite canvas).
- Implementation: `http://127.0.0.1:5177/?preview=audio`, rendered with Playwright in Edge. Desktop 1440 × 1024, mobile 390 × 844, tablet 820 × 1180 CSS pixels; device scale factor 1. Screenshots match those pixel dimensions.
- Full-view comparisons: `artifacts/audio-design-qa/audio-comparison-full.png` and `audio-comparison-mobile.png`. Each comparison contains the actual source and browser capture together. Composite panels are proportionally reduced for inspection, without stretching.
- Focused comparisons: `audio-focused-card.png`, `audio-focused-player.png`, `audio-focused-submission.png` in the same evidence directory. These retain original crop density and show source and implementation controls together. The card comparison also includes the native no-audio baseline.
- States captured: idle library, hover/playing card, idle detail carousel, empty detail, selected-file dialog, invalid file, mobile library/detail/playing/carousel/dialog and tablet detail.
- Local screenshots and recordings remain in ignored `artifacts/`; none are committed.

The concept is a direction, rather than a specification for replacing the established application layout. Its mobile title-before-art order, larger artwork and decorative active-card border were intentionally not introduced. Native card structure, author/version metadata, Add/Compare controls, navigation, detail hierarchy and illustrations remain in place. The prototype toolbar is development-only review chrome.

## Comparison history and findings

The first comparison was blocked by two P2 findings, retained in `audio-comparison-iteration1-full.png`, `audio-comparison-iteration1-mobile.png` and `audio-comparison-iteration1-controls.png`:

1. **Artwork overlapped the player.** The original signal illustration extended behind the dock and its lower portion disappeared. The active card and detail artwork now reserve space for the player within the existing cover dimensions. The focused card/player comparisons and revised mobile capture show complete illustrations above the waveform. On touch devices, cards retain their original artwork size and show a passive preview hint.
2. **Submission labels inherited column layout.** The generic dialog style stacked the file icon and permission checkbox above their labels. Scoped row styles now align them, provide a 44px permission-label target, and reset the heading margin. Revised focused-dialog and mobile captures show the compact form without collisions.

The second comparison passed. No actionable P0/P1/P2 findings remain.

## Required fidelity surfaces

- **Fonts and typography:** existing system/Segoe UI and Consolas stacks are retained. Module title, author, version and footer weights remain native. Time labels use the established monospace treatment. Form labels and errors wrap legibly at 390px. The generated concept's larger text is an accepted deviation to preserve current cards.
- **Spacing and layout:** native and prototype Scale Quantizer cards both measure 362 × 295px at desktop. The dock is confined to the cover; Add/Compare and footer positioning are unchanged. Carousel and player controls have 44px targets. Desktop, tablet and mobile captures show no horizontal overflow or collisions.
- **Colors and tokens:** existing charcoal surfaces, muted text and lavender action tokens are retained. Tape Echo uses its warm signal color and Mini Verb its teal signal color. Playing progress and pause state are visible; focus uses the existing accent outline.
- **Images and icons:** existing `ModulePreview` artwork and `Icon` components are reused as explicitly requested. No generated artwork replaces existing assets. Waveforms come from decoded recordings or actual synthetic PCM, rather than decorative shapes. The artwork is sharp and complete after reserving dock space.
- **Copy and content:** clips have no description/caption field. Module information remains native. Carousel counts describe actual clips. The file form asks for a recording, credit and permission; the development toolbar and confirmation explicitly identify synthetic clips and local-only submission.

## Functional verification

Playwright verified desktop click-to-seek/play without navigation; hover preparation without autoplay or hidden-audio requests; persistent active dock; one playback owner across players; carousel wrap and stopping the old clip; keyboard seeking/play/pause; mobile module navigation without autoplay and waveform tap-to-play; single-clip and empty states; invalid-file feedback; required credit/permission; decoded upload preview; local submission increasing the carousel count; and responsive layout at all three viewports. Runtime page errors and console errors: none. Results: `artifacts/audio-design-qa/audio-verification.json`.

`npm run check` passed: 233 test files, 1751 tests, lint, TypeScript, SDK/contract checks and production build. The production bundle excludes the synthetic fixtures and submission prototype.

## Implementation checklist and limits

- [x] Desktop hover/focus dock; waveform gesture starts playback immediately.
- [x] Mobile detail player starts only after a tap.
- [x] Optional recordings; unchanged cards when absent.
- [x] Detail carousel for multiple clips and an Add preview entry point in the prototype, including empty modules.
- [x] Local file submission, validation and review playback; no clip descriptions.
- [x] Repeat visual comparison after fixing P2 findings.

The submission flow is a local prototype, resets on reload, and does not upload to the community API. Ordinary pages use existing declared module media. Server persistence/moderation is outside this prototype. Browser validation covers Chromium/Edge; Safari and hardware-generated recordings have not been exercised. No blocking visual gaps remain.
