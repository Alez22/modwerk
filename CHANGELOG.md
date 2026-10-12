# Application changelog

## 12 October 2026

- Allowed up to 30 seconds for deployment release synchronization so a successful inventory fanout is not mistaken for a ten-second timeout. Existing idempotent retries, recipient preferences and digest processing remain in place.
- Fixed imported README provenance after adding audio previews, and limited E-Verb's monochrome capture checks to instrument screenshots.
- Documented imported-module media provenance updates and screenshot selection for mixed audio/image media.
- Added report triage: awaiting review, waiting for the reporter, investigating, confirmed bug and fix awaiting verification. Questions and suggestions are classified separately.
- Module warnings and quiet periods use confirmed bugs applicable to the current version or with unknown applicability. Unconfirmed reports remain visible; configuration reports do not blame individual modules.
- Maintainers can request information, classify, confirm, close and reopen reports through GitHub comments or consent-controlled report forms. Verified claimed maintainers can triage without release-author privileges. Existing author updates retain automatic CI-gated merge and publication.
- Added an insufficient-information closure outcome, retained closure explanations and kept older closed history without inferred outcomes. Retries and verified command acknowledgements avoid duplicate reporter notifications.
- Updated contributor prompts, GitHub report instructions and developer context. Firmware qualification, publication and verified-download resolution gates remain in force.
