/* SPDX-License-Identifier: GPL-3.0-or-later
 * Host check of boot_anim.c on a simulated clock (20 ms per composed frame): it runs to its end, ends on
 * exactly the authored frame (boot_expect.h, from base_art.final_pixels), never writes outside the frame,
 * drives one LED channel only with levels 0-15, lights lamps while the cube is out over the panel and
 * leaves every lamp dark at the end. test_recipe.py generates both headers. */
#include <stdio.h>
#include <string.h>
#include "boot_anim.c"
#include "boot_expect.h"

static unsigned failures;
#define CHECK(x) do { if (!(x)) { failures++; fprintf(stderr, "%s:%d: %s\n", __FILE__, __LINE__, #x); } } while (0)

volatile uint32_t host_dtcn3;
uint32_t host_mkii = 1;
int32_t host_lamps[134];
static unsigned char memory[1024 + 64];   /* the frame with 32 guard bytes either side */
static unsigned char *const frame = memory + 32;
static int levels[134], frames, lit_out, odd_lit, out_of_range;

void host_clear(void *window, int a, int b) { (void)window; (void)a; (void)b; }
void host_led_on(int id) { (void)id; }
void host_led_off(int id) { (void)id; }
void host_led_send(void) {}

void host_led_level(int id, int level)
{
    if (level < 0 || level > 15) out_of_range++;
    if (id & 1 && level) odd_lit++;
    if (level && now > T_OUT && now < T_REST) lit_out++;
    levels[id] = level;
}

void host_compose(void)
{
    memset(memory, 0xa5, sizeof memory);
    memset(frame, 0, 1024);
    modwerk_boot_draw(frame);
    for (int i = 0; i < 32; i++)
        CHECK(memory[i] == 0xa5 && memory[32 + 1024 + i] == 0xa5);
    frames++;
    host_dtcn3 += 132000u * 20;
}

int main(void)
{
    for (int i = 0; i < 67; i++)   /* a 17 x 4 grid of lamps over a panel-sized area, the LCD among them */
        host_lamps[2 * i] = 1500 + i % 17 * 2000, host_lamps[2 * i + 1] = 2500 + i / 17 * 3800;
    int window;
    modwerk_boot_run(&window);
    CHECK(frames >= T_END / 20 - 1 && frames <= T_END / 20 + 1);
    CHECK(!on);
    unsigned char expect[1024] = {0};
    for (int i = 0; i < BOOT_EXPECT; i++) {
        int bit = 63 - boot_expect[i][1];
        expect[boot_expect[i][0] * 8 + (bit >> 3)] |= (unsigned char)(0x80 >> (bit & 7));
    }
    CHECK(memcmp(frame, expect, 1024) == 0);
    CHECK(out_of_range == 0 && odd_lit == 0);
    CHECK(lit_out > 0);
    for (int id = 0; id < 134; id++)
        CHECK(levels[id] == 0);
    /* at rest the sixteen corners are on the nine grid points, 8 px apart */
    place(T_REST);
    CHECK(vx[0] == rest_x(0) && vy[0] == rest_y(0) && vx[5] - vx[0] == 16 * 16 && vy[10] - vy[0] == 16 * 16);
    if (failures) fprintf(stderr, "%u failures\n", failures);
    return failures != 0;
}
