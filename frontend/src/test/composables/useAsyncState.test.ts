import { describe, it, expect } from 'vitest'
import { useAsyncState } from '@/composables/useAsyncState'

describe('useAsyncState', () => {
  it('starts with loading=false, error=null, data=null', () => {
    const { loading, error, data } = useAsyncState<string>()
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
    expect(data.value).toBeNull()
  })

  it('sets loading=true while executing', async () => {
    const { loading, execute } = useAsyncState<string>()
    let resolvePromise!: (v: string) => void
    const pending = new Promise<string>((r) => { resolvePromise = r })

    const task = execute(() => pending)
    expect(loading.value).toBe(true)

    resolvePromise('done')
    await task
    expect(loading.value).toBe(false)
  })

  it('sets data on success', async () => {
    const { data, execute } = useAsyncState<number>()
    await execute(async () => 42)
    expect(data.value).toBe(42)
  })

  it('returns the resolved value from execute', async () => {
    const { execute } = useAsyncState<string>()
    const result = await execute(async () => 'hello')
    expect(result).toBe('hello')
  })

  it('sets error on failure and returns undefined', async () => {
    const { error, data, execute } = useAsyncState<string>()
    const boom = new Error('network failure')
    const result = await execute(async () => { throw boom })
    expect(error.value).toBe(boom)
    expect(data.value).toBeNull()
    expect(result).toBeUndefined()
  })

  it('clears previous error on new execution', async () => {
    const { error, execute } = useAsyncState<string>()
    await execute(async () => { throw new Error('first') })
    expect(error.value).not.toBeNull()

    await execute(async () => 'ok')
    expect(error.value).toBeNull()
  })

  it('wraps non-Error thrown values in Error', async () => {
    const { error, execute } = useAsyncState<void>()
    await execute(async () => { throw 'plain string error' })  // eslint-disable-line no-throw-literal
    expect(error.value).toBeInstanceOf(Error)
    expect(error.value?.message).toContain('plain string error')
  })

  it('reset clears all state', async () => {
    const { loading, error, data, execute, reset } = useAsyncState<number>()
    await execute(async () => 99)
    reset()
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
    expect(data.value).toBeNull()
  })
})

