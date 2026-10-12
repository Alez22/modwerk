import { useState, type ReactNode } from 'react'
import { ModulePreview } from './ModulePreview'
import { AudioPreviewPlayer } from './AudioPreviewPlayer'
import { useModuleAudioPreviews } from './audio-preview-context'
import { Icon } from './Icon'
import type { AudioPreviewClip } from './audio-preview'
import './audio-preview.css'

/** The dock is a sibling of the cover link, so seeking never opens the module page. */
export function ModuleAudioCardCover({ id, name, href, onBrowse, inert, prepare, clip, children }: {
  id: string; name: string; href: string; onBrowse?: () => void; inert?: boolean; prepare: boolean
  clip: AudioPreviewClip; children: ReactNode
}) {
  return <div className="module-cover module-audio-cover" data-module={id} inert={inert}>
    <a className="module-audio-cover-link" href={href} onClick={onBrowse} onAuxClick={onBrowse} aria-label={'View ' + name + ' (audio preview available)'}>{children}</a>
    <span className="audio-preview-hint" aria-hidden="true"><Icon name="play" size={15}/></span>
    <div className="audio-preview-dock"><AudioPreviewPlayer key={clip.id} clip={clip} name={name} prepare={prepare}/></div>
  </div>
}

export function ModuleAudioDetailPreview({ id, name }: { id: string; name: string }) {
  const { clips, onAdd } = useModuleAudioPreviews(id)
  const [selected, setSelected] = useState('')
  if (!clips.length && !onAdd) return <ModulePreview id={id}/>
  const index = Math.max(0, clips.findIndex(clip => clip.id === selected))
  const clip = clips[index]
  function step(direction: number) { setSelected(clips[(index + direction + clips.length) % clips.length].id) }
  return <div className={'module-audio-detail' + (clip ? ' has-audio' : '')} data-module={id}>
    <div className="module-audio-art">
      <ModulePreview id={id}/>
      {clip && <div className="audio-preview-dock"><AudioPreviewPlayer key={clip.id} clip={clip} name={name}/></div>}
    </div>
    {(clips.length > 1 || onAdd) && <div className="audio-preview-navigation">
      {clips.length > 1 && <div className="audio-preview-carousel" role="group" aria-label="Audio previews">
        <button type="button" onClick={() => step(-1)} aria-label="Previous audio preview"><Icon name="back" size={16}/></button>
        <span aria-live="polite" aria-atomic="true">{index + 1} / {clips.length}</span>
        <button type="button" onClick={() => step(1)} aria-label="Next audio preview"><Icon name="back" size={16}/></button>
      </div>}
      {onAdd && <button type="button" className="text-button audio-preview-add" onClick={onAdd}><Icon name="plus" size={15}/>Add preview</button>}
    </div>}
  </div>
}
