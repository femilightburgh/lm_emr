import type {
  AuthenticatedUser,
  LoginResponse,
} from './types'

const ACCESS_TOKEN_KEY = 'lightburgh_access_token'
const REFRESH_TOKEN_KEY = 'lightburgh_refresh_token'
const USER_KEY = 'lightburgh_user'

export function saveSession(
  tokens: LoginResponse,
  user: AuthenticatedUser,
): void {
  sessionStorage.setItem(
    ACCESS_TOKEN_KEY,
    tokens.access_token,
  )

  sessionStorage.setItem(
    REFRESH_TOKEN_KEY,
    tokens.refresh_token,
  )

  sessionStorage.setItem(
    USER_KEY,
    JSON.stringify(user),
  )
}

export function getAccessToken(): string | null {
  return sessionStorage.getItem(
    ACCESS_TOKEN_KEY,
  )
}

export function getRefreshToken(): string | null {
  return sessionStorage.getItem(
    REFRESH_TOKEN_KEY,
  )
}

export function getStoredUser(): AuthenticatedUser | null {
  const value = sessionStorage.getItem(
    USER_KEY,
  )

  if (!value) {
    return null
  }

  try {
    return JSON.parse(value) as AuthenticatedUser
  } catch {
    return null
  }
}

export function clearSession(): void {
  sessionStorage.removeItem(
    ACCESS_TOKEN_KEY,
  )

  sessionStorage.removeItem(
    REFRESH_TOKEN_KEY,
  )

  sessionStorage.removeItem(
    USER_KEY,
  )
}