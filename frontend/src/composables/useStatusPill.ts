/**
 * frontend/src/composables/useStatusPill.ts
 *
 * Consistent mapping from app-level run/entity status strings to
 * the visual token set (StatusKind) and display labels.
 *
 * Mirrors the logic from static/js/service.scheduler.render.js:
 *   schStatusCls()   → resolveKind()
 *   schStatusLabel() → resolveLabel()
 *
 * This composable is page-agnostic. Any Vue component that needs to
 * display a run status, job enabled/disabled state, or similar boolean
 * status can use this composable instead of duplicating the mapping.
 *
 * Usage:
 *   const { resolveKind, resolveLabel, resolveRunStatus } = useStatusPill()
 */
import type { StatusKind } from '@/types/common'
import type { RunStatus } from '@/types/history'

// ---------------------------------------------------------------------------
// Static mapping tables
// ---------------------------------------------------------------------------

const RUN_STATUS_KIND: Record<string, StatusKind> = {
  queued:    'info',
  running:   'warning',
  success:   'success',
  finished:  'success',
  partial:   'warning',
  failed:    'error',
  skipped:   'info',
  cancelled: 'info',
  retry:     'warning',
}

const RUN_STATUS_LABEL: Record<string, string> = {
  queued:    '🕒 queued',
  running:   '⚙ running',
  success:   '✓ success',
  finished:  '✓ finished',
  partial:   '⚠ partial',
  failed:    '✗ failed',
  skipped:   '— skipped',
  cancelled: '— cancelled',
  retry:     '↺ retry',
}

// ---------------------------------------------------------------------------
// Composable
// ---------------------------------------------------------------------------

export interface StatusPillHelpers {
  /**
   * Resolve a StatusKind from a raw status string.
   * Falls back to 'info' for unknown values.
   */
  resolveKind: (status: string | null | undefined) => StatusKind
  /**
   * Resolve a display label from a raw status string.
   * Falls back to the raw value or '—' for unknown/null.
   */
  resolveLabel: (status: string | null | undefined) => string
  /**
   * Convenience: resolve both kind and label for a run status in one call.
   */
  resolveRunStatus: (status: RunStatus | string | null | undefined) => {
    kind: StatusKind
    label: string
  }
  /**
   * Resolve kind/label for a boolean enabled/disabled state.
   */
  resolveEnabledState: (enabled: boolean) => { kind: StatusKind; label: string }
}

export function useStatusPill(): StatusPillHelpers {
  function resolveKind(status: string | null | undefined): StatusKind {
    if (!status) return 'muted'
    return RUN_STATUS_KIND[status.toLowerCase()] ?? 'info'
  }

  function resolveLabel(status: string | null | undefined): string {
    if (!status) return '—'
    return RUN_STATUS_LABEL[status.toLowerCase()] ?? status
  }

  function resolveRunStatus(status: RunStatus | string | null | undefined) {
    return {
      kind: resolveKind(status ?? undefined),
      label: resolveLabel(status ?? undefined),
    }
  }

  function resolveEnabledState(enabled: boolean) {
    return enabled
      ? { kind: 'success' as StatusKind, label: 'enabled' }
      : { kind: 'error' as StatusKind, label: 'disabled' }
  }

  return { resolveKind, resolveLabel, resolveRunStatus, resolveEnabledState }
}

