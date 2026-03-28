/**
 * frontend/src/composables/useAsyncState.ts
 *
 * Generic composable for promise-driven loading / error / success UI state.
 *
 * Page-agnostic: has no knowledge of scheduler, stores, or any domain entity.
 * Can be reused for any async action across all future Vue islands.
 *
 * Usage:
 *   const { loading, error, data, execute, reset } = useAsyncState<MyType>()
 *
 *   async function loadSomething() {
 *     await execute(() => fetchSomething())
 *   }
 */
import { ref } from 'vue'
import type { Ref } from 'vue'

export interface AsyncState<T> {
  /** True while the promise is pending. */
  loading: Ref<boolean>
  /** The error from the last failed execution, or null. */
  error: Ref<Error | null>
  /** The resolved value from the last successful execution, or null. */
  data: Ref<T | null>
  /**
   * Execute an async factory function.
   * Sets loading=true, clears previous error, resolves data or sets error.
   * Returns the resolved value, or undefined on failure.
   */
  execute: (factory: () => Promise<T>) => Promise<T | undefined>
  /** Reset all state to initial (loading=false, error=null, data=null). */
  reset: () => void
}

export function useAsyncState<T>(): AsyncState<T> {
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const data = ref<T | null>(null) as Ref<T | null>

  async function execute(factory: () => Promise<T>): Promise<T | undefined> {
    loading.value = true
    error.value = null
    try {
      const result = await factory()
      data.value = result
      return result
    } catch (err) {
      error.value = err instanceof Error ? err : new Error(String(err))
      return undefined
    } finally {
      loading.value = false
    }
  }

  function reset(): void {
    loading.value = false
    error.value = null
    data.value = null
  }

  return { loading, error, data, execute, reset }
}
