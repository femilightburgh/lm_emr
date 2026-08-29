import { apiRequest } from './client'


// ============================================================================
// Types
// ============================================================================


export interface Encounter {
  id: string

  episode_id: string

  staff_id: string

  title: string

  status:
    | 'OPEN'
    | 'CLOSED'

  started_at: string

  ended_at: string | null
}


export type ClinicalEventType =
  | string


export interface ClinicalEvent {
  id: string

  encounter_id: string

  event_type: ClinicalEventType

  performed_by: string

  occurred_at: string

  payload: Record<string, unknown> | null

  created_at: string

  updated_at: string
}


// ============================================================================
// Episode Encounters
// ============================================================================


export async function createEncounter(
  accessToken: string,
  payload: {
    episode_id: string
    staff_id: string
    title: string
  },
): Promise<Encounter> {
  return apiRequest<Encounter>(
    '/encounters',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    accessToken,
  )
}


export async function listEpisodeEncounters(
  accessToken: string,
  episodeId: string,
): Promise<Encounter[]> {
  return apiRequest<Encounter[]>(
    `/encounters/episode/${episodeId}`,
    {},
    accessToken,
  )
}


// ============================================================================
// Retrieve Encounter
// ============================================================================


export async function getEncounter(
  accessToken: string,
  encounterId: string,
): Promise<Encounter> {
  return apiRequest<Encounter>(
    `/encounters/${encounterId}`,
    {},
    accessToken,
  )
}


// ============================================================================
// Encounter Clinical Timeline
// ============================================================================


export async function getEncounterTimeline(
  accessToken: string,
  encounterId: string,
): Promise<ClinicalEvent[]> {
  return apiRequest<ClinicalEvent[]>(
    `/encounters/${encounterId}/timeline`,
    {},
    accessToken,
  )
}


// ============================================================================
// Close Encounter
// ============================================================================


export async function closeEncounter(
  accessToken: string,
  encounterId: string,
): Promise<Encounter> {
  return apiRequest<Encounter>(
    `/encounters/${encounterId}/close`,
    {
      method: 'POST',
    },
    accessToken,
  )
}
export async function listDoctorQueue(
  accessToken: string,
): Promise<Encounter[]> {
  return apiRequest<Encounter[]>(
    '/encounters/queue/doctor',
    {},
    accessToken,
  )
}
