import { useEffect, useRef, useState, type ReactNode } from 'react'
import { Icon } from './Icon'

type Step = { title: string; go: () => void }

/**
 * A module's page over the current one, so looking at it never navigates away. With `prev`/`next`,
 * chevrons beside the panel (and the arrow keys) page through the module set without closing it.
 */
export function ModuleDialog({ title, index, total, prev, next, status, actions, onClose, children }: { title: string; index?: number; total?: number; prev?: Step; next?: Step; status?: ReactNode; actions?: ReactNode; onClose: () => void; children: ReactNode }) {
  const dialog = useRef<HTMLDialogElement>(null), panel = useRef<HTMLDivElement>(null)
  const [direction, setDirection] = useState<'prev' | 'next'>()
  useEffect(() => {
    const element = dialog.current, previousFocus = document.activeElement
    element?.showModal()
    panel.current?.focus()
    return () => { element?.close(); if (previousFocus instanceof HTMLElement) previousFocus.focus() }
  }, [])
  useEffect(() => { panel.current?.scrollTo(0, 0) }, [title])
  const step = (which: 'prev' | 'next') => { const target = which === 'prev' ? prev : next; if (!target) return; setDirection(which); target.go() }
  const paging = !!(prev || next)
  return <dialog ref={dialog} className="module-dialog" aria-label={title} data-step={direction} onCancel={event => { event.preventDefault(); onClose() }} onClick={event => { if (event.target === event.currentTarget) onClose() }}
    onKeyDown={event => {
      if ((event.target as HTMLElement).closest('input, textarea, select, [contenteditable="true"]')) return
      if (event.key === 'ArrowLeft' && prev) { event.preventDefault(); step('prev') }
      if (event.key === 'ArrowRight' && next) { event.preventDefault(); step('next') }
    }}>
    {paging && <StepButton which="prev" target={prev} onStep={step} />}
    <div ref={panel} className="module-dialog-panel" tabIndex={-1}>
      <div className="module-dialog-bar">
        <span className="module-dialog-meta">
          {index !== undefined && total !== undefined && total > 1 && <span className="module-dialog-position" aria-label={`Module ${index + 1} of ${total}`}>
            {total <= 16 && <span className="module-dialog-trigs" aria-hidden="true">{Array.from({ length: total }, (_, i) => <i key={i} className={i === index ? 'is-on' : undefined} />)}</span>}
            <span aria-hidden="true">{String(index + 1).padStart(2, '0')}<em>/</em>{String(total).padStart(2, '0')}</span>
          </span>}
          {status}
        </span>
        <span className="module-dialog-actions">{actions}<button type="button" className="module-dialog-close" aria-label={'Close ' + title} onClick={onClose}><Icon name="close" size={18} /></button></span>
      </div>
      {children}
    </div>
    {paging && <StepButton which="next" target={next} onStep={step} />}
  </dialog>
}

function StepButton({ which, target, onStep }: { which: 'prev' | 'next'; target?: Step; onStep: (which: 'prev' | 'next') => void }) {
  return <button type="button" className={'module-dialog-step is-' + which} disabled={!target} aria-label={(which === 'prev' ? 'Previous module' : 'Next module') + (target ? ': ' + target.title : '')} onClick={() => onStep(which)}>
    <span className="module-dialog-step-icon"><Icon name="back" size={22} /></span>
    {target && <span className="module-dialog-step-label" aria-hidden="true">{target.title}</span>}
  </button>
}
