import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it } from 'vitest'
import { MissingNote, type ProjectNeeds } from './OctatrackUpdate'

const note = (needs: ProjectNeeds) => renderToStaticMarkup(createElement(MissingNote, { needs })).replace(/<[^>]+>/g, '')

describe('what the unit’s project needs', () => {
  it('names the missing modules and offers to add them, or says a load brings them back', () => {
    expect(note({ names: ['E-Verb', 'Tape Echo'], unknown: [], add: () => {} })).toBe('Your project uses E-Verb and Tape Echo, which aren’t on your Octatrack. Add to set')
    expect(note({ names: ['E-Verb'], unknown: [] })).toBe('Your project uses E-Verb, which isn’t on your Octatrack. Load onto Octatrack to bring it back.')
  })
  it('names modules the library does not know, and nothing when nothing is missing', () => {
    expect(note({ names: ['E-Verb'], unknown: ['Foo'] })).toMatch(/ It also uses Foo, which isn’t in the library\.$/)
    expect(note({ names: [], unknown: ['Foo', 'Bar'] })).toBe('Your project uses Foo and Bar, which aren’t in the library.')
    expect(note({ names: [], unknown: [] })).toBe('')
  })
})
