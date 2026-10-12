import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import { USB_LINK } from './protocol'

describe('firmware protocol flags', () => {
  it('keeps the development USB flag in the browser', () => {
    expect(USB_LINK).toBe(import.meta.env.DEV)
  })
  it('imports the native compatibility verifier in Node without Vite environment values', () => {
    const verifier = fileURLToPath(new URL('../../scripts/native-comparison.mjs', import.meta.url))
    const protocol = fileURLToPath(new URL('./protocol.ts', import.meta.url))
    const result = execFileSync(process.execPath, ['--input-type=module', '-e',
      'await import(process.argv[1]); const { USB_LINK } = await import(process.argv[2]); console.log(JSON.stringify(USB_LINK))',
      verifier, protocol], { encoding: 'utf8' })
    expect(JSON.parse(result)).toBe(false)
  })
})
