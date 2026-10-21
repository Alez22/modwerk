; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Nathaniel Pawelczyk
; ---------------------------------------------------------------------------
; RINGMOD SC -- an insert whose gain is driven by another track's audio (the
; KEY), read from the Modwerk base's key bus.
;
;   DUCK   out = in * (1 - DPTH * e),  e = follow(peak(|key|))  (ring mod sidechain)
;   RING   out = in * (1 - DPTH) + in * DPTH * key            (ring modulator)
;
; with key = sat(lowpass(mono(KEY track)) * 4): four times, so a kick at AMP
; VOL 64 reaches full, and a louder one holds the duck at full a little longer.
; In DUCK, peak() is the largest |key| over the last one to two windows of
; HOLD's length (32 + 16v samples: 0.7 ms at 0, 13 ms at the default 34,
; 47 ms at 127). Longer than half the key's cycle, it does not drop at the
; key's zero crossings; it steps down as the key decays. e follows it:
; t = max(peak, e * decay), and where t is above e only q(ATK) of the rise
; is taken. DPTH 0 or KEY OFF returns the input bit for bit.
;
; THE KEY BUS is the base's (KEYBUS, sdk/machines/octatrack/dsp-sites.json;
; docs/OCTATRACK_PACKAGE_DSP_HOOKS.md), which the package requires: while a
; reader is installed the base's tap copies every track's 32 words of audio,
; as they enter FX1, on every block, to
;   this core's bus   Y:$800 + track*$40
;   the shared window  base + (local*4 + gen)*$20
; with four generations a track, base Y:$33e00 on the tracks 5-8 core and
; Y:$3be00 on the tracks 1-4 core; gen is each core's own counter at base-1,
; stepped once a block. So a reader gets this block's audio from a track
; dispatched before it on its own core, the last block's from one dispatched
; after, and from the other core the block two generations behind its own
; counter, which the writer is not touching. A reader writes nothing in the
; bus or the window. (The tap and its layout are Sidechain Compressor's,
; Zac-Kyoti, made a base feature; this module only reads.)
;
; Which core this is comes from X:$420, the track being dispatched, so one
; source serves both payloads with no per-payload values. Nothing here
; writes beyond the instance's own r7 block. Until the bus is live on this core
; (its seed mark, below) the depth stays at 0: an image without the base's key
; bus, a card build, never reads a key from memory nothing writes.
;
; ABI (docs/remixer/HARNESS.md): r0 = audio block (interleaved stereo, in
; place), n7 = frames, r6 = parameters, r7 = state. A trig splits a block into
; two calls, the second with r0 = split*2, so the key is read from the same
; offset: r0 & $1f.
;
; Parameters. Page 1 arrives as value<<16 with an LFO's fraction in bits
; 8-15: KEY masks it off, the continuous knobs keep it.
;   x:(r6+$0)  KEY   0 OFF, 1..8 = T1..T8; above 8 = OFF
;   x:(r6+$1)  DPTH  v/128 * 129/128, so 127 is full
;   x:(r6+$2)  KLPF  key low-pass coefficient p(v): 14 Hz at 0, an octave
;                    every 14 steps, open at 127
;   x:(r6+$3)  ATK   DUCK: the follower's attack coefficient q(v), 0 = instant
;   x:(r6+$4)  HOLD  DUCK: the peak window, 32 + 16v samples
;   x:(r6+$5)  REL   DUCK: per-sample decay 1 - q(v); 0 = none
;   x:(r6+$c)  MODE  bits 16-23: 0 DUCK, else RING
; q(v) is 1 at 0 and falls from 1/32 at 1 to about 2^-16 at 127 (rq83).
;
; MODE and KEY are followed through a fade: when either changes, the depth is
; ramped to 0 first, the change is adopted with the depth at 0 and the key's
; state cleared, and the depth ramps back from the next call. $0c holds the
; pair in use.
;
; r7 block:
;   $00  key low-pass state           $06  low-pass coefficient
;   $01  follower e                   $07  follower decay
;   $02  depth, ramped per sample     $08  KEY track 0..7
;   $03  its step                     $09  follower slowness, 1 - q(ATK)
;   $0c  MODE<<16 | KEY<<8 in use     $0d  (unused)
;   $0e  this window's peak           $0f  the last window's peak
;   $10  samples left in this window  $12  the window's length
;
; Every multiply is `y1,y0`, `x0,x0`, `x1,y0`, `x1,x0` or `x0,y1` (signed
; encodings); no mpysu. Short immediates (`add #<n`), parallel moves and
; register-to-register parallel moves are all forms stock runs; `rep` and
; plain (Rn+Nn) Y moves are not, so they are not used. Labels are `rq` + two digits, none a prefix of another.
; ---------------------------------------------------------------------------
init:
        move    r7,r5                   ; r1 is the dispatcher's across init
        move    #>$ffffff,m5
        clr     a
        do      #<$14,>rq00
        move    a,x:(r5)+
