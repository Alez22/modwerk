# Full-owner menu backend prototype

`menu_owner_backend.c` connects the portable menu compositor to the full runtime
owner lease. It is proposed base-side code, not an installed registry, package
metadata format or exported ABI. The caller supplies already admitted, base-owned
storage and a trusted base dispatcher, holding the same stable loader/editor lock
through validation and invocation. The dispatcher may not wait or reenter.

Binding copies up to four owner-lease/action pairs. Several actions may use the
same lease, and different owners may use the same action ID. Duplicate pairs are
refused, as are different lease objects claiming one module/generation identity.
The caller's binding array may then disappear; lease objects, the backend object,
base dispatcher and its context must remain alive until all references retire.
The compositor independently copies labels and orders unique action keys.

For every owner check and allowed action invocation, the adapter resolves the
short menu identity to that admitted lease, then verifies its full record and
exact current published position. A retained rollback image is insufficient.
Unknown action IDs never reach the dispatcher. A retired activation cannot run
again when the old image is restored. A new activation needs a new admitted lease
and backend object; neither object may be reset to revive old references.

The adapter does not resolve or call a raw module-pool function pointer. The
trusted base dispatcher must enforce typed contribution admission, executable
entry bounds, module-set readiness and the actual handler contract. Complete
native transition hooks must retire the activation before replacement/removal;
polling cannot detect a replace-and-restore interval that happens between calls.
Dispatch success means only that the trusted callback accepted the action.
Any asynchronous job needs its own owner/source lifetime, copied intent and
cancellation contract; this adapter grants no background-work lease.
Source ownership, callback quiescence and native pointer reclamation remain
separate requirements. A successful owner check does not authorize sample writes.

The host fixture uses the unchanged real loader with synthetic machine glue,
then composes and dispatches menu actions while checking full owner identity.
Its immediate detachment acknowledgement is valid only for that host model,
which has no stock menu references. A separate stock-free ColdFire fixture
executes the compiled helper, backend and compositor with synthetic loader
answers. Neither test executes uploaded module code or qualifies a native
menu/USB lifecycle. Exact results and limits are recorded in TESTING.md.
