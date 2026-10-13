/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "controller_write_lease.h"
/* No encoded controller package/source has a qualified production binding.
 * Board-compiled: reviewed rows are compiled in, at most the capacity. */
const unsigned modwerk_controller_write_policy_count=0;
const struct mw_controller_write_policy modwerk_controller_write_policies[1]={{.version=0}};
typedef char modwerk_controller_write_policies_bounded[
    sizeof modwerk_controller_write_policies/sizeof *modwerk_controller_write_policies<=MW_CONTROLLER_WRITE_POLICY_CAPACITY?1:-1];
