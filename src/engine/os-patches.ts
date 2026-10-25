export const OS_LOAD_ADDRESS = 0x40000400
export type OsWrite = { address: number; guardLength: number; guardSha256: string; bytes: Uint8Array; note: string }
// At a slow tempo with a long TIME the stock DELAY reads past its 508-entry table into these
// zero bytes, the start of the overflow run, so nothing is written there (native: stock.DELAY_KEEP).
export const DELAY_TABLE_END = 0x400d24d0, DELAY_READS_PAST = 16

// Validate every extent and guard before copying or writing the local image.
// An error cannot leave a half-patched image for a later build to consume.
export async function applyGuardedOsWrites(original: Uint8Array, writes: readonly OsWrite[]): Promise<Uint8Array> {
  if (!original.length || original.length > 16 * 1024 * 1024 || writes.length > 4096) throw new Error('The OS write plan has invalid bounds.')
  const ordered = [...writes].sort((a, b) => a.address - b.address)
  let previousEnd = OS_LOAD_ADDRESS
  for (const write of ordered) {
    const offset = write.address - OS_LOAD_ADDRESS
    if (!Number.isInteger(write.address) || !Number.isInteger(write.guardLength) || offset < 0 || write.guardLength < 1 || write.bytes.length < 1 || write.bytes.length > write.guardLength || offset + write.guardLength > original.length || !/^[0-9a-f]{64}$/.test(write.guardSha256)) throw new Error('The OS write plan has an invalid guarded range.')
    if (write.address < previousEnd) throw new Error('The OS write plan contains overlapping guards.')
    if (write.address < DELAY_TABLE_END + DELAY_READS_PAST && write.address + write.guardLength > DELAY_TABLE_END) throw new Error(write.note + ' would write over the bytes the stock DELAY reads past its table.')
    previousEnd = write.address + write.guardLength
  }
  for (const write of ordered) {
    const offset = write.address - OS_LOAD_ADDRESS
    const digest = await crypto.subtle.digest('SHA-256', new Uint8Array(original.subarray(offset, offset + write.guardLength)).buffer)
    const hash = Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0')).join('')
    if (hash !== write.guardSha256) throw new Error('The original OS does not match the guard for ' + write.note + '.')
  }
  const result = new Uint8Array(original)
  for (const write of ordered) result.set(write.bytes, write.address - OS_LOAD_ADDRESS)
  return result
}