rq00:
        rts

proc:
        move    #>$ffffff,m0
        move    #>$ffffff,m1
; ---- MODE and KEY: adopt a change only while the depth is 0 ----------------
        move    x:(r6+$c),b
        and     #>$7f0000,b
        move    b1,x0
        move    x:(r6+$0),a             ; a knob word: positive, a0 and a2 clear
        and     #>$7f0000,a
        asr     #8,a,a
        add     x0,a
        move    a,x0                    ; MODE<<16 | KEY<<8 as the knobs have it
        move    x:(r7+$c),b
        cmp     x0,b
        beq     rq05
        move    x:(r7+$2),a
        tst     a
        bne     rq03                    ; still audible: fade out first
        move    x0,x:(r7+$c)            ; adopt it with the depth at 0
        clr     a
        move    a,x:(r7+$0)             ; and forget what was heard so far
        move    a,x:(r7+$1)
        move    a,x:(r7+$e)
        move    a,x:(r7+$f)
        move    a,x:(r7+$11)
        bra     rq04
rq05:
; ---- no key bus on this core (not placed and seeded yet, or an image without
; one, such as a card build): the depth goes to 0, so the audio passes bit for
; bit. The bus is live once the base's tap has seeded this core: its mark at
; base-2 holds exactly $10000 and its counter at base-1 is 0..3.
        move    x:>$420,b
        and     #<4,b
        move    b1,a
        asl     #$d,a,a
        move    a1,x0                   ; $8000 on the tracks 5-8 core, else 0
        move    #>$3bdfe,a
        sub     x0,a
        move    a1,r1                   ; this core's seed mark; its counter follows
        move    y:(r1)+,b
        cmp     #>$10000,b
        bne     rq03
        move    y:(r1),b
        and     #>$fffffc,b             ; Z from b1 alone
        bne     rq03
        move    x:(r6+$1),a
        asr     #7,a,b
        add     b,a                     ; v/128 * 129/128: 127 is full within 2^-14
        bra     rq04
rq03:
        clr     a
; ---- the depth's ramp: the step that reaches the target in 16 samples ------
; Within 16 LSB the value lands on the target and the step is 0.
rq04:
        move    a,x1
        move    x:(r7+$2),x0
        sub     x0,a
        asr     #4,a,a
        move    a,x0
        move    x0,a                    ; drop a0 before the test
        tst     a
        bne     rq82
        move    x1,x:(r7+$2)
rq82:
        move    a,x:(r7+$3)
; ---- KEY: OFF or out of range leaves the audio untouched -------------------
        move    x:(r7+$c),a             ; positive: a0 and a2 clear
        and     #>$007f00,a
        asr     #8,a,a                  ; sets Z: nothing reaches a0
        beq     rq90
        sub     #<9,a
        bge     rq90
        add     #<8,a                   ; a = track 0..7
        move    a,x:(r7+$8)
        move    r0,b
        and     #<$1f,b
        move    b1,x1                   ; x1 = offset of this call in the block
        move    x:>$420,b               ; the track being dispatched, 0..7
        and     #<4,b
        move    b1,x0                   ; this core's half: 4 (tracks 5-8) or 0
        move    x:(r7+$8),b
        and     #<4,b
        cmp     x0,b
        bne     rq10
; same core: this core's bus (a = the track, clean)
        asl     #6,a,a
        add     x1,a
        add     #>$800,a
        bra     rq11
