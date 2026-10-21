#NO_APP
	.file	"vector.c"
	.text
	.align	2
	.type	mg_dirty, @function
mg_dirty:
	move.l %d2,-(%sp)
	move.b 269161679,%d0
	mov3q.l #3,%d2
	move.l 1187521622,%a1
	add.l #610376,%a1
	move.b (%a1),%d1
	and.l %d0,%d2
	mov3q.l #1,%d0
	lsl.l %d2,%d0
	or.l %d0,%d1
	move.b %d1,(%a1)
	move.b 269161566,%d1
	or.l %d1,%d0
	move.b %d0,269161566
	move.l 1187521622,%a0
	add.l #635698,%a0
	move.l (%sp)+,%d2
	mov3q.l #1,(%a0)
	mov3q.l #1,269452696
	jmp 1073905152
	.size	mg_dirty, .-mg_dirty
	.align	2
	.type	mg_forward, @function
mg_forward:
	move.l %d2,-(%sp)
	moveq #51,%d1
	move.l 8(%sp),%d0
	move.l 12(%sp),%a0
	cmp.l %d0,%d1
	jeq .L7
	moveq #32,%d2
	cmp.l %d0,%d2
	jeq .L8
	moveq #49,%d1
	cmp.l %d0,%d1
	jeq .L9
	moveq #50,%d2
	mov3q.l #3,%a1
	cmp.l %d0,%d2
	jeq .L4
.L3:
	move.l (%sp)+,%d2
	rts
.L7:
	sub.l %a1,%a1
.L4:
	mov3q.l #1,%d1
	cmp.l %a0,%d1
	jeq .L10
.L14:
	tst.l %a0
	jeq .L6
	mov3q.l #2,%d1
.L6:
	lea (%a1,%a1.l*2),%a1
	moveq #-3,%d2
	add.l %a1,%d1
	lea mg_saved,%a1
	move.l (%a1,%d1.l*4),%a1
	move.l %a1,%d1
	subq.l #1,%d1
	cmp.l %d1,%d2
	jcs .L3
	move.l %a0,12(%sp)
	move.l %d0,8(%sp)
	move.l (%sp)+,%d2
	jmp (%a1)
.L10:
	clr.l %d1
	jra .L6
.L8:
	mov3q.l #1,%a1
	mov3q.l #1,%d1
	cmp.l %a0,%d1
	jne .L14
	jra .L10
.L9:
	mov3q.l #2,%a1
	mov3q.l #1,%d1
	cmp.l %a0,%d1
	jne .L14
	jra .L10
	.size	mg_forward, .-mg_forward
	.align	2
	.type	vector_generate.part.0, @function
vector_generate.part.0:
	lea (-960,%sp),%sp
	moveq #15,%d1
	movem.l #31996,(%sp)
	move.l 968(%sp),%a0
	mvz.b (%a0),%d0
	move.l %d0,78(%sp)
	cmp.l %d0,%d1
	jcc .L16
	moveq #15,%d2
	move.l %d2,78(%sp)
.L16:
	moveq #16,%d0
	move.l 968(%sp),%a0
	mvz.b 1(%a0),%d3
	move.l %d3,70(%sp)
	cmp.l %d3,%d0
	jcc .L17
	moveq #16,%d1
	move.l %d1,70(%sp)
.L17:
	moveq #11,%d0
	move.l 968(%sp),%a0
	mvz.b 2(%a0),%d2
	move.l %d2,66(%sp)
	cmp.l %d2,%d0
	jcc .L18
	moveq #11,%d1
	move.l %d1,66(%sp)
.L18:
	mov3q.l #4,%d0
	move.l 968(%sp),%a0
	mvz.b 3(%a0),%d2
	move.l %d2,82(%sp)
	cmp.l %d2,%d0
	jcc .L19
	mov3q.l #4,82(%sp)
.L19:
	move.l 968(%sp),%a0
	moveq #126,%d0
	mvz.b 4(%a0),%d1
	move.l %d1,62(%sp)
	cmp.l %d1,%d0
	jcc .L20
	moveq #126,%d1
	move.l %d1,62(%sp)
.L20:
	moveq #127,%d0
	move.l 968(%sp),%a0
	mvz.b 5(%a0),%d2
	move.l %d2,86(%sp)
	cmp.l %d2,%d0
	jcc .L21
	moveq #127,%d1
	move.l %d1,86(%sp)
.L21:
	moveq #12,%d0
	move.l 968(%sp),%a0
	mvz.b 6(%a0),%d2
	move.l %d2,58(%sp)
	cmp.l %d2,%d0
	jcc .L22
	moveq #12,%d1
	move.l %d1,58(%sp)
.L22:
	moveq #24,%d1
	move.l 968(%sp),%a0
	move.b 8(%a0),%d0
	mvz.b 7(%a0),%d2
	move.l %d2,%a6
	move.b %d0,91(%sp)
	cmp.l %d2,%d1
	jcc .L23
	move.w #24,%a6
.L23:
	move.l 968(%sp),%a0
	lea (-12,%a6),%a1
	move.l 972(%sp),%d6
	move.b 9(%a0),%d0
	move.l %a1,74(%sp)
	tst.b %d0
	jeq .L24
	moveq #64,%d1
	cmp.l %d6,%d1
	jcs .L95
	mvz.b %d0,%d0
	cmp.l %d6,%d0
	jcs .L96
.L24:
	move.l 964(%sp),%a0
	move.l %sp,%d0
	move.l 964(%sp),%a2
	add.l #960,%d0
	move.l %a2,%a1
	move.b 975(%sp),256(%a0)
	lea (704,%sp),%a0
	move.l %a0,%a3
.L27:
	st %d1
	clr.b (%a1)
	move.b %d1,3(%a1)
	move.b %d1,2(%a1)
	move.b %d1,1(%a1)
	move.l (%a1)+,(%a3)+
	cmp.l %a3,%d0
	jne .L27
	move.l 980(%sp),%d1
	move.l #-1640531527,%d4
	move.l 78(%sp),%d7
	moveq #11,%d3
	clr.l %d2
	eor.l %d4,%d1
	lsl.l %d3,%d7
	moveq #15,%d3
	lea (192,%sp),%a1
	lea (448,%sp),%a5
	move.l %a1,%d5
	move.l %d1,%d0
	clr.w %d0
	swap %d0
	eor.l %d1,%d0
	move.l #2146121005,%d1
	muls.l %d1,%d0
	move.l %d0,%d1
	lsr.l %d3,%d1
	eor.l %d1,%d0
	move.l #-2073254261,%d1
	muls.l %d1,%d0
	move.l %d0,%d3
	clr.w %d3
	swap %d3
	eor.l %d0,%d3
	mov3q.l #3,%d0
	and.l %d2,%d0
	mvz.w %d3,%d3
	tst.l %d0
	jeq .L28
.L98:
	add.l %d7,%d3
	move.l %d3,(%a5)
.L29:
	move.l %d5,%a3
	move.l %d2,%d0
	move.l %a0,50(%sp)
.L31:
	move.l -4(%a3),%d1
	lea (960,%sp),%a0
	lea (%a0,%d1.l*4),%a4
	cmp.l -512(%a4),%d3
	jcc .L92
	move.l %d1,(%a3)
	subq.l #1,%d0
	subq.l #4,%a3
	tst.l %d0
	jne .L31
.L92:
	lea (%sp,%d0.l*4),%a3
	move.l %d2,%d3
	add.l #-1640531527,%d4
	move.l 50(%sp),%a0
	addq.l #1,%d3
	addq.l #4,%a5
	addq.l #4,%d5
	move.l %d2,192(%a3)
	cmp.l %d6,%d3
	jeq .L97
.L61:
	move.l 980(%sp),%d1
	move.l %d3,%d2
	moveq #15,%d3
	eor.l %d4,%d1
	move.l %d1,%d0
	clr.w %d0
	swap %d0
	eor.l %d1,%d0
	move.l #2146121005,%d1
	muls.l %d1,%d0
	move.l %d0,%d1
	lsr.l %d3,%d1
	eor.l %d1,%d0
	move.l #-2073254261,%d1
	muls.l %d1,%d0
	move.l %d0,%d3
	clr.w %d3
	swap %d3
	eor.l %d0,%d3
	mov3q.l #3,%d0
	and.l %d2,%d0
	mvz.w %d3,%d3
	tst.l %d0
	jne .L98
.L28:
	move.l %d3,(%a5)
	tst.l %d2
	jne .L29
	clr.l %d0
	lea (%sp,%d0.l*4),%a3
	move.l %d2,%d3
	add.l #-1640531527,%d4
	addq.l #1,%d3
	addq.l #4,%a5
	addq.l #4,%d5
	move.l %d2,192(%a3)
	cmp.l %d6,%d3
	jne .L61
.L97:
	move.l 82(%sp),%a5
	moveq #24,%d5
	lea scales,%a3
	moveq #100,%d7
	move.w #12,%a4
	mvz.w (%a3,%a5.l*2),%d4
	move.l 74(%sp),%a3
	moveq #-12,%d0
	move.l 74(%sp),%a5
	sub.l %a6,%a4
	sub.l 66(%sp),%d5
	sub.l 58(%sp),%a3
	add.l 58(%sp),%a5
	clr.l 54(%sp)
	clr.l 50(%sp)
	move.l %a0,82(%sp)
	move.l %d2,46(%sp)
.L42:
	move.l %d5,%d1
	moveq #12,%d2
	add.l %d0,%d1
	remu.l %d2,%d6:%d1
	btst %d6,%d4
	jeq .L34
.L100:
	cmp.l %a3,%d0
	jge .L35
	move.l %a4,%d1
	add.l %d0,%d1
	tst.l %d1
	jlt .L99
	cmp.l %d1,%d7
	jle .L37
.L103:
	move.l %d0,54(%sp)
	moveq #12,%d2
	addq.l #1,%d0
	move.l %d1,%d7
	move.l %d5,%d1
	add.l %d0,%d1
	remu.l %d2,%d6:%d1
	btst %d6,%d4
	jne .L100
.L34:
	addq.l #1,%d0
	moveq #13,%d1
	cmp.l %d0,%d1
	jne .L42
.L105:
	move.w 72(%sp),%d0
	move.l 82(%sp),%a0
	move.l 46(%sp),%d2
	mulu.w %d3,%d0
	addq.l #8,%d0
	lsr.l #4,%d0
	jeq .L43
	mvz.w %d0,%d0
	lea (%a1,%d0.l*4),%a4
.L44:
	move.l (%a1)+,%d0
	lea (%sp,%d0.l*4),%a3
	moveq #1,%d0
	move.b %d0,704(%a3)
	cmp.l %a1,%a4
	jne .L44
.L43:
	moveq #12,%d1
	moveq #12,%d6
	move.l 66(%sp),%d0
	addq.l #7,%d0
	remu.l %d1,%d5:%d0
	mvz.w #254,%d1
	sub.l 86(%sp),%d1
	move.l 74(%sp),%a4
	move.l %d2,%a1
	move.l 74(%sp),%a5
	clr.l %d7
	moveq #12,%d0
	sub.l 66(%sp),%d0
	move.l %d5,70(%sp)
	mulu.w 978(%sp),%d1
	add.l 58(%sp),%a5
	add.l %d5,%d0
	remu.l %d6,%d5:%d0
	mvz.w #254,%d6
	sub.l 58(%sp),%a4
	move.l %a5,74(%sp)
	move.l 50(%sp),%d2
	move.l %d3,%a3
	divu.l %d6,%d1
	asr.l %d5,%d4
	move.l 78(%sp),%a5
	move.l %a2,82(%sp)
	move.l 980(%sp),50(%sp)
	mov3q.l #1,%d0
	and.l %d4,%d0
	move.b %d1,61(%sp)
	move.l %d0,78(%sp)
.L54:
	move.l %d7,%d6
	addq.l #1,%d7
	tst.b (%a0)
	jeq .L45
	move.l #-2048144789,%d1
	moveq #15,%d5
	muls.l %d7,%d1
	move.l 50(%sp),%d3
	move.l #2146121005,%d4
	eor.l %d3,%d1
	eor.l #-1255572915,%d1
	move.l %d1,%d0
	clr.w %d0
	swap %d0
	eor.l %d1,%d0
	muls.l %d4,%d0
	move.l %d0,%d1
	lsr.l %d5,%d1
	eor.l %d1,%d0
	move.l #-2073254261,%d1
	muls.l %d1,%d0
	move.l %d0,%d1
	clr.w %d1
	swap %d1
	eor.l %d0,%d1
	tst.l %d2
	jeq .L62
	move.l %d1,%d0
	lsr.l #8,%d0
	remu.l %d2,%d4:%d0
	lea (%sp,%d4.l*4),%a6
	move.l 92(%a6),%d4
	add.l #-12,%d4
.L46:
	moveq #15,%d0
	and.l %d1,%d0
	cmp.l %a5,%d0
	jcc .L51
	moveq #48,%d0
	and.l %d1,%d0
	tst.l %d0
	jne .L64
	tst.l 78(%sp)
	jne .L101
.L64:
	move.l 66(%sp),%d0
.L48:
	btst #6,%d1
	jeq .L49
	add.l #-12,%d0
.L49:
	cmp.l %a4,%d0
	jlt .L51
	cmp.l 74(%sp),%d0
	jgt .L51
	move.l %d0,%d4
.L51:
	moveq #24,%d3
	move.l %d1,%d0
	lsr.l %d3,%d0
	mov3q.l #3,%d3
	muls.w #5,%d4
	move.l %d0,%d5
	remu.l %d3,%d0:%d5
	add.l #64,%d4
	move.b %d4,1(%a0)
	addq.l #2,%d0
	mulu.w 64(%sp),%d0
	lsr.l #2,%d0
	move.b %d0,2(%a0)
	mov3q.l #3,%d0
	and.l %d6,%d0
	tst.l %d0
	jeq .L52
	and.l #3145728,%d1
	tst.l %d1
	jeq .L52
	move.b 61(%sp),%d0
	move.b %d0,3(%a0)
.L45:
	addq.l #4,%a0
	cmp.l %a1,%d6
	jne .L54
	move.l 82(%sp),%a2
	move.l %a3,%d3
	tst.l 972(%sp)
	jeq .L55
	mvz.b 91(%sp),%d0
	moveq #63,%d4
	cmp.l %d0,%d4
	jcs .L102
	move.l 972(%sp),%d5
	move.l 968(%sp),%a0
	move.l 964(%sp),%a3
	remu.l %d5,%d2:%d0
	move.b 10(%a0),%d4
	mvz.w %d5,%d0
	move.l 972(%sp),%d1
	subq.l #1,%d5
	lea (%a3,%d0.l*4),%a1
	sub.l %d2,%d1
	move.l 972(%sp),%d2
.L58:
	move.l %d1,%d6
	addq.l #1,%d1
	remu.l %d2,%d0:%d6
	tst.b %d4
	jeq .L57
	move.l %d5,%d6
	sub.l %d0,%d6
	move.l %d6,%d0
.L57:
	remu.l %d3,%d6:%d0
	lea (960,%sp),%a3
	lea (%a3,%d6.l*4),%a0
	move.l -256(%a0),(%a2)+
	cmp.l %a1,%a2
	jne .L58
.L55:
	movem.l (%sp),#31996
	mov3q.l #1,%d0
	lea (960,%sp),%sp
	rts
.L99:
	neg.l %d1
	cmp.l %d1,%d7
	jgt .L103
.L37:
	addq.l #1,%d0
	jra .L42
.L35:
	cmp.l %a5,%d0
	jgt .L39
	move.l 50(%sp),%d1
	move.l %d0,%a0
	lea (12,%a0),%a0
	lea (%sp,%d1.l*4),%a6
	addq.l #1,%d1
	move.l %d1,50(%sp)
	move.l %a0,92(%a6)
.L39:
	move.l %a4,%d1
	add.l %d0,%d1
	tst.l %d1
	jlt .L104
.L40:
	cmp.l %d1,%d7
	jle .L34
	move.l %d0,54(%sp)
	move.l %d1,%d7
	addq.l #1,%d0
	moveq #13,%d1
	cmp.l %d0,%d1
	jne .L42
	jra .L105
.L104:
	neg.l %d1
	jra .L40
.L52:
	move.b 979(%sp),%d0
	move.b %d0,3(%a0)
	jra .L45
.L62:
	move.l 54(%sp),%d4
	jra .L46
.L102:
	move.l 972(%sp),%d5
	moveq #63,%d0
	move.l 968(%sp),%a0
	move.l 964(%sp),%a3
	remu.l %d5,%d2:%d0
	move.l 972(%sp),%d1
	mvz.w %d5,%d0
	move.b 10(%a0),%d4
	subq.l #1,%d5
	sub.l %d2,%d1
	lea (%a3,%d0.l*4),%a1
	move.l 972(%sp),%d2
	jra .L58
.L101:
	move.l 70(%sp),%d0
	jra .L48
.L96:
	move.l 964(%sp),%a0
	move.l %d0,%d6
	move.l 964(%sp),%a2
	move.l %sp,%d0
	move.l %a2,%a1
	add.l #960,%d0
	move.b 975(%sp),256(%a0)
	lea (704,%sp),%a0
	move.l %a0,%a3
	jra .L27
.L95:
	mvz.b %d0,%d0
	moveq #64,%d6
	cmp.l %d6,%d0
	jcc .L24
	jra .L96
	.size	vector_generate.part.0, .-vector_generate.part.0
	.align	2
	.type	midi_control, @function
midi_control:
	subq.l #4,%sp
	move.l %a2,-(%sp)
	move.l %d2,-(%sp)
	move.l 1187521622,%a0
	mov3q.l #3,%d2
	move.b 269161679,%d0
	add.l #585088,%a0
	mvz.w 18(%sp),%d1
	move.l 20(%sp),%a1
	lsl.l #4,%d1
	and.l %d2,%d0
	mvz.w #6322,%d2
	move.l %d1,%a2
	lea (6206,%a2),%a2
	muls.l %d2,%d0
	moveq #22,%d2
	add.l %d0,%a0
	mvz.b (%a0,%a2.l),%d0
	cmp.l %d0,%d2
	jeq .L107
	mov3q.l #6,%d0
	cmp.l %a1,%d0
	jeq .L113
	lea (first.2),%a0
	mvz.b (%a0,%a1.l),%d0
.L106:
	move.l (%sp)+,%d2
	move.l (%sp)+,%a2
	addq.l #4,%sp
	rts
.L113:
	move.l 16(%sp),%d0
	addq.l #1,%d0
	move.l (%sp)+,%d2
	move.l (%sp)+,%a2
	addq.l #4,%sp
	rts
.L107:
	move.l 1187521622,%a0
	move.l %a1,%d0
	move.b 269161679,%d2
	add.l #6194,%d0
	move.l %d0,%a2
	add.l %d1,%a2
	add.l #585088,%a0
	move.l #vector_control_max,%d0
	mvz.b (%a1,%d0.l),%d0
	move.b %d2,%d1
	mov3q.l #3,%d2
	and.l %d2,%d1
	mvz.w #6322,%d2
	muls.l %d2,%d1
	add.l %d1,%a0
	move.b (%a0,%a2.l),%d1
	add.l #64,%d1
	mvz.b %d1,%d1
	cmp.l %d0,%d1
	jcc .L106
	move.l (%sp)+,%d2
	move.l %d1,%d0
	move.l (%sp)+,%a2
	addq.l #4,%sp
	rts
	.size	midi_control, .-midi_control
	.align	2
	.type	midi_format_10, @function
midi_format_10:
	lea (-24,%sp),%sp
	movem.l #1052,(%sp)
	move.b 269161676,%d0
	pea 10.w
	mvz.b %d0,%d0
	move.l %d0,-(%sp)
	jsr midi_control
	addq.l #8,%sp
	tst.l %d0
	jeq .L123
	moveq #99,%d1
	cmp.l %d0,%d1
	jcs .L124
	moveq #9,%d1
	cmp.l %d0,%d1
	jcs .L125
	moveq #10,%d3
	mov3q.l #1,%a1
	remu.l %d3,%d1:%d0
	clr.b %d4
	move.l 28(%sp),%a0
	add.l #48,%d1
	move.b %d1,(%a0)
	move.l 28(%sp),%a0
	move.b %d4,(%a0,%a1.l)
.L114:
	movem.l (%sp),#1052
	lea (24,%sp),%sp
	rts
.L124:
	moveq #100,%d2
	mov3q.l #2,%a0
	move.l %d0,%d1
	mov3q.l #3,%a1
	divu.l %d2,%d1
	move.l 28(%sp),%a2
	moveq #10,%d2
	mov3q.l #1,16(%sp)
	add.l 28(%sp),%a0
	add.l #48,%d1
	move.b %d1,(%a2)
	move.l %d0,%d1
	divu.l %d2,%d1
	move.l 28(%sp),%a2
	move.l %d1,%d4
	remu.l %d2,%d3:%d4
	move.l 16(%sp),%d2
	move.l %d3,%d1
	add.l #48,%d1
	move.b %d1,(%a2,%d2.l)
.L126:
	moveq #10,%d3
	remu.l %d3,%d1:%d0
	clr.b %d4
	add.l #48,%d1
	move.b %d1,(%a0)
	move.l 28(%sp),%a0
	move.b %d4,(%a0,%a1.l)
	jra .L114
.L123:
	move.l 28(%sp),%a0
	move.l #1330005504,(%a0)
	movem.l (%sp),#1052
	lea (24,%sp),%sp
	rts
.L125:
	moveq #10,%d2
	mov3q.l #1,%a0
	move.l %d0,%d1
	mov3q.l #2,%a1
	divu.l %d2,%d1
	clr.l 16(%sp)
	move.l 28(%sp),%a2
	add.l 28(%sp),%a0
	move.l %d1,%d4
	remu.l %d2,%d3:%d4
	move.l 16(%sp),%d2
	move.l %d3,%d1
	add.l #48,%d1
	move.b %d1,(%a2,%d2.l)
	jra .L126
	.size	midi_format_10, .-midi_format_10
	.align	2
	.type	midi_save, @function
midi_save:
	lea (-36,%sp),%sp
	clr.l %d1
	movem.l #7420,(%sp)
	move.l 40(%sp),%d6
	moveq #127,%d5
	and.l 48(%sp),%d5
	move.l 44(%sp),%a4
	lsl.l #4,%d6
	move.l %d6,%d4
	add.l #6194,%d4
.L131:
	mov3q.l #6,%d0
	cmp.l %d1,%d0
	jeq .L136
	mov3q.l #5,%d7
	move.l %d1,%d0
	cmp.l %d1,%d7
	jcc .L130
	subq.l #1,%d0
.L130:
	move.b (%a4,%d0.l),%d3
	move.l #269161679,%a2
	mov3q.l #3,%d7
	move.b (%a2),%d0
	move.l 1187521622,%a1
	add.l #585088,%a1
	move.b (%a2),%d2
	move.l %d4,%a3
	add.l %d1,%a3
	addq.l #1,%d1
	add.l #-64,%d3
	and.l %d7,%d0
	and.l %d7,%d2
	mvz.w #6322,%d7
	muls.l %d7,%d0
	muls.l %d7,%d2
	move.l %d0,%a0
	add.l #269110990,%a0
	moveq #12,%d0
	add.l %d2,%a1
	move.b %d3,(%a1,%a3.l)
	move.b %d3,(%a0,%a3.l)
	cmp.l %d1,%d0
	jne .L131
.L137:
	move.b (%a2),%d0
	move.l 1187521622,%d1
	move.l %d6,%a1
	move.b (%a2),%d2
	move.l %d1,%a2
	mov3q.l #3,%d1
	add.l #585088,%a2
	lea (6206,%a1),%a1
	and.l %d1,%d0
	and.l %d1,%d2
	muls.l %d7,%d0
	muls.l %d7,%d2
	moveq #22,%d7
	move.l %d0,%a0
	add.l #269110990,%a0
	add.l %d2,%a2
	move.b %d7,(%a2,%a1.l)
	move.b %d7,(%a0,%a1.l)
	movem.l (%sp),#7420
	lea (36,%sp),%sp
	rts
.L136:
	move.l #269161679,%a2
	mov3q.l #3,%d7
	move.b (%a2),%d0
	move.l 1187521622,%a1
	add.l #585088,%a1
	move.b (%a2),%d2
	move.b %d5,%d3
	move.l %d4,%a3
	add.l %d1,%a3
	addq.l #1,%d1
	and.l %d7,%d0
	and.l %d7,%d2
	mvz.w #6322,%d7
	add.l #-64,%d3
	muls.l %d7,%d0
	muls.l %d7,%d2
	move.l %d0,%a0
	add.l #269110990,%a0
	moveq #12,%d0
	add.l %d2,%a1
	move.b %d3,(%a1,%a3.l)
	move.b %d3,(%a0,%a3.l)
	cmp.l %d1,%d0
	jne .L131
	jra .L137
	.size	midi_save, .-midi_save
	.align	2
	.type	midi_params, @function
midi_params:
	lea (-24,%sp),%sp
	clr.l %d0
	movem.l #7196,(%sp)
	mvz.w 30(%sp),%d2
	move.l 32(%sp),%a2
	lea vector_control_max,%a4
	lea (first.2),%a3
	lsl.l #4,%d2
	move.l %d2,%a1
	add.l #6194,%d2
	lea (6206,%a1),%a1
.L146:
	mov3q.l #6,%d1
	cmp.l %d0,%d1
	jne .L139
	mov3q.l #7,%d0
.L139:
	move.l 1187521622,%a0
	mov3q.l #3,%d3
	move.b 269161679,%d1
	mvz.w #6322,%d4
	add.l #585088,%a0
	and.l %d3,%d1
	moveq #22,%d3
	muls.l %d4,%d1
	add.l %d1,%a0
	mvz.b (%a0,%a1.l),%d1
	cmp.l %d1,%d3
	jeq .L140
	move.b (%a3,%d0.l),%d1
.L141:
	mov3q.l #5,%d3
	cmp.l %d0,%d3
	jcc .L149
	move.b %d1,-1(%a2,%d0.l)
	addq.l #1,%d0
	moveq #12,%d4
	cmp.l %d0,%d4
	jne .L146
	mov3q.l #6,-(%sp)
	move.l 32(%sp),-(%sp)
	jsr midi_control
	movem.l 8(%sp),#7196
	move.l 44(%sp),%a0
	move.l %d0,(%a0)
	lea (32,%sp),%sp
	rts
.L149:
	move.b %d1,(%a2,%d0.l)
	addq.l #1,%d0
	jra .L146
.L140:
	move.l 1187521622,%a0
	mov3q.l #3,%d4
	move.b 269161679,%d3
	add.l #585088,%a0
	mvz.b (%a4,%d0.l),%d1
	and.l %d4,%d3
	mvz.w #6322,%d4
	muls.l %d4,%d3
	add.l %d3,%a0
	move.l %d2,%d3
	add.l %d0,%d3
	move.b (%a0,%d3.l),%d3
	add.l #64,%d3
	mvz.b %d3,%d3
	cmp.l %d1,%d3
	jcc .L141
	move.l %d3,%d1
	jra .L141
	.size	midi_params, .-midi_params
	.align	2
	.type	generator_page, @function
generator_page:
	lea (-32,%sp),%sp
	movem.l #15420,(%sp)
	tst.l src_page_ready
	jeq .L151
	move.l 36(%sp),%d0
	cmp.l src_page_source.l,%d0
	jeq .L152
.L151:
	lea src_page,%a0
	move.l 36(%sp),%a1
	sub.l %a0,%a1
.L153:
	move.b (%a1,%a0.l),%d0
	move.b %d0,(%a0)+
	cmp.l #src_page+402,%a0
	jne .L153
	lea vector_control_names,%a5
	clr.l %d2
	lea src_page+202,%a1
	lea (formats.6),%a4
	lea src_page+22,%a2
	move.l #src_page+28,%d1
.L160:
	move.l (%a5)+,%a3
	sub.l %a0,%a0
.L154:
	move.b (%a3,%a0.l),%d0
	jeq .L155
	move.b %d0,(%a2,%a0.l)
	addq.l #1,%a0
	mov3q.l #5,%d3
	cmp.l %a0,%d3
	jne .L154
.L155:
	add.l %a2,%a0
.L157:
	clr.b (%a0)+
	cmp.l %a0,%d1
	jne .L157
	move.l (%a4)+,%d0
	move.l %d0,%d3
	clr.w %d3
	swap %d3
	moveq #24,%d4
	move.l %d0,%d5
	lsr.l %d4,%d5
	move.l %d0,%d4
	lsr.l #8,%d4
	move.b %d0,3(%a1)
	mov3q.l #5,%d0
	move.b %d5,(%a1)
	move.b %d4,2(%a1)
	move.b %d3,1(%a1)
	cmp.l %d2,%d0
	jcs .L161
	move.l #generator_widget,%d0
	moveq #24,%d4
	move.l %d0,%d3
	move.l %d0,%d5
	clr.w %d3
	swap %d3
	lsr.l %d4,%d5
	move.l %d0,%d4
	lsr.l #8,%d4
	move.b %d0,51(%a1)
	addq.l #4,%a1
	move.b %d5,44(%a1)
	move.b %d4,46(%a1)
	addq.l #1,%d2
	addq.l #6,%a2
	addq.l #6,%d1
	moveq #12,%d0
	move.b %d3,45(%a1)
	cmp.l %d2,%d0
	jne .L160
.L171:
	mvz.w #21845,%d3
	move.l 36(%sp),%d0
	move.l #1431655765,%d4
	move.l %d4,src_page+398
	mov3q.l #1,src_page_ready
	move.l %d3,src_page+394
	move.l %d0,src_page_source
.L152:
	move.l #src_page,%d0
	movem.l (%sp),#15420
	lea (32,%sp),%sp
	rts
.L161:
	move.l #secondary_widget,%d0
	moveq #24,%d4
	move.l %d0,%d3
	move.l %d0,%d5
	clr.w %d3
	swap %d3
	lsr.l %d4,%d5
	move.l %d0,%d4
	lsr.l #8,%d4
	move.b %d0,51(%a1)
	addq.l #4,%a1
	move.b %d5,44(%a1)
	move.b %d4,46(%a1)
	addq.l #1,%d2
	addq.l #6,%a2
	addq.l #6,%d1
	moveq #12,%d0
	move.b %d3,45(%a1)
	cmp.l %d2,%d0
	jne .L160
	jra .L171
	.size	generator_page, .-generator_page
	.section	.rodata.str1.1,"aMS",@progbits,1
