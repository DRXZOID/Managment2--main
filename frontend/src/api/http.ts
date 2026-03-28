/**
 * frontend/src/api/http.ts — Low-level typed fetch wrapper.
 *
 * Responsibilities:
 * - wraps browser `fetch`
 * - centralizes JSON parsing
 * - sets correct Accept / Content-Type headers
 * - converts non-2xx responses to ApiError with server message when available
 *
 * This module has no knowledge of specific API endpoints.
 * All endpoint logic lives in api/client.ts or api/adapters/*.
 */
import { ApiError } from './errors'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

export interface JsonRequestInit {
  method?: HttpMethod
  body?: unknown
  signal?: AbortSignal
  headers?: Record<string, string>
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Build the RequestInit for a JSON request.
 * Sets Content-Type only when a body is present.
 */
function buildInit(opts: JsonRequestInit = {}): RequestInit {
  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...opts.headers,
  }
  const init: RequestInit = {
    method: opts.method ?? 'GET',
    headers,
    signal: opts.signal,
  }
  if (opts.body !== undefined) {
    headers['Content-Type'] = 'application/json'
    init.body = JSON.stringify(opts.body)
  }
  return init
}

/**
 * Extract a human-readable error message from a response body.
 * Tries common server-side error field names before falling back to statusText.
 */
async function extractErrorMessage(
  response: Response,
  fallback: string,
): Promise<string> {
  try {
    const json = await response.json()
    return (
      json?.message ??
      json?.error ??
      json?.detail ??
      fallback
    )
  } catch {
    return fallback
  }
}

// ---------------------------------------------------------------------------
// Core
// ---------------------------------------------------------------------------

/**
 * requestJson<T> — perform an HTTP request and return the parsed JSON body.
 *
 * Throws `ApiError` for any non-2xx response.
 * Throws native `TypeError` for network failures (propagated from fetch).
 *
 * @param input  URL string or Request object.
 * @param opts   Optional request options (method, body, headers, signal).
 * @returns      Parsed response body typed as T.
 */
export async function requestJson<T = unknown>(
  input: string | URL,
  opts: JsonRequestInit = {},
): Promise<T> {
  const init = buildInit(opts)
  const response = await fetch(input as string, init)

  if (!response.ok) {
    const fallback = response.statusText || `HTTP ${response.status}`
    const message = await extractErrorMessage(response, fallback)
    throw new ApiError(response.status, response.statusText, message, message)
  }

  // Handle 204 No Content — return empty object cast to T
  if (response.status === 204) {
    return {} as T
  }

  return response.json() as Promise<T>
}

