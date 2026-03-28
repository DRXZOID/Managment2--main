/**
 * frontend/src/composables/useDialogState.ts
 *
 * Composable for managing open/close/reset state of a modal dialog.
 *
 * Page-agnostic: stores only the structural open/close/data state.
 * The dialog content and business logic live in the component that
 * uses this composable.
 *
 * Usage:
 *   const dialog = useDialogState<MyPayload>()
 *   dialog.open({ id: 1, name: 'test' })   // opens with context
 *   dialog.close()                          // closes and resets
 *   if (dialog.isOpen.value) { ... }
 *   const payload = dialog.payload.value    // null when closed
 */
import { ref } from 'vue'
import type { Ref } from 'vue'

export interface DialogState<T = unknown> {
  /** True when the dialog is open. */
  isOpen: Ref<boolean>
  /**
   * The payload passed when opening the dialog.
   * Null when the dialog is closed or no payload was provided.
   */
  payload: Ref<T | null>
  /** Open the dialog, optionally providing a context payload. */
  open: (payload?: T) => void
  /** Close the dialog and clear the payload. */
  close: () => void
  /** Alias for close() — useful for "cancel" button handlers. */
  reset: () => void
}

export function useDialogState<T = unknown>(): DialogState<T> {
  const isOpen = ref(false)
  const payload = ref<T | null>(null) as Ref<T | null>

  function open(p?: T): void {
    payload.value = p ?? null
    isOpen.value = true
  }

  function close(): void {
    isOpen.value = false
    payload.value = null
  }

  return { isOpen, payload, open, close, reset: close }
}
