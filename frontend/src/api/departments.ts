import { apiRequest } from './client'


// ============================================================================
// Types
// ============================================================================

export type DepartmentCategory =
  | 'Clinical'
  | 'Diagnostic'
  | 'Administrative'
  | 'Support'


export type DepartmentStatus =
  | 'Active'
  | 'Inactive'


export interface Department {
  id: string

  hospital_id: string

  name: string

  code: string

  category: DepartmentCategory

  status: DepartmentStatus
}


// ============================================================================
// Create
// ============================================================================

export interface CreateDepartmentRequest {
  hospital_id: string
  name: string
  code: string
  category: DepartmentCategory
  status?: DepartmentStatus
}


export async function createDepartment(
  accessToken: string,
  payload: CreateDepartmentRequest,
): Promise<Department> {
  return apiRequest<Department>(
    '/departments',
    {
      method: 'POST',
      body: JSON.stringify({
        ...payload,
        status:
          payload.status ??
          'Active',
      }),
    },
    accessToken,
  )
}


// ============================================================================
// List
// ============================================================================

export async function listDepartments(
  accessToken: string,
  hospitalId: string,
): Promise<Department[]> {
  const params =
    new URLSearchParams()

  params.set(
    'hospital_id',
    hospitalId,
  )

  return apiRequest<Department[]>(
    `/departments?${params.toString()}`,
    {},
    accessToken,
  )
}


// ============================================================================
// Retrieve
// ============================================================================

export async function getDepartment(
  accessToken: string,
  departmentId: string,
): Promise<Department> {
  return apiRequest<Department>(
    `/departments/${departmentId}`,
    {},
    accessToken,
  )
}


// ============================================================================
// Update
// ============================================================================

export interface UpdateDepartmentRequest {
  name?: string
  code?: string
  category?: DepartmentCategory
  status?: DepartmentStatus
}


export async function updateDepartment(
  accessToken: string,
  departmentId: string,
  payload: UpdateDepartmentRequest,
): Promise<Department> {
  return apiRequest<Department>(
    `/departments/${departmentId}`,
    {
      method: 'PUT',
      body: JSON.stringify(
        payload,
      ),
    },
    accessToken,
  )
}


// ============================================================================
// Delete
// ============================================================================

export async function deleteDepartment(
  accessToken: string,
  departmentId: string,
): Promise<void> {
  await apiRequest<void>(
    `/departments/${departmentId}`,
    {
      method: 'DELETE',
    },
    accessToken,
  )
}