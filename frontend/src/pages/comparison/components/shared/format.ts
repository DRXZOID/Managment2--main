/**
 * format.ts — Price/label formatting utilities for the comparison page.
 */
import type { ComparisonProduct, EligibleProduct } from '../../types'

type PriceHolder = { price?: string | number | null; currency?: string | null } | null | undefined

export function formatPrice(p: PriceHolder): string {
  if (!p) return '—'
  const v = p.price
  if (v == null || v === '') return '—'
  const num = typeof v === 'string' ? parseFloat(v) : (v as number)
  if (isNaN(num)) return String(v)
  return p.currency ? `${num.toFixed(2)} ${p.currency}` : num.toFixed(2)
}

export function productLabel(p: ComparisonProduct | null | undefined): string {
  return p?.name ?? '—'
}

export function eligibleProductLabel(p: EligibleProduct): string {
  const price = formatPrice(p)
  const cat   = p.category?.name ? ` — ${p.category.name}` : ''
  return `${p.name ?? '—'} — ${price}${cat}`
}

