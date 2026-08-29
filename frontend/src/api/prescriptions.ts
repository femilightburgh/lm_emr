import { apiRequest } from './client'


export interface CreatePrescriptionRequest {
  encounter_id: string
  priority?: string

  medicine_name: string
  strength?: string | null

  dose: string
  dose_unit?: string | null

  route: string
  frequency: string

  duration?: string | null
  duration_unit?: string | null

  quantity?: string | null
  directions?: string | null
  indication?: string | null
}


export interface Prescription {
  id: string
  clinical_order_id: string

  medicine_name: string
  strength: string | null

  dose: string
  dose_unit: string | null

  route: string
  frequency: string

  duration: string | null
  duration_unit: string | null

  quantity: string | null
  directions: string | null
  indication: string | null

  created_at: string
  updated_at: string
}


export async function createPrescription(
  accessToken: string,
  payload: CreatePrescriptionRequest,
): Promise<Prescription> {
  return apiRequest<Prescription>(
    '/prescriptions',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    accessToken,
  )
}
