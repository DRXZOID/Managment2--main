import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { requestJson } from '@/api/http'
import { ApiError } from '@/api/errors'

// ---------------------------------------------------------------------------
// fetch mock helpers
// ---------------------------------------------------------------------------

function makeFetchResponse(
  body: unknown,
  status: number,
  statusText = 'OK',
): Response {
  const json = JSON.stringify(body)
  return new Response(json, {
    status,
    statusText,
    headers: { 'Content-Type': 'application/json' },
  })
}

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn())
})

afterEach(() => {
  vi.unstubAllGlobals()
})

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('requestJson', () => {
  it('returns parsed JSON on 200', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      makeFetchResponse({ stores: [] }, 200),
    )
    const result = await requestJson<{ stores: unknown[] }>('/api/stores')
    expect(result).toEqual({ stores: [] })
  })

  it('throws ApiError for 404 with server message', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      makeFetchResponse({ error: 'Not found' }, 404, 'Not Found'),
    )
    await expect(requestJson('/api/stores/999')).rejects.toSatisfy(
      (e: unknown) =>
        e instanceof ApiError &&
        (e as ApiError).status === 404 &&
        (e as ApiError).message === 'Not found',
    )
  })

  it('throws ApiError for 500 using statusText as fallback', async () => {
    // response body is not valid JSON — fallback to statusText
    const response = new Response('Internal Server Error', {
      status: 500,
      statusText: 'Internal Server Error',
    })
    vi.mocked(fetch).mockResolvedValueOnce(response)
    await expect(requestJson('/api/stores')).rejects.toSatisfy(
      (e: unknown) => e instanceof ApiError && (e as ApiError).status === 500,
    )
  })

  it('sends JSON body and Content-Type header for POST', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      makeFetchResponse({ job: { id: 1 } }, 201, 'Created'),
    )
    await requestJson('/api/admin/scrape/jobs', {
      method: 'POST',
      body: { source_key: 'test', runner_type: 'store_category_sync' },
    })
    const [, init] = vi.mocked(fetch).mock.calls[0]
    const headers = init?.headers as Record<string, string>
    expect(headers['Content-Type']).toBe('application/json')
    expect(init?.body).toContain('source_key')
  })

  it('returns empty object for 204 No Content', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(null, { status: 204 }),
    )
    const result = await requestJson('/api/something')
    expect(result).toEqual({})
  })

  it('always sets Accept: application/json', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse({}, 200))
    await requestJson('/api/stores')
    const [, init] = vi.mocked(fetch).mock.calls[0]
    const headers = init?.headers as Record<string, string>
    expect(headers['Accept']).toBe('application/json')
  })
})

