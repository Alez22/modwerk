# Application changelog

## 12 October 2026

- Fixed imported README provenance after adding audio previews, and limited E-Verb's monochrome capture checks to instrument screenshots.
- Documented imported-module media provenance updates and screenshot selection for mixed audio/image media.
- Local module README, TESTING and CPU guides can be edited without updating import checksums. Imported code, licences, archived snapshots and preserved upstream documentation retain exact integrity checks.
- Documentation PRs run a small Node-only import check so publication uses the same policy without requiring firmware builds or the full app suite. TapeHead's app checks share that policy.
- Added report triage: awaiting review, waiting for the reporter, investigating, confirmed bug and fix awaiting verification. Questions and suggestions are classified separately.
- Module warnings and quiet periods use confirmed bugs applicable to the current version or with unknown applicability. Unconfirmed reports remain visible; configuration reports do not blame individual modules.
- Maintainers can request information, classify, confirm, close and reopen reports through GitHub comments or consent-controlled report forms. Verified claimed maintainers can triage without release-author privileges. Existing author updates retain automatic CI-gated merge and publication.
- Added an insufficient-information closure outcome, retained closure explanations and kept older closed history without inferred outcomes. Retries and verified command acknowledgements avoid duplicate reporter notifications.
- Updated contributor prompts, GitHub report instructions and developer context. Firmware qualification, publication and verified-download resolution gates remain in force.
