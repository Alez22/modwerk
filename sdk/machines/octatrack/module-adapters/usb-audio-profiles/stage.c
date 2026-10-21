// SPDX-License-Identifier: GPL-3.0-or-later
#include "usb_audio_profiles.h"

/* Private board seam, called with IRQs masked. All descriptor templates are
   immutable/page-contained; only the selected profile and bounded host state
   change here. A future engine-owned lease must authorize the disconnect. */
uint32_t mu_audio_stage_locked(uint32_t next) {
 uint32_t i;
 volatile uint32_t *const cmd=(volatile uint32_t *)0xfc0b0140u;
 volatile uint32_t *const prime=(volatile uint32_t *)0xfc0b01b0u;
 volatile uint32_t *const flush=(volatile uint32_t *)0xfc0b01b4u;
 volatile uint32_t *const stat=(volatile uint32_t *)0xfc0b01b8u;
 if(next>6u || mu_audio_profile>6u) return 1u;
 if((*cmd&1u) || ((*prime|*flush|*stat)&0x00080000u)) return 2u;
 for(i=0;i<6;i++) if(*mu_audio_profile_states[i].alt || *mu_audio_profile_states[i].running) return 3u;
 if(next) {
  const struct host_state *state=mu_audio_profile_states+(next-1u);
  uint8_t *q=state->first;
  while(q<state->end) *q++=0;
  *(uint32_t *)state->bank=0xffffffffu;
  *(uint32_t *)state->step=11025u;
  *state->closed=1;
 }
 /* The existing first-block cushion owns clearing reachable host samples.
    Never bulk-clear a 90 KiB ring with the audio frame interrupt masked. */
 mu_audio_config_length=mu_audio_profile_lengths[next];
 mu_audio_profile=next;
 return 0;
}
