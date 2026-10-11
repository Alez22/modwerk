import { useEffect, useRef, type ReactNode } from 'react'
import { Icon } from './Icon'

/**
 * A module's page over the current one, so looking at it never navigates away. With `onPrev`/`onNext`,
 * chevrons (and the arrow keys) page through the module set without closing it.
 */
export function ModuleDialog({ title, position, onPrev, onNext, onClose, children }: { title: string; position?: string; onPrev?: () => void; onNext?: () => void; onClose: () => void; children: ReactNode }) {
  const dialog = useRef<HTMLDialogElement>(null)
  useEffect(() => {
    const element = dialog.current, previousFocus = document.activeElement
    element?.showModal()
    return () => { element?.close(); if (previousFocus instanceof HTMLElement) previousFocus.focus() }
  }, [])
  useEffect(() => { dialog.current?.scrollTo(0, 0) }, [title])
  return <dialog ref={dialog} className="module-dialog" aria-label={title} onCancel={event => { event.preventDefault(); onClose() }} onClick={event => { if (event.target === event.currentTarget) onClose() }}
    onKeyDown={event => {
      if ((event.target as HTMLElement).closest('input, textarea, select, [contenteditable="true"]')) return
      if (event.key === 'ArrowLeft' && onPrev) { event.preventDefault(); onPrev() }
      if (event.key === 'ArrowRight' && onNext) { event.preventDefault(); onNext() }
    }}>
    <div className="module-dialog-bar">
      {(onPrev || onNext) && <><button type="button" className="icon-button" aria-label="Previous module" disabled={!onPrev} onClick={onPrev}><Icon name="back" size={18} /></button>
        {position && <span className="module-dialog-position">{position}</span>}
        <button type="button" className="icon-button" aria-label="Next module" disabled={!onNext} onClick={onNext}><Icon name="arrow" size={18} /></button></>}
      <button type="button" className="icon-button" aria-label={'Close ' + title} onClick={onClose}><Icon name="close" size={18} /></button>
    </div>
    {children}
  </dialog>
}
