// SPDX-License-Identifier: GPL-3.0-or-later OR Elastic-2.0
// Copyright (c) 2026 Jannik Aßfalg (repeat98)
import type { Session } from './api'
import { USB_LINK } from '../engine/protocol'
/** Access follows the server session, never a username or locally stored preference. */
export function hasBetaAccess(session: Session) {
  return !!(session.user?.verified && session.user.username && (session.user.betaTester || session.admin))
}
/** The Octatrack USB link, its status, the update flow and the base install prompt: beta access on a computer, or any
 * dev build (`released`). It follows the session, so revoking beta access turns it off. */
export function hasUsbLinkAccess(session: Session, touchOnly: boolean, released = USB_LINK) {
  return !touchOnly && (released || hasBetaAccess(session))
}