.LC0:
	.string	"VEC"
	.section	.rodata
.LC1:
	.string	"VECTOR 1/2"
	.string	""
	.text
	.align	2
	.type	vector_midi_page, @function
vector_midi_page:
	lea (-28,%sp),%sp
	move.l 32(%sp),%a1
	move.l 36(%sp),%d0
	movem.l #31756,(%sp)
	lea 1(%a1,%d0.l),%a3
	tst.l src_page_ready
	jne .L173
	cmp.l midi_page_built.l,%a3
	jeq .L174
.L173:
	mov3q.l #1,%d1
	and.l 36(%sp),%d1
	lea src_page,%a0
	sub.l %a0,%a1
.L175:
	move.b (%a1,%a0.l),%d0
	move.b %d0,(%a0)+
	cmp.l #src_page+402,%a0
	jne .L175
	lea .LC0,%a1
	sub.l %a0,%a0
	lea src_page+4,%a2
.L176:
	move.b (%a1),%d0
	addq.l #1,%a1
	tst.b %d0
	jeq .L177
	move.b %d0,(%a2)+
	addq.l #1,%a0
	mov3q.l #5,%d2
	cmp.l %a0,%d2
	jne .L176
.L177:
	add.l #src_page+4,%a0
	lea src_page+10,%a1
.L179:
	clr.b (%a0)+
	cmp.l #src_page+10,%a0
	jne .L179
	moveq #86,%d0
	lea .LC1+1,%a0
	move.b %d0,src_page+9
.L181:
	move.b (%a0)+,(%a1)+
	cmp.l #.LC1+12,%a0
	jne .L181
	move.l %d1,%d0
	add.l #49,%d0
	move.b %d0,src_page+16
	move.w %d1,%d0
	lea src_page+202,%a1
	move.l #src_page+28,%d1
	mulu.w #24,%d0
	move.l %d0,%a6
	move.l %d0,%a5
	add.l #vector_control_names,%a6
	add.l #formats.1,%a5
.L187:
	move.l (%a6)+,%a4
	move.l %d1,%a2
	sub.l %a0,%a0
	subq.l #6,%a2
.L182:
	move.b (%a4,%a0.l),%d0
	jeq .L183
	move.b %d0,(%a2,%a0.l)
	addq.l #1,%a0
	mov3q.l #5,%d2
	cmp.l %a0,%d2
	jne .L182
.L183:
	add.l %a2,%a0
.L185:
	clr.b (%a0)+
	cmp.l %a0,%d1
	jne .L185
	moveq #64,%d2
	move.l (%a5)+,%d0
	moveq #24,%d1
	move.l %d0,%d3
	lsr.l %d1,%d3
	move.l %d0,%d1
	lsr.l #8,%d1
	move.b %d0,3(%a1)
	addq.l #4,%a1
	move.b %d3,-4(%a1)
	move.b %d1,-2(%a1)
	moveq #103,%d1
	move.b %d2,44(%a1)
	move.l %d0,%d2
	moveq #4,%d0
	clr.w %d2
	swap %d2
	move.b %d1,46(%a1)
	move.l %a0,%d1
	addq.l #6,%d1
	move.b %d0,45(%a1)
	moveq #-92,%d0
	move.b %d0,47(%a1)
	move.b %d2,-3(%a1)
	cmp.l #src_page+58,%a0
	jne .L187
	mvz.w #21845,%d1
	move.l #1431655765,%d2
	move.l %d2,src_page+398
	clr.l src_page_ready
	move.l %d1,src_page+394
	move.l %a3,midi_page_built
.L174:
	move.l #src_page,%d0
	movem.l (%sp),#31756
	lea (28,%sp),%sp
	rts
	.size	vector_midi_page, .-vector_midi_page
	.align	2
	.type	settings, @function
settings:
	lea (-44,%sp),%sp
	movem.l #19460,(%sp)
	clr.w %d2
	move.l 1187521622,%d0
	move.l #540019724,%a1
	move.l %a0,16(%sp)
	move.l %d0,%a0
	add.l #585088,%a0
	clr.b %d0
	move.b 269161679,%d1
	move.w %d2,40(%sp)
	move.l #185270273,%d2
	move.l %d2,32(%sp)
	mov3q.l #3,%d2
	move.b %d0,42(%sp)
	move.w 50(%sp),%d0
	move.l %a1,36(%sp)
	and.l %d2,%d1
	mvz.w #6322,%d2
	mulu.w #30,%d0
	muls.l %d2,%d1
	add.l %d1,%a0
	mvz.b 62(%a0,%d0.l),%d1
	subq.l #1,%d1
	tst.l %d1
	jeq .L227
	lea (23,%sp),%a6
	sub.l %a1,%a1
.L212:
	move.l %a1,%d1
	add.l #489,%d1
	add.l %d0,%d1
	mov3q.l #2,%d2
	cmp.l %a1,%d2
	jcc .L228
.L209:
	move.b (%a0,%d1.l),(%a6)
	addq.l #1,%a1
	moveq #9,%d1
	cmp.l %a1,%d1
	jeq .L211
	move.l %a1,%d1
	add.l #489,%d1
	addq.l #1,%a6
	add.l %d0,%d1
	mov3q.l #2,%d2
	cmp.l %a1,%d2
	jcs .L209
.L228:
	lea 63(%a1,%d0.l),%a2
	addq.l #1,%a1
	move.b (%a0,%a2.l),(%a6)+
	jra .L212
.L211:
	move.b 23(%sp),%d0
	moveq #15,%d1
	mov3q.l #4,%d2
	and.l %d0,%d1
	mvz.b %d0,%d0
	lsr.l #4,%d0
	move.w %d0,%a0
	move.b %d1,32(%sp)
	cmp.l %d0,%d2
	jcs .L229
	move.w %a0,%d0
	move.b 24(%sp),%d1
	moveq #16,%d2
	move.b %d0,35(%sp)
	moveq #31,%d0
	and.l %d1,%d0
	move.w %d0,%a0
	cmp.l %d0,%d2
	jcs .L230
.L214:
	move.w %a0,%d2
	move.b 25(%sp),%d0
	lsr.l #5,%d1
	move.b %d2,33(%sp)
	mov3q.l #1,%d2
	and.l %d2,%d1
	moveq #15,%d2
	and.l %d0,%d2
	move.b %d1,42(%sp)
	move.b %d2,%d1
	move.l %d2,%a0
	moveq #11,%d2
	cmp.l %a0,%d2
	jcs .L231
.L215:
	mvz.b %d0,%d0
	lsr.l #4,%d0
	move.b %d1,34(%sp)
	moveq #12,%d1
	move.w %d0,%a0
	cmp.l %d0,%d1
	jcs .L232
.L216:
	move.b 26(%sp),%d1
	move.w %a0,%d2
	mvz.b %d1,%d0
	move.b %d2,38(%sp)
	moveq #126,%d2
	cmp.l %d0,%d2
	jcs .L233
.L217:
	move.b 27(%sp),%d0
	move.b %d1,36(%sp)
	tst.b %d0
	jlt .L234
.L218:
	move.b 28(%sp),%d1
	move.b %d0,37(%sp)
	moveq #24,%d2
	mvz.b %d1,%d0
	cmp.l %d0,%d2
	jcs .L235
.L219:
	mvz.b 29(%sp),%d0
	move.b %d1,39(%sp)
	moveq #63,%d1
	cmp.l %d0,%d1
	jcs .L236
.L220:
	move.b 30(%sp),%d1
	lsl.l #8,%d0
	mvz.b %d1,%d2
	move.l %d2,%a0
	moveq #64,%d2
	cmp.l %a0,%d2
	jcs .L237
.L221:
	move.b %d1,%d0
	lea (32,%sp),%a3
	move.w %d0,40(%sp)
.L207:
	move.l 16(%sp),%a0
	move.l %a0,%d0
	move.l (%a3),(%a0)+
	move.l 36(%sp),(%a0)+
	move.w 40(%sp),(%a0)+
	movem.l (%sp),#19460
	move.b 42(%sp),(%a0)
	lea (44,%sp),%sp
	rts
.L237:
	moveq #64,%d1
	lea (32,%sp),%a3
	move.b %d1,%d0
	move.w %d0,40(%sp)
	jra .L207
.L236:
	move.b 30(%sp),%d1
	moveq #63,%d0
	lsl.l #8,%d0
	mvz.b %d1,%d2
	move.l %d2,%a0
	moveq #64,%d2
	cmp.l %a0,%d2
	jcc .L221
	jra .L237
.L235:
	moveq #24,%d1
	mvz.b 29(%sp),%d0
	move.b %d1,39(%sp)
	moveq #63,%d1
	cmp.l %d0,%d1
	jcc .L220
	jra .L236
.L234:
	moveq #127,%d0
	move.b 28(%sp),%d1
	moveq #24,%d2
	move.b %d0,37(%sp)
	mvz.b %d1,%d0
	cmp.l %d0,%d2
	jcc .L219
	jra .L235
.L233:
	moveq #126,%d1
	move.b 27(%sp),%d0
	move.b %d1,36(%sp)
	tst.b %d0
	jge .L218
	jra .L234
.L232:
	move.w #12,%a0
	move.b 26(%sp),%d1
	move.w %a0,%d2
	mvz.b %d1,%d0
	move.b %d2,38(%sp)
	moveq #126,%d2
	cmp.l %d0,%d2
	jcc .L217
	jra .L233
.L231:
	moveq #11,%d1
	mvz.b %d0,%d0
	lsr.l #4,%d0
	move.w %d0,%a0
	move.b %d1,34(%sp)
	moveq #12,%d1
	cmp.l %d0,%d1
	jcc .L216
	jra .L232
.L230:
	move.w #16,%a0
	move.b 25(%sp),%d0
	lsr.l #5,%d1
	move.w %a0,%d2
	move.b %d2,33(%sp)
	mov3q.l #1,%d2
	and.l %d2,%d1
	moveq #15,%d2
	and.l %d0,%d2
	move.b %d1,42(%sp)
	move.b %d2,%d1
	move.l %d2,%a0
	moveq #11,%d2
	cmp.l %a0,%d2
	jcc .L215
	jra .L231
.L229:
	move.w #4,%a0
	move.b 24(%sp),%d1
	moveq #16,%d2
	move.w %a0,%d0
	move.b %d0,35(%sp)
	moveq #31,%d0
	and.l %d1,%d0
	move.w %d0,%a0
	cmp.l %d0,%d2
	jcc .L214
	jra .L230
.L227:
	lea (32,%sp),%a3
	sub.l %a1,%a1
	move.l %a3,%a2
.L208:
	move.l %a1,%d1
	add.l #489,%d1
	lea 63(%a1,%d0.l),%a6
	add.l %d0,%d1
	mov3q.l #2,%d2
	cmp.l %a1,%d2
	jcs .L205
.L238:
	addq.l #1,%a1
	move.b (%a0,%a6.l),(%a2)+
	move.l %a1,%d1
	add.l #489,%d1
	lea 63(%a1,%d0.l),%a6
	add.l %d0,%d1
	mov3q.l #2,%d2
	cmp.l %a1,%d2
	jcc .L238
.L205:
	move.b (%a0,%d1.l),(%a2)
	addq.l #1,%a1
	mov3q.l #6,%d1
	cmp.l %a1,%d1
	jeq .L207
	addq.l #1,%a2
	jra .L208
	.size	settings, .-settings
	.align	2
	.type	draw_generator_widget.part.0, @function
draw_generator_widget.part.0:
	lea (-12,%sp),%sp
	move.l %a6,-(%sp)
	move.l %d2,-(%sp)
	mvz.b 269161676,%d0
	move.l 36(%sp),%a6
	move.l %d0,-(%sp)
	lea (13,%sp),%a0
	jsr settings
	addq.l #4,%sp
	mov3q.l #6,%d0
	cmp.l %a6,%d0
	jeq .L247
	mov3q.l #5,%d2
	move.l %a6,%d0
	cmp.l %a6,%d2
	jcc .L242
	subq.l #1,%d0
.L242:
	mvz.b 9(%sp,%d0.l),%d0
	move.l %d0,%a0
.L241:
	move.l 48(%sp),-(%sp)
	move.l 48(%sp),-(%sp)
	moveq #-2,%d0
	and.l 48(%sp),%d0
	lea vector_control_max,%a1
	mvz.b (%a1,%a6.l),%d1
	move.l %d0,-(%sp)
	move.l %d1,%d0
	cmp.l %d1,%a0
	jcc .L243
	move.l %a0,%d0
.L243:
	mulu.w #127,%d0
	divu.l %d1,%d0
	move.l %d0,-(%sp)
	move.l 48(%sp),-(%sp)
	move.l 48(%sp),-(%sp)
	move.l 48(%sp),-(%sp)
	jsr 1074035124
	lea (28,%sp),%sp
	move.l (%sp)+,%d2
	move.l (%sp)+,%a6
	lea (12,%sp),%sp
	rts
.L247:
	move.b 269161676,%d0
	move.l 1187521622,%a1
	mov3q.l #3,%d2
	move.b 269161679,%d1
	add.l #585088,%a1
	mvz.b %d0,%d0
	and.l %d2,%d1
	mulu.w #30,%d0
	move.l %d0,%a0
	mvz.w #6322,%d0
	lea (497,%a0),%a0
	muls.l %d0,%d1
	add.l %d1,%a1
	move.b (%a1,%a0.l),%d0
	moveq #127,%d1
	and.l %d0,%d1
	move.l %d1,%a0
	jra .L241
	.size	draw_generator_widget.part.0, .-draw_generator_widget.part.0
	.align	2
	.type	secondary_widget, @function
secondary_widget:
	subq.l #8,%sp
	move.l %d2,-(%sp)
	moveq #11,%d2
	move.l 24(%sp),%d0
	move.l %d0,%d1
	move.l 16(%sp),%a0
	addq.l #6,%d1
	move.l 20(%sp),%a1
	move.l 32(%sp),4(%sp)
	move.l 36(%sp),8(%sp)
	cmp.l %d1,%d2
	jcc .L252
	move.l (%sp)+,%d2
	addq.l #8,%sp
	rts
.L252:
	move.l 8(%sp),36(%sp)
	move.l 4(%sp),32(%sp)
	move.l %d1,28(%sp)
	move.l %d0,24(%sp)
	move.l %a1,20(%sp)
	move.l %a0,16(%sp)
	move.l (%sp)+,%d2
	addq.l #8,%sp
	jra (draw_generator_widget.part.0)
	.size	secondary_widget, .-secondary_widget
	.align	2
	.type	generator_widget, @function
generator_widget:
	subq.l #4,%sp
	move.l %d2,-(%sp)
	moveq #11,%d2
	move.l 20(%sp),%d0
	move.l 12(%sp),%d1
	move.l 16(%sp),%a0
	move.l 28(%sp),%a1
	move.l 32(%sp),4(%sp)
	cmp.l %d0,%d2
	jcc .L257
	move.l (%sp)+,%d2
	addq.l #4,%sp
	rts
.L257:
	move.l 4(%sp),32(%sp)
	move.l %a1,28(%sp)
	move.l %d0,24(%sp)
	move.l %d0,20(%sp)
	move.l %a0,16(%sp)
	move.l %d1,12(%sp)
	move.l (%sp)+,%d2
	addq.l #4,%sp
	jra (draw_generator_widget.part.0)
	.size	generator_widget, .-generator_widget
	.align	2
	.type	mg_view.constprop.0, @function
mg_view.constprop.0:
	lea (-12,%sp),%sp
	movem.l #1036,(%sp)
	tst.l -2147483630
	jeq .L259
	move.l #1187521622,%a0
	move.l (%a0),%d0
	add.l #-1073741824,%d0
	cmp.l #133169151,%d0
	jhi .L259
	move.l #269161676,%a1
	mov3q.l #7,%d1
	mvz.b (%a1),%d0
	cmp.l %d0,%d1
	jcs .L259
	move.b (%a1),%d1
	move.l (%a0),%d0
	mov3q.l #2,%d3
	move.b 269161679,%d2
	move.w %d2,%a0
	cmp.l 1175262852.l,%d3
	jne .L259
	tst.l 1175263034
	jne .L259
	tst.l 1175262868
	jne .L259
	move.l %a0,%d2
	mov3q.l #3,%d3
	and.l %d3,%d2
	mvz.b %d1,%d1
	add.l #585088,%d0
	move.l %d1,%a1
	lea (3089,%a1),%a1
	move.l %d2,%d1
	mvz.w #6322,%d2
	muls.l %d2,%d1
	moveq #77,%d2
	add.l %d1,%d0
	move.l %d0,%a2
	lea (%a2,%a1.l*2),%a0
	move.b 1(%a0),%d0
	mvz.b (%a0),%d1
	cmp.l %d1,%d2
	jne .L259
	tst.l 20(%sp)
	jeq .L259
	mvz.b %d0,%d0
	moveq #86,%d3
	cmp.l %d0,%d3
	jeq .L262
	move.b (%a0),%d0
.L259:
	movem.l (%sp),#1036
	clr.l %d0
	lea (12,%sp),%sp
	rts
.L262:
	movem.l (%sp),#1036
	move.l #vector_midi,%d0
	lea (12,%sp),%sp
	rts
	.size	mg_view.constprop.0, .-mg_view.constprop.0
	.section	.rodata.str1.1
.LC2:
	.string	"FWD"
.LC3:
	.string	"OFF"
.LC4:
	.string	"REV"
	.text
	.align	2
	.type	format_control, @function
format_control:
	lea (-28,%sp),%sp
	movem.l #16412,(%sp)
	move.l 36(%sp),%d2
	lea (17,%sp),%a0
	mvz.b 269161676,%d0
	move.l %d0,-(%sp)
	jsr settings
	addq.l #4,%sp
	mov3q.l #6,%d0
	cmp.l %d2,%d0
	jeq .L299
	mov3q.l #5,%d0
	cmp.l %d2,%d0
	jcs .L274
	mvz.b 17(%sp,%d2.l),%d0
	move.l %d2,%d1
	mov3q.l #1,%d3
	subq.l #2,%d1
	cmp.l %d1,%d3
	jcs .L273
	subq.l #2,%d2
	tst.l %d2
	jeq .L300
	mov3q.l #5,%d3
	remu.l %d3,%d1:%d0
	lea vector_scale_names,%a0
	move.l 32(%sp),%a1
	move.l (%a0,%d1.l*4),%a0
.L280:
	move.b (%a0)+,%d0
	move.b %d0,(%a1)+
	jne .L280
.L271:
	movem.l (%sp),#16412
	lea (28,%sp),%sp
	rts
.L274:
	mvz.b 16(%sp,%d2.l),%d0
	moveq #11,%d4
	cmp.l %d2,%d4
	jne .L301
	tst.l %d0
	jeq .L291
	move.l 32(%sp),%a1
	lea .LC4,%a0
.L284:
	move.b (%a0)+,%d0
	move.b %d0,(%a1)+
	jeq .L271
	move.b (%a0)+,%d0
	move.b %d0,(%a1)+
	jne .L284
	jra .L271
.L299:
	move.b 269161676,%d0
	move.l 1187521622,%a1
	mov3q.l #3,%d2
	move.b 269161679,%d1
	mvz.w #6322,%d3
	add.l #585088,%a1
	moveq #127,%d4
	mvz.b %d0,%d0
	and.l %d2,%d1
	mulu.w #30,%d0
	move.l %d0,%a0
	muls.l %d3,%d1
	lea (497,%a0),%a0
	add.l %d1,%a1
	move.b (%a1,%a0.l),%d0
	and.l %d4,%d0
.L273:
	moveq #99,%d3
	cmp.l %d0,%d3
	jcc .L292
.L303:
	moveq #100,%d4
	moveq #10,%d3
	move.l %d0,%d1
	mov3q.l #2,%a6
	divu.l %d4,%d1
	move.l 32(%sp),%a0
	mov3q.l #3,%a1
	add.l #48,%d1
	move.b %d1,(%a0)+
	move.l %d0,%d1
	divu.l %d3,%d1
	move.l %d1,%d2
	remu.l %d3,%d4:%d2
	move.l %d4,%d1
	add.l #48,%d1
	move.b %d1,(%a0)
	move.l 32(%sp),%a0
	add.l %a6,%a0
.L289:
	moveq #10,%d2
	remu.l %d2,%d1:%d0
	clr.b %d3
	add.l #48,%d1
	move.b %d1,(%a0)
	move.l 32(%sp),%a0
	move.b %d3,(%a0,%a1.l)
	movem.l (%sp),#16412
	lea (28,%sp),%sp
	rts
.L292:
	move.l 32(%sp),%a0
	mov3q.l #1,%a1
	clr.l %d1
	moveq #9,%d2
	cmp.l %d0,%d2
	jcc .L289
.L304:
	move.l %a1,%a6
	moveq #10,%d3
	move.l %d1,%a1
	move.l %d0,%d1
	divu.l %d3,%d1
	addq.l #2,%a1
	move.l %d1,%d2
	remu.l %d3,%d4:%d2
	move.l %d4,%d1
	add.l #48,%d1
	move.b %d1,(%a0)
	move.l 32(%sp),%a0
	add.l %a6,%a0
	jra .L289
.L291:
	move.l 32(%sp),%a1
	lea .LC2,%a0
	jra .L284
.L300:
	moveq #12,%d2
	remu.l %d2,%d1:%d0
	lea (roots.5),%a0
	move.l 32(%sp),%a1
	move.l (%a0,%d1.l*4),%a0
	jra .L280
.L301:
	moveq #10,%d4
	cmp.l %d2,%d4
	jne .L282
	tst.l %d0
	jne .L273
	move.l 32(%sp),%a1
	lea .LC3,%a0
	jra .L284
.L282:
	subq.l #8,%d2
	tst.l %d2
	jne .L273
	move.l %d0,%d1
	add.l #-12,%d1
	tst.l %d1
	jlt .L302
	move.l %d1,%d0
	moveq #99,%d3
	cmp.l %d0,%d3
	jcs .L303
	jra .L292
.L302:
	move.l 32(%sp),%a0
	moveq #12,%d2
	sub.l %d0,%d2
	move.l %d2,%d0
	mov3q.l #2,%a1
	move.b #45,(%a0)+
	mov3q.l #1,%d1
	moveq #9,%d2
	cmp.l %d0,%d2
	jcc .L289
	jra .L304
	.size	format_control, .-format_control
	.align	2
	.type	format_10, @function
format_10:
	moveq #10,%d0
	move.l %d0,8(%sp)
	jra format_control
	.size	format_10, .-format_10
	.align	2
	.type	format_8, @function
format_8:
	moveq #8,%d0
	move.l %d0,8(%sp)
	jra format_control
	.size	format_8, .-format_8
	.align	2
	.type	format_6, @function
format_6:
	mov3q.l #6,8(%sp)
	jra format_control
	.size	format_6, .-format_6
	.align	2
	.type	midi_format_4, @function
midi_format_4:
	move.l %a2,-(%sp)
	move.l %d2,-(%sp)
	move.b 269161676,%d0
	move.l 1187521622,%a0
	mov3q.l #3,%d2
	add.l #585088,%a0
	move.b 269161679,%d1
	move.l 12(%sp),%a1
	mvz.b %d0,%d0
	and.l %d2,%d1
	lsl.l #4,%d0
	mvz.w #6322,%d2
	muls.l %d2,%d1
	move.l %d0,%a2
	moveq #22,%d2
	lea (6206,%a2),%a2
	add.l %d1,%a0
	mvz.b (%a0,%a2.l),%d1
	cmp.l %d1,%d2
	jeq .L317
	moveq #8,%d0
.L312:
	move.l %d0,16(%sp)
	move.l %a1,12(%sp)
	move.l (%sp)+,%d2
	move.l 1074609936,%a1
	move.l (%sp)+,%a2
	jmp (%a1)
.L317:
	move.l 1187521622,%a2
	move.l %d0,%a0
	move.b 269161679,%d1
	mov3q.l #3,%d0
	mvz.w #6322,%d2
	add.l #585088,%a2
	lea (6198,%a0),%a0
	and.l %d0,%d1
	muls.l %d2,%d1
	add.l %d1,%a2
	move.b (%a2,%a0.l),%d0
	moveq #126,%d1
	add.l #64,%d0
	mvz.b %d0,%d0
	cmp.l %d0,%d1
	jcc .L312
	moveq #126,%d0
	move.l %d0,16(%sp)
	move.l %a1,12(%sp)
	move.l (%sp)+,%d2
	move.l 1074609936,%a1
	move.l (%sp)+,%a2
	jmp (%a1)
	.size	midi_format_4, .-midi_format_4
	.align	2
	.type	midi_format_11, @function
midi_format_11:
	move.b 269161676,%d0
	pea 11.w
	mvz.b %d0,%d0
	move.l %d0,-(%sp)
	jsr midi_control
	addq.l #8,%sp
	tst.l %d0
	jeq .L321
	move.l 4(%sp),%a1
	lea .LC4,%a0
.L320:
	move.b (%a0)+,%d0
	move.b %d0,(%a1)+
	jne .L320
	rts
.L321:
	move.l 4(%sp),%a1
	lea .LC2,%a0
	jra .L320
	.size	midi_format_11, .-midi_format_11
	.align	2
	.type	midi_format_3, @function
midi_format_3:
	move.l %d2,-(%sp)
	move.b 269161676,%d0
	mov3q.l #3,-(%sp)
	mov3q.l #5,%d2
	mvz.b %d0,%d0
	move.l %d0,-(%sp)
	jsr midi_control
	addq.l #8,%sp
	lea vector_scale_names,%a0
	remu.l %d2,%d1:%d0
	move.l 8(%sp),%a1
	move.l (%a0,%d1.l*4),%a0
.L326:
	move.b (%a0)+,%d0
	move.b %d0,(%a1)+
	jne .L326
	move.l (%sp)+,%d2
	rts
	.size	midi_format_3, .-midi_format_3
	.align	2
	.type	midi_format_2, @function
midi_format_2:
	move.l %d2,-(%sp)
	moveq #12,%d2
	move.b 269161676,%d0
	mov3q.l #2,-(%sp)
	mvz.b %d0,%d0
	move.l %d0,-(%sp)
	jsr midi_control
	addq.l #8,%sp
	lea (roots.0),%a0
	remu.l %d2,%d1:%d0
	move.l 8(%sp),%a1
	move.l (%a0,%d1.l*4),%a0
.L331:
	move.b (%a0)+,%d0
	move.b %d0,(%a1)+
	jne .L331
	move.l (%sp)+,%d2
	rts
	.size	midi_format_2, .-midi_format_2
	.align	2
	.type	format_11, @function
format_11:
	mvz.b 269161676,%d0
	lea (-12,%sp),%sp
	lea (1,%sp),%a0
	move.l %d0,-(%sp)
	jsr settings
	addq.l #4,%sp
	tst.b 11(%sp)
	jeq .L338
	lea .LC4,%a0
	move.l 16(%sp),%a1
.L337:
	move.b (%a0)+,%d0
	move.b %d0,(%a1)+
	jne .L337
	lea (12,%sp),%sp
	rts
.L338:
	move.l 16(%sp),%a1
	lea .LC2,%a0
	jra .L337
	.size	format_11, .-format_11
	.align	2
	.type	format_3, @function
format_3:
	lea (-12,%sp),%sp
	move.l %d2,-(%sp)
	mvz.b 269161676,%d0
	lea (5,%sp),%a0
	mov3q.l #5,%d2
	move.l %d0,-(%sp)
	jsr settings
	mvz.b 12(%sp),%d0
	addq.l #4,%sp
	lea vector_scale_names,%a0
	remu.l %d2,%d1:%d0
	move.l 20(%sp),%a1
	move.l (%a0,%d1.l*4),%a0
.L343:
	move.b (%a0)+,%d0
	move.b %d0,(%a1)+
	jne .L343
	move.l (%sp)+,%d2
	lea (12,%sp),%sp
	rts
	.size	format_3, .-format_3
	.align	2
	.type	format_2, @function
format_2:
	lea (-12,%sp),%sp
	move.l %d2,-(%sp)
	moveq #12,%d2
	mvz.b 269161676,%d0
	lea (5,%sp),%a0
	move.l %d0,-(%sp)
	jsr settings
	mvz.b 11(%sp),%d0
	addq.l #4,%sp
	lea (roots.5),%a0
	remu.l %d2,%d1:%d0
	move.l 20(%sp),%a1
	move.l (%a0,%d1.l*4),%a0
.L348:
	move.b (%a0)+,%d0
	move.b %d0,(%a1)+
	jne .L348
	move.l (%sp)+,%d2
	lea (12,%sp),%sp
	rts
	.size	format_2, .-format_2
	.align	2
	.type	midi_format_0, @function
midi_format_0:
	lea (-16,%sp),%sp
	movem.l #1052,(%sp)
	mov3q.l #3,%d2
	mvz.w #6322,%d3
	move.l 20(%sp),%a1
	moveq #22,%d4
	move.b 269161676,%d0
	move.l 1187521622,%a0
	add.l #585088,%a0
	move.b 269161679,%d1
	mvz.b %d0,%d0
	and.l %d2,%d1
	lsl.l #4,%d0
	muls.l %d3,%d1
	move.l %d0,%a2
	lea (6206,%a2),%a2
	add.l %d1,%a0
	mvz.b (%a0,%a2.l),%d1
	cmp.l %d1,%d4
	jeq .L360
	moveq #49,%d1
.L353:
	move.l %a1,%a0
	mov3q.l #2,%d0
	move.b #49,(%a0)+
	clr.b %d4
	move.b %d1,(%a0)
	move.b %d4,(%a1,%d0.l)
	movem.l (%sp),#1052
	lea (16,%sp),%sp
	rts
.L360:
	move.l 1187521622,%d1
	move.l %d0,%a0
	move.b 269161679,%d2
	move.l %d1,%d0
	mov3q.l #3,%d3
	mvz.w #6322,%d4
	add.l #585088,%d0
	lea (6194,%a0),%a0
	move.w %d2,%a2
	moveq #15,%d2
	move.l %a2,%d1
	and.l %d3,%d1
	muls.l %d4,%d1
	add.l %d1,%d0
	move.b (%a0,%d0.l),%d0
	add.l #64,%d0
	mvz.b %d0,%d0
	move.l %d0,%d1
	cmp.l %d0,%d2
	jcs .L361
	move.l %d1,%d3
	moveq #10,%d4
	remu.l %d4,%d2:%d3
	moveq #9,%d3
	move.l %d2,%d1
	add.l #48,%d1
	cmp.l %d0,%d3
	jcs .L353