rq10:
; other core: its publish region in the shared window, two generations behind
; this core's own counter. The two regions are $8000 apart: tracks 5-8 publish
; at $33e00 and count at $33dff, tracks 1-4 at $3be00 and $3bdff.
        move    x0,a
        asl     #$d,a,a
        move    a1,y0                   ; $8000 on the 5-8 core, else 0
        move    x:(r7+$8),a
        and     #<3,a
        asl     #2,a,a
        move    a1,x0                   ; the key's index on its core, times 4
        move    #>$3bdff,b
        sub     y0,b
        move    b1,r1
        move    y:(r1),b                ; this core's generation counter
        add     #<2,b
        and     #<3,b
        move    b1,a
        add     x0,a
        asl     #5,a,a
        add     x1,a
        add     #>$33e00,a
        add     y0,a
rq11:
        move    a1,r1                   ; the key's 32 words for this call

; ---- KLPF: p(v) = (1 - f/16) * 2^-i for u = 72 - 9v/16 ----------------------
        move    x:(r6+$2),x1
        move    #>$480000,y0            ; 9/16, and 72
        move    y0,a
        mac     -x1,y0,a
        bsr     rq88
        move    a,x:(r7+$6)

        move    x:(r7+$c),b
        and     #>$7f0000,b             ; MODE: Z from b1 alone
        bne     rq50

; ---- DUCK ------------------------------------------------------------------
        move    x:(r6+$4),a
        asr     #12,a,a
        add     #<32,a
        move    a1,x:(r7+$12)           ; HOLD: 32 + 16v samples a window
        move    x:(r6+$5),x1
        bsr     rq83
        move    a,x:(r7+$7)             ; decay = 1 - q(REL)
        move    x:(r6+$3),x1
        bsr     rq83
        move    a,x:(r7+$9)             ; slowness = 1 - q(ATK), 0 at ATK 0
        do      n7,>rq40
        bsr     rq86
        abs     a
        move    a,x0                    ; |key|, limited to 1
        move    x:(r7+$e),b
        cmp     x0,b
        tlt     x0,b                    ; b = this window's peak, kept to the end
        move    b,y1
        move    x:(r7+$f),a
        cmp     b,a
        tlt     b,a
        move    a,x0                    ; the peak over this window and the last
        move    x:(r7+$10),a
        sub     #<1,a                   ; LE: the window ends here
        move    x:(r7+$12),x1           ; the window's length
        tle     x1,a
        move    a,x:(r7+$10)
        move    x:(r7+$f),a
        tle     y1,a                    ; at its end this window becomes the last
        move    a,x:(r7+$f)
        move    #0,x1                   ; (x1 stays 0 for the tmi below)
        tle     x1,b                    ; and the next starts from nothing
        move    b,x:(r7+$e)
        move    x:(r7+$1),y1
        move    x:(r7+$7),y0
        mpy     y1,y0,b
        cmp     x0,b
        tlt     x0,b                    ; b = max(peak, e * decay)
        move    b,a
        sub     y1,a
        tmi     x1,a                    ; how far that is above e, or 0
        move    a,y1
        move    x:(r7+$9),y0
        mac     -y1,y0,b                ; hold back the slowness's share of the rise
        move    b,x:(r7+$1)
        move    b,y1
        move    x:(r7+$2),a
        move    x:(r7+$3),x0
        add     x0,a
        move    a,x:(r7+$2)
        move    a,y0
        mpy     y1,y0,a       x:(r0)+,x1        ; reduction = e * depth; x1 = left
        tfr     x1,a          a,y0              ; y0 = the reduction
        mac     -x1,y0,a      x:(r0)-,y1        ; left - left * reduction; y1 = right
        tfr     y1,b          a,x:(r0)+
        mac     -y1,y0,b
        move    b,x:(r0)+
rq40:
        rts

; ---- RING ------------------------------------------------------------------
; The key passes three stages before it multiplies the audio, each a plain
; copy at 0, so RING with S&H, SLEW and BIAS at 0 is the plain ring modulator:
;   S&H   a new key every 16v samples, held between (stepped modulation)
;   SLEW  above 0 the key's level, |key| smoothed by 1 - q(v), drives the gain
;         instead of the key itself (a tremolo that follows the key)
;   BIAS  key + h * (1 - key), h = v/256: the dry signal stays, with sidebands (AM)
; Their state is DUCK's, cleared when MODE changes: $01 the level, $0e the held
; key; $11 counts down to the next sample, $12 holds the period, $09 SLEW's
; coefficient and $0d BIAS's h.
rq50:
        move    x:(r6+$3),x1
        bsr     rq83
        move    a,x:(r7+$9)             ; SLEW: 1 - q(ATK), 0 at 0
        move    x:(r6+$4),a
        asr     #12,a,a
        move    a1,x:(r7+$12)           ; S&H: 16v samples a key, 0 = every sample
        move    x:(r6+$5),a
        asr     #1,a,a                  ; BIAS: h = v/256, ramped as the depth is
        move    a,x1
        move    x:(r7+$d),x0
        sub     x0,a
        asr     #4,a,a
        move    a,x0
        move    x0,a                    ; drop a0 before the test
        tst     a
        bne     rq56
        move    x1,x:(r7+$d)
