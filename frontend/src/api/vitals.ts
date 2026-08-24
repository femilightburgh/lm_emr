import { apiRequest } from './client'


// ============================================================================
// Vitals
// ============================================================================


export interface CreateVitalsRequest {
  encounter_id: string
  occurred_at: string

  temperature?: number | null
  heart_rate?: number | null
  respiratory_rate?: number | null

  systolic_bp?: number | null
  diastolic_bp?: number | null

  spo2?: number | null
  weight?: number | null
}


export interface VitalsPayload {
  temperature?: number | null
  heart_rate?: number | null
  respiratory_rate?: number | null

  systolic_bp?: number | null
  diastolic_bp?: number | null

  spo2?: number | null
  weight?: number | null
}


export interface Vitals {
  id: string

  encounter_id: string

  event_type: string

  performed_by: string

  occurred_at: string

  payload: VitalsPayload
}


// ============================================================================
// Create
// ============================================================================


export async function createVitals(
  accessToken: string,
  payload: CreateVitalsRequest,
): Promise<Vitals> {
  return apiRequest<Vitals>(
    '/vitals',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    accessToken,
  )
}


// ============================================================================
// List Encounter Vitals
// ============================================================================


export async function listEncounterVitals(
  accessToken: string,
  encounterId: string,
): Promise<Vitals[]> {
  return apiRequest<Vitals[]>(
    `/vitals/encounters/${encounterId}`,
    {},
    accessToken,
  )
}
