| APPLY SCENE -- hold [SCENE A] or [SCENE B] and press [YES]: what the
| crossfader blends right now becomes the active Part's base sound.
|
| One detour, at the entry of stock's base-layer YES handler (0x4005e4c8,
| handler(key, edge)). The SCENE key's held layer (keys 0x400babc6 /
| 0x400baf34) has no YES record, so a YES pressed while a scene key is held
| falls through to this handler, which on stock shows ARM ALL exactly as
| YES alone does. With a scene key held (0x460d169c), in audio mode and
| outside the one mode stock diverts YES from (0x460d1aec), the press runs
| as_apply instead and its release is swallowed; every other YES replays
| the two displaced instructions and rejoins stock.
|
| as_apply recomputes stock's scene morph (the frame builder,
| 0x4000ce42..0x4000cefa): per track and scene byte k (0-5 PLAYBACK of the
| assigned machine, 6-11 LFO, 12-17 AMP, 18-23 FX1, 24-29 FX2), side A is
| the lock of the scene at Part+0x10 or, unlocked or muted (0x80000006),
| the Part base; side B likewise (+0x11, 0x80000007). The halfword stock
| hands the DSP is A*256*wA + B*256*wB in Q15, rounded to nearest, with
| wA/wB the negated halves of the track's weight long (0x80003c60 + 4t,
| what the fader event wrote). The new base is that halfword rounded to a
| whole knob step: (hw + 0x80) >> 8. A value that differs from the base
| goes through stock's page-1 writer 0x40054cd8(track, flat, value), the
| MIDI CC store: it refuses disabled slots (AMP XVOL, empty THRU/NEIGHBOR/
| PICKUP slots), clamps to the descriptor, writes the working Part, its CS1
| copy and the live lane, and sets the unsaved bit and edited flags. The
| saved Part, both scenes, the selection, the mutes and the fader are not
| touched, so stock RELOAD PART restores the Part as it was last saved.
        .text
        .global as_yes_hook

        .set    SCENE_HELD, 0x460d169c  | 1 = SCENE A held, 2 = SCENE B, 0 = none
        .set    YES_DIVERT, 0x460d1aec  | stock sends YES to 0x4004903c while set
        .set    MIDI_MODE,  0x80000012
        .set    BANK_BASE,  0x46c82456  | the current bank's RAM
        .set    CUR_PART,   0x100b14cf  | the active Part, 0..3
        .set    MUTE_A,     0x80000006
        .set    MUTE_B,     0x80000007
        .set    WEIGHTS,    0x80003c60  | per track: (-wA << 16) | (-wB & 0xffff), Q15
        .set    P1_WRITER,  0x40054cd8
        .set    NOTIFY,     0x4005a2b8  | (text, ticks): the stock toast
        .set    XF_LAST,    0x400c0c44  | the fader value the STRT/LEN/RATE morph last sent
        .set    XF_MORPH,   0x4003f1b4  | that morph, as a fader move runs it
        .set    YES_REJOIN, 0x4005e4d0  | after the two displaced instructions

| -------- the detour: replaces `move.l 4(%sp),%d1; move.l 8(%sp),%d0` --
as_yes_hook:
        tst.l   8(%sp)                  | edge: 0 = release
        beq.s   .Lrelease
        tst.l   (SCENE_HELD).l
        beq.s   .Lstock
        tst.l   (YES_DIVERT).l
        bne.s   .Lstock
        tst.l   (MIDI_MODE).l
        bne.s   .Lstock
        lea     as_taken(%pc),%a0
        move.b  #1,(%a0)
        bra.w   as_apply                | its rts returns to the key dispatcher
.Lrelease:
        lea     as_taken(%pc),%a0       | swallow only the release of a press we took
        tst.b   (%a0)
        beq.s   .Lstock
        clr.b   (%a0)
        rts
.Lstock:
        move.l  4(%sp),%d1
        move.l  8(%sp),%d0
        jmp     (YES_REJOIN).l

| -------- the apply ------------------------------------------------------
| d7 track, d6 scene byte k, d5 wA, d4 wB, d3 the LFO/AMP/FX block - 6,
| a2 the assigned machine's PLAYBACK block, a3/a4 the A/B lock rows (0 =
| muted), a5 the working Part. 40(%sp) counts the writes.
as_apply:
        lea     -44(%sp),%sp
        movem.l %d2-%d7/%a2-%a5,(%sp)
        clr.l   40(%sp)
        movea.l (BANK_BASE).l,%a5
        moveq   #0,%d0
        move.b  (CUR_PART).l,%d0
        move.l  #0x18b2,%d1
        muls.l  %d1,%d0
        adda.l  %d0,%a5
        adda.l  #0x8ed80,%a5            | W = the active working Part
        moveq   #0,%d7
