/**
 * frontend/src/pages/comparison/types.ts — Comparison page DTO types.
 *
 * Mirrors shapes returned by:
 *   POST /api/comparison
 *   POST /api/comparison/match-decision
 *   GET  /api/comparison/eligible-target-products
 */

export type MatchStatus = 'confirmed' | 'rejected'

// ---------------------------------------------------------------------------
// Shared sub-shapes
// ---------------------------------------------------------------------------

export interface ComparisonProduct {
  id: number
  name: string | null
  price: string | number | null
  currency: string | null
  product_url: string | null
}

export interface ComparisonCategory {
  id?: number
  name: string | null
  store_name?: string | null
}

// ---------------------------------------------------------------------------
// Confirmed / auto-suggestion matches
// ---------------------------------------------------------------------------

export interface ConfirmedMatch {
  is_confirmed: boolean
  reference_product: ComparisonProduct | null
  target_product: ComparisonProduct | null
  target_category: ComparisonCategory | null
  score_percent: number | null
  score_details: Record<string, unknown> | null
}

// ---------------------------------------------------------------------------
// Candidate groups
// ---------------------------------------------------------------------------

export interface Candidate {
  target_product: ComparisonProduct | null
  target_category: ComparisonCategory | null
  score_percent: number | null
  score_details: Record<string, unknown> | null
  can_accept: boolean
  disabled_reason: string | null
}

export interface CandidateGroup {
  reference_product: ComparisonProduct | null
  candidates: Candidate[]
}

// ---------------------------------------------------------------------------
// Reference-only / target-only
// ---------------------------------------------------------------------------

export interface ReferenceOnlyItem {
  reference_product: ComparisonProduct | null
}

export interface TargetOnlyItem {
  target_product: ComparisonProduct | null
  target_category: ComparisonCategory | null
}

// ---------------------------------------------------------------------------
// Comparison result
// ---------------------------------------------------------------------------

export interface ComparisonSummary {
  candidate_groups: number
  reference_only: number
  target_only: number
}

export interface ComparisonResult {
  confirmed_matches: ConfirmedMatch[]
  candidate_groups: CandidateGroup[]
  reference_only: ReferenceOnlyItem[]
  target_only: TargetOnlyItem[]
  summary: ComparisonSummary
}

// ---------------------------------------------------------------------------
// Eligible target products (manual picker)
// ---------------------------------------------------------------------------

export interface EligibleProduct {
  id: number
  name: string | null
  price: string | number | null
  currency: string | null
  category: { id?: number; name?: string | null } | null
}

// ---------------------------------------------------------------------------
// Mapped target category (from /api/categories/<id>/mapped-target-categories)
// ---------------------------------------------------------------------------

export interface MappedTarget {
  target_category_id: number
  target_category_name: string
  target_store_id?: number | null
  target_store_name?: string | null
  match_type?: string | null
}

// ---------------------------------------------------------------------------
// Request bodies
// ---------------------------------------------------------------------------

export interface ComparisonRequestBody {
  reference_category_id: number
  target_category_ids: number[]
  target_store_id?: number | null
}

export interface MatchDecisionBody {
  reference_product_id: number
  target_product_id: number
  match_status: MatchStatus
  target_category_ids?: number[]
}

