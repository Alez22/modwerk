import { useEffect, useRef, type ReactNode } from 'react'
import './octatrack-link.css'

/** The card route of the Octatrack page (base OS file, checks, the .bin): open while no unit with the base is connected
 * over USB, folded away while one is (`open` unfolds it when the guided sync sends people here). */
export function CardInstall({ folded, open = false, onOpened, children }: { folded: boolean; open?: boolean; onOpened?: () => void; children: ReactNode }) {
  const details = useRef<HTMLDetailsElement>(null), section = useRef<HTMLElement>(null)
  useEffect(() => {
    if (!open) return
    if (details.current) details.current.open = true
    ;(details.current ?? section.current)?.scrollIntoView({ block: 'start' })
    onOpened?.()
  }, [open, onOpened])
  return folded ? <details ref={details} className="card-install"><summary>Install from the card instead</summary>{children}</details>
    : <section ref={section} className="card-install is-open" aria-labelledby="card-install-title"><h2 id="card-install-title">Install from the card</h2>{children}</section>
}