.L357:
	clr.b %d4
	move.l %a1,%a0
	mov3q.l #1,%d0
	move.b %d1,(%a0)
	move.b %d4,(%a1,%d0.l)
	movem.l (%sp),#1052
	lea (16,%sp),%sp
	rts
.L361:
	moveq #15,%d1
	moveq #10,%d4
	move.l %d1,%d3
	remu.l %d4,%d2:%d3
	moveq #9,%d3
	move.l %d2,%d1
	add.l #48,%d1
	cmp.l %d0,%d3
	jcc .L357
	jra .L353
	.size	midi_format_0, .-midi_format_0
	.align	2
	.type	midi_format_1, @function
midi_format_1:
	lea (-16,%sp),%sp
	movem.l #1052,(%sp)
	mov3q.l #3,%d2
	mvz.w #6322,%d3
	move.l 20(%sp),%a1
	moveq #22,%d4
	move.b 269161676,%d0
	move.l 1187521622,%a0
	add.l #585088,%a0
	move.b 269161679,%d1
	mvz.b %d0,%d0
	and.l %d2,%d1
	lsl.l #4,%d0
	muls.l %d3,%d1
	move.l %d0,%a2
	lea (6206,%a2),%a2
	add.l %d1,%a0
	mvz.b (%a0,%a2.l),%d1
	cmp.l %d1,%d4
	jeq .L370
	moveq #49,%d1
.L363:
	move.l %a1,%a0
	mov3q.l #2,%d0
	move.b #49,(%a0)+
	clr.b %d4
	move.b %d1,(%a0)
	move.b %d4,(%a1,%d0.l)
	movem.l (%sp),#1052
	lea (16,%sp),%sp
	rts
.L370:
	move.l 1187521622,%d1
	move.l %d0,%a0
	move.b 269161679,%d2
	move.l %d1,%d0
	mov3q.l #3,%d3
	mvz.w #6322,%d4
	add.l #585088,%d0
	lea (6195,%a0),%a0
	move.w %d2,%a2
	moveq #16,%d2
	move.l %a2,%d1
	and.l %d3,%d1
	muls.l %d4,%d1
	add.l %d1,%d0
	move.b (%a0,%d0.l),%d0
	add.l #64,%d0
	mvz.b %d0,%d0
	move.l %d0,%d1
	cmp.l %d0,%d2
	jcs .L371
	move.l %d1,%d3
	moveq #10,%d4
	remu.l %d4,%d2:%d3
	moveq #9,%d3
	move.l %d2,%d1
	add.l #48,%d1
	cmp.l %d0,%d3
	jcs .L363
.L367:
	clr.b %d4
	move.l %a1,%a0
	mov3q.l #1,%d0
	move.b %d1,(%a0)
	move.b %d4,(%a1,%d0.l)
	movem.l (%sp),#1052
	lea (16,%sp),%sp
	rts
.L371:
	moveq #16,%d1
	moveq #10,%d4
	move.l %d1,%d3
	remu.l %d4,%d2:%d3
	moveq #9,%d3
	move.l %d2,%d1
	add.l #48,%d1
	cmp.l %d0,%d3
	jcc .L367
	jra .L363
	.size	midi_format_1, .-midi_format_1
	.align	2
	.type	midi_format_5, @function
midi_format_5:
	lea (-12,%sp),%sp
	movem.l #28,(%sp)
	mov3q.l #3,%d2
	mvz.w #6322,%d3
	move.l 16(%sp),%a1
	moveq #22,%d4
	move.b 269161676,%d0
	move.l 1187521622,%a0
	add.l #585088,%a0
	move.b 269161679,%d1
	mvz.b %d0,%d0
	and.l %d2,%d1
	lsl.l #4,%d0
	muls.l %d3,%d1
	move.l %d0,%d2
	add.l #6206,%d2
	add.l %d1,%a0
	mvz.b (%a0,%d2.l),%d1
	cmp.l %d1,%d4
	jeq .L381
	moveq #52,%d0
	move.l %a1,%a0
	mov3q.l #2,%d2
	moveq #56,%d1
	mov3q.l #1,%d3
	move.b %d0,(%a0)
.L376:
	clr.b %d0
	move.b %d1,(%a1,%d3.l)
	move.b %d0,(%a1,%d2.l)
	movem.l (%sp),#28
	lea (12,%sp),%sp
	rts
.L381:
	move.l 1187521622,%d1
	move.l %d0,%a0
	move.b 269161679,%d2
	move.l %d1,%d0
	mov3q.l #3,%d1
	add.l #585088,%d0
	lea (6199,%a0),%a0
	and.l %d1,%d2
	muls.l %d3,%d2
	moveq #127,%d3
	add.l %d2,%d0
	move.b (%a0,%d0.l),%d0
	add.l #64,%d0
	mvz.b %d0,%d2
	move.l %d2,%d0
	cmp.l %d2,%d3
	jcs .L382
.L374:
	moveq #10,%d4
	moveq #99,%d3
	remu.l %d4,%d1:%d0
	divu.l %d4,%d0
	add.l #48,%d1
	cmp.l %d2,%d3
	jcc .L375
	move.l %d0,%d2
	move.l %a1,%a0
	remu.l %d4,%d3:%d2
	move.b #49,(%a0)+
	mov3q.l #3,%d2
	move.l %d3,%d0
	add.l #48,%d0
	mov3q.l #2,%d3
	move.b %d0,(%a0)
	jra .L376
.L382:
	moveq #127,%d0
	jra .L374
.L375:
	moveq #9,%d4
	cmp.l %d2,%d4
	jcs .L383
	clr.b %d0
	clr.l %d3
	move.b %d1,(%a1,%d3.l)
	mov3q.l #1,%d2
	move.b %d0,(%a1,%d2.l)
	movem.l (%sp),#28
	lea (12,%sp),%sp
	rts
.L383:
	add.l #48,%d0
	move.l %a1,%a0
	mov3q.l #2,%d2
	move.b %d0,(%a0)
	mov3q.l #1,%d3
	jra .L376
	.size	midi_format_5, .-midi_format_5
	.align	2
	.type	midi_format_6, @function
midi_format_6:
	lea (-24,%sp),%sp
	movem.l #1084,(%sp)
	mov3q.l #3,%d3
	mvz.w #6322,%d4
	move.l 28(%sp),%a1
	moveq #22,%d5
	mvz.b 269161676,%d0
	move.l 1187521622,%a0
	add.l #585088,%a0
	move.b 269161679,%d1
	move.l %d0,%d2
	lsl.l #4,%d2
	and.l %d3,%d1
	move.l %d2,%a2
	lea (6206,%a2),%a2
	muls.l %d4,%d1
	add.l %d1,%a0
	mvz.b (%a0,%a2.l),%d1
	cmp.l %d1,%d5
	jeq .L385
	addq.l #1,%d0
.L386:
	moveq #99,%d4
	cmp.l %d0,%d4
	jcs .L392
	moveq #9,%d1
	cmp.l %d0,%d1
	jcs .L395
	moveq #10,%d5
	mov3q.l #1,%d2
	remu.l %d5,%d1:%d0
	clr.b %d0
	move.l %a1,%a0
	add.l #48,%d1
	move.b %d1,(%a0)
	move.b %d0,(%a1,%d2.l)
	movem.l (%sp),#1084
	lea (24,%sp),%sp
	rts
.L385:
	move.l 1187521622,%a2
	mov3q.l #3,%d1
	move.b 269161679,%d0
	mvz.w #6322,%d3
	move.l %d2,%a0
	add.l #585088,%a2
	lea (6200,%a0),%a0
	and.l %d1,%d0
	muls.l %d3,%d0
	add.l %d0,%a2
	move.b (%a2,%a0.l),%d1
	add.l #64,%d1
	mvz.b %d1,%d0
	tst.b %d1
	jge .L386
	moveq #127,%d0
.L392:
	moveq #100,%d5
	moveq #10,%d3
	move.l %d0,%d1
	mov3q.l #1,%a2
	divu.l %d5,%d1
	mov3q.l #2,%a0
	add.l %a1,%a0
	mov3q.l #3,%d2
	add.l #48,%d1
	move.b %d1,(%a1)
	move.l %d0,%d1
	divu.l %d3,%d1
	move.l %d1,%d5
	remu.l %d3,%d4:%d5
	move.l %d4,%d1
	add.l #48,%d1
	move.b %d1,(%a1,%a2.l)
.L396:
	moveq #10,%d5
	remu.l %d5,%d1:%d0
	clr.b %d0
	add.l #48,%d1
	move.b %d1,(%a0)
	move.b %d0,(%a1,%d2.l)
	movem.l (%sp),#1084
	lea (24,%sp),%sp
	rts
.L395:
	moveq #10,%d3
	mov3q.l #1,%a0
	move.l %d0,%d1
	sub.l %a2,%a2
	divu.l %d3,%d1
	mov3q.l #2,%d2
	add.l %a1,%a0
	move.l %d1,%d5
	remu.l %d3,%d4:%d5
	move.l %d4,%d1
	add.l #48,%d1
	move.b %d1,(%a1,%a2.l)
	jra .L396
	.size	midi_format_6, .-midi_format_6
	.align	2
	.type	midi_format_7, @function
midi_format_7:
	lea (-16,%sp),%sp
	movem.l #1052,(%sp)
	mov3q.l #3,%d2
	mvz.w #6322,%d3
	move.l 20(%sp),%a1
	moveq #22,%d4
	move.b 269161676,%d0
	move.l 1187521622,%a0
	add.l #585088,%a0
	move.b 269161679,%d1
	mvz.b %d0,%d0
	and.l %d2,%d1
	lsl.l #4,%d0
	muls.l %d3,%d1
	move.l %d0,%a2
	lea (6206,%a2),%a2
	add.l %d1,%a0
	mvz.b (%a0,%a2.l),%d1
	cmp.l %d1,%d4
	jeq .L405
	moveq #50,%d1
.L398:
	move.l %a1,%a0
	mov3q.l #2,%d0
	move.b #49,(%a0)+
	clr.b %d4
	move.b %d1,(%a0)
	move.b %d4,(%a1,%d0.l)
	movem.l (%sp),#1052
	lea (16,%sp),%sp
	rts
.L405:
	move.l 1187521622,%d1
	move.l %d0,%a0
	move.b 269161679,%d2
	move.l %d1,%d0
	mov3q.l #3,%d3
	mvz.w #6322,%d4
	add.l #585088,%d0
	lea (6201,%a0),%a0
	move.w %d2,%a2
	moveq #12,%d2
	move.l %a2,%d1
	and.l %d3,%d1
	muls.l %d4,%d1
	add.l %d1,%d0
	move.b (%a0,%d0.l),%d0
	add.l #64,%d0
	mvz.b %d0,%d0
	move.l %d0,%d1
	cmp.l %d0,%d2
	jcs .L406
	move.l %d1,%d3
	moveq #10,%d4
	remu.l %d4,%d2:%d3
	moveq #9,%d3
	move.l %d2,%d1
	add.l #48,%d1
	cmp.l %d0,%d3
	jcs .L398
.L402:
	clr.b %d4
	move.l %a1,%a0
	mov3q.l #1,%d0
	move.b %d1,(%a0)
	move.b %d4,(%a1,%d0.l)
	movem.l (%sp),#1052
	lea (16,%sp),%sp
	rts
.L406:
	moveq #12,%d1
	moveq #10,%d4
	move.l %d1,%d3
	remu.l %d4,%d2:%d3
	moveq #9,%d3
	move.l %d2,%d1
	add.l #48,%d1
	cmp.l %d0,%d3
	jcc .L402
	jra .L398
	.size	midi_format_7, .-midi_format_7
	.align	2
	.type	midi_format_9, @function
midi_format_9:
	lea (-16,%sp),%sp
	movem.l #1052,(%sp)
	mov3q.l #3,%d2
	mvz.w #6322,%d3
	move.l 20(%sp),%a1
	moveq #22,%d4
	move.b 269161676,%d0
	move.l 1187521622,%a0
	add.l #585088,%a0
	move.b 269161679,%d1
	mvz.b %d0,%d0
	and.l %d2,%d1
	lsl.l #4,%d0
	muls.l %d3,%d1
	move.l %d0,%a2
	lea (6206,%a2),%a2
	add.l %d1,%a0
	mvz.b (%a0,%a2.l),%d1
	cmp.l %d1,%d4
	jeq .L414
	moveq #48,%d1
	clr.b %d4
	move.l %a1,%a2
	mov3q.l #1,%d2
	move.b %d1,(%a2)
	move.b %d4,(%a1,%d2.l)
	movem.l (%sp),#1052
	lea (16,%sp),%sp
	rts
.L414:
	move.l 1187521622,%d1
	move.l %d0,%a0
	move.b 269161679,%d2
	move.l %d1,%d0
	mov3q.l #3,%d1
	add.l #585088,%d0
	lea (6203,%a0),%a0
	and.l %d2,%d1
	moveq #63,%d2
	muls.l %d3,%d1
	add.l %d1,%d0
	move.b (%a0,%d0.l),%d0
	add.l #64,%d0
	mvz.b %d0,%d0
	move.l %d0,%d1
	cmp.l %d0,%d2
	jcs .L415
	move.l %d1,%d3
	moveq #10,%d4
	remu.l %d4,%d2:%d3
	divu.l %d4,%d3
	move.l %a1,%a2
	move.l %d2,%d1
	move.l %d3,%a0
	add.l #48,%d1
	moveq #9,%d3
	cmp.l %d0,%d3
	jcc .L411
.L416:
	move.l %a0,%d0
	add.l #48,%d0
	move.b %d0,(%a2)+
	clr.b %d4
	mov3q.l #2,%d2
	move.b %d1,(%a2)
	move.b %d4,(%a1,%d2.l)
	movem.l (%sp),#1052
	lea (16,%sp),%sp
	rts
.L415:
	moveq #63,%d1
	moveq #10,%d4
	move.l %d1,%d3
	move.l %a1,%a2
	remu.l %d4,%d2:%d3
	divu.l %d4,%d3
	move.l %d2,%d1
	move.l %d3,%a0
	add.l #48,%d1
	moveq #9,%d3
	cmp.l %d0,%d3
	jcs .L416
.L411:
	clr.b %d4
	move.b %d1,(%a2)
	mov3q.l #1,%d2
	move.b %d4,(%a1,%d2.l)
	movem.l (%sp),#1052
	lea (16,%sp),%sp
	rts
	.size	midi_format_9, .-midi_format_9
	.align	2
	.type	midi_format_8, @function
midi_format_8:
	lea (-16,%sp),%sp
	movem.l #28,(%sp)
	mov3q.l #3,%d2
	mvz.w #6322,%d3
	move.l 20(%sp),%a1
	moveq #22,%d4
	move.b 269161676,%d0
	move.l 1187521622,%a0
	add.l #585088,%a0
	move.b 269161679,%d1
	mvz.b %d0,%d0
	and.l %d2,%d1
	lsl.l #4,%d0
	muls.l %d3,%d1
	move.l %d0,%d2
	add.l #6206,%d2
	add.l %d1,%a0
	mvz.b (%a0,%d2.l),%d1
	cmp.l %d1,%d4
	jeq .L426
	moveq #48,%d0
	clr.b %d4
	move.l %a1,%a0
	mov3q.l #1,%d1
	move.b %d0,(%a0)
	move.b %d4,(%a1,%d1.l)
	movem.l (%sp),#28
	lea (16,%sp),%sp
	rts
.L426:
	move.l 1187521622,%d1
	move.l %d0,%a0
	move.b 269161679,%d2
	move.l %d1,%d0
	mov3q.l #3,%d1
	add.l #585088,%d0
	lea (6202,%a0),%a0
	and.l %d1,%d2
	muls.l %d3,%d2
	add.l %d2,%d0
	move.b (%a0,%d0.l),%d0
	moveq #24,%d2
	add.l #64,%d0
	mvz.b %d0,%d0
	cmp.l %d0,%d2
	jcs .L427
	move.l %d0,%d2
	add.l #-12,%d2
	tst.l %d2
	jge .L422
	move.b #45,(%a1)
	moveq #12,%d2
	mov3q.l #1,%d1
	sub.l %d0,%d2
	mov3q.l #2,12(%sp)
.L420:
	move.l %d2,%d3
	moveq #10,%d4
	remu.l %d4,%d0:%d3
	lea (%a1,%d1.l),%a0
	moveq #9,%d3
	add.l #48,%d0
	cmp.l %d2,%d3
	jge .L423
	clr.b %d4
	move.b #49,(%a0)
	move.l 12(%sp),%a0
	add.l %a1,%a0
	move.b %d0,(%a0)
	addq.l #2,%d1
	move.b %d4,(%a1,%d1.l)
	movem.l (%sp),#28
	lea (16,%sp),%sp
	rts
.L427:
	moveq #12,%d2
.L422:
	mov3q.l #1,12(%sp)
	clr.l %d1
	jra .L420
.L423:
	clr.b %d4
	move.l 12(%sp),%d1
	move.b %d0,(%a0)
	move.b %d4,(%a1,%d1.l)
	movem.l (%sp),#28
	lea (16,%sp),%sp
	rts
	.size	midi_format_8, .-midi_format_8
	.align	2
	.type	midi_generate, @function
midi_generate:
	link.w %fp,#-136
	movem.l #15612,(%sp)
	move.b 269161680,%d0
	move.l 1187521622,%d1
	add.l #-1073741824,%d1
	cmp.l #133169151,%d1
	jhi .L435
	mov3q.l #7,%d1
	cmp.l 8(%fp),%d1
	jcs .L435
	mvz.b %d0,%d1
	moveq #15,%d2
	cmp.l %d1,%d2
	jcs .L435
	move.l 1187521622,%d1
	ext.w %d0
	move.b 269161679,%d3
	mvz.w #2224,%d5
	move.l 8(%fp),%d4
	mulu.w #36568,%d0
	muls.l %d5,%d4
	move.b %d3,-61(%fp)
	move.l %d1,%d3
	add.l #18640,%d3
	move.l %d4,%a0
	add.l %d0,%a0
	move.l %a0,-68(%fp)
	lea (%a0,%d3.l),%a5
	tst.l 12(%fp)
	jeq .L495
	move.l %d0,%a0
	move.l #36437,%a1
	add.l %d1,%a0
	tst.b (%a0,%a1.l)
	jeq .L438
.L497:
	move.b 40(%a5),%d2
.L439:
	pea -56(%fp)
	pea -51(%fp)
	move.l 8(%fp),-(%sp)
	jsr midi_params
	mvz.b %d2,%d2
	lea (12,%sp),%sp
	tst.l 16(%fp)
	jeq .L440
	move.l -56(%fp),%d0
	moveq #127,%d6
	addq.l #1,%d0
	and.l %d0,%d6
	move.l %d6,-56(%fp)
.L440:
	move.l 1187521622,%d0
	move.l %d2,%a0
	move.b 269161679,%d1
	subq.l #1,%a0
	moveq #63,%d4
	cmp.l %a0,%d4
	jcs .L435
	mov3q.l #3,%d5
	and.l %d5,%d1
	move.l %d0,%a2
	add.l #585088,%a2
	move.l 8(%fp),%d0
	mvz.w #6322,%d6
	lsl.l #5,%d0
	muls.l %d6,%d1
	add.l #994,%d0
	add.l %d1,%a2
	add.l %d0,%a2
	tst.b 1(%a2)
	jlt .L435
	mvz.b 1(%a2),%d0
	moveq #127,%d1
	cmp.l %d0,%d1
	jcs .L435
	move.l -56(%fp),-(%sp)
	move.l %d0,-(%sp)
	moveq #19,%d5
	move.l %d2,-(%sp)
	pea -51(%fp)
	pea phrase
	jsr (vector_generate.part.0)
	lea (20,%sp),%sp
	move.l %fp,-84(%fp)
	move.b (%a2),%d4
	mvz.b (%a2),%d0
	move.l %fp,%d1
	add.l #-40,%d1
	move.l %a5,%a0
	sub.l %d1,%a0
	move.l %a0,-60(%fp)
	move.w %d0,%d2
	move.l -60(%fp),%a1
	move.l %d1,%a0
	mvz.b %d4,%d4
	mulu.w #43691,%d2
	lsr.l %d5,%d2
	muls.w #12,%d2
	sub.l %d2,%d0
	mvz.b %d0,%d0
	sub.l %d0,%d4
	move.l %d4,-72(%fp)
.L441:
	move.b (%a1,%a0.l),%d0
	move.b %d0,(%a0)+
	cmp.l -84(%fp),%a0
	jne .L441
	move.l #268544542,%a1
	clr.l %d2
	sub.l %d3,%a1
	move.l %a1,-80(%fp)
	move.l #268544541,%a1
	sub.l %d3,%a1
	move.l %a5,%d0
	add.l #80,%d0
	lea phrase,%a0
	lea (2097,%a5),%a3
	lea (50,%a5),%a2
	lea (49,%a5),%a4
	move.l %a1,-88(%fp)
.L460:
	mov3q.l #7,%d7
	and.l %d2,%d7
	move.l %d2,%d5
	lsr.l #3,%d5
	mov3q.l #7,%a1
	mov3q.l #1,%d4
	move.l %d0,%a5
	sub.l %d5,%a1
	add.l %d1,%a1
	mvz.b (%a1),%d3
	lea (-32,%a5),%a5
	asr.l %d7,%d3
	and.l %d3,%d4
	move.l %d4,-96(%fp)
	tst.b (%a0)
	jeq .L442
	mvz.b 1(%a0),%d4
	mov3q.l #5,%d6
	add.l #-64,%d4
	move.l %d4,-76(%fp)
	divs.l %d6,%d4
	move.l -72(%fp),%d6
	add.l %d4,%d6
	tst.l %d6
	jlt .L469
	moveq #127,%d4
	cmp.l %d6,%d4
	jge .L443
	moveq #127,%d6
.L443:
	mvz.b (%a5),%d4
	move.l %d4,-76(%fp)
	mvz.b %d6,%d4
	cmp.l -76(%fp),%d4
	jeq .L465
.L464:
	move.b %d6,(%a5)
	move.l -88(%fp),%a5
	move.b %d6,(%a5,%a4.l)
	tst.b (%a0)
	jeq .L444
.L465:
	move.b 3(%a0),%d4
	mvz.b (%a4),%d3
	mvz.b %d4,%d6
	cmp.l %d6,%d3
	jeq .L445
	move.l -88(%fp),%a5
	move.b %d4,(%a4)
	move.b %d4,(%a5,%a2.l)
	tst.b (%a0)
	jne .L445
.L446:
	mvz.b (%a2),%d4
	cmp.l #255,%d4
	jeq .L496
	st %d4
.L447:
	move.l -80(%fp),%a5
	move.b %d4,(%a2)
	move.b %d4,(%a5,%a2.l)
	mov3q.l #1,%d4
	lsl.l %d7,%d4
	tst.b (%a0)
	jeq .L449
	move.b (%a1),%d6
	or.l %d4,%d6
.L450:
	move.b %d6,(%a1)
	tst.l -96(%fp)
	jne .L451
	tst.b (%a0)
	jeq .L452
.L451:
	move.l %a3,%a1
	tst.b -(%a1)
	jeq .L453
	clr.b %d3
	clr.b (%a1)
	move.l -88(%fp),%a1
	move.b %d3,(%a1,%a3.l)
.L453:
	tst.b (%a3)
	jeq .L454
	clr.b %d3
	move.l -80(%fp),%a1
	clr.b (%a3)
	move.b %d3,(%a1,%a3.l)
.L454:
	move.w #15,%a5
	move.l %d4,%d7
	not.l %d7
	move.w #39,%a1
	sub.l %d5,%a5
	move.b (%a5,%d1.l),%d3
	sub.l %d5,%a1
	and.l %d7,%d3
	move.b %d3,(%a5,%d1.l)
	move.b (%a1,%d1.l),%d3
	and.l %d7,%d3
	move.b %d3,(%a1,%d1.l)
	move.b (%a0),%d3
	jeq .L452
	lea (locked.3),%a5
	move.b %d3,(%a5,%d2.l)
	move.w #23,%a1
	sub.l %d5,%a1
	add.l %d1,%a1
	move.b (%a1),%d3
	and.l %d7,%d3
.L459:
	move.b %d3,(%a1)
	addq.l #1,%d2
	addq.l #4,%a0
	addq.l #2,%a3
	lea (32,%a2),%a2
	add.l #32,%d0
	lea (32,%a4),%a4
	moveq #64,%d3
	cmp.l %d2,%d3
	jne .L460
	move.l #268544541,%a2
	sub.l %d1,%a2
	add.l -68(%fp),%a2
	move.l %d1,%a0
	move.l -60(%fp),%d1
	subq.l #1,%d1
.L462:
	move.b (%a0)+,%d0
	mvz.b (%a0,%d1.l),%d2
	mvz.b %d0,%d3
	cmp.l %d3,%d2
	jeq .L461
	move.b %d0,(%a0,%d1.l)
	move.b %d0,(%a2,%a0.l)
.L461:
	cmp.l -84(%fp),%a0
	jne .L462
	move.l -56(%fp),-(%sp)
	pea -51(%fp)
	move.l 8(%fp),-(%sp)
	jsr midi_save
	mov3q.l #3,%d4
	mov3q.l #1,%d2
	lea (12,%sp),%sp
	move.b -61(%fp),%d0
	move.l 1187521622,%a0
	move.l %d2,%d1
	add.l #610376,%a0
	move.b (%a0),%d3
	and.l %d4,%d0
	lsl.l %d0,%d1
	or.l %d1,%d3
	move.b %d3,(%a0)
	move.l #1187500772,%d3
	move.b 269161566,%d0
	or.l %d0,%d1
	move.b %d1,269161566
	move.l 1187521622,%a0
	add.l #635698,%a0
	mov3q.l #1,(%a0)
	mov3q.l #1,269452696
	jsr 1073905152
	move.l 8(%fp),%d5
	move.l %d5,%d4
	lsl.l %d5,%d2
	lea (locked.3),%a0
	sub.l %a0,%d3
	not.l %d2
.L463:
	lea (%a0,%d3.l),%a1
	move.b (%a1),%d0
	move.b (%a0)+,%d1
	and.l %d2,%d0
	lsl.l %d4,%d1
	or.l %d1,%d0
	move.b %d0,(%a1)
	cmp.l #locked.3+64,%a0
	jne .L463
	move.l 8(%fp),%a0
	pea 8(%a0)
	jsr 1074387488
	movem.l -136(%fp),#15612
	addq.l #4,%sp
	mov3q.l #1,%d0
	unlk %fp
	rts
.L435:
	movem.l -136(%fp),#15612
	clr.l %d0
	unlk %fp
	rts
.L438:
	mvz.w #36435,%d0
	move.b (%a0,%d0.l),%d2
	jra .L439
.L495:
	lea (24,%a5),%a1
	move.l %a5,%a0
.L434:
	addq.l #1,%a0
	tst.b -1(%a0)
	jne .L435
	cmp.l %a0,%a1
	jne .L434
	lea (32,%a5),%a0
	lea (40,%a5),%a1
.L436:
	addq.l #1,%a0
	tst.b -1(%a0)
	jne .L435
	cmp.l %a0,%a1
	jne .L436
	lea (48,%a5),%a0
	lea (2096,%a5),%a1
.L437:
	mvz.b (%a0),%d2
	addq.l #1,%a0
	cmp.l #255,%d2
	jne .L435
	cmp.l %a0,%a1
	jne .L437
	move.l %d0,%a0
	move.l #36437,%a1
	add.l %d1,%a0
	tst.b (%a0,%a1.l)
	jeq .L438
	jra .L497
.L444:
	mvz.b (%a4),%d4
	cmp.l #255,%d4
	jeq .L446
	st %d4
	move.l -88(%fp),%a5
	move.b %d4,(%a4)
	move.b %d4,(%a5,%a2.l)
	tst.b (%a0)
	jeq .L446
	jra .L445
.L496:
	mov3q.l #1,%d4
	lsl.l %d7,%d4
.L449:
	move.b (%a1),%d6
	move.l %d4,%d7
	not.l %d7
	and.l %d7,%d6
	jra .L450
.L445:
	move.b 2(%a0),%d4
	mvz.b (%a2),%d3
	mvz.b %d4,%d6
	cmp.l %d3,%d6
	jne .L447
	mov3q.l #1,%d4
	lsl.l %d7,%d4
	move.b (%a1),%d6
	or.l %d4,%d6
	jra .L450
.L452:
	move.l %d0,%a1
	lea (-29,%a1),%a1
.L457:
	mvz.b (%a1),%d3
	addq.l #1,%a1
	cmp.l #255,%d3
	jne .L456
	cmp.l %d0,%a1
	jne .L457
	clr.b %d3
	lea (locked.3),%a1
	move.b %d3,(%a1,%d2.l)
.L492:
	move.w #23,%a1
	move.l %d4,%d7
	not.l %d7
	sub.l %d5,%a1
	add.l %d1,%a1
	move.b (%a1),%d3
	and.l %d7,%d3
	jra .L459
.L456:
	moveq #1,%d6
	lea (locked.3),%a1
	move.b %d6,(%a1,%d2.l)
	tst.b (%a0)
	jne .L492
	move.w #23,%a1
	sub.l %d5,%a1
	add.l %d1,%a1
	move.b (%a1),%d3
	or.l %d4,%d3
	jra .L459
.L442:
	mvz.b (%a5),%d4
	cmp.l #255,%d4
	jeq .L444
	st %d6
	move.b %d6,(%a5)
	move.l -88(%fp),%a5
	move.b %d6,(%a5,%a4.l)
	tst.b (%a0)
	jne .L465
	jra .L444
.L469:
	clr.b %d6
	mvz.b (%a5),%d4
	move.l %d4,-76(%fp)
	mvz.b %d6,%d4
	cmp.l -76(%fp),%d4
	jne .L464
	jra .L465
	.size	midi_generate, .-midi_generate
	.section	.rodata.str1.1
.LC5:
	.string	"VECTOR GENERATED"
.LC6:
	.string	"NO CHANGE"
	.text
	.align	2
	.type	vector_midi_yes, @function
