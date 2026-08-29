import type {
  Gender,
  EmploymentStatus,
  EmploymentType,
  Profession,
} from '../types'

import { apiRequest } from './client'


// ============================================================================
// Staff Types
// ============================================================================

export interface Staff {
  id: string
  hospital_id: string
  user_account_id: string | null

  staff_number: string

  first_name: string
  middle_name: string | null
  last_name: string

  gender: Gender
  date_of_birth: string

  phone_number: string | null
  email: string | null

  created_at: string
  updated_at: string
}


export interface StaffListResponse {
  items: Staff[]
  total: number
}


export interface CreateStaffRequest {
  hospital_id: string

  staff_number: string

  first_name: string
  middle_name?: string | null
  last_name: string

  gender: Gender
  date_of_birth: string

  phone_number?: string | null
  email?: string | null

  profession: Profession
  employment_status: EmploymentStatus
  employment_type: EmploymentType

  date_employed: string
  date_left?: string | null
}


export interface UpdateStaffRequest {
  first_name?: string | null
  middle_name?: string | null
  last_name?: string | null

  gender?: Gender | null
  date_of_birth?: string | null

  phone_number?: string | null
  email?: string | null
}


export interface LinkUserAccountRequest {
  user_account_id: string
}


// ============================================================================
// Staff API
// ============================================================================

export async function getCurrentStaff(
  accessToken: string,
): Promise<Staff> {
  return apiRequest<Staff>(
    '/staff/me',
    {},
    accessToken,
  )
}


export async function createStaff(
  accessToken: string,
  payload: CreateStaffRequest,
): Promise<Staff> {
  return apiRequest<Staff>(
    '/staff',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    accessToken,
  )
}


export async function listStaff(
  accessToken: string,
  hospitalId: string,
): Promise<StaffListResponse> {
  const params = new URLSearchParams({
    hospital_id: hospitalId,
  })

  return apiRequest<StaffListResponse>(
    `/staff?${params.toString()}`,
    {},
    accessToken,
  )
}


export async function getStaff(
  accessToken: string,
  staffId: string,
): Promise<Staff> {
  return apiRequest<Staff>(
    `/staff/${staffId}`,
    {},
    accessToken,
  )
}


export async function updateStaff(
  accessToken: string,
  staffId: string,
  payload: UpdateStaffRequest,
): Promise<Staff> {
  return apiRequest<Staff>(
    `/staff/${staffId}`,
    {
      method: 'PUT',
      body: JSON.stringify(payload),
    },
    accessToken,
  )
}


export async function linkUserAccount(
  accessToken: string,
  staffId: string,
  userAccountId: string,
): Promise<Staff> {
  return apiRequest<Staff>(
    `/staff/${staffId}/link-user`,
    {
      method: 'POST',
      body: JSON.stringify({
        user_account_id: userAccountId,
      }),
    },
    accessToken,
  )
}
