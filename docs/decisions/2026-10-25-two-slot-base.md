# Base updates must never brick a unit: two slots — 25 October 2026

The owner asked to make the whole base update very safe, "especially regarding USB dropouts or power cuts", and
set the bar: "we cannot, under any circumstances brick devices", with the update shown on the Octatrack itself.

- **The single-copy write stays only until the two-slot base replaces it.** A power cut during today's write needs
  the startup menu's MIDI recovery (a DIN interface). The owner chose a two-slot layout with a small boot stub
  ([OCTATRACK_TWO_SLOT_BASE.md](../OCTATRACK_TWO_SLOT_BASE.md)) and the update on the unit's screen.
- **Elektron's recovery stays the floor.** The owner pointed out that FUNC at power-on already has a good recovery
  flow. Nothing of ours writes below `0x4000`, so it always works.
- **No release pause.** A pause of base releases until the two-slot base ships was agreed and then dropped by the
  owner the same hour: bases keep shipping meanwhile.
- **The site never invites a power-off mid-write** (PR #920): a USB dropout during the save is waited out and the
  save repeated until the unit confirms the new base.