vector_midi_yes:
	move.b 269161676,%d0
	mov3q.l #1,-(%sp)
	mov3q.l #1,-(%sp)
	mvz.b %d0,%d0
	move.l %d0,-(%sp)
	jsr midi_generate
	lea (12,%sp),%sp
	tst.l %d0
	jeq .L500
	move.l #.LC5,%d0
	pea 32.w
	move.l %d0,-(%sp)
	jsr 1074111160
	addq.l #8,%sp
	rts
.L500:
	move.l #.LC6,%d0
	pea 32.w
	move.l %d0,-(%sp)
	jsr 1074111160
	addq.l #8,%sp
	rts
	.size	vector_midi_yes, .-vector_midi_yes
	.align	2
	.type	vector_midi_knob, @function
vector_midi_knob:
	link.w %fp,#-44
	movem.l #1036,(%sp)
	mvz.b 269161676,%d2
	tst.l 16(%fp)
	jeq .L504
	addq.l #6,8(%fp)
.L504:
	pea -26(%fp)
	pea -22(%fp)
	move.l %d2,-(%sp)
	jsr midi_params
	lea (12,%sp),%sp
	mov3q.l #5,%d3
	move.w -14(%fp),-3(%fp)
	move.b -12(%fp),-1(%fp)
	move.l -26(%fp),-32(%fp)
	move.l -18(%fp),-7(%fp)
	move.l -22(%fp),-11(%fp)
	cmp.l 8(%fp),%d3
	jcs .L505
	lea (-22,%fp),%a0
	add.l 8(%fp),%a0
	mvz.b (%a0),%d0
	add.l 12(%fp),%d0
	tst.l %d0
	jlt .L524
	move.l 8(%fp),%d1
	lea vector_control_max,%a1
	mvz.b (%a1,%d1.l),%d1
	move.l %d1,%a1
	cmp.l %d1,%d0
	jge .L516
	move.l %d0,%a1
.L516:
	move.w %a1,%d0
	move.l 8(%fp),%d3
	move.b %d0,(%a0)
	mvz.b %d0,%d0
	mvz.b -11(%fp,%d3.l),%d1
	cmp.l %d1,%d0
	jeq .L503
.L514:
	move.l -26(%fp),-(%sp)
	pea -22(%fp)
	move.l %d2,-(%sp)
	jsr midi_save
	clr.l -(%sp)
	mov3q.l #1,-(%sp)
	move.l %d2,-(%sp)
	jsr midi_generate
	lea (24,%sp),%sp
	tst.l %d0
	jeq .L525
.L503:
	movem.l -44(%fp),#1036
	unlk %fp
	rts
.L505:
	mov3q.l #6,%d0
	cmp.l 8(%fp),%d0
	jeq .L508
	moveq #-22,%d1
	move.l 8(%fp),%a1
	add.l %fp,%d1
	subq.l #1,%a1
	add.l %a1,%d1
	move.l %d1,%a0
	mvz.b (%a0),%d0
	add.l 12(%fp),%d0
	tst.l %d0
	jlt .L526
	move.l 8(%fp),%d3
	lea vector_control_max,%a0
	mvz.b (%a0,%d3.l),%d3
	move.l %d3,%a0
	cmp.l %d3,%d0
	jlt .L527
	move.w %a0,%d0
	move.l %d1,%a2
	move.l %a1,8(%fp)
	move.b %d0,(%a2)
.L530:
	move.l 8(%fp),%d3
	mvz.b %d0,%d0
	mvz.b -11(%fp,%d3.l),%d1
	cmp.l %d1,%d0
	jne .L514
	jra .L503
.L524:
	clr.b (%a0)
	clr.b %d0
	move.l 8(%fp),%d3
	mvz.b -11(%fp,%d3.l),%d1
	mvz.b %d0,%d0
	cmp.l %d1,%d0
	jne .L514
	jra .L503
.L508:
	move.l -32(%fp),%d0
	moveq #127,%d1
	add.l 12(%fp),%d0
	cmp.l %d0,%d1
	jlt .L528
	tst.l %d0
	jlt .L529
	move.l %d0,-26(%fp)
	cmp.l -32(%fp),%d0
	jne .L514
.L523:
	movem.l -44(%fp),#1036
	unlk %fp
	rts
.L528:
	moveq #127,%d0
	move.l %d0,-26(%fp)
	cmp.l -32(%fp),%d0
	jeq .L523
	jra .L514
.L525:
	move.l -32(%fp),-(%sp)
	pea -11(%fp)
	move.l %d2,-(%sp)
	jsr midi_save
	lea (12,%sp),%sp
	movem.l -44(%fp),#1036
	unlk %fp
	rts
.L527:
	move.l %d0,%a0
	move.l %d1,%a2
	move.w %a0,%d0
	move.l %a1,8(%fp)
	move.b %d0,(%a2)
	jra .L530
.L529:
	clr.l %d0
	move.l %d0,-26(%fp)
	cmp.l -32(%fp),%d0
	jeq .L523
	jra .L514
.L526:
	clr.b (%a0)
	clr.b %d0
	move.l %a1,8(%fp)
	move.l 8(%fp),%d3
	mvz.b -11(%fp,%d3.l),%d1
	mvz.b %d0,%d0
	cmp.l %d1,%d0
	jne .L514
	jra .L503
	.size	vector_midi_knob, .-vector_midi_knob
	.align	2
	.type	vector_midi_assign.part.0, @function
vector_midi_assign.part.0:
	clr.w %d0
	link.w %fp,#-12
	move.l 8(%fp),%a0
	pea 1(%a0)
	pea -12(%fp)
	move.l %a0,-(%sp)
	move.l #137366540,%a0
	move.l %a0,-8(%fp)
	move.w %d0,-4(%fp)
	move.b %d0,-2(%fp)
	move.l #185270273,%d0
	move.l %d0,-12(%fp)
	jsr midi_save
	clr.l -(%sp)
	clr.l -(%sp)
	move.l 8(%fp),-(%sp)
	jsr midi_generate
	lea (24,%sp),%sp
	unlk %fp
	rts
	.size	vector_midi_assign.part.0, .-vector_midi_assign.part.0
	.align	2
	.type	vector_midi_assign, @function
vector_midi_assign:
	tst.l 8(%sp)
	jne .L537
	rts
.L537:
	jra (vector_midi_assign.part.0)
	.size	vector_midi_assign, .-vector_midi_assign
	.align	2
	.type	format_9, @function
format_9:
	lea (-36,%sp),%sp
	movem.l #16412,(%sp)
	move.l 40(%sp),%a6
	lea (25,%sp),%a0
	mvz.b 269161676,%d0
	move.l %d0,-(%sp)
	jsr settings
	mvz.b 37(%sp),%d0
	addq.l #4,%sp
	moveq #99,%d1
	cmp.l %d0,%d1
	jcc .L539
	moveq #100,%d2
	mov3q.l #2,%a0
	move.l %d0,%d1
	mov3q.l #3,%a1
	divu.l %d2,%d1
	moveq #10,%d2
	add.l %a6,%a0
	mov3q.l #1,16(%sp)
	add.l #48,%d1
	move.b %d1,(%a6)
	move.l %d0,%d1
	divu.l %d2,%d1
	move.l %d1,%d4
	remu.l %d2,%d3:%d4
	move.l 16(%sp),%d4
	move.l %d3,%d1
	add.l #48,%d1
	move.b %d1,(%a6,%d4.l)
.L541:
	moveq #10,%d2
	remu.l %d2,%d1:%d0
	clr.b %d3
	add.l #48,%d1
	move.b %d1,(%a0)
	move.b %d3,(%a6,%a1.l)
	movem.l (%sp),#16412
	lea (36,%sp),%sp
	rts
.L539:
	moveq #9,%d4
	cmp.l %d0,%d4
	jcs .L545
	moveq #10,%d2
	mov3q.l #1,%a1
	remu.l %d2,%d1:%d0
	clr.b %d3
	move.l %a6,%a0
	add.l #48,%d1
	move.b %d1,(%a0)
	move.b %d3,(%a6,%a1.l)
	movem.l (%sp),#16412
	lea (36,%sp),%sp
	rts
.L545:
	moveq #10,%d2
	mov3q.l #1,%a0
	move.l %d0,%d1
	mov3q.l #2,%a1
	divu.l %d2,%d1
	clr.l 16(%sp)
	add.l %a6,%a0
	move.l %d1,%d4
	remu.l %d2,%d3:%d4
	move.l 16(%sp),%d4
	move.l %d3,%d1
	add.l #48,%d1
	move.b %d1,(%a6,%d4.l)
	jra .L541
	.size	format_9, .-format_9
	.align	2
	.type	format_7, @function
format_7:
	lea (-36,%sp),%sp
	movem.l #16412,(%sp)
	move.l 40(%sp),%a6
	lea (25,%sp),%a0
	mvz.b 269161676,%d0
	move.l %d0,-(%sp)
	jsr settings
	mvz.b 35(%sp),%d0
	addq.l #4,%sp
	moveq #99,%d1
	cmp.l %d0,%d1
	jcc .L547
	moveq #100,%d2
	mov3q.l #2,%a0
	move.l %d0,%d1
	mov3q.l #3,%a1
	divu.l %d2,%d1
	moveq #10,%d2
	add.l %a6,%a0
	mov3q.l #1,16(%sp)
	add.l #48,%d1
	move.b %d1,(%a6)
	move.l %d0,%d1
	divu.l %d2,%d1
	move.l %d1,%d4
	remu.l %d2,%d3:%d4
	move.l 16(%sp),%d4
	move.l %d3,%d1
	add.l #48,%d1
	move.b %d1,(%a6,%d4.l)
.L549:
	moveq #10,%d2
	remu.l %d2,%d1:%d0
	clr.b %d3
	add.l #48,%d1
	move.b %d1,(%a0)
	move.b %d3,(%a6,%a1.l)
	movem.l (%sp),#16412
	lea (36,%sp),%sp
	rts
.L547:
	moveq #9,%d4
	cmp.l %d0,%d4
	jcs .L553
	moveq #10,%d2
	mov3q.l #1,%a1
	remu.l %d2,%d1:%d0
	clr.b %d3
	move.l %a6,%a0
	add.l #48,%d1
	move.b %d1,(%a0)
	move.b %d3,(%a6,%a1.l)
	movem.l (%sp),#16412
	lea (36,%sp),%sp
	rts
.L553:
	moveq #10,%d2
	mov3q.l #1,%a0
	move.l %d0,%d1
	mov3q.l #2,%a1
	divu.l %d2,%d1
	clr.l 16(%sp)
	add.l %a6,%a0
	move.l %d1,%d4
	remu.l %d2,%d3:%d4
	move.l 16(%sp),%d4
	move.l %d3,%d1
	add.l #48,%d1
	move.b %d1,(%a6,%d4.l)
	jra .L549
	.size	format_7, .-format_7
	.align	2
	.type	format_5, @function
format_5:
	lea (-36,%sp),%sp
	movem.l #16412,(%sp)
	move.l 40(%sp),%a6
	lea (25,%sp),%a0
	mvz.b 269161676,%d0
	move.l %d0,-(%sp)
	jsr settings
	mvz.b 34(%sp),%d0
	addq.l #4,%sp
	moveq #99,%d1
	cmp.l %d0,%d1
	jcc .L555
	moveq #100,%d2
	mov3q.l #2,%a0
	move.l %d0,%d1
	mov3q.l #3,%a1
	divu.l %d2,%d1
	moveq #10,%d2
	add.l %a6,%a0
	mov3q.l #1,16(%sp)
	add.l #48,%d1
	move.b %d1,(%a6)
	move.l %d0,%d1
	divu.l %d2,%d1
	move.l %d1,%d4
	remu.l %d2,%d3:%d4
	move.l 16(%sp),%d4
	move.l %d3,%d1
	add.l #48,%d1
	move.b %d1,(%a6,%d4.l)
.L557:
	moveq #10,%d2
	remu.l %d2,%d1:%d0
	clr.b %d3
	add.l #48,%d1
	move.b %d1,(%a0)
	move.b %d3,(%a6,%a1.l)
	movem.l (%sp),#16412
	lea (36,%sp),%sp
	rts
.L555:
	moveq #9,%d4
	cmp.l %d0,%d4
	jcs .L561
	moveq #10,%d2
	mov3q.l #1,%a1
	remu.l %d2,%d1:%d0
	clr.b %d3
	move.l %a6,%a0
	add.l #48,%d1
	move.b %d1,(%a0)
	move.b %d3,(%a6,%a1.l)
	movem.l (%sp),#16412
	lea (36,%sp),%sp
	rts
.L561:
	moveq #10,%d2
	mov3q.l #1,%a0
	move.l %d0,%d1
	mov3q.l #2,%a1
	divu.l %d2,%d1
	clr.l 16(%sp)
	add.l %a6,%a0
	move.l %d1,%d4
	remu.l %d2,%d3:%d4
	move.l 16(%sp),%d4
	move.l %d3,%d1
	add.l #48,%d1
	move.b %d1,(%a6,%d4.l)
	jra .L557
	.size	format_5, .-format_5
	.align	2
	.type	format_4, @function
format_4:
	lea (-36,%sp),%sp
	movem.l #16412,(%sp)
	move.l 40(%sp),%a6
	lea (25,%sp),%a0
	mvz.b 269161676,%d0
	move.l %d0,-(%sp)
	jsr settings
	mvz.b 33(%sp),%d0
	addq.l #4,%sp
	moveq #99,%d1
	cmp.l %d0,%d1
	jcc .L563
	moveq #100,%d2
	mov3q.l #2,%a0
	move.l %d0,%d1
	mov3q.l #3,%a1
	divu.l %d2,%d1
	moveq #10,%d2
	add.l %a6,%a0
	mov3q.l #1,16(%sp)
	add.l #48,%d1
	move.b %d1,(%a6)
	move.l %d0,%d1
	divu.l %d2,%d1
	move.l %d1,%d4
	remu.l %d2,%d3:%d4
	move.l 16(%sp),%d4
	move.l %d3,%d1
	add.l #48,%d1
	move.b %d1,(%a6,%d4.l)
.L565:
	moveq #10,%d2
	remu.l %d2,%d1:%d0
	clr.b %d3
	add.l #48,%d1
	move.b %d1,(%a0)
	move.b %d3,(%a6,%a1.l)
	movem.l (%sp),#16412
	lea (36,%sp),%sp
	rts
.L563:
	moveq #9,%d4
	cmp.l %d0,%d4
	jcs .L569
	moveq #10,%d2
	mov3q.l #1,%a1
	remu.l %d2,%d1:%d0
	clr.b %d3
	move.l %a6,%a0
	add.l #48,%d1
	move.b %d1,(%a0)
	move.b %d3,(%a6,%a1.l)
	movem.l (%sp),#16412
	lea (36,%sp),%sp
	rts
.L569:
	moveq #10,%d2
	mov3q.l #1,%a0
	move.l %d0,%d1
	mov3q.l #2,%a1
	divu.l %d2,%d1
	clr.l 16(%sp)
	add.l %a6,%a0
	move.l %d1,%d4
	remu.l %d2,%d3:%d4
	move.l 16(%sp),%d4
	move.l %d3,%d1
	add.l #48,%d1
	move.b %d1,(%a6,%d4.l)
	jra .L565
	.size	format_4, .-format_4
	.align	2
	.type	format_1, @function
format_1:
	lea (-36,%sp),%sp
	movem.l #16412,(%sp)
	move.l 40(%sp),%a6
	lea (25,%sp),%a0
	mvz.b 269161676,%d0
	move.l %d0,-(%sp)
	jsr settings
	mvz.b 30(%sp),%d0
	addq.l #4,%sp
	moveq #99,%d1
	cmp.l %d0,%d1
	jcc .L571
	moveq #100,%d2
	mov3q.l #2,%a0
	move.l %d0,%d1
	mov3q.l #3,%a1
	divu.l %d2,%d1
	moveq #10,%d2
	add.l %a6,%a0
	mov3q.l #1,16(%sp)
	add.l #48,%d1
	move.b %d1,(%a6)
	move.l %d0,%d1
	divu.l %d2,%d1
	move.l %d1,%d4
	remu.l %d2,%d3:%d4
	move.l 16(%sp),%d4
	move.l %d3,%d1
	add.l #48,%d1
	move.b %d1,(%a6,%d4.l)
.L573:
	moveq #10,%d2
	remu.l %d2,%d1:%d0
	clr.b %d3
	add.l #48,%d1
	move.b %d1,(%a0)
	move.b %d3,(%a6,%a1.l)
	movem.l (%sp),#16412
	lea (36,%sp),%sp
	rts
.L571:
	moveq #9,%d4
	cmp.l %d0,%d4
	jcs .L577
	moveq #10,%d2
	mov3q.l #1,%a1
	remu.l %d2,%d1:%d0
	clr.b %d3
	move.l %a6,%a0
	add.l #48,%d1
	move.b %d1,(%a0)
	move.b %d3,(%a6,%a1.l)
	movem.l (%sp),#16412
	lea (36,%sp),%sp
	rts
.L577:
	moveq #10,%d2
	mov3q.l #1,%a0
	move.l %d0,%d1
	mov3q.l #2,%a1
	divu.l %d2,%d1
	clr.l 16(%sp)
	add.l %a6,%a0
	move.l %d1,%d4
	remu.l %d2,%d3:%d4
	move.l 16(%sp),%d4
	move.l %d3,%d1
	add.l #48,%d1
	move.b %d1,(%a6,%d4.l)
	jra .L573
	.size	format_1, .-format_1
	.align	2
	.type	format_0, @function
format_0:
	lea (-36,%sp),%sp
	movem.l #16412,(%sp)
	move.l 40(%sp),%a6
	lea (25,%sp),%a0
	mvz.b 269161676,%d0
	move.l %d0,-(%sp)
	jsr settings
	mvz.b 29(%sp),%d0
	addq.l #4,%sp
	moveq #99,%d1
	cmp.l %d0,%d1
	jcc .L579
	moveq #100,%d2
	mov3q.l #2,%a0
	move.l %d0,%d1
	mov3q.l #3,%a1
	divu.l %d2,%d1
	moveq #10,%d2
	add.l %a6,%a0
	mov3q.l #1,16(%sp)
	add.l #48,%d1
	move.b %d1,(%a6)
	move.l %d0,%d1
	divu.l %d2,%d1
	move.l %d1,%d4
	remu.l %d2,%d3:%d4
	move.l 16(%sp),%d4
	move.l %d3,%d1
	add.l #48,%d1
	move.b %d1,(%a6,%d4.l)
.L581:
	moveq #10,%d2
	remu.l %d2,%d1:%d0
	clr.b %d3
	add.l #48,%d1
	move.b %d1,(%a0)
	move.b %d3,(%a6,%a1.l)
	movem.l (%sp),#16412
	lea (36,%sp),%sp
	rts
.L579:
	moveq #9,%d4
	cmp.l %d0,%d4
	jcs .L585
	moveq #10,%d2
	mov3q.l #1,%a1
	remu.l %d2,%d1:%d0
	clr.b %d3
	move.l %a6,%a0
	add.l #48,%d1
	move.b %d1,(%a0)
	move.b %d3,(%a6,%a1.l)
	movem.l (%sp),#16412
	lea (36,%sp),%sp
	rts
.L585:
	moveq #10,%d2
	mov3q.l #1,%a0
	move.l %d0,%d1
	mov3q.l #2,%a1
	divu.l %d2,%d1
	clr.l 16(%sp)
	add.l %a6,%a0
	move.l %d1,%d4
	remu.l %d2,%d3:%d4
	move.l 16(%sp),%d4
	move.l %d3,%d1
	add.l #48,%d1
	move.b %d1,(%a6,%d4.l)
	jra .L581
	.size	format_0, .-format_0
	.align	2
	.globl	vector_next_seed
	.type	vector_next_seed, @function
vector_next_seed:
	move.l 4(%sp),%d0
	moveq #127,%d1
	addq.l #1,%d0
	and.l %d1,%d0
	rts
	.size	vector_next_seed, .-vector_next_seed
	.align	2
	.globl	vector_pack
	.type	vector_pack, @function
vector_pack:
	move.l %d3,-(%sp)
	move.l %d2,-(%sp)
	move.l 16(%sp),%a0
	mov3q.l #4,%d2
	move.l 12(%sp),%a1
	move.b 3(%a0),%d0
	mvz.b %d0,%d1
	cmp.l %d1,%d2
	jcc .L589
	moveq #4,%d0
.L589:
	move.b (%a0),%d1
	lsl.l #4,%d0
	moveq #15,%d3
	mvz.b %d1,%d2
	cmp.l %d2,%d3
	jcc .L590
	moveq #15,%d1
.L590:
	or.l %d1,%d0
	move.b %d0,(%a1)
	move.b 10(%a0),%d0
	jeq .L591
	moveq #1,%d0
.L591:
	move.b 1(%a0),%d1
	lsl.l #5,%d0
	moveq #16,%d3
	mvz.b %d1,%d2
	cmp.l %d2,%d3
	jcc .L592
	moveq #16,%d1
.L592:
	or.l %d1,%d0
	moveq #12,%d2
	move.b %d0,1(%a1)
	move.b 6(%a0),%d0
	mvz.b %d0,%d1
	cmp.l %d1,%d2
	jcc .L593
	moveq #12,%d0
.L593:
	move.b 2(%a0),%d1
	lsl.l #4,%d0
	moveq #11,%d3
	mvz.b %d1,%d2
	cmp.l %d2,%d3
	jcc .L594
	moveq #11,%d1
.L594:
	or.l %d1,%d0
	moveq #126,%d2
	move.b %d0,2(%a1)
	move.b 4(%a0),%d0
	mvz.b %d0,%d1
	cmp.l %d1,%d2
	jcc .L595
	moveq #126,%d0
.L595:
	move.b %d0,3(%a1)
	move.b 5(%a0),%d0
	jpl .L596
	moveq #127,%d0
.L596:
	move.b %d0,4(%a1)
	moveq #24,%d3
	move.b 7(%a0),%d0
	mvz.b %d0,%d1
	cmp.l %d1,%d3
	jcc .L597
	moveq #24,%d0
.L597:
	move.b %d0,5(%a1)
	moveq #63,%d2
	move.b 8(%a0),%d0
	mvz.b %d0,%d1
	cmp.l %d1,%d2
	jcc .L598
	moveq #63,%d0
.L598:
	move.b %d0,6(%a1)
	moveq #64,%d3
	move.b 9(%a0),%d0
	mvz.b %d0,%d1
	cmp.l %d1,%d3
	jcc .L599
	moveq #64,%d0
.L599:
	moveq #127,%d1
	and.l 20(%sp),%d1
	move.b %d0,7(%a1)
	move.b %d1,8(%a1)
	move.l (%sp)+,%d2
	move.l (%sp)+,%d3
	rts
	.size	vector_pack, .-vector_pack
	.align	2
	.type	save_settings, @function
save_settings:
	lea (-40,%sp),%sp
	movem.l #23580,(%sp)
	move.l 52(%sp),-(%sp)
	move.l 52(%sp),-(%sp)
	lea (39,%sp),%a4
	move.l %a4,-(%sp)
	jsr vector_pack
	move.w 58(%sp),%d3
	sub.l %a6,%a6
	lea (12,%sp),%sp
	mulu.w #30,%d3
.L608:
	move.b (%a4)+,%d2
	mov3q.l #2,%d0
	cmp.l %a6,%d0
	jcc .L612
	move.l #269161679,%a3
	mov3q.l #3,%d4
	move.b (%a3),%d0
	move.l 1187521622,%a1
	add.l #585088,%a1
	move.b (%a3),%d1
	lea (489,%a6),%a2
	addq.l #1,%a6
	add.l %d3,%a2
	and.l %d4,%d0
	and.l %d4,%d1
	mvz.w #6322,%d4
	muls.l %d4,%d0
	muls.l %d4,%d1
	move.l %d0,%a0
	add.l #269110990,%a0
	moveq #9,%d0
	add.l %d1,%a1
	move.b %d2,(%a1,%a2.l)
	move.b %d2,(%a0,%a2.l)
	cmp.l %a6,%d0
	jne .L608
.L613:
	move.b (%a3),%d0
	move.l 1187521622,%a1
	mov3q.l #3,%d2
	move.b (%a3),%d1
	add.l #585088,%a1
	and.l %d2,%d0
	and.l %d2,%d1
	muls.l %d4,%d0
	muls.l %d4,%d1
	moveq #2,%d4
	move.l %d0,%a0
	add.l #269110990,%a0
	add.l %d1,%a1
	move.b %d4,62(%a1,%d3.l)
	move.b %d4,62(%a0,%d3.l)
	movem.l (%sp),#23580
	lea (40,%sp),%sp
	rts
.L612:
	move.l #269161679,%a3
	mov3q.l #3,%d4
	move.b (%a3),%d0
	move.l 1187521622,%a1
	add.l #585088,%a1
	move.b (%a3),%d1
	lea (63,%a6),%a2
	addq.l #1,%a6
	add.l %d3,%a2
	and.l %d4,%d0
	and.l %d4,%d1
	mvz.w #6322,%d4
	muls.l %d4,%d0
	muls.l %d4,%d1
	move.l %d0,%a0
	add.l #269110990,%a0
	moveq #9,%d0
	add.l %d1,%a1
	move.b %d2,(%a1,%a2.l)
	move.b %d2,(%a0,%a2.l)
	cmp.l %a6,%d0
	jne .L608
	jra .L613
	.size	save_settings, .-save_settings
	.align	2
	.globl	vector_unpack
	.type	vector_unpack, @function
vector_unpack:
	move.l %d2,-(%sp)
	moveq #15,%d1
	move.l 16(%sp),%a0
	mov3q.l #4,%d2
	move.l 8(%sp),%a1
	move.b (%a0),%d0
	and.l %d1,%d0
	move.b %d0,(%a1)
	mvz.b (%a0),%d0
	lsr.l #4,%d0
	move.b %d0,%d1
	cmp.l %d0,%d2
	jcc .L615
	moveq #4,%d1
.L615:
	move.b %d1,3(%a1)
	moveq #31,%d1
	moveq #16,%d2
	move.b 1(%a0),%d0
	and.l %d1,%d0
	move.b %d0,%d1
	cmp.l %d0,%d2
	jcc .L616
	moveq #16,%d1
.L616:
	move.b %d1,1(%a1)
	mov3q.l #1,%d1
	moveq #15,%d2
	mvz.b 1(%a0),%d0
	lsr.l #5,%d0
	and.l %d1,%d0
	move.b %d0,10(%a1)
	move.b 2(%a0),%d0
	and.l %d2,%d0
	moveq #11,%d2
	move.b %d0,%d1
	cmp.l %d0,%d2
	jcc .L617
	moveq #11,%d1
.L617:
	move.b %d1,2(%a1)
	moveq #12,%d2
	mvz.b 2(%a0),%d0
	lsr.l #4,%d0
	move.b %d0,%d1
	cmp.l %d0,%d2
	jcc .L618
	moveq #12,%d1
.L618:
	move.b %d1,6(%a1)
	moveq #126,%d2
	move.b 3(%a0),%d0
	mvz.b %d0,%d1
	cmp.l %d1,%d2
	jcc .L619
	moveq #126,%d0
.L619:
	move.b %d0,4(%a1)
	move.b 4(%a0),%d0
	jpl .L620
	moveq #127,%d0
.L620:
	move.b %d0,5(%a1)
	moveq #24,%d2
	move.b 5(%a0),%d0
	mvz.b %d0,%d1
	cmp.l %d1,%d2
	jcc .L621
	moveq #24,%d0
.L621:
	move.b %d0,7(%a1)
	moveq #63,%d2
	move.b 6(%a0),%d0
	mvz.b %d0,%d1
	cmp.l %d1,%d2
	jcc .L622
	moveq #63,%d0
.L622:
	move.b %d0,8(%a1)
	moveq #64,%d2
	move.b 7(%a0),%d0
	mvz.b %d0,%d1
	cmp.l %d1,%d2
	jcc .L623
	moveq #64,%d0
.L623:
	move.b %d0,9(%a1)
	moveq #127,%d1
	move.b 8(%a0),%d0
	move.l 12(%sp),%a0
	move.l (%sp)+,%d2
	and.l %d0,%d1
	move.l %d1,(%a0)
	rts
	.size	vector_unpack, .-vector_unpack
	.align	2
	.globl	vector_generate
	.type	vector_generate, @function
vector_generate:
	subq.l #4,%sp
	move.l %a2,-(%sp)
	move.l %d2,-(%sp)
	move.l 16(%sp),%d0
	move.l 20(%sp),%d1
	move.l 24(%sp),%a0
	tst.l %d0
	jeq .L628
	tst.l %d1
	jeq .L628
	lea (-1,%a0),%a2
	moveq #63,%d2
	cmp.l %a2,%d2
	jcs .L628
	moveq #127,%d2
	cmp.l 28(%sp),%d2
	jcs .L628
	move.l %a0,24(%sp)
	move.l %d1,20(%sp)
	move.l %d0,16(%sp)
	move.l (%sp)+,%d2
	move.l (%sp)+,%a2
	addq.l #4,%sp
	jra (vector_generate.part.0)
.L628:
	move.l (%sp)+,%d2
	clr.l %d0
	move.l (%sp)+,%a2
	addq.l #4,%sp
	rts
	.size	vector_generate, .-vector_generate
	.align	2
	.globl	vector_track_empty
	.type	vector_track_empty, @function
vector_track_empty:
	move.l 4(%sp),%d1
	tst.l %d1
	jeq .L638
	mvz.w #2329,%d0
	cmp.l 8(%sp),%d0
	jcc .L638
	move.l %d1,%d0
	move.l %d1,%a0
	add.l #64,%d0
.L639:
	addq.l #1,%a0
	tst.b -1(%a0)
	jne .L638
	cmp.l %a0,%d0
	jne .L639
	move.l %d1,%a0
	move.l %d1,%d0
	lea (72,%a0),%a0
	add.l #80,%d0
.L640:
	addq.l #1,%a0
	tst.b -1(%a0)
	jne .L638
	cmp.l %a0,%d0
	jne .L640
	move.l %d1,%a0
	add.l #2137,%d1
	lea (89,%a0),%a0
.L641:
	mvz.b (%a0),%d0
	addq.l #1,%a0
	cmp.l #255,%d0
	jne .L638
	cmp.l %a0,%d1
	jne .L641
	mov3q.l #1,%d0
	rts
.L638:
	clr.l %d0
	rts
	.size	vector_track_empty, .-vector_track_empty
	.align	2
	.globl	vector_write_phrase
	.type	vector_write_phrase, @function
