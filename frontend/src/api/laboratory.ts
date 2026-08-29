import {
  apiRequest,
} from './client'

import type {
  ClinicalOrder,
} from './clinicalOrders'


export type LaboratoryAnalyteDataType =
  | 'NUMERIC'
  | 'TEXT'
  | 'BOOLEAN'
  | 'CODED'


export interface LaboratoryTestAnalyte {
  id: string
  laboratory_test_id: string
  code: string
  name: string
  data_type: LaboratoryAnalyteDataType
  unit: string | null
  reference_low: number | null
  reference_high: number | null
  reference_text: string | null
  options: string[] | null
  required: boolean
  display_order: number
}


export interface LaboratoryTest {
  id: string
  code: string
  name: string
  specimen: string | null
  description: string | null
  result_fields: Record<string, unknown>
  analytes: LaboratoryTestAnalyte[]
  active: boolean
}


export interface LaboratoryQueueItem {
  id: string
  encounter_id: string
  patient_id: string
  patient_name: string
  hospital_number: string
  episode_number: string
  ordering_clinician_name: string
  order_type: 'LABORATORY'
  status:
    | 'REQUESTED'
    | 'RECEIVED'
    | 'IN_PROGRESS'
  priority: string
  details: Record<string, unknown>
  ordered_at: string
  started_at: string | null
}


export interface CreateLaboratoryAnalyteRequest {
  code: string
  name: string
  data_type: LaboratoryAnalyteDataType
  unit?: string | null
  reference_low?: number | null
  reference_high?: number | null
  reference_text?: string | null
  options?: string[] | null
  required?: boolean
  display_order?: number
}


export interface CreateLaboratoryTestRequest {
  code: string
  name: string
  specimen?: string | null
  description?: string | null
  analytes?: CreateLaboratoryAnalyteRequest[]
}


export interface UpdateLaboratoryAnalyteRequest {
  name?: string
  unit?: string | null
  reference_low?: number | null
  reference_high?: number | null
  reference_text?: string | null
  options?: unknown[] | null
  required?: boolean
  display_order?: number
}


export async function createLaboratoryTest(
  accessToken: string,
  request: CreateLaboratoryTestRequest,
): Promise<LaboratoryTest> {
  return apiRequest<LaboratoryTest>(
    '/laboratory/tests',
    {
      method: 'POST',
      body: JSON.stringify(request),
    },
    accessToken,
  )
}


export async function createLaboratoryAnalyte(
  accessToken: string,
  testCode: string,
  request: CreateLaboratoryAnalyteRequest,
): Promise<LaboratoryTestAnalyte> {
  return apiRequest<LaboratoryTestAnalyte>(
    `/laboratory/tests/${encodeURIComponent(
      testCode,
    )}/analytes`,
    {
      method: 'POST',
      body: JSON.stringify(request),
    },
    accessToken,
  )
}


export async function updateLaboratoryAnalyte(
  accessToken: string,
  testCode: string,
  analyteId: string,
  request: UpdateLaboratoryAnalyteRequest,
): Promise<LaboratoryTestAnalyte> {
  return apiRequest<LaboratoryTestAnalyte>(
    `/laboratory/tests/${encodeURIComponent(
      testCode,
    )}/analytes/${analyteId}`,
    {
      method: 'PATCH',
      body: JSON.stringify(request),
    },
    accessToken,
  )
}


export async function listLaboratoryTests(
  accessToken: string,
): Promise<LaboratoryTest[]> {
  return apiRequest<LaboratoryTest[]>(
    '/laboratory/tests',
    {},
    accessToken,
  )
}


export async function listLaboratoryQueue(
  accessToken: string,
): Promise<LaboratoryQueueItem[]> {
  return apiRequest<LaboratoryQueueItem[]>(
    '/clinical-orders/queue/laboratory',
    {},
    accessToken,
  )
}


export async function receiveLaboratoryOrder(
  accessToken: string,
  orderId: string,
): Promise<ClinicalOrder> {
  return apiRequest<ClinicalOrder>(
    `/clinical-orders/${orderId}/receive`,
    {
      method: 'POST',
    },
    accessToken,
  )
}


export async function startLaboratoryOrder(
  accessToken: string,
  orderId: string,
): Promise<ClinicalOrder> {
  return apiRequest<ClinicalOrder>(
    `/clinical-orders/${orderId}/start`,
    {
      method: 'POST',
    },
    accessToken,
  )
}