rq56:
        move    a,x:(r7+$13)
        do      n7,>rq60
        bsr     rq86
        move    a,y1                    ; key, limited to +/-1
        move    x:(r7+$12),b
        tst     b
        beq     rq52                    ; S&H 0: every sample
        move    x:(r7+$11),a
        sub     #<1,a                   ; LE: take a new key here
        tle     b,a
        move    a,x:(r7+$11)
        move    x:(r7+$e),a
        tle     y1,a
        move    a,x:(r7+$e)
        move    a,y1                    ; the held key
rq52:
        move    x:(r7+$9),b
        tst     b
        beq     rq54                    ; SLEW 0: the key itself
        move    b,y0
        move    y1,a
        abs     a
        move    a,y1                    ; |key|, limited to 1
        move    x:(r7+$1),x1            ; the level so far
        mac     -y1,y0,a
        mac     x1,y0,a                 ; |key| + slow * (level - |key|)
        move    a,x:(r7+$1)
        move    a,y1
rq54:
        move    x:(r7+$d),y0
        move    y1,a
        mac     -y1,y0,a
        add     y0,a                    ; key + h * (1 - key): h = 0 adds nothing
        move    a,y1
        move    x:(r7+$13),x0
        move    y0,a
        add     x0,a
        move    a,x:(r7+$d)             ; h's ramp
        move    x:(r7+$2),y0
        mpy     y1,y0,b       x:(r0)+,x1        ; depth * key; x1 = left
        tfr     x1,a          b,x0
        mac     -x1,y0,a      x:(r0)-,y1        ; y1 = right
        mac     x1,x0,a
        tfr     y1,b          a,x:(r0)+
        mac     -y1,y0,b
        mac     x0,y1,b
        move    b,x:(r0)+
        move    x:(r7+$2),a
        move    x:(r7+$3),x0
        add     x0,a
        move    a,x:(r7+$2)
rq60:
rq90:
        rts

; ---- 1 - q for the knob word in x1 ------------------------------------------
; q at 0 is 1 (at once). Above it the knob is laid over the useful end of the law:
; u = 40 + 11v/16, so 1 is about 0.7 ms and 127 about 1.3 s, a doubling every
; 11.6 steps.
rq83:
        move    x1,b
        and     #>$7f0000,b             ; Z from b1 alone
        bne     rq89
        clr     a
        rts
rq89:
        move    #>$580000,y0            ; 11/16
        mpy     x1,y0,a
        add     #>$280000,a             ; + 40
        bsr     rq88
        move    a,x0
        move    #>$7fffff,a
        sub     x0,a
        rts

; ---- (1 - f/16) * 2^-i for u in a: i = u>>3, f = u&7 (u in bits 16-22) ----
rq88:
        move    a,x1
        move    x1,b                    ; u >= 0: b2 stays clear
        and     #>$070000,b
        asl     #3,b,b
        move    b1,x0                   ; f/16
        move    #>$7fffff,a
        sub     x0,a
        asl     #1,a,a                  ; doubled: the loop below runs i+1 times
        move    x1,b
        asr     #$13,b,b
        add     #<1,b
        move    b1,y0                   ; i+1, 1..16
        do      y0,>rq84
        asr     #1,a,a
rq84:
        rts

; ---- the key for one frame: mono, low-passed, times four ------------------
; Out: a = key * 4, not yet limited. Straight-line.
rq86:
        move    y:(r1)+,a
        move    y:(r1)+,x0
        add     x0,a
        asr     #1,a,a
        move    a,y1                    ; mono key
        move    x:(r7+$6),y0
        move    x:(r7+$0),a
        mac     y1,y0,a
        move    x:(r7+$0),y1
        mac     -y1,y0,a
        move    a,x:(r7+$0)             ; lp += c*(key - lp)
        asl     #2,a,a
        rts