vector_write_phrase:
	lea (-40,%sp),%sp
	movem.l #15612,(%sp)
	move.l 44(%sp),%d3
	tst.l %d3
	jeq .L648
	move.l 48(%sp),%d0
	cmp.l #2329,%d0
	jls .L648
	tst.l 52(%sp)
	jeq .L648
	move.l 52(%sp),%a0
	moveq #63,%d1
	move.b 256(%a0),%d4
	move.l %d4,%d0
	subq.l #1,%d0
	mvz.b %d0,%d0
	cmp.l %d0,%d1
	jcs .L648
	tst.l 56(%sp)
	jne .L651
	move.l 48(%sp),-(%sp)
	move.l %d3,-(%sp)
	jsr vector_track_empty
	addq.l #8,%sp
	tst.l %d0
	jeq .L647
.L651:
	mvz.b %d4,%d4
	move.l 52(%sp),%a2
	clr.l %d1
	move.l %a2,%a0
.L655:
	move.b (%a0),%d0
	mov3q.l #1,%d5
	mvz.b %d0,%d2
	cmp.l %d2,%d5
	jcs .L648
	cmp.l %d4,%d1
	jcs .L652
	tst.b %d0
	jne .L648
.L653:
	addq.l #1,%d1
	addq.l #4,%a0
	moveq #64,%d0
	cmp.l %d1,%d0
	jne .L655
.L688:
	move.l %d3,%a3
	move.l %d3,%a1
	move.l %d3,%a4
	clr.l %d5
	lea (89,%a3),%a3
	lea (121,%a1),%a1
	lea (2202,%a4),%a4
.L667:
	mov3q.l #7,%d1
	and.l %d5,%d1
	move.l %d5,%d4
	lsr.l #3,%d4
	mov3q.l #7,%a0
	mov3q.l #1,%d2
	sub.l %d4,%a0
	add.l %d3,%a0
	mvz.b (%a0),%d0
	asr.l %d1,%d0
	and.l %d2,%d0
	tst.b (%a2)
	jeq .L668
	move.b 1(%a2),%d2
.L656:
	move.b %d2,(%a3)
	tst.b (%a2)
	jeq .L669
	move.b 2(%a2),%d2
.L657:
	move.b %d2,13(%a3)
	tst.b (%a2)
	jeq .L670
	move.b 3(%a2),%d2
.L658:
	move.b %d2,15(%a3)
	mov3q.l #1,%d2
	lsl.l %d1,%d2
	move.b (%a0),%d1
	tst.b (%a2)
	jeq .L659
	or.l %d2,%d1
.L660:
	move.b %d1,(%a0)
	tst.l %d0
	jne .L661
	tst.b (%a2)
	jeq .L662
.L661:
	clr.b %d0
	clr.b (%a4)
	move.w #15,%a5
	clr.l %d1
	sub.l %d4,%d1
	add.l %d3,%d1
	sub.l %d4,%a5
	move.w #79,%a0
	move.b %d0,1(%a4)
	move.l %d2,%d0
	not.l %d0
	sub.l %d4,%a0
	move.b (%a5,%d3.l),%d7
	and.l %d0,%d7
	move.b %d7,(%a5,%d3.l)
	move.l %d1,%a5
	move.b 31(%a5),%d7
	and.l %d0,%d7
	move.b %d7,31(%a5)
	move.b (%a0,%d3.l),%d1
	and.l %d1,%d0
	move.b %d0,(%a0,%d3.l)
.L662:
	move.l %a3,%a0
	clr.l %d1
.L663:
	move.b (%a0)+,%d0
	not.l %d0
	tst.b %d0
	sne %d0
	mvs.b %d0,%d0
	neg.l %d0
	or.l %d0,%d1
	cmp.l %a1,%a0
	jne .L663
	move.w #23,%a0
	sub.l %d4,%a0
	add.l %d3,%a0
	move.b (%a0),%d0
	tst.b (%a2)
	jne .L664
	tst.l %d1
	jeq .L664
	or.l %d0,%d2
.L666:
	move.b %d2,(%a0)
	addq.l #1,%d5
	addq.l #4,%a2
	lea (32,%a3),%a3
	addq.l #2,%a4
	lea (32,%a1),%a1
	moveq #64,%d0
	cmp.l %d5,%d0
	jne .L667
	mov3q.l #1,%d0
.L647:
	movem.l (%sp),#15612
	lea (40,%sp),%sp
	rts
.L648:
	movem.l (%sp),#15612
	clr.l %d0
	lea (40,%sp),%sp
	rts
.L652:
	tst.b %d0
	jeq .L653
	move.b 1(%a0),%d0
	moveq #120,%d5
	mvz.b %d0,%d2
	subq.l #4,%d0
	mvz.b %d0,%d0
	subq.l #4,%d2
	cmp.l %d0,%d5
	jcs .L648
	mov3q.l #5,%d5
	rems.l %d5,%d0:%d2
	tst.l %d0
	jne .L648
	mvz.b 2(%a0),%d2
	moveq #126,%d5
	cmp.l %d2,%d5
	jcs .L647
	tst.b 3(%a0)
	jlt .L647
	addq.l #1,%d1
	addq.l #4,%a0
	moveq #64,%d0
	cmp.l %d1,%d0
	jne .L655
	jra .L688
.L664:
	not.l %d2
	and.l %d0,%d2
	jra .L666
.L659:
	move.l %d2,%d7
	not.l %d7
	and.l %d7,%d1
	jra .L660
.L670:
	st %d2
	jra .L658
.L669:
	st %d2
	jra .L657
.L668:
	st %d2
	jra .L656
	.size	vector_write_phrase, .-vector_write_phrase
	.align	2
	.globl	vector_signed_track
	.type	vector_signed_track, @function
vector_signed_track:
	move.l %d2,-(%sp)
	move.l 12(%sp),%d0
	mov3q.l #7,%d1
	move.l 8(%sp),%a0
	cmp.l %d0,%d1
	jcs .L692
	mvz.b 34(%a0,%d0.l),%d1
	mov3q.l #1,%d2
	cmp.l %d1,%d2
	jcs .L692
	moveq #30,%d1
	moveq #83,%d2
	muls.l %d1,%d0
	lea 60(%a0,%d0.l),%a0
	mvz.b (%a0),%d0
	cmp.l %d0,%d2
	jeq .L696
.L692:
	move.l (%sp)+,%d2
	clr.l %d0
	rts
.L696:
	mvz.b 1(%a0),%d0
	moveq #50,%d1
	cmp.l %d0,%d1
	jne .L692
	mvz.b 2(%a0),%d0
	subq.l #1,%d0
	tst.l %d0
	jeq .L693
	move.b 2(%a0),%d0
	mov3q.l #2,%d1
	move.l (%sp)+,%d2
	eor.l %d1,%d0
	tst.b %d0
	seq %d0
	mvs.b %d0,%d0
	neg.l %d0
	rts
.L693:
	move.l (%sp)+,%d2
	mov3q.l #1,%d0
	rts
	.size	vector_signed_track, .-vector_signed_track
	.align	2
	.type	generate_track, @function
generate_track:
	lea (-60,%sp),%sp
	move.l 1187521622,%d0
	add.l #-1073741824,%d0
	movem.l #17420,(%sp)
	cmp.l #133169151,%d0
	jls .L734
.L714:
	clr.l %d0
.L697:
	movem.l (%sp),#17420
	lea (60,%sp),%sp
	rts
.L734:
	move.l 1187521622,%a0
	mov3q.l #3,%d1
	move.b 269161679,%d0
	mvz.w #6322,%d2
	move.l 64(%sp),-(%sp)
	add.l #585088,%a0
	and.l %d1,%d0
	muls.l %d2,%d0
	pea (%a0,%d0.l)
	jsr vector_signed_track
	addq.l #8,%sp
	tst.l %d0
	jeq .L697
	move.b 269161680,%d0
	moveq #15,%d1
	mvz.b %d0,%d3
	move.l %d3,32(%sp)
	cmp.l %d3,%d1
	jcs .L714
	ext.w %d0
	move.l 1187521622,%d2
	lea staging,%a0
	move.w %d0,%d1
	move.l %d2,36(%sp)
	move.b 269161679,%d3
	move.w 66(%sp),%d0
	mulu.w #36568,%d1
	move.b %d3,47(%sp)
	mulu.w #2330,%d0
	add.l %d1,%d0
	add.l %d0,%d2
	move.l %d2,%a6
	sub.l %a0,%a6
	move.l %d0,28(%sp)
.L701:
	move.b (%a0,%a6.l),%d0
	move.b %d0,(%a0)+
	cmp.l #staging+2330,%a0
	jne .L701
	tst.l 68(%sp)
	jeq .L735
.L702:
	mvz.w #36437,%d0
	move.l 36(%sp),%a0
	add.l %d1,%a0
	tst.b (%a0,%d0.l)
	jeq .L703
	move.b staging+80,%d0
.L704:
	mvz.b %d0,%d0
	moveq #63,%d2
	move.l %d0,%d1
	subq.l #1,%d1
	cmp.l %d1,%d2
	jcs .L714
	move.l 64(%sp),-(%sp)
	lea (53,%sp),%a0
	move.l %d0,20(%sp)
	jsr settings
	addq.l #4,%sp
	move.l 1187521622,%d1
	add.l #585088,%d1
	move.b 269161679,%d3
	move.w 66(%sp),%d2
	move.l 16(%sp),%d0
	move.w %d3,%a1
	mulu.w #30,%d2
	move.l %d2,%a0
	mov3q.l #3,%d2
	lea (497,%a0),%a0
	move.l %a1,%d3
	and.l %d2,%d3
	mvz.w #6322,%d2
	muls.l %d2,%d3
	add.l %d3,%d1
	move.b (%a0,%d1.l),%d1
	moveq #127,%d3
	and.l %d1,%d3
	move.l %d3,40(%sp)
	tst.l 72(%sp)
	jeq .L706
	move.l %d3,%d1
	moveq #127,%d2
	addq.l #1,%d1
	and.l %d1,%d2
	move.l %d2,40(%sp)
.L706:
	move.l 1187521622,%d1
	add.l #585088,%d1
	move.b 269161679,%d3
	move.w 66(%sp),%d2
	move.w %d3,%a1
	mulu.w #24,%d2
	move.l %d2,%a0
	mov3q.l #3,%d2
	lea (291,%a0),%a0
	move.l %a1,%d3
	and.l %d2,%d3
	mvz.w #6322,%d2
	muls.l %d2,%d3
	add.l %d3,%d1
	moveq #127,%d3
	mvz.b (%a0,%d1.l),%d1
	cmp.l %d1,%d3
	jcs .L714
	move.l 40(%sp),-(%sp)
	move.l %d1,-(%sp)
	move.l %d0,-(%sp)
	pea 61(%sp)
	pea phrase
	jsr (vector_generate.part.0)
	move.l 88(%sp),-(%sp)
	pea phrase
	pea 2330.w
	pea staging
	jsr vector_write_phrase
	lea (36,%sp),%sp
	tst.l %d0
	jeq .L697
	move.l 36(%sp),%a1
	cmp.l 1187521622.l,%a1
	jne .L714
	mvz.b 269161680,%d1
	cmp.l 32(%sp),%d1
	jne .L714
	mvz.b 47(%sp),%d1
	mvz.b 269161679,%d2
	cmp.l %d1,%d2
	jne .L714
	move.l 28(%sp),%a1
	sub.l #staging-268525901,%a1
	lea staging,%a0
	move.l %a1,32(%sp)
.L709:
	lea (%a0,%a6.l),%a2
	move.b (%a0)+,%d1
	mvz.b (%a2),%d2
	move.l %a2,20(%sp)
	mvz.b %d1,%d3
	cmp.l %d2,%d3
	jeq .L708
	move.b %d1,(%a2)
	move.l 32(%sp),%a1
	lea (-1,%a0),%a2
	move.b (%a2),(%a1,%a0.l)
.L708:
	cmp.l #staging+2330,%a0
	jne .L709
	move.l 40(%sp),-(%sp)
	pea 53(%sp)
	move.l 72(%sp),-(%sp)
	move.l %d0,28(%sp)
	jsr save_settings
	mov3q.l #3,%d2
	mov3q.l #1,%a6
	move.l %a6,%d3
	move.b 59(%sp),%d1
	move.l 1187521622,%a1
	add.l #610376,%a1
	and.l %d2,%d1
	move.l %d1,56(%sp)
	move.l 56(%sp),%d2
	move.b (%a1),%d1
	lea (12,%sp),%sp
	lsl.l %d2,%d3
	or.l %d3,%d1
	move.b %d1,(%a1)
	move.b 269161566,%d1
	or.l %d3,%d1
	move.l %a6,%d3
	move.b %d1,269161566
	move.l 1187521622,%a0
	add.l #635698,%a0
	mov3q.l #1,(%a0)
	mov3q.l #1,269452696
	jsr 1073905152
	move.l #1187501196,%a6
	move.l 64(%sp),%d1
	move.l 16(%sp),%d0
	lea staging+121,%a1
	lsl.l %d1,%d3
	move.l %d3,24(%sp)
	not.l %d3
	move.b %d3,23(%sp)
.L710:
	lea (-32,%a1),%a0
.L712:
	addq.l #1,%a0
	mvz.b -1(%a0),%d1
	cmp.l #255,%d1
	jne .L715
	cmp.l %a1,%a0
	jne .L712
	sub.l %a0,%a0
.L711:
	move.b (%a6),%d1
	move.b 23(%sp),%d3
	move.l %a0,%d2
	lea (32,%a1),%a1
	and.l %d3,%d1
	or.l %d2,%d1
	move.b %d1,(%a6)+
	cmp.l #1187501260,%a6
	jne .L710
	move.l 64(%sp),-(%sp)
	move.l %d0,20(%sp)
	jsr 1074387488
	addq.l #4,%sp
	mov3q.l #1,1187497772
	movem.l (%sp),#17420
	move.l 16(%sp),%d0
	lea (60,%sp),%sp
	rts
.L735:
	pea 2330.w
	pea staging
	move.l %d1,24(%sp)
	jsr vector_track_empty
	addq.l #8,%sp
	move.l 16(%sp),%d1
	tst.l %d0
	jne .L702
	movem.l (%sp),#17420
	lea (60,%sp),%sp
	rts
.L703:
	mvz.w #36435,%d0
	move.b (%a0,%d0.l),%d0
	jra .L704
.L715:
	move.b 27(%sp),%d2
	move.w %d2,%a0
	jra .L711
	.size	generate_track, .-generate_track
	.align	2
	.type	change_control, @function
change_control:
	link.w %fp,#-32
	lea (-22,%fp),%a0
	move.l %a2,-(%sp)
	move.l %d2,-(%sp)
	mvz.b 269161676,%d1
	move.l %d1,-(%sp)
	move.l %d1,-32(%fp)
	jsr settings
	move.w -30(%fp),%d1
	addq.l #4,%sp
	move.l 1187521622,%a0
	add.l #585088,%a0
	move.w -14(%fp),-3(%fp)
	move.b -12(%fp),-1(%fp)
	move.l -18(%fp),-7(%fp)
	move.l -22(%fp),-11(%fp)
	mulu.w #30,%d1
	move.b 269161679,%d0
	move.l %d1,%a1
	mov3q.l #3,%d1
	lea (497,%a1),%a1
	and.l %d1,%d0
	mvz.w #6322,%d1
	muls.l %d1,%d0
	add.l %d0,%a0
	move.b (%a0,%a1.l),%d1
	moveq #127,%d0
	and.l %d0,%d1
	mov3q.l #5,%d0
	mvz.b %d1,%d2
	cmp.l 8(%fp),%d0
	jcs .L737
	lea (-22,%fp),%a1
	add.l 8(%fp),%a1
	move.l 12(%fp),%a0
	mvz.b (%a1),%d1
	add.l %d1,%a0
	tst.l %a0
	jlt .L757
.L740:
	move.l 8(%fp),%a2
	move.l #vector_control_max,%d0
	mvz.b (%a2,%d0.l),%d0
	cmp.l %d0,%a0
	jge .L743
	move.l %a0,%d0
.L743:
	cmp.l %d1,%d0
	jeq .L736
	move.b %d0,(%a1)
	move.l %d2,%d0
.L746:
	move.l %d0,-(%sp)
	pea -22(%fp)
	move.l -32(%fp),-(%sp)
	lea save_settings,%a0
	move.l %a0,-28(%fp)
	jsr (%a0)
	clr.l -(%sp)
	mov3q.l #1,-(%sp)
	move.l -32(%fp),-(%sp)
	jsr generate_track
	lea (24,%sp),%sp
	move.l -28(%fp),%a0
	tst.l %d0
	jeq .L758
.L747:
	mov3q.l #-1,-(%sp)
	jsr 1074059592
	mov3q.l #1,1187497772
	addq.l #4,%sp
.L736:
	move.l -40(%fp),%d2
	move.l -36(%fp),%a2
	unlk %fp
	rts
.L737:
	mov3q.l #6,%d0
	cmp.l 8(%fp),%d0
	jeq .L739
	move.l 8(%fp),%d1
	move.l 12(%fp),%a0
	lea -23(%fp,%d1.l),%a1
	mvz.b (%a1),%d1
	add.l %d1,%a0
	tst.l %a0
	jge .L740
.L757:
	tst.l %d1
	jeq .L736
	clr.b %d0
	move.b %d0,(%a1)
	move.l %d2,%d0
	jra .L746
.L758:
	move.l %d2,-(%sp)
	pea -11(%fp)
	move.l -32(%fp),-(%sp)
	jsr (%a0)
	lea (12,%sp),%sp
	mov3q.l #-1,-(%sp)
	jsr 1074059592
	mov3q.l #1,1187497772
	addq.l #4,%sp
	jra .L736
.L739:
	move.l 12(%fp),%d0
	add.l %d2,%d0
	tst.l %d0
	jlt .L744
	moveq #127,%d1
	cmp.l %d0,%d1
	jge .L745
	moveq #127,%d0
.L745:
	cmp.l %d2,%d0
	jeq .L736
	move.l %d0,-(%sp)
	pea -22(%fp)
	move.l -32(%fp),-(%sp)
	lea save_settings,%a0
	move.l %a0,-28(%fp)
	jsr (%a0)
	clr.l -(%sp)
	mov3q.l #1,-(%sp)
	move.l -32(%fp),-(%sp)
	jsr generate_track
	lea (24,%sp),%sp
	move.l -28(%fp),%a0
	tst.l %d0
	jne .L747
	jra .L758
.L744:
	tst.b %d1
	jeq .L736
	clr.l %d0
	move.l %d0,-(%sp)
	pea -22(%fp)
	move.l -32(%fp),-(%sp)
	lea save_settings,%a0
	move.l %a0,-28(%fp)
	jsr (%a0)
	clr.l -(%sp)
	mov3q.l #1,-(%sp)
	move.l -32(%fp),-(%sp)
	jsr generate_track
	lea (24,%sp),%sp
	move.l -28(%fp),%a0
	tst.l %d0
	jne .L747
	jra .L758
	.size	change_control, .-change_control
	.align	2
	.type	generator_view, @function
generator_view:
	move.l 1187521622,%d0
	add.l #-1073741824,%d0
	move.l %d2,-(%sp)
	cmp.l #133169151,%d0
	jhi .L762
	tst.b -2147483627.l
	jeq .L770
.L762:
	clr.l %d0
.L759:
	move.l (%sp)+,%d2
	rts
.L770:
	move.b 269161676,%d1
	move.l 1187521622,%a0
	mov3q.l #3,%d2
	move.b 269161679,%d0
	add.l #585088,%a0
	mvz.b %d1,%d1
	and.l %d2,%d0
	move.l %d1,-(%sp)
	mvz.w #6322,%d1
	muls.l %d1,%d0
	pea (%a0,%d0.l)
	jsr vector_signed_track
	addq.l #8,%sp
	tst.l %d0
	jeq .L762
	move.l edit_view,%d0
	tst.l %d0
	jne .L762
	tst.b 1187502296.l
	jne .L759
	tst.l 1175263034
	jne .L759
	tst.l 1175262868
	seq %d0
	move.l (%sp)+,%d2
	mvs.b %d0,%d0
	neg.l %d0
	rts
	.size	generator_view, .-generator_view
	.align	2
	.globl	vector_validate_part
	.type	vector_validate_part, @function
vector_validate_part:
	lea (-136,%sp),%sp
	clr.l %d1
	movem.l #23804,(%sp)
	move.l 140(%sp),%d2
	move.l %d2,%a4
	lea (40,%sp),%a2
	sub.l %a6,%a6
	move.l %d2,%d4
	clr.l %d3
	move.l %a2,%a3
	add.l #60,%d4
	lea (34,%a4),%a4
.L777:
	mvz.b (%a4,%d1.l),%d0
	mov3q.l #1,%d6
	cmp.l %d0,%d6
	jcs .L775
	lea (%a6,%d4.l),%a0
	moveq #83,%d7
	mvz.b (%a0),%d0
	cmp.l %d0,%d7
	jeq .L802
.L775:
	addq.l #1,%d1
	lea (30,%a6),%a6
	lea (12,%a3),%a3
	cmp.l #240,%a6
	jne .L777
	move.l %d2,-(%sp)
	move.l 148(%sp),%a0
	clr.l %d5
	jsr (%a0)
	addq.l #4,%sp
	sub.l %a0,%a0
.L782:
	btst %d5,%d3
	jne .L803
	addq.l #1,%d5
	lea (30,%a0),%a0
	lea (12,%a2),%a2
	cmp.l #240,%a0
	jne .L782
.L806:
	movem.l (%sp),#23804
	lea (136,%sp),%sp
	rts
.L802:
	mvz.b 1(%a0),%d0
	moveq #50,%d6
	cmp.l %d0,%d6
	jne .L775
	mvz.b 2(%a0),%d0
	subq.l #1,%d0
	tst.l %d0
	jeq .L773
	mvz.b 2(%a0),%d0
	subq.l #2,%d0
	tst.l %d0
	jne .L775
.L773:
	mov3q.l #1,%d0
	lsl.l %d1,%d0
	sub.l %a0,%a0
	or.l %d0,%d3
.L776:
	lea 60(%a6,%a0.l),%a1
	mov3q.l #5,%d7
	cmp.l %a0,%d7
	jcc .L774
.L804:
	move.l %a0,%d6
	mov3q.l #6,%d7
	remu.l %d7,%d0:%d6
	lea (%a6,%d0.l),%a1
	moveq #12,%d0
	lea (492,%a1),%a1
	add.l %d2,%a1
	move.b (%a1),(%a3,%a0.l)
	clr.b (%a1)
	addq.l #1,%a0
	cmp.l %a0,%d0
	jeq .L775
	lea 60(%a6,%a0.l),%a1
	mov3q.l #5,%d7
	cmp.l %a0,%d7
	jcs .L804
.L774:
	add.l %d2,%a1
	move.b (%a1),(%a3,%a0.l)
	clr.b (%a1)
	addq.l #1,%a0
	jra .L776
.L803:
	clr.l %d1
	lea (%a0,%d2.l),%a3
.L781:
	mov3q.l #5,%d4
	cmp.l %d1,%d4
	jcs .L779
.L805:
	lea (%a2,%d1.l),%a4
	mov3q.l #5,%d4
	move.l %d2,%a1
	add.l %d1,%a1
	move.b (%a4),60(%a0,%a1.l)
	addq.l #1,%d1
	cmp.l %d1,%d4
	jcc .L805
.L779:
	move.l %d1,%d6
	mov3q.l #6,%d7
	remu.l %d7,%d4:%d6
	lea (%a2,%d1.l),%a4
	addq.l #1,%d1
	lea (%a3,%d4.l),%a1
	moveq #12,%d4
	move.b (%a4),492(%a1)
	cmp.l %d1,%d4
	jne .L781
	addq.l #1,%d5
	lea (30,%a0),%a0
	lea (12,%a2),%a2
	cmp.l #240,%a0
	jne .L782
	jra .L806
	.size	vector_validate_part, .-vector_validate_part
	.align	2
	.globl	st_validate_part
	.type	st_validate_part, @function
st_validate_part:
	pea st_stock_validate
	move.l 8(%sp),-(%sp)
	jsr vector_validate_part
	addq.l #8,%sp
	rts
	.size	st_validate_part, .-st_validate_part
	.align	2
	.globl	st_selected
	.type	st_selected, @function
st_selected:
	move.l 1187521622,%d0
	add.l #-1073741824,%d0
	move.l %d2,-(%sp)
	cmp.l #133169151,%d0
	jhi .L812
	tst.b -2147483627.l
	jeq .L815
.L812:
	move.l (%sp)+,%d2
	clr.l %d0
	rts
.L815:
	move.b 269161676,%d1
	move.l 1187521622,%a0
	mov3q.l #3,%d2
	move.b 269161679,%d0
	add.l #585088,%a0
	mvz.b %d1,%d1
	and.l %d2,%d0
	move.l %d1,-(%sp)
	mvz.w #6322,%d1
	muls.l %d1,%d0
	pea (%a0,%d0.l)
	jsr vector_signed_track
	addq.l #8,%sp
	move.l (%sp)+,%d2
	rts
	.size	st_selected, .-st_selected
	.align	2
	.type	pool_context, @function
pool_context:
	move.l pool_bank,%d0
	cmp.l 1187521622.l,%d0
	jeq .L822
.L818:
	clr.l %d0
	rts
.L822:
	move.b 269161679,%d0
	mov3q.l #3,%d1
	and.l %d1,%d0
	cmp.l pool_part.l,%d0
	jne .L818
	mvz.b 269161676,%d0
	cmp.l pool_track.l,%d0
	jne .L818
	jra st_selected
	.size	pool_context, .-pool_context
	.align	2
	.globl	st_key
	.type	st_key, @function
st_key:
	lea (-20,%sp),%sp
	moveq #49,%d0
	move.l %a2,-(%sp)
	move.l %d2,-(%sp)
	move.l 32(%sp),%a1
	mov3q.l #1,%d2
	move.l 36(%sp),%a0
	cmp.l %a1,%d0
	sne %d1
	mvs.b %d1,%d1
	neg.l %d1
	cmp.l %a0,%d2
	jeq .L824
	mov3q.l #1,%d0
	lsl.l %d1,%d0
	move.l mine,%d2
	move.l %d2,20(%sp)
	and.l %d0,%d2
	tst.l %d2
	jne .L839
	tst.l %a0
	jne .L833
	mov3q.l #1,%d0
.L828:
	move.l %d1,%a2
	moveq #-3,%d2
	lea (%a2,%d1.l*2),%a2
	add.l %a2,%d0
	lea saved,%a2
	move.l (%a2,%d0.l*4),%d0
	move.l %d0,%d1
	subq.l #1,%d1
	cmp.l %d1,%d2
	jcs .L823
.L840:
	move.l %a1,32(%sp)
	move.l %a0,36(%sp)
	move.l (%sp)+,%d2
	move.l %d0,%a1
	move.l (%sp)+,%a2
	lea (20,%sp),%sp
	jmp (%a1)
.L833:
	move.l %d1,%a2
	mov3q.l #2,%d0
	lea (%a2,%d1.l*2),%a2
	moveq #-3,%d2
	add.l %a2,%d0
	lea saved,%a2
	move.l (%a2,%d0.l*4),%d0
	move.l %d0,%d1
	subq.l #1,%d1
	cmp.l %d1,%d2
	jcc .L840
.L823:
	move.l (%sp)+,%d2
	move.l (%sp)+,%a2
	lea (20,%sp),%sp
	rts
.L839:
	tst.l %a0
	jne .L823
	not.l %d0
	and.l 20(%sp),%d0
	move.l (%sp)+,%d2
	move.l (%sp)+,%a2
	move.l %d0,mine
	lea (20,%sp),%sp
	rts
.L824:
	move.l %d1,16(%sp)
	move.l %a0,8(%sp)
	move.l %a1,12(%sp)
	jsr st_selected
	move.l 16(%sp),%d1
	move.l 8(%sp),%a0
	move.l 12(%sp),%a1
	tst.l %d0
	jeq .L829
	move.b 1175456541,%d0
	btst #5,%d0
	jne .L829
	moveq #62,%d0
	cmp.l %a1,%d0
	jeq .L841
	moveq #49,%d2
	cmp.l %a1,%d2
	jne .L829
	move.l %d1,16(%sp)
	move.l %a0,8(%sp)
	move.l %a1,12(%sp)
	jsr generator_view
	move.l 16(%sp),%d1
	move.l 8(%sp),%a0
	move.l 12(%sp),%a1
	tst.l %d0
	jeq .L829
	mov3q.l #1,%d0
	or.l %d0,mine
	move.b 269161676,%d0
	mov3q.l #1,-(%sp)
	mov3q.l #1,-(%sp)
	mvz.b %d0,%d0
	move.l %d0,-(%sp)
	jsr generate_track
	lea (12,%sp),%sp
	tst.l %d0
	jeq .L832
	pea 32.w
	move.l #.LC5,%d0
	move.l %d0,-(%sp)
	jsr 1074111160
	mov3q.l #-1,-(%sp)
	jsr 1074059592
	mov3q.l #1,1187497772
	lea (12,%sp),%sp
.L842:
	move.l (%sp)+,%d2
	move.l (%sp)+,%a2
	lea (20,%sp),%sp
	rts
.L829:
	clr.l %d0
	jra .L828
.L841:
	tst.b 1187502296.l
	jne .L829
	tst.l edit_view
	seq %d0
	mov3q.l #2,%d1
	or.l %d1,mine
	mov3q.l #-1,-(%sp)
	mvs.b %d0,%d0
	neg.l %d0
	move.l %d0,edit_view
	jsr 1074059592
	addq.l #4,%sp
	move.l (%sp)+,%d2
	mov3q.l #1,1187497772
	move.l (%sp)+,%a2
	lea (20,%sp),%sp
	rts
.L832:
	pea 32.w
	move.l #.LC6,%d0
	move.l %d0,-(%sp)
	jsr 1074111160
	mov3q.l #-1,-(%sp)
	jsr 1074059592
	mov3q.l #1,1187497772
	lea (12,%sp),%sp
	jra .L842
	.size	st_key, .-st_key
	.align	2
	.type	pool_flex, @function
pool_flex:
	move.l pool_bank,%d0
	cmp.l 1187521622.l,%d0
	jeq .L850
.L843:
	rts