.Ltrack:
        | the A and B lock rows: W + 0x662 + (scene*8 + t)*32, or 0 when muted
        suba.l  %a3,%a3
        tst.b   (MUTE_A).l
        bne.s   1f
        moveq   #0,%d0
        move.b  0x10(%a5),%d0
        bsr.w   as_row
        movea.l %a0,%a3
1:      suba.l  %a4,%a4
        tst.b   (MUTE_B).l
        bne.s   2f
        moveq   #0,%d0
        move.b  0x11(%a5),%d0
        bsr.w   as_row
        movea.l %a0,%a4
2:      | the weights
        lea     (WEIGHTS).l,%a0
        move.l  (%a0,%d7.l*4),%d0
        move.l  %d0,%d5
        swap    %d5
        ext.l   %d5
        neg.l   %d5                     | wA
        move.w  %d0,%d4
        ext.l   %d4
        neg.l   %d4                     | wB
        | PLAYBACK: W + 0x2a + t*30 + machine*6 (+ k)
        moveq   #0,%d0
        move.b  0x22(%a5,%d7.l),%d0
        move.l  %d0,%d1
        add.l   %d1,%d1
        add.l   %d1,%d0
        add.l   %d0,%d0                 | machine*6
        move.l  %d7,%d1
        lsl.l   #5,%d1
        sub.l   %d7,%d1
        sub.l   %d7,%d1                 | t*30
        add.l   %d1,%d0
        lea     0x2a(%a5,%d0.l),%a2
        | LFO/AMP/FX1/FX2: W + 0x11a + t*24 + (k - 6)
        move.l  %d7,%d3
        lsl.l   #3,%d3
        move.l  %d3,%d1
        add.l   %d1,%d1
        add.l   %d1,%d3                 | t*24
        add.l   %a5,%d3
        add.l   #0x114,%d3
        moveq   #0,%d6
.Lparam:
        moveq   #-1,%d1                 | side A lock, -1 = none
        cmpa.l  #0,%a3
        beq.s   3f
        move.b  (%a3,%d6.l),%d1
        extb.l  %d1
3:      moveq   #-1,%d2                 | side B lock
        cmpa.l  #0,%a4
        beq.s   4f
        move.b  (%a4,%d6.l),%d2
        extb.l  %d2
4:      move.l  %d1,%d0
        and.l   %d2,%d0
        bmi.s   .Lnext                  | both unlocked: stock passes the base through
        moveq   #6,%d0
        cmp.l   %d0,%d6
        bge.s   5f
        lea     (%a2,%d6.l),%a0
        bra.s   6f
5:      movea.l %d3,%a0
        adda.l  %d6,%a0
6:      moveq   #0,%d0
        move.b  (%a0),%d0               | the Part base
        tst.l   %d1
        bpl.s   7f
        move.l  %d0,%d1
7:      tst.l   %d2
        bpl.s   8f
        move.l  %d0,%d2
8:      muls.l  %d5,%d1
        muls.l  %d4,%d2
        add.l   %d2,%d1
        moveq   #64,%d2
        add.l   %d2,%d1
        asr.l   #7,%d1                  | the DSP halfword, rounded as the MAC rounds
        add.l   #0x80,%d1
        asr.l   #8,%d1                  | to a whole knob step
        cmp.l   %d0,%d1
        beq.s   .Lnext
        move.l  %d1,-(%sp)              | value
        move.l  %d6,-(%sp)              | flat = the scene byte numbering
        move.l  %d7,-(%sp)              | track
        jsr     (P1_WRITER).l
        lea     12(%sp),%sp
        addq.l  #1,40(%sp)
.Lnext:
        addq.l  #1,%d6
        moveq   #30,%d0
        cmp.l   %d0,%d6
        blt.w   .Lparam
        addq.l  #1,%d7
        moveq   #8,%d0
        cmp.l   %d0,%d7
        blt.w   .Ltrack
        tst.l   40(%sp)
        beq.s   9f
        | STRT/LEN/RATE reach the voices as a message on a fader move only:
        | send it again from the new base, as a fader move would.
        moveq   #-1,%d0
        move.l  %d0,(XF_LAST).l
        jsr     (XF_MORPH).l
9:      pea     (0x30).w
        pea     as_text(%pc)
        jsr     (NOTIFY).l
        addq.l  #8,%sp
        movem.l (%sp),%d2-%d7/%a2-%a5
        lea     44(%sp),%sp
        rts

| a0 = W + 0x662 + (d0*8 + d7)*32: scene d0's lock row for track d7
as_row:
        lsl.l   #3,%d0
        add.l   %d7,%d0
        lsl.l   #5,%d0
        movea.l %a5,%a0
        adda.l  %d0,%a0
        adda.l  #0x662,%a0
        rts

as_text:
        .asciz  "SCENE APPLIED"
| In .text: a DRAM unit's text is RAM, and .data would cost an 8 KB boundary.
as_taken:
        .byte   0
        .align  2
