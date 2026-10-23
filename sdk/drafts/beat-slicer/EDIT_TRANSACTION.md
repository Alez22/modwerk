# Apply/Undo transaction coordinator

`edit_transaction.c` is a portable base-side coordinator, **not a native atomic
publisher, installed service or exported ABI**. The source, ownership, playback,
exchange and quarantine callbacks are synthetic in its tests. Live enablement
still requires their separate owner-reviewed implementation and qualification.

Apply names the exact prepared candidate. The coordinator acquires the preview
backend's same lock, revalidates the complete candidate, checks the playback
policy and revalidates again before publishing. A no-op candidate writes nothing
and creates no history. Pending locks or preflight callbacks yield without a
write. The lock stays held through publication, refresh and post-validation.

Before an exchange it allocates history identity and enters the guard's writer
lifetime, retiring earlier previews. The backend receives full expected and
desired tables, including all inactive rows. It must return either:

- `COMMITTED`: desired markers and all required native refreshes completed.
- `UNCHANGED`: the complete prior state, including auxiliary native state,
  is intact or restored after an internal failure.
- `FAULT`: neither guarantee can be made.

The coordinator checks metadata and the complete resulting table before
reporting success. Publication cannot return pending: ownership and any rollback
must finish before unlocking. A backend fault or inconsistent post-state revokes
previews, invokes native quarantine while still locked and permanently faults
the journal. Quarantine must independently keep native consumers away from an
inconsistent source. Merely invalidating a preview cannot do that. No such
native quarantine is implemented here, and the coordinator cannot repair an
untrusted backend or an unsafe read after the fact.

A successful Apply stores its own before/after tables and source snapshot in
base-owned storage. It retains no candidate/session pointer. Undo requires its
distinct confirmation ID, unchanged guard revision, owner/source/editor/playback
identity, chosen tempo, metadata and every expected after-row. An intervening
tracked edit retires Undo even if it restores identical bytes. Unselected tempo
changes alone remain allowed. Undo checks playback policy against the complete
table being restored, including its old end/loop points; it is not a
bypass for the audio requirement.

A rolled-back Undo keeps history but issues a new confirmation ID. Counter
exhaustion retires it instead of reusing an ID. A successful Undo consumes the
journal. New Apply calls cannot silently replace existing history: the caller
must explicitly discard it first. Forgetting history does not change settings.
Faulted journals cannot be reused. All calls have one background owner; callback
reentry is refused while a transaction is active.

The host and ColdFire fixtures inject failure after every table scalar and the
auxiliary refresh, model complete rollback, test stale data and identity at
callback boundaries, and exercise session reuse, cancellation, confirmation
replay, exhaustion and quarantine. Those results prove orchestration against
the authored backend contract. They do not prove stock atomicity, cache/ISR
exclusion, actual voice refresh, persistence, audible output or physical Undo.

The pinned target layout uses 4,056 bytes per journal. A journal, preview
session, candidate and guard total 10,092 bytes before any backend/menu state,
code or stack. Plan a real contiguous allocation for this caller-owned state;
zero object BSS does not remove that requirement. See TESTING.md for source
bindings, the full compiled Flex transaction fixture and refresh-order limits.