.L850:
	move.b 269161679,%d0
	mov3q.l #3,%d1
	and.l %d1,%d0
	cmp.l pool_part.l,%d0
	jne .L843
	mvz.b 269161676,%d0
	cmp.l pool_track.l,%d0
	jne .L843
	jsr st_selected
	tst.l %d0
	jeq .L843
	mov3q.l #1,pool_browse
	mov3q.l #1,pool_direct
	jsr st_stock_pool_open
	mov3q.l #-1,-(%sp)
	jsr 1074059592
	mov3q.l #1,1187497772
	addq.l #4,%sp
	rts
	.size	pool_flex, .-pool_flex
	.align	2
	.type	pool_static, @function
pool_static:
	move.l pool_bank,%d0
	cmp.l 1187521622.l,%d0
	jeq .L858
.L851:
	rts
.L858:
	move.b 269161679,%d0
	mov3q.l #3,%d1
	and.l %d1,%d0
	cmp.l pool_part.l,%d0
	jne .L851
	mvz.b 269161676,%d0
	cmp.l pool_track.l,%d0
	jne .L851
	jsr st_selected
	tst.l %d0
	jeq .L851
	clr.l pool_browse
	mov3q.l #1,pool_direct
	jsr st_stock_pool_open
	mov3q.l #-1,-(%sp)
	jsr 1074059592
	mov3q.l #1,1187497772
	addq.l #4,%sp
	rts
	.size	pool_static, .-pool_static
	.align	2
	.globl	st_type
	.type	st_type, @function
st_type:
	move.l 1187521622,%d0
	add.l #-1073741824,%d0
	move.l %d2,-(%sp)
	cmp.l #133169151,%d0
	jhi .L861
	move.l 1187521622,%d0
	mov3q.l #3,%d2
	move.b 269161679,%d1
	add.l #585088,%d0
	move.l 12(%sp),%a0
	lea (-34,%a0),%a0
	and.l %d2,%d1
	mvz.w #6322,%d2
	muls.l %d2,%d1
	mov3q.l #7,%d2
	add.l %d1,%d0
	move.l %a0,%d1
	sub.l %d0,%d1
	cmp.l %d1,%d2
	jcc .L868
.L861:
	move.l 8(%sp),%d0
	move.l (%sp)+,%d2
	rts
.L868:
	mov3q.l #1,%d2
	cmp.l 8(%sp),%d2
	jcs .L861
	move.l %d1,-(%sp)
	move.l %d0,-(%sp)
	jsr vector_signed_track
	addq.l #8,%sp
	tst.l %d0
	jeq .L861
	mov3q.l #5,8(%sp)
	move.l 8(%sp),%d0
	move.l (%sp)+,%d2
	rts
	.size	st_type, .-st_type
	.align	2
	.globl	st_chooser_type
	.type	st_chooser_type, @function
st_chooser_type:
	move.l %d3,-(%sp)
	move.l %d2,-(%sp)
	tst.l pool_direct
	jeq .L873
	jsr pool_context
	tst.l %d0
	jne .L883
.L873:
	move.l 1187521622,%d0
	add.l #-1073741824,%d0
	cmp.l #133169151,%d0
	jhi .L876
	move.l 1187521622,%d1
	mov3q.l #3,%d3
	move.b 269161679,%d0
	add.l #585088,%d1
	move.w %d0,%a0
	move.l 16(%sp),%d0
	add.l #-34,%d0
	move.l %a0,%d2
	and.l %d3,%d2
	mvz.w #6322,%d3
	muls.l %d3,%d2
	add.l %d2,%d1
	sub.l %d1,%d0
	mov3q.l #7,%d2
	cmp.l %d0,%d2
	jcc .L884
.L876:
	move.l 12(%sp),%d0
	move.l (%sp)+,%d2
	move.l (%sp)+,%d3
	rts
.L884:
	mov3q.l #1,%d3
	cmp.l 12(%sp),%d3
	jcs .L876
	move.l %d0,-(%sp)
	move.l %d1,-(%sp)
	jsr vector_signed_track
	addq.l #8,%sp
	tst.l %d0
	jeq .L876
	move.l (%sp)+,%d2
	mov3q.l #5,%d0
	move.l (%sp)+,%d3
	rts
.L883:
	move.l 1187521622,%d0
	mov3q.l #3,%d2
	move.b 269161679,%d1
	mvz.w #6322,%d3
	move.l pool_track,%a0
	add.l #585088,%d0
	lea (34,%a0),%a0
	and.l %d2,%d1
	muls.l %d3,%d1
	add.l %d1,%d0
	add.l %a0,%d0
	cmp.l 16(%sp),%d0
	jne .L873
	move.l (%sp)+,%d2
	move.l pool_browse,%d0
	move.l (%sp)+,%d3
	rts
	.size	st_chooser_type, .-st_chooser_type
	.align	2
	.globl	st_assign
	.type	st_assign, @function
st_assign:
	lea (-60,%sp),%sp
	move.l 1187521622,%d0
	add.l #-1073741824,%d0
	movem.l #19468,(%sp)
	cmp.l #133169151,%d0
	jhi .L886
	mov3q.l #7,%d0
	cmp.l 68(%sp),%d0
	jcs .L886
	move.l 1187521622,%d1
	move.l 64(%sp),%a0
	sub.l %d1,%a0
	move.l %a0,%a6
	add.l #-585088,%a6
	move.l %d1,36(%sp)
	mvz.w #6322,%d1
	move.l %a6,%d0
	remu.l %d1,%d2:%d0
	move.l %d2,%a0
	tst.l %d2
	jne .L886
	cmp.l #25287,%a6
	jhi .L886
	move.l 68(%sp),%d1
	mov3q.l #1,%d2
	move.l 64(%sp),%a2
	lea 34(%a2,%d1.l),%a1
	mvz.b (%a1),%d1
	cmp.l %d1,%d2
	jcc .L915
	mov3q.l #1,32(%sp)
.L887:
	move.l 68(%sp),%d1
	moveq #30,%d0
	muls.l %d0,%d1
	tst.l 72(%sp)
	jne .L888
	tst.l pool_direct
	jeq .L889
	move.l %d1,20(%sp)
	move.l %a0,24(%sp)
	jsr pool_context
	move.l 20(%sp),%d1
	move.l 24(%sp),%a0
	tst.l %d0
	jeq .L889
	move.l 1187521622,%d0
	add.l #585088,%d0
	move.b 269161679,%d2
	move.w %d2,%a1
	mov3q.l #3,%d2
	move.l %a1,%d3
	and.l %d2,%d3
	mvz.w #6322,%d2
	muls.l %d2,%d3
	add.l %d3,%d0
	cmp.l 64(%sp),%d0
	jne .L889
	move.l 68(%sp),%d3
	cmp.l pool_track.l,%d3
	jne .L889
	mov3q.l #2,72(%sp)
.L888:
	move.l 68(%sp),-(%sp)
	move.l 68(%sp),-(%sp)
	move.l %d1,28(%sp)
	move.l %a0,32(%sp)
	jsr vector_signed_track
	addq.l #8,%sp
	move.l 20(%sp),%d1
	move.l 24(%sp),%a0
	tst.l %d0
	jeq .L916
.L891:
	move.l 64(%sp),%a1
	move.l #268525902,%d0
	sub.l 36(%sp),%d0
	lea 60(%a1,%d1.l),%a0
	lea 66(%a1,%d1.l),%a1
	move.l %a1,%d1
	move.l #268526334,%a1
	sub.l 36(%sp),%a1
.L898:
	move.b (%a0),(%a0,%d0.l)
	lea (432,%a0),%a2
	move.b (%a2),(%a1,%a0.l)
	addq.l #1,%a0
	cmp.l %a0,%d1
	jne .L898
	mov3q.l #1,%d0
	cmp.l 72(%sp),%d0
	jne .L885
	mvz.w #6322,%d1
	move.l %a6,%d0
	move.l #1187521622,%a0
	move.l (%a0),pool_bank
	mov3q.l #1,pool_pending
	divu.l %d1,%d0
	move.l 68(%sp),%d1
	move.l %d1,pool_track
	move.l %d0,pool_part
.L885:
	movem.l (%sp),#19468
	move.l 32(%sp),%d0
	lea (60,%sp),%sp
	rts
.L886:
	movem.l (%sp),#19468
	mov3q.l #1,32(%sp)
	move.l 32(%sp),%d0
	lea (60,%sp),%sp
	rts
.L889:
	move.l 68(%sp),-(%sp)
	move.l 68(%sp),-(%sp)
	move.l %d1,28(%sp)
	jsr vector_signed_track
	addq.l #8,%sp
	move.l 20(%sp),%d1
	tst.l %d0
	jeq .L891
	clr.b %d3
	move.l 64(%sp),%a0
	move.l #268525902,%d0
	move.l 64(%sp),%a1
	sub.l 36(%sp),%d0
	move.b %d3,62(%a0,%d1.l)
	move.b %d3,61(%a0,%d1.l)
	move.b %d3,60(%a0,%d1.l)
	lea 60(%a1,%d1.l),%a0
	lea 66(%a1,%d1.l),%a1
	move.l %a1,%d1
	move.l #268526334,%a1
	sub.l 36(%sp),%a1
	jra .L898
.L915:
	mvz.b (%a1),%d3
	move.l %d3,32(%sp)
	jra .L887
.L916:
	move.l 68(%sp),%a1
	moveq #50,%d2
	pea 1(%a1)
	pea vector_defaults
	move.l %sp,%d0
	add.l #59,%d0
	move.l %d0,-(%sp)
	move.l %d0,40(%sp)
	move.l %d1,32(%sp)
	move.l 76(%sp),%a2
	move.l %a0,36(%sp)
	lea 60(%a2,%d1.l),%a2
	move.l %a2,52(%sp)
	jsr vector_pack
	move.b #83,(%a2)
	move.l 76(%sp),%a1
	move.l 32(%sp),%d1
	move.l %d1,%a2
	lea (63,%a2),%a2
	move.b %d2,61(%a1,%d1.l)
	moveq #2,%d2
	move.b %d2,62(%a1,%d1.l)
	move.l %d1,%a1
	lea (489,%a1),%a1
	move.l 40(%sp),%d0
	lea (12,%sp),%sp
	move.l %a1,40(%sp)
	move.l 24(%sp),%a0
	move.l %a2,44(%sp)
.L895:
	move.l 40(%sp),%a1
	mov3q.l #2,%d2
	add.l %a0,%a1
	cmp.l %a0,%d2
	jcc .L917
	move.l %d0,%a3
	addq.l #1,%a0
	move.l 64(%sp),%a2
	moveq #9,%d2
	move.b (%a3),(%a2,%a1.l)
	cmp.l %a0,%d2
	jeq .L891
	addq.l #1,%d0
	jra .L895
.L917:
	move.l 64(%sp),%a2
	move.l %d0,%a3
	move.l 44(%sp),%a1
	add.l %a0,%a1
	addq.l #1,%a0
	move.b (%a3)+,(%a2,%a1.l)
	move.l %a3,%d0
	jra .L895
	.size	st_assign, .-st_assign
	.align	2
	.globl	st_pool_choice_draw
	.type	st_pool_choice_draw, @function
st_pool_choice_draw:
	subq.l #8,%sp
	move.l 1175346736,%d0
	move.l %a3,-(%sp)
	move.l %a2,-(%sp)
	tst.l %d0
	jeq .L918
	lea pool_labels,%a3
	cmp.l 1175346732.l,%a3
	jeq .L929
	clr.l %d0
.L918:
	move.l (%sp)+,%a2
	move.l (%sp)+,%a3
	addq.l #8,%sp
	rts
.L929:
	move.l %d0,%a0
	lea (36,%a0),%a0
	move.l %a0,12(%sp)
	move.l %a0,-(%sp)
	move.l %d0,12(%sp)
	jsr 1073960572
	move.l 12(%sp),%a1
	addq.l #4,%sp
	clr.l %d0
	move.l 40(%a1),%a2
	move.l (%a3)+,-(%sp)
	mov3q.l #-1,-(%sp)
	lea (-23,%a2),%a2
	move.l %a2,-(%sp)
	mov3q.l #5,-(%sp)
	move.l 28(%sp),-(%sp)
	move.l #1074505846,-(%sp)
	move.l %d0,32(%sp)
	jsr 1073818584
	lea (24,%sp),%sp
	move.l 8(%sp),%d0
	cmp.l 1175346752.l,%d0
	jeq .L930
.L920:
	subq.l #7,%a2
	mov3q.l #1,%d1
	cmp.l %d0,%d1
	jne .L923
.L931:
	move.l (%sp)+,%a2
	mov3q.l #1,1187497772
	move.l (%sp)+,%a3
	addq.l #8,%sp
	rts
.L930:
	move.l 12(%sp),%a1
	move.l (%a1),%a0
	mov3q.l #-1,-(%sp)
	pea 5(%a2)
	pea -5(%a0)
	pea -1(%a2)
	mov3q.l #3,-(%sp)
	move.l %a1,-(%sp)
	move.l %d0,32(%sp)
	jsr 1073816148
	lea (24,%sp),%sp
	subq.l #7,%a2
	mov3q.l #1,%d1
	move.l 8(%sp),%d0
	cmp.l %d0,%d1
	jeq .L931
.L923:
	move.l (%a3)+,-(%sp)
	mov3q.l #-1,-(%sp)
	move.l %a2,-(%sp)
	mov3q.l #5,-(%sp)
	mov3q.l #1,%d0
	move.l 28(%sp),-(%sp)
	move.l #1074505846,-(%sp)
	move.l %d0,32(%sp)
	jsr 1073818584
	lea (24,%sp),%sp
	move.l 8(%sp),%d0
	cmp.l 1175346752.l,%d0
	jne .L920
	jra .L930
	.size	st_pool_choice_draw, .-st_pool_choice_draw
	.section	.rodata.str1.1
.LC7:
	.string	"\253 MACHINE:VECTOR \273"
	.text
	.align	2
	.globl	st_pool_choice_open
	.type	st_pool_choice_open, @function
st_pool_choice_open:
	jsr st_selected
	tst.l %d0
	jeq .L932
	tst.l 1175346736
	jne .L932
	tst.l 1175351520
	jne .L932
	move.l #1187521622,%a0
	mov3q.l #3,%d1
	move.l (%a0),pool_bank
	move.b 269161679,%d0
	and.l %d0,%d1
	move.l %d1,pool_part
	mvz.b 269161676,%d0
	mov3q.l #2,-(%sp)
	mov3q.l #6,-(%sp)
	move.l #1175346744,-(%sp)
	move.l %d0,pool_track
	clr.l pool_direct
	clr.l pool_pending
	jsr 1074261088
	lea (12,%sp),%sp
	move.l 1187521622,%a0
	mov3q.l #3,%d1
	move.b 269161679,%d0
	move.l pool_track,%a1
	add.l #585088,%a0
	and.l %d1,%d0
	mvz.w #6322,%d1
	muls.l %d1,%d0
	add.l %d0,%a0
	mvz.b 34(%a0,%a1.l),%d0
	move.l %d0,-(%sp)
	move.l #1175346744,-(%sp)
	jsr 1074261424
	lea (handlers.7),%a0
	move.l %a0,1175346728
	move.l #pool_labels,%d0
	move.l %d0,1175346732
	clr.l 1175346740
	move.l #1074190164,-(%sp)
	mov3q.l #1,-(%sp)
	clr.l -(%sp)
	mov3q.l #-1,-(%sp)
	pea 64.w
	pea 110.w
	jsr 1074102940
	lea (32,%sp),%sp
	move.l %d0,1175346736
	tst.l %d0
	jeq .L932
	clr.l -(%sp)
	pea .LC7
	move.l %d0,-(%sp)
	jsr 1074098360
	move.l #1074585796,-(%sp)
	jsr 1073943700
	lea (16,%sp),%sp
	jra st_pool_choice_draw
.L932:
	rts
	.size	st_pool_choice_open, .-st_pool_choice_open
	.align	2
	.globl	st_pool_choice_left
	.type	st_pool_choice_left, @function
st_pool_choice_left:
	tst.l 1175346736
	jeq .L942
	move.l #pool_labels,%d0
	cmp.l 1175346732.l,%d0
	jeq .L949
.L942:
	rts
.L949:
	jsr 1074190164
	clr.l pool_direct
	jsr st_stock_pool_open
	jmp 1074235708
	.size	st_pool_choice_left, .-st_pool_choice_left
	.align	2
	.globl	st_pool_choice_right
	.type	st_pool_choice_right, @function
st_pool_choice_right:
	subq.l #4,%sp
	tst.l 1175346736
	jeq .L950
	move.l #pool_labels,%d0
	cmp.l 1175346732.l,%d0
	jeq .L963
.L950:
	addq.l #4,%sp
	rts
.L963:
	jsr pool_context
	tst.l %d0
	jeq .L950
	move.l 1175346752,%d1
	mov3q.l #1,%d0
	cmp.l %d1,%d0
	jcs .L950
	move.l %d1,(%sp)
	jsr 1074190164
	jsr pool_context
	tst.l %d0
	jeq .L950
	move.l (%sp),pool_browse
	mov3q.l #1,pool_direct
	jsr st_stock_pool_open
	mov3q.l #-1,-(%sp)
	jsr 1074059592
	mov3q.l #1,1187497772
	addq.l #4,%sp
	addq.l #4,%sp
	rts
	.size	st_pool_choice_right, .-st_pool_choice_right
	.align	2
	.globl	st_pool_left
	.type	st_pool_left, @function
st_pool_left:
	lea (-12,%sp),%sp
	move.l 16(%sp),%d1
	move.l 20(%sp),%a0
	tst.l 1175351520
	jeq .L964
	tst.l pool_direct
	jne .L981
.L966:
	move.l %a0,20(%sp)
	move.l %d1,16(%sp)
	lea (12,%sp),%sp
	jmp 1074235708
.L981:
	move.l %d1,4(%sp)
	move.l %a0,(%sp)
	jsr pool_context
	move.l 4(%sp),%d1
	move.l (%sp),%a0
	tst.l %d0
	jeq .L966
	tst.l 1175351520
	jeq .L966
	move.l pool_browse,%d0
	move.l %d0,8(%sp)
	jsr 1074235876
	clr.l pool_direct
	jsr st_pool_choice_open
	tst.l 1175346736
	jeq .L964
	move.l #pool_labels,%d0
	cmp.l 1175346732.l,%d0
	jne .L964
	move.l 8(%sp),-(%sp)
	move.l #1175346744,-(%sp)
	jsr 1074261424
	lea (20,%sp),%sp
	jra st_pool_choice_draw
.L964:
	lea (12,%sp),%sp
	rts
	.size	st_pool_left, .-st_pool_left
	.align	2
	.globl	st_pool_right
	.type	st_pool_right, @function
st_pool_right:
	subq.l #8,%sp
	move.l 12(%sp),%d1
	move.l 16(%sp),%a0
	tst.l 1175351520
	jeq .L983
	tst.l 1175352218
	jne .L983
	mov3q.l #5,%d0
	cmp.l 1175352206.l,%d0
	jeq .L992
.L983:
	move.l %a0,16(%sp)
	move.l %d1,12(%sp)
	addq.l #8,%sp
	jmp 1074237596
.L992:
	move.l %d1,4(%sp)
	move.l %a0,(%sp)
	jsr st_selected
	move.l 4(%sp),%d1
	move.l (%sp),%a0
	tst.l %d0
	jeq .L983
	jsr 1074235876
	addq.l #8,%sp
	jra st_pool_choice_open
	.size	st_pool_right, .-st_pool_right
	.align	2
	.globl	st_draw_page
	.type	st_draw_page, @function
st_draw_page:
	subq.l #4,%sp
	jsr 1073946408
	move.l %d0,(%sp)
	jsr st_selected
	tst.l %d0
	jeq .L993
	tst.l edit_view
	jne .L993
	tst.b 1187502296.l
	jne .L993
	tst.l 1175263034
	jne .L993
	tst.l 1175262868
	jne .L993
	move.l (%sp),-(%sp)
	jsr generator_page
	move.l %d0,4(%sp)
	addq.l #4,%sp
.L993:
	move.l (%sp),%d0
	addq.l #4,%sp
	rts
	.size	st_draw_page, .-st_draw_page
	.align	2
	.globl	st_setup_page
	.type	st_setup_page, @function
st_setup_page:
	subq.l #4,%sp
	move.l %d2,-(%sp)
	move.l 1187521622,%d0
	add.l #-1073741824,%d0
	move.l 12(%sp),%d1
	cmp.l #133169151,%d0
	jhi .L1001
	tst.b -2147483627.l
	jeq .L1008
.L1001:
	move.l (%sp)+,%d2
	move.l %d1,%d0
	addq.l #4,%sp
	rts
.L1008:
	move.b 269161676,%d0
	move.l 1187521622,%a0
	add.l #585088,%a0
	mvz.b %d0,%d2
	move.b 269161679,%d0
	move.l %d2,%a1
	mov3q.l #3,%d2
	move.l %a1,-(%sp)
	and.l %d2,%d0
	mvz.w #6322,%d2
	muls.l %d2,%d0
	pea (%a0,%d0.l)
	move.l %d1,12(%sp)
	jsr vector_signed_track
	addq.l #8,%sp
	move.l 4(%sp),%d1
	tst.l %d0
	jeq .L1001
	tst.l edit_view
	jne .L1001
	mov3q.l #5,%d0
	cmp.l 1175280688.l,%d0
	jne .L1001
	move.l %d1,12(%sp)
	move.l (%sp)+,%d2
	addq.l #4,%sp
	jra generator_page
	.size	st_setup_page, .-st_setup_page
	.align	2
	.globl	st_knob
	.type	st_knob, @function
st_knob:
	lea (-12,%sp),%sp
	mov3q.l #5,%d0
	move.l %d2,-(%sp)
	move.l 20(%sp),%d1
	move.l 24(%sp),%a0
	cmp.l %d1,%d0
	jcc .L1016
.L1009:
	move.l (%sp)+,%d2
	lea (12,%sp),%sp
	rts
.L1016:
	move.l 1187521622,%d0
	add.l #-1073741824,%d0
	cmp.l #133169151,%d0
	jhi .L1009
	tst.b -2147483627.l
	jne .L1009
	move.b 269161676,%d2
	move.l 1187521622,%a1
	add.l #585088,%a1
	move.b 269161679,%d0
	mvz.b %d2,%d2
	move.l %d2,12(%sp)
	mov3q.l #3,%d2
	and.l %d2,%d0
	mvz.w #6322,%d2
	move.l 12(%sp),-(%sp)
	muls.l %d2,%d0
	pea (%a1,%d0.l)
	move.l %d1,16(%sp)
	move.l %a0,12(%sp)
	jsr vector_signed_track
	addq.l #8,%sp
	move.l 8(%sp),%d1
	tst.l %d0
	jeq .L1009
	tst.l edit_view
	jne .L1009
	tst.b 1187502296.l
	jne .L1009
	tst.l 1175263034
	jne .L1009
	tst.l 1175262868
	jne .L1009
	tst.l st_layer
	jne .L1009
	move.l 4(%sp),24(%sp)
	move.l %d1,20(%sp)
	move.l (%sp)+,%d2
	lea (12,%sp),%sp
	jra change_control
	.size	st_knob, .-st_knob
	.align	2
	.globl	st_setup_knob
	.type	st_setup_knob, @function
st_setup_knob:
	move.l %d2,-(%sp)
	mov3q.l #5,%d0
	cmp.l 8(%sp),%d0
	jcc .L1018
.L1020:
	move.l (%sp)+,%d2
	clr.l %d0
	rts
.L1018:
	move.l 1187521622,%d0
	add.l #-1073741824,%d0
	cmp.l #133169151,%d0
	jhi .L1020
	tst.b -2147483627.l
	jne .L1020
	move.b 269161676,%d1
	move.l 1187521622,%a0
	mov3q.l #3,%d2
	move.b 269161679,%d0
	add.l #585088,%a0
	mvz.b %d1,%d1
	and.l %d2,%d0
	move.l %d1,-(%sp)
	mvz.w #6322,%d1
	muls.l %d1,%d0
	pea (%a0,%d0.l)
	jsr vector_signed_track
	addq.l #8,%sp
	tst.l %d0
	jeq .L1020
	tst.l edit_view
	jne .L1020
	move.l 12(%sp),-(%sp)
	move.l 12(%sp),%a0
	pea 6(%a0)
	jsr change_control
	addq.l #8,%sp
	move.l (%sp)+,%d2
	mov3q.l #1,%d0
	rts
	.size	st_setup_knob, .-st_setup_knob
	.align	2
	.globl	mg_page
	.type	mg_page, @function
mg_page:
	link.w %fp,#-16
	move.l #mg_page_layer,%d1
	move.l 1074061804,%d0
	cmp.l mg_active.l,%d1
	jeq .L1027
.L1029:
	move.l 8(%fp),%d0
	unlk %fp
	rts
.L1027:
	cmp.l #mg_page_site,%d0
	seq %d0
	mvs.b %d0,%d0
	neg.l %d0
	move.l %d0,-(%sp)
	pea -16(%fp)
	jsr (mg_view.constprop.0)
	addq.l #8,%sp
	tst.l %d0
	jeq .L1029
	move.l %d0,%a1
	move.l 16(%a1),%a0
	tst.l %a0
	jeq .L1029
	move.l mg_second,-(%sp)
	move.l 8(%fp),-(%sp)
	jsr (%a0)
	addq.l #8,%sp
	unlk %fp
	rts
	.size	mg_page, .-mg_page
	.align	2
	.globl	mg_arp_setup
	.type	mg_arp_setup, @function
mg_arp_setup:
	move.l 1074061804,%a1
	move.l -2147483630,%d0
	move.l %d2,-(%sp)
	tst.l %d0
	jeq .L1038
	move.l 1187521622,%d0
	add.l #-1073741824,%d0
	cmp.l #133169151,%d0
	jhi .L1040
	move.l #269161676,%a0
	mov3q.l #7,%d1
	mvz.b (%a0),%d0
	cmp.l %d0,%d1
	jcs .L1040
	move.b (%a0),%d0
	move.l 1187521622,%a0
	mov3q.l #3,%d2
	move.b 269161679,%d1
	add.l #585088,%a0
	mvz.b %d0,%d0
	and.l %d2,%d1
	mvz.w #6322,%d2
	add.l #3089,%d0
	muls.l %d2,%d1
	moveq #77,%d2
	add.l %d1,%a0
	lea (%a0,%d0.l*2),%a0
	move.b 1(%a0),%d0
	mvz.b (%a0),%d1
	cmp.l %d1,%d2
	jne .L1040
	cmp.l #mg_page_site,%a1
	jne .L1040
	mvz.b %d0,%d0
	moveq #86,%d1
	cmp.l %d0,%d1
	jeq .L1042
	move.b (%a0),%d0
.L1040:
	clr.l %d0
.L1038:
	move.l (%sp)+,%d2
	rts
.L1042:
	mov3q.l #1,%d2
	eor.l %d2,mg_second
	mov3q.l #-1,-(%sp)
	jsr 1074059592
	addq.l #4,%sp
	move.l (%sp)+,%d2
	mov3q.l #1,1187497772
	mov3q.l #1,%d0
	rts
	.size	mg_arp_setup, .-mg_arp_setup
	.align	2
	.globl	mg_track_tap
	.type	mg_track_tap, @function
mg_track_tap:
	mov3q.l #7,%d0
	cmp.l 4(%sp),%d0
	jcs .L1049
	move.l #mg_page_site,%d0
	cmp.l 1074061804.l,%d0
	jeq .L1053
.L1049:
	rts
.L1053:
	tst.l 1074513600
	jne .L1049
	clr.l 4(%sp)
	jmp 1073947176
	.size	mg_track_tap, .-mg_track_tap
	.section	.rodata.str1.1
.LC8:
	.string	"VECTOR"
	.text
	.align	2
	.globl	mg_note_setup_draw
	.type	mg_note_setup_draw, @function
mg_note_setup_draw:
	lea (-12,%sp),%sp
	move.l %a2,-(%sp)
	jsr mg_stock_note_draw
	move.l 1074061804,%d0
	move.l 1074513600,%a0
	cmp.l #mg_page_site,%d0
	jne .L1054
	tst.l %a0
	jne .L1071
.L1054:
	move.l (%sp)+,%a2
	lea (12,%sp),%sp
	rts
.L1071:
	tst.l -2147483630
	jeq .L1054
	move.l 1187521622,%d0
	add.l #-1073741824,%d0
	cmp.l #133169151,%d0
	jhi .L1054
	mvz.b 269161676,%d0
	mov3q.l #7,%d1
	cmp.l %d0,%d1
	jcs .L1054
	move.l 40(%a0),%a1
	lea (36,%a0),%a0
	move.l %a1,12(%sp)
	clr.l -(%sp)
	move.l %a0,12(%sp)
	pea -10(%a1)
	pea 50.w
	mov3q.l #2,-(%sp)
	mov3q.l #3,-(%sp)
	move.l %a0,-(%sp)
	jsr 1073816148
	pea .LC3
	mov3q.l #-1,-(%sp)
	move.l 44(%sp),%a2
	lea (-20,%a2),%a2
	move.l %a2,-(%sp)
	mov3q.l #5,-(%sp)
	move.l 48(%sp),-(%sp)
	move.l #1074505846,-(%sp)
	jsr 1073818584
	lea (48,%sp),%sp
	move.l mg_cursor,%d0
	tst.l %d0
	jeq .L1058
	move.l 12(%sp),%a2
	lea (-28,%a2),%a2
.L1059:
	pea .LC8
	mov3q.l #-1,-(%sp)
	move.l %a2,-(%sp)
	mov3q.l #5,-(%sp)
	move.l 24(%sp),-(%sp)
	move.l #1074505846,-(%sp)
	jsr 1073818584
	lea (24,%sp),%sp
	move.l mg_cursor,%d0
	mov3q.l #1,%d1
	cmp.l %d0,%d1
	jne .L1057
.L1058:
	mov3q.l #-1,-(%sp)
	pea 6(%a2)
	pea 50.w
	pea -1(%a2)
	mov3q.l #3,-(%sp)
	subq.l #8,%a2
	move.l 28(%sp),-(%sp)
	move.l %d0,28(%sp)
	jsr 1073816148
	lea (24,%sp),%sp
	tst.l 4(%sp)
	jeq .L1059
.L1057:
	move.l (%sp)+,%a2
	mov3q.l #1,1187497772
	lea (12,%sp),%sp
	rts
	.size	mg_note_setup_draw, .-mg_note_setup_draw
	.align	2
	.globl	mg_key
	.type	mg_key, @function
