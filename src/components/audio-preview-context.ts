import { createContext, useContext } from 'react'
import { moduleAudioPreviews, type AudioPreviewClip } from './audio-preview'

export type AudioPreviewContextValue = {
  clips: Readonly<Record<string, readonly AudioPreviewClip[]>>
  onAdd: (id: string) => void
}

// The prototype supplies local clips; ordinary pages use only declared module media.
export const AudioPreviewContext = createContext<AudioPreviewContextValue | null>(null)

export function useModuleAudioPreviews(id: string) {
  const context = useContext(AudioPreviewContext)
  return { clips: context?.clips[id] ?? moduleAudioPreviews(id), onAdd: context ? () => context.onAdd(id) : undefined }
}
