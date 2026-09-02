import { apiRequest } from './client'


// ============================================================================
// Reception Overview
// ============================================================================

export interface ReceptionOverview {
  total_patients: number
  currently_admitted: number
  checked_in_today: number

  waiting_for_nursing: number
  nursing_in_progress: number
  routed: number
  awaiting_investigations: number
  awaiting_review: number
}


export async function getReceptionOverview(
  accessToken: string,
): Promise<ReceptionOverview> {
  return apiRequest<ReceptionOverview>(
    '/reception/overview',
    {},
    accessToken,
  )
}


// ============================================================================
// Patient Flow
// ============================================================================

export interface ReceptionPatientFlowItem {
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

  professional_name: string | null
  professional_role: string | null
  department_name: string | null

  checked_in_at: string | null
  opened_at: string
}


export interface ReceptionPatientFlowResponse {
  items: ReceptionPatientFlowItem[]
}


export async function getReceptionPatientFlow(
  accessToken: string,
): Promise<ReceptionPatientFlowResponse> {
  return apiRequest<ReceptionPatientFlowResponse>(
    '/reception/patient-flow',
    {},
    accessToken,
  )
}