mg_key:
	link.w %fp,#-80
	moveq #51,%d0
	movem.l #1036,(%sp)
	move.l 12(%fp),%a1
	cmp.l 8(%fp),%d0
	jeq .L1102
	moveq #32,%d1
	cmp.l 8(%fp),%d1
	jeq .L1103
	moveq #49,%d2
	cmp.l 8(%fp),%d2
	jeq .L1104
	moveq #50,%d3
	cmp.l 8(%fp),%d3
	jeq .L1105
	move.l 1074061804,%d1
	mov3q.l #1,%d0
	lea vector_midi,%a0
	move.l %a0,-16(%fp)
	cmp.l %a1,%d0
	jne .L1074
	cmp.l #mg_page_site,%d1
	seq %d0
	move.l mg_active,%a0
	moveq #16,%d2
	move.l %d2,-58(%fp)
	mvs.b %d0,%d0
	neg.l %d0
	cmp.l #mg_list_layer,%a0
	jeq .L1150
.L1079:
	cmp.l #mg_page_layer,%a0
	jeq .L1151
.L1074:
	move.l %a1,-(%sp)
	move.l 8(%fp),-(%sp)
	jsr mg_forward
	addq.l #8,%sp
.L1072:
	movem.l -80(%fp),#1036
	unlk %fp
	rts
.L1150:
	cmp.l #mg_page_site,%d1
	jne .L1079
	tst.l -2147483630
	jeq .L1079
	move.l 1187521622,%d1
	add.l #-1073741824,%d1
	cmp.l #133169151,%d1
	jhi .L1079
	mvz.b 269161676,%d1
	mov3q.l #7,%d3
	cmp.l %d1,%d3
	jcs .L1079
	moveq #49,%d1
	cmp.l 8(%fp),%d1
	jeq .L1152
	moveq #51,%d1
	cmp.l 8(%fp),%d1
	jeq .L1096
	moveq #32,%d2
	cmp.l 8(%fp),%d2
	jne .L1079
	move.l -58(%fp),%d3
	or.l %d3,mg_mine
	cmp.l mg_cursor.l,%d0
	jls .L1088
	mov3q.l #1,mg_cursor
.L1088:
	jsr mg_note_setup_draw
.L1155:
	movem.l -80(%fp),#1036
	unlk %fp
	rts
.L1151:
	move.l %d0,-(%sp)
	pea -16(%fp)
	move.l %a1,-62(%fp)
	jsr (mg_view.constprop.0)
	addq.l #8,%sp
	move.l -62(%fp),%a1
	tst.l %d0
	jeq .L1074
	moveq #49,%d2
	cmp.l 8(%fp),%d2
	jeq .L1153
	moveq #50,%d2
	cmp.l 8(%fp),%d2
	jne .L1074
	tst.l mg_second
	jeq .L1074
	move.l -58(%fp),%d3
	mov3q.l #-1,-(%sp)
	clr.l mg_second
	or.l %d3,mg_mine
	jsr 1074059592
	movem.l -80(%fp),#1036
	mov3q.l #1,1187497772
	addq.l #4,%sp
	unlk %fp
	rts
.L1102:
	mov3q.l #1,-58(%fp)
.L1073:
	mov3q.l #1,%d0
	cmp.l %a1,%d0
	jeq .L1076
	move.l mg_mine,%d0
	move.l -58(%fp),%d1
	and.l %d0,%d1
	tst.l %d1
	jne .L1154
	move.l 1074061804,%d0
	move.l #vector_midi,%d1
	move.l %a1,-(%sp)
	move.l 8(%fp),-(%sp)
	move.l %d1,-16(%fp)
	jsr mg_forward
	addq.l #8,%sp
	jra .L1072
.L1076:
	move.l 1074061804,%d1
	move.l #vector_midi,%d2
	move.l mg_active,%a0
	move.l %d2,-16(%fp)
	cmp.l #mg_page_site,%d1
	seq %d0
	mvs.b %d0,%d0
	neg.l %d0
	cmp.l #mg_list_layer,%a0
	jne .L1079
	jra .L1150
.L1154:
	tst.l %a1
	jne .L1072
	move.l -58(%fp),%d1
	not.l %d1
	and.l %d0,%d1
	movem.l -80(%fp),#1036
	move.l %d1,mg_mine
	unlk %fp
	rts
.L1103:
	mov3q.l #2,-58(%fp)
	jra .L1073
.L1153:
	move.l %d0,%a2
	move.l 24(%a2),%a0
	tst.l %a0
	jeq .L1074
	move.l -58(%fp),%d1
	or.l %d1,mg_mine
	cmp.l #vector_midi_yes,%a0
	jne .L1099
	move.b 269161676,%d0
	mov3q.l #1,-(%sp)
	mov3q.l #1,-(%sp)
	mvz.b %d0,%d0
	move.l %d0,-(%sp)
	jsr midi_generate
	lea (12,%sp),%sp
	tst.l %d0
	jeq .L1111
	pea 32.w
	move.l #.LC5,%d0
	move.l %d0,-(%sp)
	jsr 1074111160
	addq.l #8,%sp
.L1101:
	mov3q.l #-1,-(%sp)
	jsr 1074059592
	mov3q.l #1,1187497772
	addq.l #4,%sp
.L1156:
	movem.l -80(%fp),#1036
	unlk %fp
	rts
.L1104:
	mov3q.l #4,-58(%fp)
	jra .L1073
.L1105:
	moveq #8,%d3
	move.l %d3,-58(%fp)
	jra .L1073
.L1111:
	pea 32.w
	move.l #.LC6,%d0
	move.l %d0,-(%sp)
	jsr 1074111160
	addq.l #8,%sp
	jra .L1101
.L1096:
	move.l -58(%fp),%d1
	move.l mg_cursor,%d0
	or.l %d1,mg_mine
	tst.l %d0
	jeq .L1088
	subq.l #1,%d0
	move.l %d0,mg_cursor
	jsr mg_note_setup_draw
	jra .L1155
.L1099:
	jsr (%a0)
	mov3q.l #-1,-(%sp)
	jsr 1074059592
	mov3q.l #1,1187497772
	addq.l #4,%sp
	jra .L1156
.L1152:
	mov3q.l #1,-(%sp)
	pea 49.w
	move.l %d0,-62(%fp)
	jsr mg_forward
	addq.l #8,%sp
	move.l mg_cursor,%d2
	mvz.b 269161676,%d1
	move.l -62(%fp),%d0
	move.l %d2,-58(%fp)
	tst.l %d2
	jeq .L1106
	cmp.l %d2,%d0
	jcs .L1107
	move.l -16(%fp),%a0
	move.l %a0,-66(%fp)
	tst.l %a0
	jeq .L1108
	move.l 8(%a0),%d2
	move.l %d2,-58(%fp)
.L1081:
	move.l %d1,%a1
	lea (3089,%a1),%a1
	move.l %a1,%d2
	add.l %d2,%d2
	move.l 1187521622,%a0
	add.l #585088,%a0
	move.b 269161679,%d3
	move.l %d2,-50(%fp)
	mov3q.l #3,%d2
	and.l %d2,%d3
	mvz.w #6322,%d2
	muls.l %d2,%d3
	add.l %d3,%a0
	add.l -50(%fp),%a0
	move.b 1(%a0),%d3
	mvz.b (%a0),%d2
	move.b %d3,-54(%fp)
	moveq #77,%d3
	cmp.l %d2,%d3
	jne .L1083
	tst.l %d0
	jeq .L1083
	mvz.b -54(%fp),%d0
	move.l -16(%fp),%a1
	cmp.l 8(%a1),%d0
	jeq .L1084
	move.b (%a0),%d0
	tst.l -66(%fp)
	jeq .L1085
.L1086:
	move.l %d1,%a0
	add.l #-2147457426,%a0
	move.b (%a0),%d0
	mvz.b -2147483646,%d2
	mvz.b %d0,%d0
	cmp.l %d0,%d2
	jeq .L1157
	move.w %d1,%d2
	move.l %d1,%d3
	move.l #mg_arp_page,%d0
	lsl.l #5,%d3
	lea mg_arp_setup_slots,%a0
	move.l %a0,-36(%fp)
	clr.l -32(%fp)
	mulu.w #68,%d2
	move.l %d3,%a1
	sub.l #mg_arp_page-1005,%d3
	move.l %d3,-24(%fp)
	move.l %d2,%a0
	move.l #-1187473662,%d2
	sub.l %a1,%d2
	add.l #1187474924,%a0
	move.l %d2,-20(%fp)
.L1091:
	move.l 1187521622,%a1
	move.l #269161679,%a2
	move.b (%a2),-51(%fp)
	mov3q.l #3,%d3
	move.l %d0,%a2
	add.l #585088,%a1
	move.b (%a2)+,-37(%fp)
	move.b -51(%fp),%d2
	move.l %a2,%d0
	move.l -24(%fp),%a2
	add.l %d0,%a2
	move.l %a2,-42(%fp)
	and.l %d3,%d2
	mvz.w #6322,%d3
	muls.l %d3,%d2
	add.l %d2,%a1
	move.b -37(%fp),%d2
	move.b %d2,(%a1,%a2.l)
	move.l #269161679,%a2
	move.b (%a2),%d3
	move.w %d3,%a1
	mov3q.l #3,%d3
	move.l %a1,%d2
	and.l %d3,%d2
	mvz.w #6322,%d3
	muls.l %d3,%d2
	move.l -42(%fp),%d3
	move.l %d2,%a1
	add.l #269110990,%a1
	move.b -37(%fp),%d2
	move.b %d2,(%a1,%d3.l)
	mov3q.l #3,%d3
	move.l 1187521622,%a1
	add.l #585088,%a1
	move.b (%a2),-39(%fp)
	move.l -36(%fp),%a2
	move.l %a1,-28(%fp)
	addq.l #1,-36(%fp)
	move.b (%a2)+,-54(%fp)
	move.b -39(%fp),%d2
	move.l -20(%fp),%a2
	add.l %a0,%a2
	move.l %a2,-46(%fp)
	and.l %d3,%d2
	mvz.w #6322,%d3
	muls.l %d3,%d2
	move.l %d2,%a1
	move.b -54(%fp),%d2
	add.l -28(%fp),%a1
	move.b %d2,(%a1,%a2.l)
	move.b 269161679,%d3
	move.w %d3,%a1
	mov3q.l #3,%d3
	move.l %a1,%d2
	and.l %d3,%d2
	mvz.w #6322,%d3
	muls.l %d3,%d2
	move.l -46(%fp),%d3
	move.l %d2,%a1
	add.l #269110990,%a1
	move.b -54(%fp),%d2
	move.b %d2,(%a1,%d3.l)
	tst.l -32(%fp)
	jeq .L1090
	move.b -37(%fp),-32(%a0)
.L1090:
	move.b -54(%fp),(%a0)+
	cmp.l #mg_arp_page+6,%d0
	jne .L1091
	move.l %d1,%d0
	lsl.l #4,%d0
	move.l %d0,%a1
	add.l #6210,%d0
	lea (6194,%a1),%a1
	move.l %d0,-54(%fp)
.L1092:
	move.l 1187521622,%a0
	mov3q.l #3,%d3
	move.b 269161679,%d0
	mvz.w #6322,%d2
	add.l #585088,%a0
	and.l %d3,%d0
	clr.b %d3
	muls.l %d2,%d0
	mov3q.l #3,%d2
	add.l %d0,%a0
	move.b %d3,(%a0,%a1.l)
	mvz.w #6322,%d3
	move.b 269161679,%d0
	and.l %d2,%d0
	muls.l %d3,%d0
	move.l %d0,%a0
	add.l #269110990,%a0
	clr.b %d0
	move.b %d0,(%a0,%a1.l)
	addq.l #1,%a1
	cmp.l -54(%fp),%a1
	jne .L1092
	tst.l -66(%fp)
	jeq .L1110
	move.l 1187521622,%a0
	mov3q.l #3,%d2
	move.b 269161679,%d0
	move.w #77,%a1
	mvz.w #6322,%d3
	add.l #585088,%a0
	add.l -50(%fp),%a0
	and.l %d2,%d0
	move.w %a1,%d2
	muls.l %d3,%d0
	mov3q.l #3,%d3
	move.b %d2,(%a0,%d0.l)
	mvz.w #6322,%d2
	move.l -50(%fp),%a0
	move.b 269161679,%d0
	and.l %d3,%d0
	move.w %a1,%d3
	muls.l %d2,%d0
	add.l %d0,%a0
	add.l #269110990,%a0
	move.b %d3,(%a0)
	tst.l -66(%fp)
	jeq .L1158
.L1094:
	move.l 1187521622,%a0
	mov3q.l #3,%d2
	move.b 269161679,%d0
	move.l %d1,%d3
	add.l #591267,%a0
	add.l %d3,%d3
	lea (-55,%fp),%a1
	move.l #269117169,%a2
	and.l %d2,%d0
	mvz.w #6322,%d2
	add.l %d3,%a0
	add.l %d3,%a2
	mvz.w #6322,%d3
	muls.l %d2,%d0
	mov3q.l #3,%d2
	move.b (%a1),(%a0,%d0.l)
	move.b 269161679,%d0
	and.l %d2,%d0
	muls.l %d3,%d0
	move.b (%a1),(%a2,%d0.l)
	move.l %d1,-62(%fp)
	jsr mg_dirty
	move.l -62(%fp),%d1
	tst.l -66(%fp)
	jeq .L1088
	move.l -66(%fp),%a1
	move.l 12(%a1),%a0
	tst.l %a0
	jeq .L1088
	cmp.l #vector_midi_assign,%a0
	jne .L1095
	move.l %d1,-(%sp)
	jsr (vector_midi_assign.part.0)
	addq.l #4,%sp
	jsr mg_note_setup_draw
	jra .L1155
.L1083:
	tst.l -66(%fp)
	jne .L1086
.L1085:
	move.l 1187521622,%a0
	mov3q.l #3,%d2
	move.b 269161679,%d0
	mvz.w #6322,%d3
	add.l #585088,%a0
	add.l -50(%fp),%a0
	and.l %d2,%d0
	moveq #77,%d2
	muls.l %d3,%d0
	mvz.b (%a0,%d0.l),%d0
	cmp.l %d0,%d2
	jeq .L1086
	jsr mg_note_setup_draw
	jra .L1155
.L1158:
	mvz.w #255,%d0
	move.l %d0,-58(%fp)
	jra .L1094
.L1106:
	clr.l -66(%fp)
	jra .L1081
.L1107:
	clr.l -66(%fp)
	clr.l -58(%fp)
	jra .L1081
.L1157:
	move.l %d1,%a0
	add.l #-2147457418,%a0
	move.b (%a0),%d0
	move.b -2147483645,%d3
	move.w %d3,%a0
	move.l %d1,%d3
	lsl.l #5,%d3
	move.l %a0,%d2
	eor.l %d2,%d0
	move.w %d1,%d2
	lea mg_arp_setup_slots,%a0
	move.l %a0,-36(%fp)
	move.l %d3,%a1
	sub.l #mg_arp_page-1005,%d3
	move.l %d3,-24(%fp)
	tst.b %d0
	seq %d0
	mulu.w #68,%d2
	move.l %d2,%a0
	move.l #-1187473662,%d2
	sub.l %a1,%d2
	mvs.b %d0,%d0
	add.l #1187474924,%a0
	move.l %d2,-20(%fp)
	neg.l %d0
	move.l %d0,-32(%fp)
	move.l #mg_arp_page,%d0
	jra .L1091
.L1110:
	move.l 1187521622,%a0
	mov3q.l #3,%d2
	move.b 269161679,%d0
	move.w #-1,%a1
	mvz.w #6322,%d3
	add.l #585088,%a0
	add.l -50(%fp),%a0
	and.l %d2,%d0
	move.w %a1,%d2
	muls.l %d3,%d0
	mov3q.l #3,%d3
	move.b %d2,(%a0,%d0.l)
	mvz.w #6322,%d2
	move.l -50(%fp),%a0
	move.b 269161679,%d0
	and.l %d3,%d0
	move.w %a1,%d3
	muls.l %d2,%d0
	add.l %d0,%a0
	add.l #269110990,%a0
	move.b %d3,(%a0)
	tst.l -66(%fp)
	jne .L1094
	jra .L1158
.L1084:
	cmp.l -66(%fp),%a1
	jeq .L1088
	move.l 12(%a1),%a0
	tst.l %a0
	jeq .L1086
	cmp.l #vector_midi_assign,%a0
	jeq .L1086
	clr.l -(%sp)
	move.l %d1,-(%sp)
	move.l %d1,-62(%fp)
	jsr (%a0)
	addq.l #8,%sp
	move.l -62(%fp),%d1
	jra .L1086
.L1095:
	mov3q.l #1,-(%sp)
	move.l %d1,-(%sp)
	jsr (%a0)
	addq.l #8,%sp
	jsr mg_note_setup_draw
	jra .L1155
.L1108:
	clr.l -58(%fp)
	jra .L1081
	.size	mg_key, .-mg_key
	.align	2
	.globl	mg_knob
	.type	mg_knob, @function
mg_knob:
	link.w %fp,#-16
	mov3q.l #5,%d1
	move.l 1074061804,%d0
	cmp.l 8(%fp),%d1
	jcs .L1159
	lea mg_page_layer,%a1
	cmp.l mg_active.l,%a1
	jeq .L1171
.L1159:
	unlk %fp
	rts
.L1171:
	cmp.l #mg_page_site,%d0
	seq %d0
	mvs.b %d0,%d0
	neg.l %d0
	move.l %d0,-(%sp)
	pea -16(%fp)
	jsr (mg_view.constprop.0)
	addq.l #8,%sp
	tst.l %d0
	jeq .L1159
	move.l %d0,%a1
	move.l 20(%a1),%a0
	tst.l %a0
	jeq .L1159
	move.l mg_second,%d0
	cmp.l #vector_midi_knob,%a0
	jne .L1161
	move.l %d0,-(%sp)
	move.l 12(%fp),-(%sp)
	move.l 8(%fp),-(%sp)
	jsr (%a0)
	lea (12,%sp),%sp
	mov3q.l #-1,-(%sp)
	jsr 1074059592
	mov3q.l #1,1187497772
	addq.l #4,%sp
.L1172:
	unlk %fp
	rts
.L1161:
	move.l %d0,-(%sp)
	move.l 12(%fp),-(%sp)
	move.l 8(%fp),-(%sp)
	jsr (%a0)
	lea (12,%sp),%sp
	mov3q.l #-1,-(%sp)
	jsr 1074059592
	mov3q.l #1,1187497772
	addq.l #4,%sp
	jra .L1172
	.size	mg_knob, .-mg_knob
	.align	2
	.globl	mg_tick
	.type	mg_tick, @function
mg_tick:
	lea (-28,%sp),%sp
	movem.l #7180,(%sp)
	move.l 1074061804,%a1
	move.l #1187521622,%a0
	move.l (%a0),%a2
	moveq #28,%d3
	move.l mg_seen,%d1
	cmp.l #mg_page_site,%a1
	seq %d0
	move.b -2147483645,%d2
	mvs.b %d0,%d0
	neg.l %d0
	lsl.l %d3,%d2
	eor.l %d2,%d0
	move.l %a2,%d2
	eor.l %d2,%d0
	cmp.l #mg_page_site,%a1
	jne .L1174
	eor.l #vector_midi,%d0
	cmp.l %d0,%d1
	jeq .L1175
	move.l %d0,mg_seen
	move.l (%a0),%d0
	add.l #-1073741824,%d0
	cmp.l #133169151,%d0
	jhi .L1175
	move.l (%a0),%a4
	mov3q.l #3,%d3
	mvz.w #6322,%d2
	move.b 269161679,%d0
	move.w #1008,%a2
	add.l #585088,%a4
	move.l #1187474894,%a3
	move.l #-2147457418,%d1
	and.l %d3,%d0
	muls.l %d2,%d0
	add.l %d0,%a4
	lea (6179,%a4),%a1
.L1179:
	move.b (%a1),%d0
	move.l %a1,%a0
	moveq #77,%d3
	mvz.b -(%a0),%d2
	cmp.l %d2,%d3
	jne .L1176
	mvz.b %d0,%d0
	moveq #86,%d2
	cmp.l %d0,%d2
	jeq .L1177
	move.b (%a0),%d0
.L1176:
	addq.l #2,%a1
	addq.l #1,%d1
	lea (68,%a3),%a3
	lea (32,%a2),%a2
	cmp.l #-2147457410,%d1
	jne .L1179
.L1175:
	tst.l -2147483630
	jeq .L1180
	move.l #1187521622,%a0
	move.l (%a0),%d0
	add.l #-1073741824,%d0
	cmp.l #133169151,%d0
	jhi .L1180
	mvz.b 269161676,%d2
	move.l (%a0),%d1
	mov3q.l #7,%d3
	move.b 269161679,%d0
	cmp.l %d2,%d3
	jcs .L1184
	mov3q.l #3,%d3
	and.l %d3,%d0
	mvz.w #6322,%d3
	move.l 1074513600,%a1
	add.l #585088,%d1
	muls.l %d3,%d0
	move.l %d0,%a2
	add.l %d1,%a2
	tst.l %a1
	jne .L1185
	clr.l mg_opened
.L1186:
	move.l mg_shown,%d1
	mov3q.l #2,%d0
	cmp.l 1175262852.l,%d0
	jne .L1194
	tst.l 1175263034
	jne .L1194
	tst.l 1175262868
	jne .L1194
	move.l %d2,%a0
	lea (3089,%a0),%a0
	lea (%a2,%a0.l*2),%a0
	move.b 1(%a0),%d0
	mvz.b (%a0),%d3
	move.l %d3,%a2
	moveq #77,%d3
	cmp.l %a2,%d3
	jne .L1194
	mvz.b %d0,%d0
	moveq #86,%d3
	cmp.l %d0,%d3
	jeq .L1199
	move.b (%a0),%d0
.L1194:
	clr.l mg_second
	move.l %d2,mg_shown
	tst.l %a1
	jne .L1195
.L1192:
	move.l mg_active,%d0
	tst.l %d0
	jeq .L1173
	tst.l mg_mine
	jne .L1173
	cmp.l #mg_page_layer,%d0
	seq %d2
	move.l %d0,-(%sp)
	jsr 1073943660
	clr.l mg_active
	move.l 1175262812,%a0
	addq.l #4,%sp
	neg.l %d2
.L1224:
	clr.b %d0
.L1210:
	mvz.b %d0,%d0
	mvz.b %d2,%d2
	cmp.l %d0,%d2
	jeq .L1173
	mov3q.l #-1,-(%sp)
	jsr 1074059592
	mov3q.l #1,1187497772
	addq.l #4,%sp
.L1173:
	movem.l (%sp),#7180
	lea (28,%sp),%sp
	rts
.L1177:
	tst.b (%a4,%a2.l)
	jeq .L1176
	move.l 1187521622,%a0
	mov3q.l #3,%d3
	move.b 269161679,%d0
	mvz.w #6322,%d2
	add.l #585088,%a0
	and.l %d3,%d0
	clr.b %d3
	muls.l %d2,%d0
	mov3q.l #3,%d2
	add.l %d0,%a0
	move.b %d3,(%a0,%a2.l)
	mvz.w #6322,%d3
	move.b 269161679,%d0
	and.l %d2,%d0
	muls.l %d3,%d0
	move.l %d0,%a0
	add.l #269110990,%a0
	clr.b %d0
	move.b %d0,(%a0,%a2.l)
	move.l %d1,%a0
	move.b -8(%a0),%d0
	mvz.b -2147483646,%d2
	mvz.b %d0,%d0
	cmp.l %d0,%d2
	jeq .L1287
.L1178:
	move.l %d1,20(%sp)
	move.l %a1,24(%sp)
	jsr mg_dirty
	move.l 24(%sp),%a1
	move.l 20(%sp),%d1
.L1289:
	addq.l #2,%a1
	addq.l #1,%d1
	lea (68,%a3),%a3
	lea (32,%a2),%a2
	cmp.l #-2147457410,%d1
	jne .L1179
	jra .L1175
.L1174:
	cmp.l %d0,%d1
	jeq .L1180
	move.l %d0,mg_seen
.L1180:
	tst.l mg_active
	jeq .L1288
	mvz.b 269161676,%d2
	move.l 1187521622,%d0
	move.b 269161679,%d0
.L1184:
	clr.l mg_opened
	cmp.l mg_shown.l,%d2
	jeq .L1191
	clr.l mg_second
	move.l %d2,mg_shown
	jra .L1192
.L1287:
	move.b (%a0),%d0
	mvz.b -2147483645,%d2
	mvz.b %d0,%d0
	cmp.l %d0,%d2
	jne .L1178
	clr.b (%a3)
	move.l %d1,20(%sp)
	move.l %a1,24(%sp)
	jsr mg_dirty
	move.l 24(%sp),%a1
	move.l 20(%sp),%d1
	jra .L1289
.L1200:
	tst.l %a1
	jeq .L1222
.L1195:
	lea mg_list_layer,%a3
.L1201:
	move.l mg_active,%d0
	cmp.l %d0,%a3
	jne .L1290
	tst.l (%a3)
	jeq .L1173
	tst.l mg_mine
	jne .L1173
	cmp.l #mg_page_layer,%a3
	seq %d2
	move.l %a3,-(%sp)
	jsr 1073943660
	clr.l mg_active
	move.l 1175262812,%a0
	addq.l #4,%sp
	neg.l %d2
	cmp.l #mg_list_layer,%a3
	jeq .L1202
.L1203:
	tst.l %a0
	jeq .L1224
	tst.l (%a0)
	jne .L1224
	lea mg_keys,%a4
	lea mg_saved,%a2
.L1214:
	mvz.b (%a4)+,%d0
	sub.l %a0,%a0
	mulu.w #24,%d0
	move.l %d0,%a1
	add.l #1187502302,%a1
.L1213:
	move.l (%a1,%a0.l),%d0
	cmp.l #mg_key,%d0
	jeq .L1212
	move.l %d0,(%a2,%a0.l)
.L1212:
	addq.l #4,%a0
	moveq #12,%d0
	cmp.l %a0,%d0
	jne .L1213
	lea (12,%a2),%a2
	cmp.l #mg_saved+48,%a2
	jne .L1214
	clr.l (%a3)
	move.l %a3,-(%sp)
	jsr 1073943700
	cmp.l #mg_page_layer,%a3
	seq %d0
	move.l %a3,mg_active
	addq.l #4,%sp
	neg.l %d0
	jra .L1210
.L1202:
	tst.l 1074513572
	jne .L1224
	lea mg_list_layer,%a3
	lea mg_keys,%a4
	lea mg_saved,%a2
	jra .L1214
.L1288:
	movem.l (%sp),#7180
	clr.l mg_opened
	clr.l mg_second
	lea (28,%sp),%sp
	rts
.L1290:
	tst.l mg_mine
	jne .L1173
	tst.l %d0
	jne .L1205
	move.l 1175262812,%a0
	cmp.l #mg_list_layer,%a3
	jeq .L1206
	tst.l %a0
	jeq .L1173
	tst.l (%a0)
	jne .L1173
	clr.b %d2
.L1292:
	lea mg_keys,%a4
	lea mg_saved,%a2
	jra .L1214
.L1185:
	move.l mg_opened,%d1
	tst.l %d1
	jeq .L1291
	mov3q.l #1,%a1
	jra .L1186
.L1191:
	clr.l mg_second
	jra .L1192
.L1291:
	move.l %d2,%a0
	lea (3089,%a0),%a0
	lea (%a2,%a0.l*2),%a0
	mov3q.l #1,mg_opened
	move.b 1(%a0),%d0
	mvz.b (%a0),%d3
	move.l %d3,%a1
	moveq #77,%d3
	cmp.l %a1,%d3
	jne .L1189
	mvz.b %d0,%d0
	moveq #86,%d3
	cmp.l %d0,%d3
	jeq .L1220
	move.b (%a0),%d0
.L1189:
	move.l %d1,mg_cursor
	jsr mg_note_setup_draw
.L1293:
	mov3q.l #1,%a1
	jra .L1186
.L1206:
	tst.l 1074513572
	jne .L1173
	clr.b %d2
	jra .L1292
.L1205:
	cmp.l #mg_page_layer,%d0
	seq %d2
	move.l %d0,-(%sp)
	jsr 1073943660
	clr.l mg_active
	move.l 1175262812,%a0
	addq.l #4,%sp
	neg.l %d2
	cmp.l #mg_list_layer,%a3
	jeq .L1202
	tst.l %a3
	jne .L1203
	clr.b %d0
	jra .L1210
.L1220:
	mov3q.l #1,%d1
	move.l %d1,mg_cursor
	jsr mg_note_setup_draw
	jra .L1293
.L1199:
	cmp.l %d2,%d1
	jeq .L1200
	clr.l mg_second
	move.l %d2,mg_shown
	tst.l %a1
	jne .L1195
.L1222:
	lea mg_page_layer,%a3
	jra .L1201
	.size	mg_tick, .-mg_tick
	.align	2
	.globl	st_ui_tick
	.type	st_ui_tick, @function
st_ui_tick:
	lea (-64,%sp),%sp
	movem.l #19580,(%sp)
	jsr mg_tick
	tst.l pool_direct
	jeq .L1295
	tst.l 1175351520
	jne .L1382
	clr.l pool_direct
.L1295:
	tst.l pool_pending
	jne .L1383
.L1297:
	move.l 1187521622,%d0
	add.l #-1073741824,%d0
	cmp.l #133169151,%d0
	jls .L1299
	mov3q.l #1,%d1
	move.l -2147457608,%d0
	cmp.l %d0,%d1
	jeq .L1384
	move.l %d0,last_transport
.L1379:
	move.l 1187521622,%d3
	clr.l %d2
	mvz.b 269161679,%d1
	move.l %d1,40(%sp)
	mvz.b 269161676,%d4
.L1307:
	move.l layer_gen,%a2
	move.l active,%d0
	cmp.l shown_bank.l,%d3
	jeq .L1385
.L1314:
	tst.l %a2
	jeq .L1321
	tst.l %d0
	jne .L1339
	move.l 40(%sp),%d5
	clr.l edit_view
	move.l %d3,shown_bank
	move.l %d5,shown_part
	move.l %d4,shown_track
