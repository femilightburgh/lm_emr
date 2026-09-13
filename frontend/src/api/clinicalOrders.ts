import { apiRequest } from './client'


export type ClinicalOrderType =
  | 'LABORATORY'
  | 'RADIOLOGY'
  | 'MEDICATION'
  | 'DIAGNOSTIC'
  | 'DIAGNOSTIC'


export type ClinicalOrderStatus =
  | 'REQUESTED'
  | 'RECEIVED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'CANCELLED'


export interface ClinicalOrderItem {
  id: string
  clinical_order_id: string
  item_type: 'LABORATORY' | 'DIAGNOSTIC'
  status: ClinicalOrderStatus
  laboratory_test_id: string | null
  diagnostic_investigation_id: string | null
  display_order: number
  details: Record<string, unknown>
  created_at: string
  updated_at: string
}


export interface ClinicalOrder {
  id: string
  encounter_id: string
  ordered_by: string
  order_type: ClinicalOrderType
  status: ClinicalOrderStatus
  priority: string
  details: Record<string, unknown>
  items: ClinicalOrderItem[]
  ordered_at: string
  started_at: string | null
  completed_at: string | null
  cancelled_at: string | null
  created_at: string
  updated_at: string
}


export interface CreateClinicalOrderItemRequest {
  laboratory_test_id?: string
  diagnostic_investigation_id?: string
}

export interface CreateClinicalOrderRequest {
  encounter_id: string
  order_type: ClinicalOrderType
  priority?: string
  details: Record<string, unknown>
  items?: CreateClinicalOrderItemRequest[]
}


export async function createClinicalOrder(
  accessToken: string,
  payload: CreateClinicalOrderRequest,
): Promise<ClinicalOrder> {
  return apiRequest<ClinicalOrder>(
    '/clinical-orders',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    accessToken,
  )
}


export async function listEncounterClinicalOrders(
  accessToken: string,
  encounterId: string,
): Promise<ClinicalOrder[]> {
  return apiRequest<ClinicalOrder[]>(
    `/clinical-orders/encounters/${encounterId}`,
    {},
    accessToken,
  )
}



export async function listEpisodeClinicalOrders(
  accessToken: string,
  episodeId: string,
): Promise<ClinicalOrder[]> {
  return apiRequest<ClinicalOrder[]>(
    `/clinical-orders/episodes/${episodeId}`,
    {},
    accessToken,
  )
}

export async function getClinicalOrder(
  accessToken: string,
  orderId: string,
): Promise<ClinicalOrder> {
  return apiRequest<ClinicalOrder>(
    `/clinical-orders/${orderId}`,
    {},
    accessToken,
  )
}


export async function cancelClinicalOrder(
  accessToken: string,
  orderId: string,
): Promise<ClinicalOrder> {
  return apiRequest<ClinicalOrder>(
    `/clinical-orders/${orderId}/cancel`,
    {
      method: 'POST',
    },
    accessToken,
  )
}
