import { apiRequest } from './client'

export type DiagnosisType =
  | 'DIFFERENTIAL'
  | 'PROVISIONAL'
  | 'FINAL'

export type DiagnosisCertainty =
  | 'SUSPECTED'
  | 'POSSIBLE'
  | 'CONFIRMED'
  | 'RULED_OUT'

export interface ClinicalDiagnosis {
  id: string
  encounter_id: string
  episode_id: string
  diagnosis_name: string
  code_system: string | null
  code: string | null
  diagnosis_type: DiagnosisType
  certainty: DiagnosisCertainty
  onset_date: string | null
  diagnosed_by: string
  diagnosed_at: string
  resolved_at: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface CreateClinicalDiagnosisRequest {
  encounter_id: string
  diagnosis_name: string
  code_system?: string | null
  code?: string | null
  diagnosis_type: DiagnosisType
  certainty: DiagnosisCertainty
  onset_date?: string | null
  notes?: string | null
}

export async function createClinicalDiagnosis(
  accessToken: string,
  payload: CreateClinicalDiagnosisRequest,
): Promise<ClinicalDiagnosis> {
  return apiRequest<ClinicalDiagnosis>(
    '/diagnoses',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    accessToken,
  )
}

export async function listEncounterDiagnoses(
  accessToken: string,
  encounterId: string,
): Promise<ClinicalDiagnosis[]> {
  return apiRequest<ClinicalDiagnosis[]>(
    `/diagnoses/encounters/${encounterId}`,
    {},
    accessToken,
  )
}

export async function getClinicalDiagnosis(
  accessToken: string,
  diagnosisId: string,
): Promise<ClinicalDiagnosis> {
  return apiRequest<ClinicalDiagnosis>(
    `/diagnoses/${diagnosisId}`,
    {},
    accessToken,
  )
}
