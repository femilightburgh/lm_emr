import type {
  AuthenticatedUser,
  CreatePatientRequest,
  LoginRequest,
  LoginResponse,
  Patient,
  PatientListResponse,
} from './types'

const API_BASE_URL = 'http://localhost:8000/api/v1'


async function request<T>(
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
      detail = body.detail ?? detail
    } catch {
      // Ignore non-JSON error responses.
    }

    throw new Error(detail)
  }

  return response.json() as Promise<T>
}


// ============================================================================
// Authentication
// ============================================================================


export async function login(
  payload: LoginRequest,
): Promise<LoginResponse> {
  return request<LoginResponse>(
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
  return request<LoginResponse>(
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
  return request<AuthenticatedUser>(
    '/auth/me',
    {},
    accessToken,
  )
}


// ============================================================================
// Patients
// ============================================================================


export async function listPatients(
  accessToken: string,
): Promise<PatientListResponse> {
  return request<PatientListResponse>(
    '/patients',
    {},
    accessToken,
  )
}


export async function searchPatients(
  accessToken: string,
  query: string,
): Promise<PatientListResponse> {
  const params = new URLSearchParams()

  if (query.trim()) {
    params.set('name', query.trim())
  }

  return request<PatientListResponse>(
    `/patients?${params.toString()}`,
    {},
    accessToken,
  )
}


export async function getPatient(
  accessToken: string,
  patientId: string,
): Promise<Patient> {
  return request<Patient>(
    `/patients/${patientId}`,
    {},
    accessToken,
  )
}


export async function createPatient(
  accessToken: string,
  payload: CreatePatientRequest,
): Promise<Patient> {
  return request<Patient>(
    '/patients',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    accessToken,
  )
}