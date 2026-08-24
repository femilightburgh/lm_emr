import {
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from 'react'

import {
  assignPermission,
  assignRoleToUser,
  createRole,
  createStaff,
  deleteRole,
  getRole,
  listPermissions,
  listRoles,
  listStaff,
  listUsers,
  linkUserAccount,
  onboardStaff,
  PLATFORM_PERMISSIONS,
  removePermission,
  removeRoleFromUser,
  updateRole,
  type AdminUser,
  type OnboardStaffResponse,
  type Permission,
  type Role,
  type Staff,
} from '../../api'

import type {
  EmploymentStatus,
  EmploymentType,
  Gender,
  Profession,
} from '../../types'

import AdministrationOverview from './AdministrationOverview'
import AdministrationRoles from './AdministrationRoles'
import AdministrationStaff from './AdministrationStaff'
import AdministrationUsers from './AdministrationUsers'
import AdministrationDepartments from './AdministrationDepartments'


type AdminTab =
  | 'overview'
  | 'users'
  | 'staff'
  | 'roles'
  | 'departments'
  | 'permissions'


interface Props {
  accessToken: string
  currentUserEmail: string
  hospitalId: string
}


interface CreateStaffPayload {
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
}


export default function AdministratorWorkspace({
  accessToken,
  currentUserEmail,
  hospitalId,
}: Props) {
  const [tab, setTab] =
    useState<AdminTab>('overview')

  const [users, setUsers] =
    useState<AdminUser[]>([])

  const [staff, setStaff] =
    useState<Staff[]>([])

  const [roles, setRoles] =
    useState<Role[]>([])

  const [selectedRole, setSelectedRole] =
    useState<Role | null>(null)

  const [permissions, setPermissions] =
    useState<Permission[]>([])

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)

  const [roleName, setRoleName] =
    useState('')

  const [roleDescription, setRoleDescription] =
    useState('')

  const [editingRole, setEditingRole] =
    useState(false)

  const [savingRole, setSavingRole] =
    useState(false)

  const [selectedPermission, setSelectedPermission] =
    useState('')

  const [selectedUser, setSelectedUser] =
    useState<AdminUser | null>(null)


  // ==========================================================================
  // Error handling
  // ==========================================================================

  function showError(
    err: unknown,
    fallback: string,
  ) {
    setError(
      err instanceof Error
        ? err.message
        : fallback,
    )
  }


  // ==========================================================================
  // Users
  // ==========================================================================

  async function loadUsers() {
    setLoading(true)
    setError(null)

    try {
      const response =
        await listUsers(accessToken)

      setUsers(response)
    } catch (err) {
      showError(
        err,
        'Unable to load hospital users.',
      )
    } finally {
      setLoading(false)
    }
  }


  async function refreshSelectedUser(
    userId: string,
  ) {
    try {
      const response =
        await listUsers(accessToken)

      setUsers(response)

      const refreshed =
        response.find(
          user => user.id === userId,
        )

      if (refreshed) {
        setSelectedUser(refreshed)
      }
    } catch (err) {
      showError(
        err,
        'Unable to refresh user.',
      )
    }
  }


  async function handleAssignRole(
    user: AdminUser,
    role: Role,
  ) {
    setError(null)

    try {
      await assignRoleToUser(
        accessToken,
        user.id,
        role.name,
      )

      await refreshSelectedUser(
        user.id,
      )
    } catch (err) {
      showError(
        err,
        'Unable to assign role.',
      )
    }
  }


  async function handleRemoveRole(
    user: AdminUser,
    roleName: string,
  ) {
    setError(null)

    try {
      await removeRoleFromUser(
        accessToken,
        user.id,
        roleName,
      )

      await refreshSelectedUser(
        user.id,
      )
    } catch (err) {
      showError(
        err,
        'Unable to remove role.',
      )
    }
  }


  // ==========================================================================
  // Staff
  // ==========================================================================

  async function loadStaff() {
    setLoading(true)
    setError(null)

    try {
      const response =
        await listStaff(
          accessToken,
          hospitalId,
        )

      setStaff(response.items)
    } catch (err) {
      showError(
        err,
        'Unable to load hospital staff.',
      )
    } finally {
      setLoading(false)
    }
  }


  async function handleCreateStaff(
    payload: CreateStaffPayload,
  ) {
    console.log(
      'PARENT HANDLE CREATE STAFF CALLED',
      payload,
    )

    setError(null)

    try {
      console.log(
        'ABOUT TO CALL createStaff()',
      )

      await createStaff(
        accessToken,
        payload,
      )

      console.log(
        'createStaff() COMPLETED',
      )

      await loadStaff()
    } catch (err) {
      console.error(
        'CREATE STAFF ERROR',
        err,
      )

      showError(
        err,
        'Unable to create staff profile.',
      )

      throw err
    }
  }


  async function handleLinkUser(
    member: Staff,
    userId: string,
  ) {
    setError(null)

    try {
      await linkUserAccount(
        accessToken,
        member.id,
        userId,
      )

      await Promise.all([
        loadStaff(),
        loadUsers(),
      ])
    } catch (err) {
      showError(
        err,
        'Unable to link user account.',
      )
    }
  }

  // ==========================================================================
  // Roles
  // ==========================================================================

  async function loadRoles() {
    setLoading(true)
    setError(null)

    try {
      const response =
        await listRoles(accessToken)

      setRoles(response)
    } catch (err) {
      showError(
        err,
        'Unable to load hospital roles.',
      )
    } finally {
      setLoading(false)
    }
  }


  async function openRole(
    roleId: string,
  ) {
    setError(null)

    try {
      const role =
        await getRole(
          accessToken,
          roleId,
        )

      setSelectedRole(role)

      const permissionResponse =
        await listPermissions(
          accessToken,
          roleId,
        )

      setPermissions(
        permissionResponse.permissions,
      )

      setTab('permissions')
    } catch (err) {
      showError(
        err,
        'Unable to load role.',
      )
    }
  }


  function beginCreateRole() {
    setSelectedRole(null)
    setRoleName('')
    setRoleDescription('')
    setEditingRole(false)
  }


  function beginEditRole(
    role: Role,
  ) {
    setSelectedRole(role)
    setRoleName(role.name)
    setRoleDescription(
      role.description ?? '',
    )
    setEditingRole(true)
  }


  async function handleSaveRole(
    event: FormEvent,
  ) {
    event.preventDefault()

    const name =
      roleName.trim()

    if (!name) {
      setError(
        'Role name is required.',
      )

      return
    }

    setSavingRole(true)
    setError(null)

    try {
      if (
        editingRole &&
        selectedRole
      ) {
        const updated =
          await updateRole(
            accessToken,
            selectedRole.id,
            {
              name,
              description:
                roleDescription.trim() ||
                null,
            },
          )

        setRoles(current =>
          current.map(role =>
            role.id === updated.id
              ? updated
              : role,
          ),
        )

        setSelectedRole(updated)
      } else {
        const created =
          await createRole(
            accessToken,
            {
              name,
              description:
                roleDescription.trim() ||
                null,
            },
          )

        setRoles(current => [
          ...current,
          created,
        ])

        setSelectedRole(created)
        setEditingRole(true)
      }

      setRoleName('')
      setRoleDescription('')
    } catch (err) {
      showError(
        err,
        editingRole
          ? 'Unable to update role.'
          : 'Unable to create role.',
      )
    } finally {
      setSavingRole(false)
    }
  }


  async function handleDeleteRole(
    role: Role,
  ) {
    const confirmed =
      window.confirm(
        `Delete the role "${role.name}"?`,
      )

    if (!confirmed) {
      return
    }

    setError(null)

    try {
      await deleteRole(
        accessToken,
        role.id,
      )

      setRoles(current =>
        current.filter(
          item => item.id !== role.id,
        ),
      )

      if (
        selectedRole?.id === role.id
      ) {
        setSelectedRole(null)
        setPermissions([])
      }
    } catch (err) {
      showError(
        err,
        'Unable to delete role.',
      )
    }
  }


  async function handleOnboardStaff(
    email: string,
    roleName: string,
  ): Promise<OnboardStaffResponse> {
    setError(null)

    try {
      const response =
        await onboardStaff(
          accessToken,
          {
            email,
            role_name: roleName,
          },
        )

      await loadUsers()

      return response
    } catch (err) {
      showError(
        err,
        'Unable to create staff invitation.',
      )

      throw err
    }
  }


  // ==========================================================================
  // Permissions
  // ==========================================================================

  async function refreshPermissions(
    roleId: string,
  ) {
    const response =
      await listPermissions(
        accessToken,
        roleId,
      )

    setPermissions(
      response.permissions,
    )
  }


  async function handleAssignPermission() {
    if (
      !selectedRole ||
      !selectedPermission
    ) {
      return
    }

    setError(null)

    try {
      await assignPermission(
        accessToken,
        selectedRole.id,
        selectedPermission,
      )

      await refreshPermissions(
        selectedRole.id,
      )

      setSelectedPermission('')
    } catch (err) {
      showError(
        err,
        'Unable to assign permission.',
      )
    }
  }


  async function handleRemovePermission(
    permissionCode: string,
  ) {
    if (!selectedRole) {
      return
    }

    setError(null)

    try {
      await removePermission(
        accessToken,
        selectedRole.id,
        permissionCode,
      )

      await refreshPermissions(
        selectedRole.id,
      )
    } catch (err) {
      showError(
        err,
        'Unable to remove permission.',
      )
    }
  }


  const availablePermissions =
    useMemo(() => {
      const assigned =
        new Set(
          permissions.map(
            permission =>
              permission.code,
          ),
        )

      return PLATFORM_PERMISSIONS.filter(
        permission =>
          !assigned.has(
            permission.code,
          ),
      )
    }, [permissions])


  // ==========================================================================
  // Initial loading
  // ==========================================================================

  useEffect(() => {
    void Promise.all([
      loadUsers(),
      loadRoles(),
      loadStaff(),
    ])
  }, [])


  // ==========================================================================
  // Render
  // ==========================================================================

  return (
    <section className="admin-workspace">

      {/* ==================================================================== */}
      {/* Header                                                               */}
      {/* ==================================================================== */}

      <div className="admin-heading">

        <div>
          <p className="eyebrow">
            ADMINISTRATION
          </p>

          <h2>
            Administrator workspace
          </h2>

          <p>
            Manage hospital users, staff,
            roles, and authorization
            permissions.
          </p>
        </div>

        <div className="admin-account">
          {currentUserEmail}
        </div>

      </div>


      {/* ==================================================================== */}
      {/* Global Error                                                         */}
      {/* ==================================================================== */}

      {error && (
        <div className="admin-error">
          {error}
        </div>
      )}


      {/* ==================================================================== */}
      {/* Navigation                                                           */}
      {/* ==================================================================== */}

      <nav className="admin-tabs">

        <button
          type="button"
          className={
            tab === 'overview'
              ? 'admin-tab active'
              : 'admin-tab'
          }
          onClick={() =>
            setTab('overview')
          }
        >
          Overview
        </button>


        <button
          type="button"
          className={
            tab === 'users'
              ? 'admin-tab active'
              : 'admin-tab'
          }
          onClick={() =>
            setTab('users')
          }
        >
          Users
        </button>


        <button
          type="button"
          className={
            tab === 'staff'
              ? 'admin-tab active'
              : 'admin-tab'
          }
          onClick={() =>
            setTab('staff')
          }
        >
          Staff
        </button>


        <button
          type="button"
          className={
            tab === 'departments'
              ? 'admin-tab active'
              : 'admin-tab'
          }
          onClick={() =>
            setTab('departments')
          }
        >
          Departments
        </button>


        <button
          type="button"
          className={
            tab === 'roles'
              ? 'admin-tab active'
              : 'admin-tab'
          }
          onClick={() =>
            setTab('roles')
          }
        >
          Roles
        </button>


        <button
          type="button"
          className={
            tab === 'permissions'
              ? 'admin-tab active'
              : 'admin-tab'
          }
          onClick={() =>
            setTab('permissions')
          }
        >
          Permissions
        </button>

      </nav>


      {/* ==================================================================== */}
      {/* Overview                                                             */}
      {/* ==================================================================== */}

      {tab === 'overview' && (
        <AdministrationOverview
          userCount={users.length}
          roleCount={roles.length}
          onUsers={() =>
            setTab('users')
          }
          onRoles={() =>
            setTab('roles')
          }
        />
      )}


      {/* ==================================================================== */}
      {/* Users                                                                */}
      {/* ==================================================================== */}

      {tab === 'users' && (
        <AdministrationUsers
          users={users}
          roles={roles}
          loading={loading}
          selectedUser={selectedUser}

          onRefresh={() =>
            void loadUsers()
          }

          onSelectUser={setSelectedUser}

          onCloseUser={() =>
            setSelectedUser(null)
          }

          onAssignRole={(
            user,
            role,
          ) => {
            void handleAssignRole(
              user,
              role,
            )
          }}

          onRemoveRole={(
            user,
            roleName,
          ) => {
            void handleRemoveRole(
              user,
              roleName,
            )
          }}

          onOnboardStaff={(
            email,
            roleName,
          ) =>
            handleOnboardStaff(
              email,
              roleName,
            )
          }
        />
      )}


      {/* ==================================================================== */}
      {/* Staff                                                                */}
      {/* ==================================================================== */}

      {tab === 'staff' && (
        <AdministrationStaff
          hospitalId={hospitalId}

          staff={staff}
          users={users}
          loading={loading}

          onRefresh={() =>
            void loadStaff()
          }

          onLinkUser={(
            member,
            userId,
          ) =>
            handleLinkUser(
              member,
              userId,
            )
          }

          onCreateStaff={
            handleCreateStaff
          }
        />
      )}


      {/* ==================================================================== */}
      {/* Departments                                                          */}
      {/* ==================================================================== */}

      {tab === 'departments' && (
        <AdministrationDepartments
          accessToken={accessToken}
          hospitalId={hospitalId}
        />
      )}


      {/* ==================================================================== */}
      {/* Roles / Permissions                                                  */}
      {/* ==================================================================== */}

      {(tab === 'roles' ||
        tab === 'permissions') && (
        <AdministrationRoles
          roles={roles}
          selectedRole={selectedRole}
          permissions={permissions}
          availablePermissions={
            availablePermissions
          }

          roleName={roleName}

          roleDescription={
            roleDescription
          }

          editingRole={editingRole}

          savingRole={savingRole}

          selectedPermission={
            selectedPermission
          }

          onSelectRole={roleId => {
            void openRole(roleId)
          }}

          onCreateRole={
            beginCreateRole
          }

          onEditRole={
            beginEditRole
          }

          onDeleteRole={role => {
            void handleDeleteRole(role)
          }}

          onSaveRole={
            handleSaveRole
          }

          onRoleNameChange={
            setRoleName
          }

          onRoleDescriptionChange={
            setRoleDescription
          }

          onManagePermissions={() => {
            setTab('permissions')
          }}

          onBackToRoles={() => {
            setTab('roles')
          }}

          onPermissionChange={
            setSelectedPermission
          }

          onAssignPermission={() => {
            void handleAssignPermission()
          }}

          onRemovePermission={
            permissionCode => {
              void handleRemovePermission(
                permissionCode,
              )
            }
          }
        />
      )}

    </section>
  )
}