import { apiRequest } from './client'


// ============================================================================
// Types
// ============================================================================


export interface UserRole {
  id: string
  role_id: string
  role_name: string
  is_active: boolean
}


export interface AdminUser {
  id: string
  email: string
  hospital_id: string
  is_superuser: boolean
  status: string
  roles: UserRole[]
}


export interface Role {
  id: string
  hospital_id: string
  name: string
  description: string | null
  is_template: boolean
}


export interface Permission {
  code: string
  name: string
  description: string
}


export interface CreateRoleRequest {
  name: string
  description: string | null
}


export interface UpdateRoleRequest {
  name: string
  description: string | null
}


export interface AssignPermissionRequest {
  permission_code: string
}


export interface AssignRoleRequest {
  role_name: string
}


export interface OnboardStaffRequest {
  email: string
  role_name: string
}


export interface OnboardStaffResponse {
  user: AdminUser
  invitation_token: string
  invitation_expires_at: string
}


export interface RolePermissionsResponse {
  permissions: Permission[]
}


// ============================================================================
// Users
// ============================================================================


export async function listUsers(
  accessToken: string,
): Promise<AdminUser[]> {
  return apiRequest<AdminUser[]>(
    '/authorization/users',
    {},
    accessToken,
  )
}


export async function getUser(
  accessToken: string,
  userId: string,
): Promise<AdminUser> {
  return apiRequest<AdminUser>(
    `/authorization/users/${userId}`,
    {},
    accessToken,
  )
}


export async function onboardStaff(
  accessToken: string,
  payload: OnboardStaffRequest,
): Promise<OnboardStaffResponse> {
  return apiRequest<OnboardStaffResponse>(
    '/authorization/users/onboard',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    accessToken,
  )
}


// ============================================================================
// Roles
// ============================================================================


export async function listRoles(
  accessToken: string,
): Promise<Role[]> {
  return apiRequest<Role[]>(
    '/authorization/roles',
    {},
    accessToken,
  )
}


export async function getRole(
  accessToken: string,
  roleId: string,
): Promise<Role> {
  return apiRequest<Role>(
    `/authorization/roles/${roleId}`,
    {},
    accessToken,
  )
}


export async function createRole(
  accessToken: string,
  payload: CreateRoleRequest,
): Promise<Role> {
  return apiRequest<Role>(
    '/authorization/roles',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    accessToken,
  )
}


export async function updateRole(
  accessToken: string,
  roleId: string,
  payload: UpdateRoleRequest,
): Promise<Role> {
  return apiRequest<Role>(
    `/authorization/roles/${roleId}`,
    {
      method: 'PUT',
      body: JSON.stringify(payload),
    },
    accessToken,
  )
}


export async function deleteRole(
  accessToken: string,
  roleId: string,
): Promise<void> {
  return apiRequest<void>(
    `/authorization/roles/${roleId}`,
    {
      method: 'DELETE',
    },
    accessToken,
  )
}


// ============================================================================
// Role Permissions
// ============================================================================


export async function assignPermission(
  accessToken: string,
  roleId: string,
  permissionCode: string,
): Promise<void> {
  return apiRequest<void>(
    `/authorization/roles/${roleId}/permissions`,
    {
      method: 'POST',
      body: JSON.stringify({
        permission_code: permissionCode,
      }),
    },
    accessToken,
  )
}


export async function listPermissions(
  accessToken: string,
  roleId: string,
): Promise<RolePermissionsResponse> {
  return apiRequest<RolePermissionsResponse>(
    `/authorization/roles/${roleId}/permissions`,
    {},
    accessToken,
  )
}


export async function removePermission(
  accessToken: string,
  roleId: string,
  permissionCode: string,
): Promise<void> {
  return apiRequest<void>(
    `/authorization/roles/${roleId}/permissions/${encodeURIComponent(
      permissionCode,
    )}`,
    {
      method: 'DELETE',
    },
    accessToken,
  )
}


// ============================================================================
// User Roles
// ============================================================================


export async function assignRoleToUser(
  accessToken: string,
  userId: string,
  roleName: string,
): Promise<void> {
  return apiRequest<void>(
    `/authorization/users/${userId}/roles`,
    {
      method: 'POST',
      body: JSON.stringify({
        role_name: roleName,
      }),
    },
    accessToken,
  )
}


export async function removeRoleFromUser(
  accessToken: string,
  userId: string,
  roleName: string,
): Promise<void> {
  return apiRequest<void>(
    `/authorization/users/${userId}/roles/${encodeURIComponent(
      roleName,
    )}`,
    {
      method: 'DELETE',
    },
    accessToken,
  )
}


// ============================================================================
// Platform Permission Catalogue
// ============================================================================
//
// This catalogue is used by the administrator UI.
// The backend remains authoritative.
// ============================================================================


export const PLATFORM_PERMISSIONS: Permission[] = [
  {
    code: 'patient.read',
    name: 'Read Patients',
    description:
      'Allows viewing patient records within the hospital.',
  },
  {
    code: 'patient.create',
    name: 'Create Patients',
    description:
      'Allows registering new patients.',
  },
  {
    code: 'patient.update',
    name: 'Update Patients',
    description:
      'Allows modifying patient information.',
  },
  {
    code: 'patient.delete',
    name: 'Delete Patients',
    description:
      'Allows deleting patient records.',
  },
  {
    code: 'staff.read',
    name: 'Read Staff',
    description:
      'Allows viewing staff records.',
  },
  {
    code: 'staff.create',
    name: 'Create Staff',
    description:
      'Allows creating staff records.',
  },
  {
    code: 'staff.update',
    name: 'Update Staff',
    description:
      'Allows modifying staff records.',
  },
  {
    code: 'staff.delete',
    name: 'Delete Staff',
    description:
      'Allows deleting staff records.',
  },
  {
    code: 'department.read',
    name: 'Read Departments',
    description:
      'Allows viewing hospital departments.',
  },
  {
    code: 'department.create',
    name: 'Create Departments',
    description:
      'Allows creating hospital departments.',
  },
  {
    code: 'department.update',
    name: 'Update Departments',
    description:
      'Allows modifying hospital departments.',
  },
  {
    code: 'department.delete',
    name: 'Delete Departments',
    description:
      'Allows deleting hospital departments.',
  },
  {
    code: 'role.read',
    name: 'Read Roles',
    description:
      'Allows viewing roles.',
  },
  {
    code: 'role.create',
    name: 'Create Roles',
    description:
      'Allows creating roles.',
  },
  {
    code: 'role.update',
    name: 'Update Roles',
    description:
      'Allows modifying roles.',
  },
  {
    code: 'role.delete',
    name: 'Delete Roles',
    description:
      'Allows deleting roles.',
  },
  {
    code: 'laboratory_catalogue.read',
    name: 'Read Laboratory Catalogue',
    description:
      'Allows viewing laboratory tests and analyte definitions.',
  },
  {
    code: 'laboratory_catalogue.update',
    name: 'Update Laboratory Catalogue',
    description:
      'Allows maintaining laboratory analyte metadata and reference intervals.',
  },
]