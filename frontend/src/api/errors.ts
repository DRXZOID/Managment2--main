/**
 * frontend/src/api/errors.ts — Typed API error class.
 *
 * ApiError is raised by the HTTP layer for any non-2xx response and
 * provides structured access to the HTTP status, raw status text, and
 * any server-provided error message.
 */

export class ApiError extends Error {
  /** HTTP status code (e.g. 400, 404, 500) */
  readonly status: number
  /** HTTP status text (e.g. "Bad Request") */
  readonly statusText: string
  /** Human-readable detail extracted from the server response body, if any. */
  readonly details: string | undefined

  constructor(
    status: number,
    statusText: string,
    message: string,
    details?: string,
  ) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.statusText = statusText
    this.details = details
  }

  /** True when the error is a client-side bad-request (4xx). */
  get isClientError(): boolean {
    return this.status >= 400 && this.status < 500
  }

  /** True when the error is a server-side failure (5xx). */
  get isServerError(): boolean {
    return this.status >= 500
  }

  /** True when the request was not found (404). */
  get isNotFound(): boolean {
    return this.status === 404
  }

  /** True when the request conflicted with current server state (409). */
  get isConflict(): boolean {
    return this.status === 409
  }
}

