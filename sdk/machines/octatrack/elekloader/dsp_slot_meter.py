# SPDX-License-Identifier: GPL-3.0-or-later
"""The per-slot DSP cycle meter (build_core.py --slot-meter): what one FX slot of each core really costs.

Without the flag nothing here runs and the receiver, transfer.c and the C sources build as before.

What it measures. On each core one slot at a time (the ColdFire picks it, status.c), timed by the core's own
timer 0, free-running at the core clock / 2 (2 cycles a count; stock's DSP code never touches the timers, the
setting is Octabam's probe 55, TCSR0 = TRM | TE, no interrupt). METER (opcode 12) points the slot's effect id at a
wrapper in the receiver: it stamps timer 0, calls the effect's own proc, stamps again and adds the difference to
the frame's total when the call is the watched slot's (its r7, the instance block the dispatcher passes). Every
other id dispatches as before, so slots that are not watched cost nothing. The frame hook folds each frame's total
into the window's peak and 48-bit sum, and the load meter's 1,024-frame window publishes, next to its own words,
the mean and the peak counts a frame, each tagged with the watched slot's key (r7 >> 8; 0 for a window that began
before the slot was armed). The reading includes the wrapper's own jsr, rts and a register load inside the stamps
(about 9 cycles a call).

Its cost (from dsp_asm's words; 56300 timing taken as a cycle a word plus 3 for jsr/rts and 4 for a branch, not
measured on a unit): about 35 cycles per call of the watched slot (about 30 on another instance of the same effect id on
that core), about 30 a frame while a slot is watched and 7 while none is, about 40 once per window, and nothing on
any other slot. It takes 210 words of each core's code arena. The ColdFire's frame path is untouched: arming and the two 24-bit reads are status.c tick work (PEEK,
one bit a packet), and only while a host asked for slot readings in the last 10 s (MWLD v2, ep0.c).

Not proven on a unit yet: the timer setting ran on hardware in Octabam's probe 55, but the memory form of MOVEP
(`movep x:<<$ffff8c,x:>abs`) has no site in stock code, and the wrapper adds one level to the system stack under
the effect's proc."""

METER_OPCODE = 12
X_WORDS = 10  # THEN, KEY, FRAME, MAX, SUMHI, SUMLO, WKEY, PROC, ID, R7
PUB_WORDS = 2  # P words after the load meter's five (status.c reads them as words 5 and 6)

IDLEPUB = ('idlepub:                            ; then the published window: serial, least, most, sum, missed\n'
           '        nop\n        nop\n        nop\n        nop\n        nop\n')


def words(table_home, ids):
    """The X words the meter keeps on each core: just past the dispatch tables (init[ids], proc[ids])."""
    base = table_home + 2 * ids
    names = ('THEN', 'KEY', 'FRAME', 'MAX', 'SUMHI', 'SUMLO', 'WKEY', 'PROC', 'ID', 'R7')
    return {name: base + i for i, name in enumerate(names)}