.L1316:
	move.l 1175262812,%a0
	tst.l %d2
	jeq .L1294
	tst.l %a0
	jeq .L1294
	tst.l (%a0)
	jne .L1294
	move.l #st_key,%d1
	move.l #1187503478,%a0
	lea saved-1187503478,%a1
.L1328:
	move.l (%a0),%d0
	cmp.l %d1,%d0
	jeq .L1327
	move.l %d0,(%a1,%a0.l)
.L1327:
	addq.l #4,%a0
	cmp.l #1187503490,%a0
	jne .L1328
	move.l #1187503790,%a0
	lea saved-1187503778,%a1
.L1330:
	move.l (%a0),%d0
	cmp.l %d1,%d0
	jeq .L1329
	move.l %d0,(%a1,%a0.l)
.L1329:
	addq.l #4,%a0
	cmp.l #1187503802,%a0
	jne .L1330
	jsr generator_view
	move.l %d0,layer_gen
	tst.l %d0
	jeq .L1341
	lea st_layer,%a0
	clr.l (%a0)
	move.l %a0,-(%sp)
	jsr 1073943700
	mov3q.l #-1,-(%sp)
	mov3q.l #1,active
	jsr 1074059592
	mov3q.l #1,1187497772
	addq.l #8,%sp
.L1294:
	movem.l (%sp),#19580
	lea (64,%sp),%sp
	rts
.L1299:
	move.l 1187521622,%a2
	mov3q.l #3,%d5
	move.b 269161679,%d0
	mvz.w #6322,%d6
	add.l #585088,%a2
	sub.l %a6,%a6
	clr.l %d2
	lea vector_signed_track,%a3
	and.l %d5,%d0
	muls.l %d6,%d0
	add.l %d0,%a2
.L1303:
	move.l %a6,-(%sp)
	move.l %a2,-(%sp)
	jsr (%a3)
	addq.l #8,%sp
	tst.l %d0
	jeq .L1302
	mov3q.l #1,%d0
	move.l %a6,%d1
	lsl.l %d1,%d0
	or.l %d0,%d2
.L1302:
	addq.l #1,%a6
	moveq #8,%d5
	cmp.l %a6,%d5
	jne .L1303
	move.l -2147457608,%d0
	mov3q.l #1,%d5
	cmp.l %d0,%d5
	jeq .L1386
.L1308:
	move.l %d0,last_transport
	move.l 1187521622,%d3
	move.b 269161679,%d5
	move.b %d5,47(%sp)
	mvz.b %d5,%d6
	mvz.b 269161676,%d4
	move.l %d6,40(%sp)
.L1334:
	move.w #497,%a6
	clr.l %d0
	lea (-435,%a2),%a3
.L1312:
	btst %d0,%d2
	jeq .L1311
	mvz.b (%a3,%a6.l),%d1
	mov3q.l #1,%d5
	cmp.l %d1,%d5
	jeq .L1387
.L1311:
	addq.l #1,%d0
	lea (30,%a6),%a6
	moveq #8,%d1
	cmp.l %d0,%d1
	jne .L1312
.L1388:
	mov3q.l #7,%d5
	cmp.l %d4,%d5
	jcs .L1335
	tst.b 34(%a2,%d4.l)
	jne .L1335
	move.l #1074606108,%d0
.L1313:
	move.l %d0,1074618188
	tst.l %d2
	jeq .L1307
	tst.l -2147483630
	seq %d2
	move.l layer_gen,%a2
	move.l active,%d0
	mvs.b %d2,%d2
	neg.l %d2
	cmp.l shown_bank.l,%d3
	jne .L1314
	jra .L1385
.L1387:
	move.l %d0,-(%sp)
	lea (57,%sp),%a0
	move.l %d0,36(%sp)
	move.l %d1,40(%sp)
	jsr settings
	move.l 1187521622,%a0
	add.l #585088,%a0
	move.b 269161679,%d5
	move.w %d5,%a1
	mov3q.l #3,%d5
	move.l %a1,%d6
	and.l %d5,%d6
	mvz.w #6322,%d5
	muls.l %d5,%d6
	add.l %d6,%a0
	move.b (%a0,%a6.l),%d6
	move.w %d6,%a0
	moveq #127,%d6
	move.l %a0,%d5
	and.l %d6,%d5
	mov3q.l #3,%d6
	move.l %d5,(%sp)
	pea 57(%sp)
	move.l 40(%sp),%d0
	move.l %d0,-(%sp)
	move.l %d0,44(%sp)
	jsr save_settings
	move.b 59(%sp),%d5
	move.l 1187521622,%a1
	add.l #610376,%a1
	and.l %d6,%d5
	move.l %d5,60(%sp)
	move.b (%a1),%d5
	move.l 48(%sp),%d1
	move.l 60(%sp),%d6
	lea (12,%sp),%sp
	lsl.l %d6,%d1
	move.w %d5,%a0
	move.l %a0,%d5
	or.l %d1,%d5
	move.b %d5,(%a1)
	move.b 269161566,%d6
	move.w %d6,%a0
	move.l %a0,%d5
	or.l %d5,%d1
	move.b %d1,269161566
	move.l 1187521622,%a0
	add.l #635698,%a0
	mov3q.l #1,(%a0)
	mov3q.l #1,269452696
	jsr 1073905152
	lea (30,%a6),%a6
	move.l 32(%sp),%d0
	moveq #8,%d1
	addq.l #1,%d0
	cmp.l %d0,%d1
	jne .L1312
	jra .L1388
.L1383:
	jsr pool_context
	tst.l %d0
	jeq .L1389
	tst.l 1175346736
	jne .L1297
	tst.l 1175351520
	jne .L1297
	jsr st_pool_choice_open
	jra .L1297
.L1385:
	move.l 40(%sp),%d6
	cmp.l shown_part.l,%d6
	jne .L1314
	cmp.l shown_track.l,%d4
	jne .L1314
	tst.l %a2
	jeq .L1315
	tst.l %d0
	jeq .L1316
	lea st_layer,%a3
	tst.l %d2
	jeq .L1319
	tst.l st_layer
	jeq .L1318
.L1319:
	tst.l mine
	jne .L1294
	move.l %a3,-(%sp)
	jsr 1073943660
	clr.l active
	move.l %d3,shown_bank
	move.l %d4,shown_track
	lea (44,%sp),%a1
	addq.l #4,%sp
	move.l (%a1),shown_part
	jra .L1316
.L1386:
	cmp.l last_transport.l,%d5
	jeq .L1308
	tst.l %d2
	jeq .L1309
	sub.l %a3,%a3
	lea generate_track,%a6
.L1310:
	clr.l -(%sp)
	moveq #8,%d6
	clr.l -(%sp)
	move.l %a3,-(%sp)
	jsr (%a6)
	addq.l #1,%a3
	lea (12,%sp),%sp
	cmp.l %a3,%d6
	jne .L1310
	mov3q.l #1,last_transport
	move.l 1187521622,%d3
	move.b 269161679,%d0
	move.w #497,%a6
	lea (-435,%a2),%a3
	move.b %d0,47(%sp)
	mvz.b %d0,%d1
	clr.l %d0
	mvz.b 269161676,%d4
	move.l %d1,40(%sp)
	jra .L1312
.L1335:
	move.l #1074606510,%d0
	jra .L1313
.L1321:
	tst.l %d0
	jeq .L1390
	move.l #st_edit_layer,%d0
	tst.l mine
	jne .L1294
.L1391:
	move.l %d0,-(%sp)
	jsr 1073943660
	clr.l active
	clr.l edit_view
	move.l %d3,shown_bank
	lea (44,%sp),%a0
	addq.l #4,%sp
	move.l %d4,shown_track
	move.l (%a0),shown_part
	jra .L1316
.L1390:
	move.l 40(%sp),%d1
	clr.l edit_view
	move.l %d3,shown_bank
	move.l %d1,shown_part
	move.l %d4,shown_track
	jra .L1316
.L1339:
	move.l #st_layer,%d0
	tst.l mine
	jne .L1294
	jra .L1391
.L1384:
	mov3q.l #1,%d6
	cmp.l last_transport.l,%d6
	jeq .L1379
	mov3q.l #1,last_transport
	move.l 1187521622,%d3
	clr.l %d2
	mvz.b 269161679,%d1
	move.l %d1,40(%sp)
	mvz.b 269161676,%d4
	jra .L1307
.L1382:
	jsr pool_context
	tst.l %d0
	jne .L1295
	clr.l pool_direct
	jra .L1295
.L1389:
	clr.l pool_pending
	jra .L1297
.L1341:
	lea st_edit_layer,%a0
	clr.l (%a0)
	move.l %a0,-(%sp)
	jsr 1073943700
	mov3q.l #-1,-(%sp)
	mov3q.l #1,active
	jsr 1074059592
	mov3q.l #1,1187497772
	addq.l #8,%sp
	jra .L1294
.L1315:
	tst.l %d0
	jeq .L1316
	lea st_edit_layer,%a3
	tst.l %d2
	jeq .L1319
	tst.l st_edit_layer
	jne .L1319
.L1318:
	jsr generator_view
	cmp.l %d0,%a2
	jne .L1319
	movem.l (%sp),#19580
	lea (64,%sp),%sp
	rts
.L1309:
	mov3q.l #1,last_transport
	move.l 1187521622,%d3
	move.b 269161679,%d5
	move.b %d5,47(%sp)
	mvz.b %d5,%d6
	mvz.b 269161676,%d4
	move.l %d6,40(%sp)
	jra .L1334
	.size	st_ui_tick, .-st_ui_tick
	.section	.rodata
	.align	2
	.type	formats.1, @object
	.size	formats.1, 48
formats.1:
	.long	midi_format_0
	.long	midi_format_1
	.long	midi_format_2
	.long	midi_format_3
	.long	midi_format_4
	.long	midi_format_5
	.long	midi_format_6
	.long	midi_format_7
	.long	midi_format_8
	.long	midi_format_9
	.long	midi_format_10
	.long	midi_format_11
	.type	first.2, @object
	.size	first.2, 12
first.2:
	.base64	"CwsAAQgwAQwMAAAA"
	.local	locked.3
	.comm	locked.3,64,1
	.section	.rodata.str1.1
.LC9:
	.string	"C"
.LC10:
	.string	"C#"
.LC11:
	.string	"D"
.LC12:
	.string	"D#"
.LC13:
	.string	"E"
.LC14:
	.string	"F"
.LC15:
	.string	"F#"
.LC16:
	.string	"G"
.LC17:
	.string	"G#"
.LC18:
	.string	"A"
.LC19:
	.string	"A#"
.LC20:
	.string	"B"
	.section	.rodata
	.align	2
	.type	roots.5, @object
	.size	roots.5, 48
roots.5:
	.long	.LC9
	.long	.LC10
	.long	.LC11
	.long	.LC12
	.long	.LC13
	.long	.LC14
	.long	.LC15
	.long	.LC16
	.long	.LC17
	.long	.LC18
	.long	.LC19
	.long	.LC20
	.set	roots.0,roots.5
	.align	2
	.type	formats.6, @object
	.size	formats.6, 48
formats.6:
	.long	format_0
	.long	format_1
	.long	format_2
	.long	format_3
	.long	format_4
	.long	format_5
	.long	format_6
	.long	format_7
	.long	format_8
	.long	format_9
	.long	format_10
	.long	format_11
	.align	2
	.type	handlers.7, @object
	.size	handlers.7, 8
handlers.7:
	.long	pool_static
	.long	pool_flex
	.type	mg_keys, @object
	.size	mg_keys, 4
mg_keys:
	.ascii	"3 12"
	.local	mg_opened
	.comm	mg_opened,4,2
	.local	mg_cursor
	.comm	mg_cursor,4,2
	.local	mg_shown
	.comm	mg_shown,4,2
	.local	mg_second
	.comm	mg_second,4,2
	.local	mg_mine
	.comm	mg_mine,4,2
	.local	mg_saved
	.comm	mg_saved,48,2
	.local	mg_active
	.comm	mg_active,4,2
	.local	mg_seen
	.comm	mg_seen,4,2
	.type	mg_arp_setup_slots, @object
	.size	mg_arp_setup_slots, 6
mg_arp_setup_slots:
	.base64	"AAAHAAAA"
	.type	mg_arp_page, @object
	.size	mg_arp_page, 6
mg_arp_page:
	.string	"@"
	.base64	"AAUABg=="
	.globl	vector_midi
	.align	2
	.type	vector_midi, @object
	.size	vector_midi, 32
vector_midi:
	.long	1
	.long	.LC8
	.long	86
	.long	vector_midi_assign
	.long	vector_midi_page
	.long	vector_midi_knob
	.long	vector_midi_yes
	.long	0
	.data
	.align	2
	.type	midi_page_built, @object
	.size	midi_page_built, 4
midi_page_built:
	.zero	4
	.section	.rodata.str1.1
.LC21:
	.string	"001 STATIC"
.LC22:
	.string	"002 FLEX"
	.section	.rodata
	.align	2
	.type	pool_labels, @object
	.size	pool_labels, 8
pool_labels:
	.long	.LC21
	.long	.LC22
	.data
	.align	2
	.type	pool_browse, @object
	.size	pool_browse, 4
pool_browse:
	.zero	4
	.align	2
	.type	pool_direct, @object
	.size	pool_direct, 4
pool_direct:
	.zero	4
	.align	2
	.type	pool_pending, @object
	.size	pool_pending, 4
pool_pending:
	.zero	4
	.align	2
	.type	pool_track, @object
	.size	pool_track, 4
pool_track:
	.zero	4
	.align	2
	.type	pool_part, @object
	.size	pool_part, 4
pool_part:
	.zero	4
	.align	2
	.type	pool_bank, @object
	.size	pool_bank, 4
pool_bank:
	.zero	4
	.align	2
	.type	src_page_source, @object
	.size	src_page_source, 4
src_page_source:
	.zero	4
	.align	2
	.type	src_page_ready, @object
	.size	src_page_ready, 4
src_page_ready:
	.zero	4
	.type	src_page, @object
	.size	src_page, 402
src_page:
	.zero	402
	.type	phrase, @object
	.size	phrase, 257
phrase:
	.zero	257
	.type	staging, @object
	.size	staging, 2330
staging:
	.zero	2330
	.align	2
	.type	mine, @object
	.size	mine, 4
mine:
	.zero	4
	.align	2
	.type	last_transport, @object
	.size	last_transport, 4
last_transport:
	.zero	4
	.align	2
	.type	saved, @object
	.size	saved, 24
saved:
	.zero	24
	.align	2
	.type	layer_gen, @object
	.size	layer_gen, 4
layer_gen:
	.zero	4
	.align	2
	.type	edit_view, @object
	.size	edit_view, 4
edit_view:
	.zero	4
	.align	2
	.type	shown_track, @object
	.size	shown_track, 4
shown_track:
	.zero	4
	.align	2
	.type	shown_part, @object
	.size	shown_part, 4
shown_part:
	.zero	4
	.align	2
	.type	shown_bank, @object
	.size	shown_bank, 4
shown_bank:
	.zero	4
	.align	2
	.type	active, @object
	.size	active, 4
active:
	.zero	4
	.section	.rodata
	.align	2
	.type	scales, @object
	.size	scales, 10
scales:
	.word	4095
	.word	1453
	.word	2741
	.word	1709
	.word	1193
	.globl	vector_scale_names
	.section	.rodata.str1.1
.LC23:
	.string	"CHR"
.LC24:
	.string	"MIN"
.LC25:
	.string	"MAJ"
.LC26:
	.string	"DOR"
.LC27:
	.string	"PENT"
	.section	.rodata
	.align	2
	.type	vector_scale_names, @object
	.size	vector_scale_names, 20
vector_scale_names:
	.long	.LC23
	.long	.LC24
	.long	.LC25
	.long	.LC26
	.long	.LC27
	.globl	vector_control_max
	.type	vector_control_max, @object
	.size	vector_control_max, 12
vector_control_max:
	.base64	"DxALBH5/fwwYP0AB"
	.globl	vector_control_names
	.section	.rodata.str1.1
.LC28:
	.string	"TYPE"
.LC29:
	.string	"DENS"
.LC30:
	.string	"ROOT"
.LC31:
	.string	"SCAL"
.LC32:
	.string	"GATE"
.LC33:
	.string	"ACNT"
.LC34:
	.string	"SEED"
.LC35:
	.string	"SPAN"
.LC36:
	.string	"OFST"
.LC37:
	.string	"ROT"
.LC38:
	.string	"RPT"
.LC39:
	.string	"DIR"
	.section	.rodata
	.align	2
	.type	vector_control_names, @object
	.size	vector_control_names, 48
vector_control_names:
	.long	.LC28
	.long	.LC29
	.long	.LC30
	.long	.LC31
	.long	.LC32
	.long	.LC33
	.long	.LC34
	.long	.LC35
	.long	.LC36
	.long	.LC37
	.long	.LC38
	.long	.LC39
	.globl	vector_defaults
	.type	vector_defaults, @object
	.size	vector_defaults, 11
vector_defaults:
	.byte	11
	.byte	11
	.byte	0
	.byte	1
	.byte	32
	.byte	48
	.byte	12
	.byte	12
	.byte	0
	.byte	0
	.byte	0

#APP
/* Original VECTOR integration; registration seams adapted from octabam's */
/* MIT Analog BD machine.s (Sam Banks / repeat98). Replayed stock instructions */
/* are generated only in the private local build by prepare.py. */
        .text
        .global st_machine_name, st_src_names, st_main_commit
        .global st_src_commit, st_src_commit2, st_name_a, st_name_b
        .global st_setup_open, st_chooser_open, st_setup_row, st_chooser_row
        .global st_setup_edit6, st_setup_draw6, st_tick_hook
        .equ BANK_PTR, 0x46c82456
        .equ PART_OFF, 0x8ed80
st_machine_name:
        move.l 4(%sp),%d0
        cmpi.l #5,%d0
        beq.s 1f
        jmp st_name_replay
1:      lea st_name(%pc),%a0
        move.l %a0,%d0
        rts
st_src_names:
        .long 0x400b3eac,0x400b3e98,0x400b7c67,0x400b5413,0x400b7a63,st_name
st_row_type:
        lea -20(%sp),%sp
        movem.l %d1/%a0-%a1,8(%sp)
        move.l %d0,(%sp)
        move.l %a0,4(%sp)
        jsr st_type
        movem.l 8(%sp),%d1/%a0-%a1
        lea 20(%sp),%sp
        rts
st_main_commit:
        lea -32(%sp),%sp
        movem.l %d0-%d2/%a0-%a1,12(%sp)
        move.l %a1,%d2
        add.l %d0,%d2
        addi.l #PART_OFF,%d2
        move.l %d2,(%sp)
        move.l %d1,4(%sp)
        moveq #0,%d2
        cmpi.l #5,%d4
        bne.s 1f
        moveq #1,%d2
1:      move.l %d2,8(%sp)
        jsr st_assign
        cmpi.l #5,%d4
        bne.s 2f
        move.l %d0,%d4
2:      movem.l 12(%sp),%d0-%d2/%a0-%a1
        lea 32(%sp),%sp
        jmp st_main_replay
st_src_commit:
        pea 0x4005a61c
        bra.s st_src_common
st_src_commit2:
        pea 0x4005a856
st_src_common:
        move.l 0x460d5c30,%d1
        lea -32(%sp),%sp
        movem.l %d0/%d2-%d3/%a0-%a1,12(%sp)
        move.l %a1,%d3
        add.l %d0,%d3
        addi.l #PART_OFF,%d3
        move.l %d3,(%sp)
        move.l %d2,4(%sp)
        moveq #0,%d3
        cmpi.l #5,%d1
        bne.s 1f
        moveq #1,%d3
1:      move.l %d3,8(%sp)
        move.l %d1,%d3
        jsr st_assign
        cmpi.l #5,%d3
        beq.s 2f
        move.l %d3,%d0
2:      move.l %d0,%d1
        movem.l 12(%sp),%d0/%d2-%d3/%a0-%a1
        lea 32(%sp),%sp
        rts
st_setup_open:
        move.b (%a0),%d3
        move.l %d0,-(%sp)
        mvs.b %d3,%d0
        bsr st_row_type
        move.l %d0,%d3
        move.l (%sp)+,%d0
        mvs.b %d3,%d4
        pea 0x400bb704
        jmp 0x400585e6
st_chooser_open:
        mvs.b (%a0),%d0
        bsr st_chooser_row_type
        move.l %d0,-(%sp)
        pea 0x460e7386
        jmp 0x40078890
st_name_a:
        bsr st_name_pick
        jmp 0x4003d722
st_name_b:
        bsr st_name_pick
        jmp 0x4004c374
st_name_pick:
        bsr st_row_type
        lea st_src_names(%pc),%a0
        move.l (%a0,%d0.l*4),%d1
        rts
st_setup_row:
        mvs.b (%a0),%d0
        lea 24(%sp),%sp
        bsr st_row_type
        jmp 0x4003c986
st_chooser_row:
        mvs.b (%a0),%d0
        bsr st_chooser_row_type
        cmp.l %d0,%d2
        bne.s 1f
        jmp 0x400786ce
1:      jmp 0x400786fc
st_chooser_row_type:
        lea -20(%sp),%sp
        movem.l %d1/%a0-%a1,8(%sp)
        move.l %d0,(%sp)
        move.l %a0,4(%sp)
        jsr st_chooser_type
        movem.l 8(%sp),%d1/%a0-%a1
        lea 20(%sp),%sp
        rts
/* SRC SETUP on row five edits the real underlying pool's settings. */
st_pool_kind:
        move.l %a0,-(%sp)
        move.l %d1,-(%sp)
        movea.l BANK_PTR,%a0
        mvz.b 0x100b14cf,%d1
        mulu.w #6322,%d1
        adda.l %d1,%a0
        mvz.b 0x100b14cc,%d1
        adda.l #0x8eda2,%a0
        mvz.b (%a0,%d1.l),%d0
        move.l (%sp)+,%d1
        move.l (%sp)+,%a0
        rts
st_setup_edit6:
        cmpi.l #5,%d2
        bne.s 1f
        lea -28(%sp),%sp
        movem.l %d0-%d1/%a0-%a1,12(%sp)
        move.l %a3,(%sp)
        move.l %d3,4(%sp)
        jsr st_setup_knob
        move.l %d0,8(%sp)
        movem.l 12(%sp),%d0-%d1/%a0-%a1
        tst.l 8(%sp)
        lea 28(%sp),%sp
        beq.s 2f
        jmp 0x4003a624
2:
        bsr st_pool_kind
        move.l %d0,%d2
1:      jmp st_edit_replay
st_setup_draw6:
        cmpi.l #5,%d6
        bne.s 1f
        lea -20(%sp),%sp
        movem.l %d0-%d1/%a0-%a1,4(%sp)
        move.l 92(%sp),(%sp)
        jsr st_setup_page
        move.l %d0,92(%sp)
        movem.l 4(%sp),%d0-%d1/%a0-%a1
        lea 20(%sp),%sp
        move.l %d0,-(%sp)
        bsr st_pool_kind
        move.l %d0,%d6
        move.l (%sp)+,%d0
1:      jmp st_draw_replay
st_tick_hook:
        jsr 0x4005213c
        jsr 0x4007e940
        jsr st_ui_tick
        jmp 0x40052228
st_name:
        .asciz "VECTOR"
        .data
        .balign 4
        .global st_layer, st_edit_layer
st_layer:
        .long 0,st_keys,st_encs,0,0,-1,-1
st_edit_layer:
        .long 0,st_keys,0,0,0,-1,-1
st_keys:
        .irp k,0x31,0x3e
        .byte \k,0
        .long st_key,st_key,st_key,0,0
        .word 0,0
        .endr
        .byte 0xff,0
        .long 0,0,0,0,0
        .word 0,0
st_encs:
        .irp k,0,1,2,3,4,5
        .byte \k,0
        .long st_knob,0,0,0,0
        .endr
        .byte 0xff,0
        .long 0,0,0,0,0

/* Only the stock parameter-page DRAW call chooses the generator descriptor.
 * The parameter resolver and every playback/editor consumer remain stock. */
        .text
        .balign 2
        .global st_src_draw
st_src_draw:
        pea -1.w
        pea -1.w
        jsr st_draw_page
        jmp 0x4004e4d0

/* Stock double-tap TRACK enters the VECTOR backing-pool modal. */
        .global st_pool_open, st_stock_pool_open, st_list_draw, st_pool_title
st_pool_open:
        lea -16(%sp),%sp
        movem.l %d0-%d1/%a0-%a1,(%sp)
        jsr st_selected
        tst.l %d0
        beq.s .pool_stock
        movem.l (%sp),%d0-%d1/%a0-%a1
        lea 16(%sp),%sp
        jmp st_pool_choice_open
.pool_stock:
        movem.l (%sp),%d0-%d1/%a0-%a1
        lea 16(%sp),%sp
st_stock_pool_open:
        move.l %a2,-(%sp)
        tst.l 0x460e70e0
        jmp 0x400791ec
st_list_draw:
        lea -16(%sp),%sp
        movem.l %d0-%d1/%a0-%a1,(%sp)
        jsr st_pool_choice_draw
        tst.l %d0
        beq.s .list_stock
        movem.l (%sp),%d0-%d1/%a0-%a1
        lea 16(%sp),%sp
        rts
.list_stock:
        movem.l (%sp),%d0-%d1/%a0-%a1
        lea 16(%sp),%sp
        lea -24(%sp),%sp
        movem.l %d2-%d3/%a2-%a5,(%sp)
        jmp 0x4006d78c
st_pool_title:
        moveq #1,%d6
        cmpi.l #5,%d0
        bne.s .title_stock
        lea -16(%sp),%sp
        movem.l %d0-%d1/%a0-%a1,(%sp)
        jsr st_selected
        tst.l %d0
        beq.s .title_unsigned
        movem.l (%sp),%d0-%d1/%a0-%a1
        lea 16(%sp),%sp
        bra.s .title_pool
.title_unsigned:
        movem.l (%sp),%d0-%d1/%a0-%a1
        lea 16(%sp),%sp
.title_stock:
        cmp.l %d0,%d6
        bcs.s .title_plain
.title_pool:
        jmp 0x40077b62
.title_plain:
        jmp 0x40077b70

/* Validate the rest of each Part with the real stock routine. */
        .text
        .balign 2
        .global st_validate, st_stock_validate
st_validate:
        jmp st_validate_part
st_stock_validate:
        lea -96(%sp),%sp
        movem.l %d2-%d7/%a2-%fp,(%sp)
        jmp 0x40002320

| SPDX-License-Identifier: MIT
| The sites of the MIDI generator registry (midi_generators.c, events.json ot_midi_generators): the base's, and a
| card build's generator module patches the same ones. Each replays its own instructions, never stock's bytes.
        .text
        .balign 2
        .global mg_tap_site, mg_page_site, mg_setup_site
| Double-tap TRACK (0x40083afc, 10 bytes): d2 is the tapped track, the current one. Stock asks for MIDI mode
| (0x40033970) and does nothing in it (0x40083b7e).
mg_tap_site:
        jsr 0x40033970
        tst.l %d0
        beq.s 1f
        lea -16(%sp),%sp
        movem.l %d0-%d1/%a0-%a1,(%sp)
        move.l %d2,-(%sp)
        jsr mg_track_tap
        addq.l #4,%sp
        movem.l (%sp),%d0-%d1/%a0-%a1
        lea 16(%sp),%sp
        jmp 0x40083b7e
1:      jmp 0x40083b06
| The main page drawer's MIDI arm (0x4004e1ea, 10 bytes): 0x40031ee0(-1, its page argument) is the descriptor; a
| generator's page replaces it. Stock pops the two arguments at 0x4004e1f4.
mg_page_site:
        move.l 8(%fp),-(%sp)
        pea -1.w
        jsr 0x40031ee0
        lea -12(%sp),%sp
        movem.l %d1/%a0-%a1,(%sp)
        move.l %d0,-(%sp)
        jsr mg_page
        addq.l #4,%sp
        movem.l (%sp),%d1/%a0-%a1
        lea 12(%sp),%sp
        jmp 0x4004e1f4
| The setup opener 0x40032228(page) in MIDI mode, page 2 (0x40032280, 8 bytes): ARP SETUP's open routine from its
| window record, then 0x400322ec calls it. The opener has no frame here, so rts returns to its caller.
mg_setup_site:
        lea -16(%sp),%sp
        movem.l %d0-%d1/%a0-%a1,(%sp)
        jsr mg_arp_setup
        tst.l %d0
        movem.l (%sp),%d0-%d1/%a0-%a1   | movem and lea keep the condition codes
        lea 16(%sp),%sp
        bne.s 1f
        move.l 0x400cfeda,%a1
        jmp 0x400322ec
1:      rts
| MIDI NOTE SETUP's drawer 0x40036548 (8 bytes): its displaced prologue, filled from the user's own OS (the base's
| modwerk_stock_ placeholders; a card build's StockCopy of the same span), then the rest of it.
        .global mg_stock_note_draw
mg_stock_note_draw:
        .globl modwerk_stock_40036548_8
modwerk_stock_40036548_8:
        .space 8
        jmp 0x40036550

| Input layers (stock's list at 0x460d165c: a pushed layer links last). Keys: code, then the press, release and
| repeat handlers; encoders A-F: the turn handler.
        .data
        .balign 4
        .global mg_list_layer, mg_page_layer
mg_list_layer:
        .long 0,mg_list_keys,0,0,0,-1,-1
mg_page_layer:
        .long 0,mg_page_keys,mg_page_encs,0,0,-1,-1
mg_list_keys:
        .irp k,0x33,0x20,0x31
        .byte \k,0
        .long mg_key,mg_key,mg_key,0,0
        .word 0,0
        .endr
        .byte 0xff,0
        .long 0,0,0,0,0
        .word 0,0
mg_page_keys:
        .irp k,0x31,0x32
        .byte \k,0
        .long mg_key,mg_key,mg_key,0,0
        .word 0,0
        .endr
        .byte 0xff,0
        .long 0,0,0,0,0
        .word 0,0
mg_page_encs:
        .irp k,0,1,2,3,4,5
        .byte \k,0
        .long mg_knob,0,0,0,0
        .endr
        .byte 0xff,0
        .long 0,0,0,0,0
        .text

.text
.balign 2
st_name_replay:
.space 6
jmp 0x400334de
st_main_replay:
.space 6
jmp 0x40079822
st_edit_replay:
.space 8
jmp 0x4003a536
st_draw_replay:
.space 8
jmp 0x4003cda0
