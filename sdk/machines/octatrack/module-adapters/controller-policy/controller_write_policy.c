/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "controller_write_lease.h"
/* Board-compiled reviewed rows, one per exact encoded/source controller
 * binding: {identity, version, image_bytes, entry, begin_return, end_return}.
 * None is qualified yet. The table is sized by its rows; the trailing
 * version-0 row is never trusted (C needs one element) and is not counted. */
#define MW_REVIEWED_CONTROLLER_POLICIES /* none */
const struct mw_controller_write_policy modwerk_controller_write_policies[] = {
    MW_REVIEWED_CONTROLLER_POLICIES {.version = 0}
};
const unsigned modwerk_controller_write_policy_count =
    sizeof modwerk_controller_write_policies / sizeof *modwerk_controller_write_policies - 1u;
typedef char modwerk_controller_write_policies_bounded[
    sizeof modwerk_controller_write_policies / sizeof *modwerk_controller_write_policies - 1u <=
    MW_CONTROLLER_WRITE_POLICY_CAPACITY ? 1 : -1];
typedef char modwerk_controller_write_policy_row_is_96_bytes[
    sizeof(struct mw_controller_write_policy) == 96u ? 1 : -1];
