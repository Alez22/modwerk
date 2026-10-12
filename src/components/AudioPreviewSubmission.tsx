import { useEffect, useRef, useState } from 'react'
import { Icon } from './Icon'
import { AudioPreviewPlayer } from './AudioPreviewPlayer'
import { waveformPeaks, type AudioPreviewClip } from './audio-preview'

const MAX_BYTES = 12 * 1024 * 1024
const MAX_SECONDS = 90

export function AudioPreviewSubmission({ name, onAdd, onClose }: { name: string; onAdd: (clip: AudioPreviewClip) => void; onClose: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null)
  const urls = useRef<string[]>([])
  const [file, setFile] = useState<File | null>(null)
  const [credit, setCredit] = useState('')
  const [rights, setRights] = useState(false)
  const [prepared, setPrepared] = useState<AudioPreviewClip | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const generation = useRef({ value: 0 })

  useEffect(() => {
    const element = dialog.current
    if (element && !element.open) element.showModal()
    const localUrls = urls.current
    const request = generation.current
    return () => { request.value++; for (const url of localUrls) URL.revokeObjectURL(url) }
  }, [])

  async function choose(selected?: File) {
    const current = ++generation.current.value
    setFile(selected ?? null); setPrepared(null); setError('')
    if (!selected) { setBusy(false); return }
    setBusy(true)
    try {
      if (!/\.(wav|mp3|ogg)$/i.test(selected.name)) throw new Error('Choose a WAV, MP3 or Ogg recording.')
      if (selected.size > MAX_BYTES) throw new Error('Choose a recording smaller than 12 MB.')
      const decoded = await new OfflineAudioContext(1, 1, 44100).decodeAudioData(await selected.arrayBuffer())
      if (current !== generation.current.value) return
      if (!decoded.duration || decoded.duration > MAX_SECONDS) throw new Error('Choose a recording up to 90 seconds long.')
      const peaks = waveformPeaks(Array.from({ length: decoded.numberOfChannels }, (_, index) => decoded.getChannelData(index)))
      const url = URL.createObjectURL(selected)
      urls.current.push(url)
      setPrepared({ id: crypto.randomUUID(), url, duration: decoded.duration, peaks, credit: '' })
    } catch (failure) {
      if (current === generation.current.value) setError(failure instanceof Error ? failure.message : 'This recording could not be read.')
    } finally { if (current === generation.current.value) setBusy(false) }
  }

  function submit() {
    if (!prepared || !credit.trim() || !rights) return
    // Ownership moves to the prototype, which releases it on reset or unmount.
    urls.current.splice(urls.current.indexOf(prepared.url), 1)
    onAdd({ ...prepared, credit: credit.trim() })
    onClose()
  }

  return <dialog ref={dialog} className="app-dialog audio-submission-dialog" aria-labelledby="audio-submission-title" onCancel={event => { event.preventDefault(); onClose() }}>
    <form onSubmit={event => { event.preventDefault(); submit() }}>
      <div className="section-title"><h2 id="audio-submission-title">Add audio preview</h2><button type="button" className="icon-button" aria-label="Close audio preview form" onClick={onClose}><Icon name="close" size={18}/></button></div>
      <p className="audio-submission-module">{name}</p>
      <label className="audio-submission-file"><Icon name="file" size={22}/><span><strong>{file?.name ?? 'Choose audio file'}</strong><small>WAV / MP3 / Ogg · 12 MB · up to 90 seconds</small></span><input type="file" accept="audio/wav,audio/x-wav,audio/mpeg,audio/ogg,.wav,.mp3,.ogg" aria-label="Choose audio preview file" onChange={event => { void choose(event.target.files?.[0]) }}/></label>
      {busy && <p role="status" className="service-note">Preparing recording…</p>}
      {error && <p role="alert" className="file-error">{error}</p>}
      {prepared && <AudioPreviewPlayer key={prepared.id} clip={prepared} name={name}/>}
      <label className="audio-submission-credit">Credit<input required maxLength={100} value={credit} onChange={event => setCredit(event.target.value)} autoComplete="name" placeholder="Your name"/></label>
      <label className="audio-submission-rights"><input type="checkbox" required checked={rights} onChange={event => setRights(event.target.checked)}/><span>I have permission to share this recording.</span></label>
      <p className="service-note">This prototype adds the clip locally. Nothing is uploaded.</p>
      <div className="audio-submission-actions"><button type="button" className="button button-quiet" onClick={onClose}>Cancel</button><button type="submit" className="button button-primary" disabled={!prepared || !credit.trim() || !rights || busy}>Add preview</button></div>
    </form>
  </dialog>
}
