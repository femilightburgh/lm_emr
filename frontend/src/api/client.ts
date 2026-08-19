const API_BASE_URL =
  'http://localhost:8000/api/v1'


export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  accessToken?: string,
): Promise<T> {
  const headers = new Headers({
    'Content-Type': 'application/json',
    ...(options.headers ?? {}),
  })

  if (accessToken) {
    headers.set(
      'Authorization',
      `Bearer ${accessToken}`,
    )
  }

  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,
      headers,
    },
  )

  if (!response.ok) {
    let detail = 'Request failed.'

    try {
      const body = await response.json()

      if (typeof body.detail === 'string') {
        detail = body.detail
      } else if (Array.isArray(body.detail)) {
        detail = body.detail
          .map(
            (item: {
              msg?: string
            }) => item.msg ?? 'Validation error.',
          )
          .join(' ')
      }
    } catch {
      // Ignore non-JSON error responses.
    }

    throw new Error(detail)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}