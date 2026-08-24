import type {
  CreatePatientRequest,
  Patient,
  PatientListResponse,
} from '../types'

import { apiRequest } from './client'


// ============================================================================
// Patient Types
// ============================================================================

export type {
  Patient,
  PatientListResponse,
  CreatePatientRequest,
}


// ============================================================================
// List Patients
// ============================================================================

export async function listPatients(
  accessToken: string,
): Promise<PatientListResponse> {
  return apiRequest<PatientListResponse>(
    '/patients',
    {},
    accessToken,
  )
}


// ============================================================================
// Search Patients
// ============================================================================

export async function searchPatients(
  accessToken: string,
  query: string,
): Promise<PatientListResponse> {
  const params =
    new URLSearchParams()

  if (query.trim()) {
    params.set(
      'name',
      query.trim(),
    )
  }

  const queryString =
    params.toString()

  return apiRequest<PatientListResponse>(
    queryString
      ? `/patients?${queryString}`
      : '/patients',
    {},
    accessToken,
  )
}


// ============================================================================
// Retrieve Patient
// ============================================================================

export async function getPatient(
  accessToken: string,
  patientId: string,
): Promise<Patient> {
  return apiRequest<Patient>(
    `/patients/${patientId}`,
    {},
    accessToken,
  )
}


// ============================================================================
// Create Patient
// ============================================================================

export async function createPatient(
  accessToken: string,
  payload: CreatePatientRequest,
): Promise<Patient> {
  return apiRequest<Patient>(
    '/patients',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    accessToken,
  )
}