import { apiRequest } from './client'


// ============================================================================
// Episodes
// ============================================================================


export interface CreateEpisodeRequest {
  patient_id: string
  title: string
}


export interface DoctorQueueItem {
  id: string
  patient_id: string
  patient_name: string
  hospital_number: string

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
    | 'AWAITING_INVESTIGATIONS'
    | 'AWAITING_REVIEW'

  managing_doctor_id: string | null

  checked_in_at: string | null
  routed_at: string | null
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
    | 'AWAITING_INVESTIGATIONS'
    | 'AWAITING_REVIEW'

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
// Doctor Clinic Queue
// ============================================================================


export async function listDoctorClinicQueue(
  accessToken: string,
): Promise<DoctorQueueItem[]> {
  return apiRequest<DoctorQueueItem[]>(
    '/episodes/queue/doctor/clinic',
    {},
    accessToken,
  )
}


// ============================================================================
// Doctor Ward Queue
// ============================================================================


export async function listDoctorWardQueue(
  accessToken: string,
): Promise<DoctorQueueItem[]> {
  return apiRequest<DoctorQueueItem[]>(
    '/episodes/queue/doctor/ward',
    {},
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


export async function listNursingInpatients(
  accessToken: string,
): Promise<Episode[]> {
  return apiRequest<Episode[]>(
    '/episodes/queue/nursing/inpatients',
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
// Admit Episode
// ============================================================================


export async function admitEpisode(
  accessToken: string,
  episodeId: string,
  encounterId: string,
): Promise<Episode> {
  return apiRequest<Episode>(
    `/episodes/${episodeId}/admit?encounter_id=${encodeURIComponent(
      encounterId,
    )}`,
    {
      method: 'POST',
    },
    accessToken,
  )
}


export type ConsultationDisposition =
  | 'ORDER_INVESTIGATIONS'


export async function completeConsultation(
  accessToken: string,
  episodeId: string,
  payload: {
    encounter_id: string
    disposition: ConsultationDisposition
  },
): Promise<Episode> {
  return apiRequest<Episode>(
    `/episodes/${episodeId}/complete-consultation`,
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    accessToken,
  )
}


export type WardReviewDisposition =
  | 'CONTINUE_ADMISSION'
  | 'DISCHARGE'
  | 'TRANSFER'
  | 'REFERRAL'
  | 'OTHER'


export async function completeWardReview(
  accessToken: string,
  episodeId: string,
  payload: {
    encounter_id: string
    disposition: WardReviewDisposition
    details: string | null
  },
): Promise<Episode> {
  return apiRequest<Episode>(
    `/episodes/${episodeId}/complete-ward-review`,
    {
      method: 'POST',
      body: JSON.stringify(payload),
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