import { apiRequest } from './client'


// ============================================================================
// Episodes
// ============================================================================


export interface CreateEpisodeRequest {
  patient_id: string
  title: string
}


export interface Episode {
  id: string
  hospital_id: string
  patient_id: string
  managing_doctor_id: string | null
  episode_number: string
  title: string

  status:
    | 'OPEN'
    | 'ADMITTED'
    | 'CLOSED'
    | 'CANCELLED'

  flow_status:
    | 'AWAITING_CHECK_IN'
    | 'WAITING_FOR_NURSING'
    | 'NURSING_IN_PROGRESS'
    | 'ROUTED'

  checked_in_at: string | null
  checked_in_by: string | null

  triaged_at: string | null
  triaged_by: string | null

  routed_at: string | null
  routed_by: string | null

  current_department_id: string | null

  opened_at: string
  closed_at: string | null
}


// ============================================================================
// Create
// ============================================================================


export async function createEpisode(
  accessToken: string,
  payload: CreateEpisodeRequest,
): Promise<Episode> {
  return apiRequest<Episode>(
    '/episodes',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    accessToken,
  )
}


// ============================================================================
// Retrieve
// ============================================================================


export async function getEpisode(
  accessToken: string,
  episodeId: string,
): Promise<Episode> {
  return apiRequest<Episode>(
    `/episodes/${episodeId}`,
    {},
    accessToken,
  )
}


// ============================================================================
// Reception Check-In
// ============================================================================


export async function checkInEpisode(
  accessToken: string,
  episodeId: string,
): Promise<Episode> {
  return apiRequest<Episode>(
    `/episodes/${episodeId}/check-in`,
    {
      method: 'POST',
    },
    accessToken,
  )
}


// ============================================================================
// Nursing Queue
// ============================================================================


export async function listNursingQueue(
  accessToken: string,
): Promise<Episode[]> {
  return apiRequest<Episode[]>(
    '/episodes/queue/nursing',
    {},
    accessToken,
  )
}


// ============================================================================
// Start Nursing
// ============================================================================


export async function startNursing(
  accessToken: string,
  episodeId: string,
): Promise<Episode> {
  return apiRequest<Episode>(
    `/episodes/${episodeId}/nursing/start`,
    {
      method: 'POST',
    },
    accessToken,
  )
}


// ============================================================================
// Route Episode
// ============================================================================


export async function routeEpisode(
  accessToken: string,
  episodeId: string,
  departmentId: string,
): Promise<Episode> {
  return apiRequest<Episode>(
    `/episodes/${episodeId}/route?department_id=${encodeURIComponent(
      departmentId,
    )}`,
    {
      method: 'POST',
    },
    accessToken,
  )
}


// ============================================================================
// Patient Episodes
// ============================================================================


export async function listPatientEpisodes(
  accessToken: string,
  patientId: string,
): Promise<Episode[]> {
  return apiRequest<Episode[]>(
    `/episodes/patient/${patientId}`,
    {},
    accessToken,
  )
}