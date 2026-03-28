/**
 * useGapActions.ts — Gap item status action for POST /api/gap/status.
 *
 * Tracks which target_product_id is currently being updated so the row
 * button can show a spinner without blocking the rest of the UI.
 */
import { ref } from 'vue'
import type { Ref } from 'vue'
import { postGapStatus } from '@/api/gap'
import type { GapItemStatus } from '@/types/gap'

export interface GapActionsState {
  actionInProgressId: Ref<number | null>
  actionError: Ref<string | null>
  setStatus: (
    referenceCategoryId: number,
    targetProductId: number,
    status: GapItemStatus,
  ) => Promise<boolean>
}

export function useGapActions(): GapActionsState {
  const actionInProgressId = ref<number | null>(null)
  const actionError = ref<string | null>(null)

  /**
   * Returns true on success, false on failure.
   * Caller is responsible for reloading gap data on success.
   */
  async function setStatus(
    referenceCategoryId: number,
    targetProductId: number,
    status: GapItemStatus,
  ): Promise<boolean> {
    actionInProgressId.value = targetProductId
    actionError.value = null
    try {
      await postGapStatus(referenceCategoryId, targetProductId, status)
      return true
    } catch (err) {
      actionError.value = 'Помилка зміни статусу: ' + (err instanceof Error ? err.message : String(err))
      return false
    } finally {
      actionInProgressId.value = null
    }
  }

  return { actionInProgressId, actionError, setStatus }
}

