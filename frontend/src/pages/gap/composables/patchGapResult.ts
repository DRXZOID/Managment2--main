/**
 * patchGapResult.ts — Pure helper to apply a local status update to a GapResult.
 *
 * Used after a successful POST /api/gap/status to avoid a full reload.
 * Does NOT mutate — returns a new GapResult with updated item status and summary.
 */
import type { GapResult, GapItemStatus } from '@/types/gap'

/**
 * Return a new GapResult with the given item's status changed and summary recalculated.
 * If the item is not found, returns the original result unchanged.
 */
export function patchGapItemStatus(
  result: GapResult,
  targetProductId: number,
  newStatus: GapItemStatus,
): GapResult {
  let found = false

  const updatedGroups = result.groups.map((group) => ({
    ...group,
    items: group.items.map((item) => {
      if (item.target_product?.id === targetProductId) {
        found = true
        return { ...item, status: newStatus }
      }
      return item
    }),
  }))

  if (!found) return result

  // Recalculate summary counters from the updated items
  let newCount = 0
  let inProgressCount = 0
  let doneCount = 0
  for (const group of updatedGroups) {
    for (const item of group.items) {
      if (item.status === 'new') newCount++
      else if (item.status === 'in_progress') inProgressCount++
      else if (item.status === 'done') doneCount++
    }
  }

  return {
    ...result,
    groups: updatedGroups,
    summary: {
      total: result.summary.total,
      new: newCount,
      in_progress: inProgressCount,
      done: doneCount,
    },
  }
}