def receiver(text, null_proc, ids, table_home, table_end):
    """The receiver (dsp_receiver.asm, after dsp_loader.receiver_source's substitutions) with the meter."""
    x = words(table_home, ids)
    if x['R7'] >= table_end:
        raise ValueError('The slot meter\'s X words do not fit past the dispatch tables.')
    a = {k: '$%x' % v for k, v in x.items()}
    a.update(PROCTAB='$%x' % (table_home + ids), IDMAX=str(ids - 1), NULLPROC='$%x' % null_proc)
    edits = (
        # METER (12): after SUM in the opcode chain.
        ('        cmp     #>9,a\n        beq     summed\n',
         '        cmp     #>9,a\n        beq     summed\n        cmp     #>12,a\n        beq     zqarm\n'),
        # BIND, UNBIND and BYPASS of the watched id stop the meter first, so none of them keeps the wrapper.
        ('binding:\n', '''binding:
        move    x:>{KEY},a              ; slot meter: a change to the watched id stops it first
        tst     a
        beq     zqbound
        move    x:(r0+4),a
        and     #>$ffff,a
        move    x:>{ID},x0
        cmp     x0,a
        bne     zqbound
        bsr     zqoff
zqbound:
'''),
        # Each frame (before any effect runs): the frame just run into the window's peak and sum.
        ('counted:\n', '''counted:
        move    x:>{KEY},a              ; slot meter: fold the watched slot's last frame into the window
        tst     a
        beq     zqnofold
        move    x:>{FRAME},x0
        move    x:>{MAX},a
        cmp     x0,a
        tlt     x0,a
        move    a1,x:>{MAX}
        move    #>0,x1
        move    x:>{SUMHI},a
        move    x:>{SUMLO},a0
        add     x,a
        move    a1,x:>{SUMHI}
        move    a0,x:>{SUMLO}
        move    x1,x:>{FRAME}
zqnofold:
'''),
        # Once a window, beside the load meter's publication: key << 16 | mean, key << 16 | peak (counts a frame).
        ('tallied:\n', '''        move    x:>{SUMHI},a            ; slot meter: the window's mean (sum / 1024) and peak counts a frame,
        move    x:>{SUMLO},a0           ; each with the key the whole window watched in bits 16-23
        asr     #10,a,a
        move    a0,x0
        move    x0,a
        move    #>$ffff,x1
        cmp     x1,a
        tgt     x1,a
        move    a1,x0
        move    x:>{WKEY},a
        asl     #8,a,a
        and     #>$ff0000,a
        or      x0,a
        move    #>zqpub,r1
        move    a1,p:(r1)+
        move    x:>{MAX},a
        cmp     x1,a
        tgt     x1,a
        move    a1,x0
        move    x:>{WKEY},a
        asl     #8,a,a
        and     #>$ff0000,a
        or      x0,a
        move    a1,p:(r1)
        move    x:>{KEY},x0             ; the next window is the watched slot's from its start
        move    x0,x:>{WKEY}
        move    #>0,x0
        move    x0,x:>{MAX}
        move    x0,x:>{SUMHI}
        move    x0,x:>{SUMLO}
tallied:
'''),
        # Before `accepted`: dsp_asm cannot branch back to a label, and the handler ends at accepted or badsaved.
        ('accepted:\n', '''; METER (12, build_core.py --slot-meter, dsp_slot_meter.py): watch the slot whose instance block is (r0+5) (0
; stops) on its effect id (r0+4). Refused when that id runs nothing (the null stub).
zqarm:
        bsr     zqoff
        move    x:(r0+5),a
        tst     a
        beq     accepted
        move    a1,x1
        move    x:(r0+4),a
        cmp     #>{IDMAX},a
        bgt     badsaved
        move    a1,x:>{ID}
        add     #>{PROCTAB},a
        move    a1,r1
        move    x1,x:>{KEY}
        move    x:(r1),x0
        move    x0,a
        cmp     #>{NULLPROC},a
        beq     zqnone
        move    x0,x:>{PROC}
        move    x:>$ffff8f,a            ; TCSR0: timer 0 counts already (TE)?
        and     #>1,a
        bne     zqtime
        move    #>0,x0
        move    x0,x:>$ffff8e           ; TLR0
        move    #>$ffffff,x0
        move    x0,x:>$ffff8d           ; TCPR0
        move    #>$000201,x0
        move    x0,x:>$ffff8f           ; TCSR0: TRM | TE, no interrupt: free-running at CLK/2
zqtime:
        move    #>0,x0
        move    x0,x:>{FRAME}
        move    x0,x:>{MAX}
        move    x0,x:>{SUMHI}
        move    x0,x:>{SUMLO}
        move    x0,x:>{WKEY}            ; the window under way began before this slot: it publishes no key
        move    #>zqwrap,x0
        move    x0,x:(r1)               ; the dispatch calls the wrapper from this frame on
        bra     accepted
zqnone:
        move    #>0,x0
        move    x0,x:>{KEY}
        bra     badsaved
accepted:
'''),
        ('finish:\n        rts\n', '''finish:
        rts
; Stop watching: the id's own proc back, unless something rebound it since.
zqoff:
        move    x:>{KEY},a
        tst     a
        beq     zqkept
        move    #>0,x0
        move    x0,x:>{KEY}
        move    x0,x:>{WKEY}
        move    x:>{ID},a
        add     #>{PROCTAB},a
        move    a1,r1
        move    x:>{PROC},x1
        move    x:(r1),a
        cmp     #>zqwrap,a
        bne     zqkept
        move    x1,x:(r1)
zqkept:
        rts
; The watched id's proc, as the dispatch calls it (jsr (r2), the id in r1, r7 the instance block). Before its own
; proc only X memory changes, so that proc starts as stock's dispatch starts it (r2 its own address); after it a,
; x0, x1 and the flags change, which no caller of a proc can rely on (every effect writes them).
zqwrap:
        movep   x:<<$ffff8c,x:>{THEN}   ; TCR0
        move    r7,x:>{R7}
        move    x:>{PROC},r2
        jsr     (r2)
        movep   x:<<$ffff8c,a
        move    x:>{THEN},x0
        sub     x0,a
        move    a1,x0                   ; the call's counts (CLK/2), mod 2^24
        move    x:>{R7},x1
        move    x:>{KEY},a
        cmp     x1,a
        bne     zqskip
        move    x:>{FRAME},a
        add     x0,a
        move    a1,x:>{FRAME}
zqskip:
        rts
'''),
        (IDLEPUB, IDLEPUB + '''zqpub:                                  ; slot meter: key << 16 | mean, key << 16 | peak (counts a frame)
        nop
        nop
'''),
    )
    for old, new in edits:
        if text.count(old) != 1:
            raise ValueError('The DSP receiver changed (%s); review the slot meter.' % old.strip().splitlines()[0])
        text = text.replace(old, new.format(**a) if '{' in new else new)
    return text


def install(loader):
    """Wrap a dsp_loader module's receiver_source (the plain one, or the resident build's copy) with the meter."""
    original = loader.receiver_source

    def metered(text, null, table_words, *rest, **named):
        ids = named.get('ids', rest[3] if len(rest) > 3 else 32)
        return receiver(original(text, null, table_words, *rest, **named), null[1], ids, loader.TABLE_HOME, loader.TABLE_END)
    loader.receiver_source = metered


TRANSFER = (
    # METER is a command like PEEK: id in word 4, the slot's r7 in word 5; its answer is a flag, never a reject.
    ('op!=DL_PEEK', 'op!=DL_PEEK && op!=%du' % METER_OPCODE),
    ('opcode==DL_BASE || opcode==DL_PEEK || opcode==DL_SUM', 'opcode==DL_BASE || opcode==DL_PEEK || opcode==DL_SUM || opcode==%du' % METER_OPCODE),
    ('jobs[c].opcode==DL_PEEK || jobs[c].opcode==DL_SUM)', 'jobs[c].opcode==DL_PEEK || jobs[c].opcode==DL_SUM || jobs[c].opcode==%du)' % METER_OPCODE),
)


def transfer(text):
    for old, new in TRANSFER:
        if text.count(old) != 1:
            raise ValueError('transfer.c changed (%s); review the slot meter.' % old)
        text = text.replace(old, new)
    return text
