# Octatrack: two-slot base (power-cut-safe updates)

**Status: design, being built (owner, 25 October 2026).** Nothing here runs on a unit yet.

The owner's rule: updating the base must never brick a unit, whatever USB or the power does, and the unit shows
the update on its own screen. Today's base (`flash.c`) keeps one copy of the OS in flash and rewrites it in place.
A power cut during that write (about 10 s) leaves no bootable OS. The unit can still be recovered from the startup
menu, but only with a DIN MIDI interface. With two slots, an update writes only the copy that is not running, so
a power cut or USB dropout at any moment leaves the running copy whole.

## What the unit gives us (MKII, OS 1.40C, read from the user's own file)

- **Elektron's bootloader**, flash `0x0000`-`0x3fff`, is never written. At reset it sets the caches, unpacks the
  section at flash `0x4012` into RAM at `0x40000400` with its own unpacker (`0x207e(src, dst)`, the kit's
  codec), turns the caches off again and calls `0x40000400` with one boot word on the stack. It checks nothing.
- **FUNC at power-on** opens the startup menu in that bootloader: TESTMODE, EMPTY RESET, MIDI UPGRADE, SEND
  UPGRADE. MIDI UPGRADE takes an OS `.syx` over DIN only, checks the received file (checksum, its version
  against the MK1 and downgrade rules), never what flash holds, erases `0x4000`-`0xfffff` and writes it. So
  whatever we write above `0x4000`, recovery stays possible; it removes the two-slot layout and leaves stock.
- **Flash is at least 8 MB.** The OS window is `0x4000`-`0x1fffff` (8 KB sectors to `0x10000`, then 64 KB). A
  second stock routine writes "bulk data" at `0x200000`-`0x7fffff`; nothing of ours goes there.
- **The OS reads its version from flash** at `0x4004`-`0x4012`, the container header (the SYSTEM page shows it).
- **Stock's upgrade screen**, `0x4007f9cc(step, current, total)`: PREPARING FLASH (0), WRITING OS DATA (1),
  VERIFYING OS DATA (3) with a progress bar, drawn and sent to the LCD at once. Stock calls it after the same
  quiesce `flash.c` uses.

## Layout

| Flash | Holds |
| --- | --- |
| `0x000000`-`0x003fff` | Elektron's bootloader and startup menu. Never written. |
| `0x004000`-`0x005fff` | The stub's container: stock 1.40C's header (the version the OS shows), then the stub. Written once per unit. |
| `0x006000`-`0x00ffff` | Unused. |
| `0x010000`-`0x0fffff` | Slot A, 960 KB. |
| `0x100000`-`0x1effff` | Slot B, 960 KB. |
| `0x1f0000`-`0x1fffff` | Unused. |
| `0x200000`-`0x7fffff` | Stock's bulk data. Never written. |

A slot is one 256-byte record page, then a plain base container (the kit's `.bin` deciphered, as `flash.c` takes
it today). The record holds a magic, the slot's generation, the container's length and a check over those, all
programmed last; then two words left erased at write time: *tries* (the stub clears one bit for each start of a
slot not yet confirmed) and *confirmed* (the base clears it once it has run healthy).

## The stub

A few hundred bytes of ColdFire code, our own, never written over USB once in place. At each start it:

1. copies itself to internal SRAM and runs from there (unpacking a slot overwrites `0x40000400`);
2. reads both records: a slot counts when its record is whole and the container's own section sum matches;
3. picks the newest counting slot. If it is not confirmed, it clears one *tries* bit first; once two tries are
   used without a confirmation, it picks the other counting slot instead (the previous base);
4. leaves a note in SRAM (which slot, whether it fell back) for the base to read;
5. unpacks that slot with the bootloader's own unpacker and enters it exactly as the bootloader would (same
   cache settings, same stack, same boot word).

With no counting slot it can only stop; by construction one always counts (below). Stock's card update and MIDI
recovery write a plain container at `0x4000`, which replaces the stub: the unit is back to one slot, as stock.

## The base

- **Write** (`flash.c`): after the RAM-boot trial, the running new base writes its own container into the slot the
  stub did *not* start, behind stock's quiesce and with stock's upgrade screen: erase, program, verify the body,
  then the record. A power cut or a lost USB reply anywhere before the record leaves that slot not counting, and
  the stub starts the other one.
- **Confirm**: a base started from an unconfirmed slot confirms it after it has run healthy for a while (its
  frame interrupt running, no crash record), with or without a computer connected.
- **Convert** a one-slot unit: write slot B (above any old container, so the running OS in flash stays whole),
  verify it, then write the stub's sector. That sector (8 KB, under a second) is the only moment a power cut can
  still cost a startup-menu recovery, once per unit. A unit installed from the card later converts on its first
  USB update.
- **Report**: status says the layout, the running slot, whether it is confirmed and whether the stub fell back,
  so the site can say "Update undone: the new base didn't start, your previous base runs".

## Showing it on the Octatrack

- Receiving the new base and trying it: a box on the unit ("BASE UPDATE", step and progress).
- Writing: stock's own upgrade screen (PREPARING FLASH, WRITING OS DATA, VERIFYING OS DATA, with the bar). Owners
  know it from Elektron's updates.
- After the restart: "BASE UPDATED", or "UPDATE UNDONE" when the stub fell back.

## Tests before any unit

- Host tests of the record, the stub's choice and the writer against a flash model that clears bits only, with a
  power cut injected after every erase and program step: the stub must then start a whole base, every time.
- The stub's ColdFire code run in an emulator with the bootloader's unpacker from the user's own 1.40C (private,
  never in Git), from the bootloader's hand-over to the jump into the unpacked image.

## Hardware run (the owner's MKII, a DIN MIDI interface at hand)

1. Read-only: confirm `0x100000`-`0x1fffff` is blank or unused, and that the SRAM note area survives to `.boot`.
2. Convert, update A to B and back, power off and on after each.
3. Pull the power during the slot write, several times at different points; pull the USB cable during the write.
4. Install a base that fails to start: after two power cycles the stub must start the previous one.
