const API_BASE_URL =
  (import.meta.env.VITE_API_BASE as string) || `${window.location.origin}/api/v1`


const ACCESS_TOKEN_KEY =
  'lightburgh_access_token'

const REFRESH_TOKEN_KEY =
  'lightburgh_refresh_token'


let refreshPromise:
  Promise<string | null> | null = null


async function refreshAccessToken(): Promise<string | null> {
  const refreshToken =
    sessionStorage.getItem(
      REFRESH_TOKEN_KEY,
    )

  if (!refreshToken) {
    return null
  }

  if (!refreshPromise) {
    refreshPromise = (async () => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/auth/refresh`,
          {
            method: 'POST',
            headers: {
              'Content-Type':
                'application/json',
            },
            body: JSON.stringify({
              refresh_token:
                refreshToken,
            }),
          },
        )

        if (!response.ok) {
          sessionStorage.removeItem(
            ACCESS_TOKEN_KEY,
          )

          sessionStorage.removeItem(
            REFRESH_TOKEN_KEY,
          )

          sessionStorage.removeItem(
            'lightburgh_user',
          )

          return null
        }

        const tokens =
          await response.json() as {
            access_token: string
            refresh_token: string
            token_type?: string
          }

        sessionStorage.setItem(
          ACCESS_TOKEN_KEY,
          tokens.access_token,
        )

        sessionStorage.setItem(
          REFRESH_TOKEN_KEY,
          tokens.refresh_token,
        )

        window.dispatchEvent(
          new CustomEvent(
            'lightburgh:session-refreshed',
            { detail: tokens },
          ),
        )

        return tokens.access_token
      } catch {
        return null
      } finally {
        refreshPromise = null
      }
    })()
  }

  return refreshPromise
}


async function parseError(
  response: Response,
): Promise<string> {
  let detail =
    `Request failed (${response.status}).`

  try {
    const body =
      await response.json()

    if (
      typeof body.detail ===
      'string'
    ) {
      detail = body.detail
    } else if (
      Array.isArray(body.detail)
    ) {
      detail = body.detail
        .map(
          (item: {
            loc?: unknown
            msg?: string
            type?: string
          }) => {
            const location =
              Array.isArray(item.loc)
                ? item.loc.join('.')
                : ''

            const message =
              item.msg ??
              'Validation error.'

            return location
              ? `${location}: ${message}`
              : message
          },
        )
        .join(' ')
    } else {
      detail = JSON.stringify(body)
    }
  } catch {
    const raw =
      await response.text().catch(
        () => '',
      )

    if (raw) {
      detail =
        `Request failed (${response.status}): ${raw}`
    }
  }

  return detail
}


export async function apiRequestBlob(
  path: string,
  options: RequestInit = {},
  accessToken?: string,
): Promise<Blob> {
  const headers = new Headers(
    options.headers ?? {},
  )

  const currentAccessToken =
    accessToken ??
    sessionStorage.getItem(
      ACCESS_TOKEN_KEY,
    )

  if (currentAccessToken) {
    headers.set(
      'Authorization',
      `Bearer ${currentAccessToken}`,
    )
  }

  let response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,
      headers,
    },
  )

  if (
    response.status === 401 &&
    currentAccessToken &&
    path !== '/auth/refresh'
  ) {
    const newAccessToken =
      await refreshAccessToken()

    if (newAccessToken) {
      const retryHeaders =
        new Headers(
          options.headers ?? {},
        )

      retryHeaders.set(
        'Authorization',
        `Bearer ${newAccessToken}`,
      )

      response = await fetch(
        `${API_BASE_URL}${path}`,
        {
          ...options,
          headers: retryHeaders,
        },
      )
    }
  }

  if (!response.ok) {
    const detail =
      await parseError(response)

    throw new Error(detail)
  }

  return response.blob()
}


export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  accessToken?: string,
): Promise<T> {
  const headers = new Headers(
    options.headers ?? {},
  )

  if (!(options.body instanceof FormData)) {
    headers.set(
      'Content-Type',
      'application/json',
    )
  }

  const currentAccessToken =
    accessToken ??
    sessionStorage.getItem(
      ACCESS_TOKEN_KEY,
    )

  if (currentAccessToken) {
    headers.set(
      'Authorization',
      `Bearer ${currentAccessToken}`,
    )
  }

  let response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,
      headers,
    },
  )


  // ========================================================================
  // Access-token refresh
  // ========================================================================

  if (
    response.status === 401 &&
    currentAccessToken &&
    path !== '/auth/refresh'
  ) {
    const newAccessToken =
      await refreshAccessToken()

    if (newAccessToken) {
      const retryHeaders =
        new Headers(
          options.headers ?? {},
        )

      if (!(options.body instanceof FormData)) {
        retryHeaders.set(
          'Content-Type',
          'application/json',
        )
      }

      retryHeaders.set(
        'Authorization',
        `Bearer ${newAccessToken}`,
      )

      response = await fetch(
        `${API_BASE_URL}${path}`,
        {
          ...options,
          headers: retryHeaders,
        },
      )
    }
  }


  if (!response.ok) {
    const detail =
      await parseError(response)

    throw new Error(detail)
  }


  if (response.status === 204) {
    return undefined as T
  }


  return response.json() as Promise<T>
}
