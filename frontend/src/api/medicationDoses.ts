import { apiRequest } from './client'


export type MedicationDoseStatus =
  | 'PENDING'
  | 'GIVEN'
  | 'HELD'
  | 'MISSED'
  | 'CANCELLED'


export type MedicationTreatmentStatus =
  | 'ACTIVE'
  | 'DISCONTINUED'


export type MedicationAdministrationStatus =
  | 'GIVEN'
  | 'HELD'
  | 'MISSED'
  | 'REFUSED'


export interface MedicationAdministration {
  id: string
  dose_id: string
  administered_by: string
  status: MedicationAdministrationStatus
  administered_at: string | null
  dose_given: string | null
  reason: string | null
  notes: string | null
}


export interface MedicationDoseQueueItem {
  id: string
  treatment_id: string
  scheduled_at: string
  status: MedicationDoseStatus
  treatment_status: MedicationTreatmentStatus

  medicine_name: string
  strength: string | null
  dose: string
  dose_unit: string | null
  route: string
  frequency: string

  duration: string | null
  duration_unit: string | null
  directions: string | null

  administration: MedicationAdministration | null
}


export interface MedicationNursingDose {
  id: string
  treatment_id: string
  scheduled_at: string

  scheduled_state:
    | 'UPCOMING'
    | 'DUE'
    | 'OVERDUE'
    | 'MISSED'

  administration_status:
    | MedicationAdministrationStatus
    | null

  administration_at: string | null
  dose_given: string | null
  reason: string | null
  notes: string | null

  medicine_name: string
  strength: string | null
  dose: string
  dose_unit: string | null
  route: string
  frequency: string
  directions: string | null
}


export interface MedicationNursingRound {
  scheduled_at: string
  doses: MedicationNursingDose[]
}


export interface MedicationPrescriptionSummary {
  treatment_id: string
  prescription_id: string

  medicine_name: string
  strength: string | null
  dose: string
  dose_unit: string | null
  route: string
  frequency: string
  directions: string | null

  total_scheduled: number
  given_count: number
  held_count: number
  missed_count: number
  refused_count: number
  remaining_count: number

  next_dose_at: string | null
  next_dose_state:
    | 'UPCOMING'
    | 'DUE'
    | 'OVERDUE'
    | 'MISSED'
    | null
}


export interface MedicationTreatmentHistory {
  treatment: MedicationPrescriptionSummary
  doses: MedicationNursingDose[]
}


export interface MedicationNursingSummary {
  prescriptions: MedicationPrescriptionSummary[]

  round: {
    current_round:
      MedicationNursingRound | null

    upcoming_rounds:
      MedicationNursingRound[]

    previous_round:
      MedicationNursingRound | null
  }
}


export interface CreateMedicationAdministrationRequest {
  status: MedicationAdministrationStatus
  administered_at?: string | null
  dose_given?: string | null
  reason?: string | null
  notes?: string | null
}


export async function getMedicationNursingSummary(
  accessToken: string,
  episodeId: string,
): Promise<MedicationNursingSummary> {
  return apiRequest<MedicationNursingSummary>(
    `/clinical-orders/medication-nursing-summary/episode/${episodeId}`,
    {},
    accessToken,
  )
}


export async function listEpisodeMedicationDoses(
  accessToken: string,
  episodeId: string,
  fromTime?: string,
  toTime?: string,
): Promise<MedicationDoseQueueItem[]> {
  const params = new URLSearchParams()

  if (fromTime) {
    params.set(
      'from_time',
      fromTime,
    )
  }

  if (toTime) {
    params.set(
      'to_time',
      toTime,
    )
  }

  const query =
    params.toString()

  return apiRequest<MedicationDoseQueueItem[]>(
    `/clinical-orders/medication-doses/episode/${episodeId}${
      query
        ? `?${query}`
        : ''
    }`,
    {},
    accessToken,
  )
}


export async function getMedicationTreatmentHistory(
  accessToken: string,
  treatmentId: string,
): Promise<MedicationTreatmentHistory> {
  return apiRequest<MedicationTreatmentHistory>(
    `/clinical-orders/medication-treatments/${treatmentId}/history`,
    {},
    accessToken,
  )
}


export async function recordMedicationAdministration(
  accessToken: string,
  doseId: string,
  payload: CreateMedicationAdministrationRequest,
): Promise<MedicationAdministration> {
  return apiRequest<MedicationAdministration>(
    `/clinical-orders/medication-doses/${doseId}/administration`,
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    accessToken,
  )
}
