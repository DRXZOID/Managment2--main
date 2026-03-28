import { describe, it, expect } from 'vitest'
import { ApiError } from '@/api/errors'

describe('ApiError', () => {
  it('is an instance of Error', () => {
    const err = new ApiError(404, 'Not Found', 'Resource not found')
    expect(err).toBeInstanceOf(Error)
    expect(err).toBeInstanceOf(ApiError)
  })

  it('sets name to ApiError', () => {
    const err = new ApiError(400, 'Bad Request', 'Invalid input')
    expect(err.name).toBe('ApiError')
  })

  it('exposes status and statusText', () => {
    const err = new ApiError(422, 'Unprocessable Entity', 'Validation failed')
    expect(err.status).toBe(422)
    expect(err.statusText).toBe('Unprocessable Entity')
    expect(err.message).toBe('Validation failed')
  })

  it('exposes optional details', () => {
    const err = new ApiError(400, 'Bad Request', 'Something failed', 'source_key is required')
    expect(err.details).toBe('source_key is required')
  })

  it('details is undefined when not provided', () => {
    const err = new ApiError(500, 'Internal Server Error', 'Oops')
    expect(err.details).toBeUndefined()
  })

  describe('isClientError', () => {
    it('true for 4xx', () => {
      expect(new ApiError(400, '', '').isClientError).toBe(true)
      expect(new ApiError(404, '', '').isClientError).toBe(true)
      expect(new ApiError(499, '', '').isClientError).toBe(true)
    })
    it('false for 5xx', () => {
      expect(new ApiError(500, '', '').isClientError).toBe(false)
    })
    it('false for 2xx (edge case)', () => {
      expect(new ApiError(200, '', '').isClientError).toBe(false)
    })
  })

  describe('isServerError', () => {
    it('true for 5xx', () => {
      expect(new ApiError(500, '', '').isServerError).toBe(true)
      expect(new ApiError(503, '', '').isServerError).toBe(true)
    })
    it('false for 4xx', () => {
      expect(new ApiError(404, '', '').isServerError).toBe(false)
    })
  })

  describe('isNotFound', () => {
    it('true for 404 only', () => {
      expect(new ApiError(404, '', '').isNotFound).toBe(true)
      expect(new ApiError(400, '', '').isNotFound).toBe(false)
    })
  })

  describe('isConflict', () => {
    it('true for 409 only', () => {
      expect(new ApiError(409, '', '').isConflict).toBe(true)
      expect(new ApiError(404, '', '').isConflict).toBe(false)
    })
  })
})

