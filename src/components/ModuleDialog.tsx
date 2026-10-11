import { useEffect, useRef, type ReactNode } from 'react'
import { Icon } from './Icon'

/** A module's page over the current one, so looking at it never navigates away. */
export function ModuleDialog({ title, onClose, children }: { title: string; onClose: () => void; children: ReactNode }) {
  const dialog = useRef<HTMLDialogElement>(null)
  useEffect(() => {
    const element = dialog.current, previousFocus = document.activeElement
    element?.showModal()
    return () => { element?.close(); if (previousFocus instanceof HTMLElement) previousFocus.focus() }
  }, [])
  return <dialog ref={dialog} className="module-dialog" aria-label={title} onCancel={event => { event.preventDefault(); onClose() }} onClick={event => { if (event.target === event.currentTarget) onClose() }}>
    <button type="button" className="icon-button module-dialog-close" aria-label={'Close ' + title} onClick={onClose}><Icon name="close" size={18} /></button>
    {children}
  </dialog>
}
