/**
 * frontend/src/types/history.ts — Scrape run history frontend DTO types.
 *
 * These reflect the shapes returned by:
 *   GET /api/scrape-runs          → { runs: ScrapeRunSummary[] }
 *   GET /api/scrape-runs/:id      → { run: ScrapeRunSummary }
 *   GET /api/admin/scrape/jobs/:id/runs → { runs: ScrapeRunSummary[] }
 *
 * RFC-012 retry-state flags are included as-is from the serializer.
 * Field names match the current serializer output (pricewatch/web/serializers.py).
 */
import type { StoreSummary } from './store'

// ---------------------------------------------------------------------------
// Run status
// ---------------------------------------------------------------------------

/**
 * RunStatus — the canonical set of run status values as seen in the DB/API.
 * Matches the status strings used in service.scheduler.render.js schStatusCls().
 */
export type RunStatus =
  | 'queued'
  | 'running'
  | 'success'
  | 'finished'
  | 'partial'
  | 'failed'
  | 'skipped'
  | 'cancelled'
  | 'retry'
  | (string & {})  // allow unknown future statuses

export type TriggerType = 'manual' | 'scheduled' | (string & {})

// ---------------------------------------------------------------------------
// Scrape run summary
// ---------------------------------------------------------------------------

export interface ScrapeRunSummary {
  id: number
  store_id: number | null
  store: StoreSummary | null
  job_id: number | null
  run_type: string
  trigger_type: TriggerType | null
  status: RunStatus
  attempt: number
  queued_at: string | null
  started_at: string | null
  finished_at: string | null
  worker_id: string | null
  categories_processed: number | null
  products_processed: number | null
  products_created: number | null
  products_updated: number | null
  price_changes_detected: number | null
  error_message: string | null
  metadata_json: Record<string, unknown> | null
  checkpoint_out_json: Record<string, unknown> | null
  // RFC-012 §5.4 retry-state flags
  retryable: boolean
  retry_of_run_id: number | null
  retry_processed: boolean
  retry_exhausted: boolean
}

