/* SPDX-License-Identifier: GPL-3.0-or-later
 * events_test.c's machine: the generated header's shape (three events, the second and third
 * at one site, and a raised event with no site), its sites inside the host test's fake stock code. */
#ifndef MODWERK_RUNTIME_EVENTS_H
#define MODWERK_RUNTIME_EVENTS_H
#define RUNTIME_SITE_EVENTS 4u
#define RUNTIME_SITE_EVENT_SPANS { {0x1080u, 8u}, {0x10a0u, 8u}, {0x10a0u, 8u}, {0u, 0u} }
#define RUNTIME_SITE_EVENT_ROWS(r) { r[0], r[1], r[2], r[3] }
extern const unsigned char modwerk_raise_test[];
#define RUNTIME_SITE_EVENT_RAISES { 0, 0, 0, (uintptr_t)modwerk_raise_test }
#endif
