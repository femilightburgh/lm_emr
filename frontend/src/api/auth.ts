import type {
  AuthenticatedUser,
  LoginRequest,
  LoginResponse,
} from '../types'

import { apiRequest } from './client'


export async function login(
  payload: LoginRequest,
): Promise<LoginResponse> {
  return apiRequest<LoginResponse>(
    '/auth/login',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
  )
}


export async function refreshAccessToken(
  refreshToken: string,
): Promise<LoginResponse> {
  return apiRequest<LoginResponse>(
    '/auth/refresh',
    {
      method: 'POST',
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    },
  )
}


export async function getCurrentUser(
  accessToken: string,
): Promise<AuthenticatedUser> {
  return apiRequest<AuthenticatedUser>(
    '/auth/me',
    {},
    accessToken,
  )
}

export interface ActivateUserRequest {
  token: string
  password: string
}


export async function activateUser(
  payload: ActivateUserRequest,
): Promise<void> {
  return apiRequest<void>(
    '/auth/activate',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
  )
}