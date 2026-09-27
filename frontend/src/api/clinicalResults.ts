import { apiRequest } from './client'


export type ClinicalResultType =
  | 'LABORATORY'
  | 'RADIOLOGY'


export interface ClinicalResultValue {
  id: string
  clinical_result_id: string
  analyte_id: string | null

  analyte_code: string | null
  analyte_name: string

  custom_analyte_name: string | null
  custom_analyte_code: string | null
  custom_unit: string | null
  custom_reference_low: number | null
  custom_reference_high: number | null
  custom_reference_text: string | null

  value: number | string | boolean | null

  unit: string | null
  reference_low: number | null
  reference_high: number | null
  reference_text: string | null

  abnormal_flag: string | null
  comment: string | null

  created_at: string
  updated_at: string
}


export interface ClinicalResult {
  id: string
  order_id: string
  order_item_id: string | null
  result_type: ClinicalResultType
  status: 'DRAFT' | 'FINAL'
  specimen: string | null
  collected_at: string | null
  reported_at: string | null
  interpretation: string | null
  values: ClinicalResultValue[]
  result_data: Record<string, unknown>
  recorded_by: string
  recorded_at: string
  created_at: string
  updated_at: string
}


export interface CreateClinicalResultValueRequest {
  analyte_id?: string
  custom_analyte_name?: string
  custom_analyte_code?: string
  custom_unit?: string
  custom_reference_low?: number
  custom_reference_high?: number
  custom_reference_text?: string
  value_numeric?: number
  value_text?: string
  value_boolean?: boolean
  value_code?: string
  abnormal_flag?: string
  comment?: string
}


export interface CreateClinicalResultRequest {
  order_id: string
  order_item_id?: string
  result_type: ClinicalResultType
  specimen?: string
  collected_at?: string
  reported_at?: string
  interpretation?: string
  values: CreateClinicalResultValueRequest[]
  result_data?: Record<string, unknown>
}


export async function listOrderClinicalResults(
  accessToken: string,
  orderId: string,
): Promise<ClinicalResult[]> {
  return apiRequest<ClinicalResult[]>(
    `/clinical-results/orders/${orderId}`,
    {},
    accessToken,
  )
}


export async function getClinicalResult(
  accessToken: string,
  resultId: string,
): Promise<ClinicalResult> {
  return apiRequest<ClinicalResult>(
    `/clinical-results/${resultId}`,
    {},
    accessToken,
  )
}


export async function updateClinicalResult(
  accessToken: string,
  resultId: string,
  request: CreateClinicalResultRequest,
): Promise<ClinicalResult> {
  return apiRequest<ClinicalResult>(
    `/clinical-results/${resultId}`,
    {
      method: 'PUT',
      body: JSON.stringify(request),
    },
    accessToken,
  )
}


export async function finalizeClinicalResult(
  accessToken: string,
  resultId: string,
): Promise<ClinicalResult> {
  return apiRequest<ClinicalResult>(
    `/clinical-results/${resultId}/finalize`,
    {
      method: 'POST',
    },
    accessToken,
  )
}


export async function createClinicalResult(
  accessToken: string,
  request: CreateClinicalResultRequest,
): Promise<ClinicalResult> {
  return apiRequest<ClinicalResult>(
    '/clinical-results',
    {
      method: 'POST',
      body: JSON.stringify(request),
    },
    accessToken,
  )
}
