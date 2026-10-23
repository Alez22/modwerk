# Private native editor integration

These fixtures exercise original Beat Slicer code through the actual stock
menus in a full 1.40C emulator boot. They are not installable modules, an
exported editor ABI, a production scheduler or hardware qualification.

## SLICE contribution

`test_menu_boot.c` composes the six-row unsliced and nine-row selected-slice
menus, retaining every stock label, callback and order. It appends one
`BEAT GRID` action whose callback posts a preview intent. It returns promptly;
the driver later borrows a bounded main service to begin the preview. Owner
generation is checked both at selection and before consuming that intent.

The native remembered selection is restored to an original stock index before
dispatching the added action. Otherwise a later stock-only menu could inherit
an out-of-range appended index. The fixture admits only one contribution per
boot. Later opens retire its token and use the stock menu. All old storage
stays pinned forever: neither hiding a window nor replacing its global pointers
establishes safe package reclamation or re-admission.

The runner verifies labels/callbacks, scrolls and selects through normal panel
events, compares the resulting preview with the host oracle, and checks cancel,
stale selection and owner retirement after queuing. It explicitly prepares the
required marker state using stock clearing/grid creation; the saved test sample
already has four slices and must not be assumed unsliced merely because its
audio file was loaded again.

## Configuration and read-only results

`test_grid_ui_boot.c` adds a private configuration dialog with SAMPLE/PROJECT
BPM, 1/4/16/32/64-beat spacing and SMOOTH/EXACT boundaries. Selecting an option
advances a configuration epoch; changing it during a preview cancels the old
request before another read. Fixed label/callback arrays remain alive throughout
the run. The callback only changes intent/state; source reads and planning occur
in the bounded main service, with private planning outside the source lock.

The result shows the total slice count and whether the planner flags a need for
fades. A quiet-boundary result is not audible qualification. READY results are
revalidated, and a stale result becomes unavailable. BACK and stock NO cancel;
owner retirement cancels and closes only this fixture's own popup. None of the
dialogs offers Apply or writes markers/PCM.

For cancellation, the fixture checks the observed stock window pointer and its
own label-table identity. Stock close clears the window pointer while retaining
other table pointers. That observation may retire a read-only job, but it does
not authorize freeing/reusing any storage. The native UI/loader serialization
boundary, queued-event retirement and real package removal remain unqualified.

## Reproduce privately

Build with `menu_boot_native.py` or `grid_ui_boot_native.py`, supplying the private
stock MAIN and a new private output directory. These extend the compiled source
fixture and verify that it fits the same eight-page reservation. Run
`boot_menu_native.py` or `boot_grid_ui_native.py` with their documented `--help`
arguments, including explicit private-injection opt-in. `--selected` prepares
the four-slice/nine-row variant. Keep the source/card, compiled artifacts, LCD
dumps and logs private. Retained receipts contain hashes and observations only.

Both runners use the actual scheduler/DSP boot and stock drawing/selection,
with no UI mocks. The configured controls run compares all 20 combinations,
restarts after an option change and invalidates a completed result. Its READY
invalidation is synthetic guard input; actual stock edit/clear invalidation has
separate full-boot tests. Native calls still come from the emulator driver;
there is no installed idle service. Source identities, admission and owner
generation are test-owned, with partial writer coverage and unqualified full
interrupt masking. Static reads, atomic publication, playback, source-built
browser/USB packages and physical persistence remain unfinished.
