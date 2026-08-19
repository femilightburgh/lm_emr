import type {
  FormEvent,
} from 'react'

import type {
  Permission,
  Role,
} from '../../api'


interface AdministrationRolesProps {
  roles: Role[]
  selectedRole: Role | null
  permissions: Permission[]
  availablePermissions: Permission[]
  roleName: string
  roleDescription: string
  editingRole: boolean
  savingRole: boolean
  selectedPermission: string

  onSelectRole: (
    roleId: string,
  ) => void

  onCreateRole: () => void

  onEditRole: (
    role: Role,
  ) => void

  onDeleteRole: (
    role: Role,
  ) => void

  onSaveRole: (
    event: FormEvent,
  ) => void

  onRoleNameChange: (
    value: string,
  ) => void

  onRoleDescriptionChange: (
    value: string,
  ) => void

  onManagePermissions: () => void

  onBackToRoles: () => void

  onPermissionChange: (
    value: string,
  ) => void

  onAssignPermission: () => void

  onRemovePermission: (
    permissionCode: string,
  ) => void
}


export default function AdministrationRoles({
  roles,
  selectedRole,
  permissions,
  availablePermissions,
  roleName,
  roleDescription,
  editingRole,
  savingRole,
  selectedPermission,

  onSelectRole,
  onCreateRole,
  onEditRole,
  onDeleteRole,
  onSaveRole,
  onRoleNameChange,
  onRoleDescriptionChange,
  onManagePermissions,
  onBackToRoles,
  onPermissionChange,
  onAssignPermission,
  onRemovePermission,
}: AdministrationRolesProps) {
  return (
    <>
      <div className="admin-two-column">

        <section className="admin-panel">

          <div className="admin-panel-header">

            <div>
              <p className="eyebrow">
                ROLE MANAGEMENT
              </p>

              <h3>
                Hospital roles
              </h3>
            </div>

            <button
              type="button"
              className="primary-button"
              onClick={onCreateRole}
            >
              New role
            </button>

          </div>


          <form
            className="admin-role-form"
            onSubmit={onSaveRole}
          >

            <label>
              Role name

              <input
                value={roleName}
                onChange={event =>
                  onRoleNameChange(
                    event.target.value,
                  )
                }
                placeholder="e.g. Nurse Manager"
              />
            </label>


            <label>
              Description

              <input
                value={roleDescription}
                onChange={event =>
                  onRoleDescriptionChange(
                    event.target.value,
                  )
                }
                placeholder="Describe this role"
              />
            </label>


            <div className="form-actions">

              <button
                type="submit"
                className="primary-button"
                disabled={savingRole}
              >
                {savingRole
                  ? 'Saving...'
                  : editingRole
                    ? 'Update role'
                    : 'Create role'}
              </button>

            </div>

          </form>


          <div className="admin-role-list">

            {roles.length === 0 ? (
              <div className="admin-empty">
                No roles found.
              </div>
            ) : (
              roles.map(role => (
                <div
                  className={
                    selectedRole?.id === role.id
                      ? 'admin-role-item selected'
                      : 'admin-role-item'
                  }
                  key={role.id}
                >

                  <button
                    type="button"
                    className="admin-role-select"
                    onClick={() =>
                      onSelectRole(role.id)
                    }
                  >
                    <strong>
                      {role.name}
                    </strong>

                    <span>
                      {role.description ||
                        'No description'}
                    </span>
                  </button>


                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() =>
                      onEditRole(role)
                    }
                  >
                    Edit
                  </button>

                </div>
              ))
            )}

          </div>

        </section>


        <section className="admin-panel">

          <div className="admin-panel-header">

            <div>
              <p className="eyebrow">
                ROLE DETAILS
              </p>

              <h3>
                {selectedRole
                  ? selectedRole.name
                  : 'Select a role'}
              </h3>
            </div>

          </div>


          {!selectedRole ? (
            <div className="admin-empty">
              Select a role to manage its
              permissions.
            </div>
          ) : (
            <>

              <p className="admin-description">
                {selectedRole.description ||
                  'No description provided.'}
              </p>

              <button
                type="button"
                className="primary-button"
                onClick={onManagePermissions}
              >
                Manage permissions
              </button>

              <button
                type="button"
                className="danger-button"
                onClick={() =>
                  onDeleteRole(
                    selectedRole,
                  )
                }
              >
                Delete role
              </button>

            </>
          )}

        </section>

      </div>


      {/* ================================================================== */}
      {/* Permissions for selected role                                      */}
      {/* ================================================================== */}

      <div className="admin-panel">

        <div className="admin-panel-header">

          <div>
            <p className="eyebrow">
              PERMISSIONS
            </p>

            <h3>
              {selectedRole
                ? `${selectedRole.name} permissions`
                : 'Role permissions'}
            </h3>
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={onBackToRoles}
          >
            Back to roles
          </button>

        </div>


        {!selectedRole ? (
          <div className="admin-empty">
            Select a role first.
          </div>
        ) : (
          <>

            <div className="permission-assignment">

              <select
                value={selectedPermission}
                onChange={event =>
                  onPermissionChange(
                    event.target.value,
                  )
                }
              >
                <option value="">
                  Select permission
                </option>

                {availablePermissions.map(
                  permission => (
                    <option
                      value={
                        permission.code
                      }
                      key={
                        permission.code
                      }
                    >
                      {permission.name}
                    </option>
                  ),
                )}

              </select>


              <button
                type="button"
                className="primary-button"
                disabled={
                  !selectedPermission
                }
                onClick={
                  onAssignPermission
                }
              >
                Assign permission
              </button>

            </div>


            <div className="permission-list">

              {permissions.length === 0 ? (
                <div className="admin-empty">
                  This role currently has
                  no permissions.
                </div>
              ) : (
                permissions.map(
                  permission => (
                    <div
                      className="permission-item"
                      key={
                        permission.code
                      }
                    >

                      <div>
                        <strong>
                          {permission.name}
                        </strong>

                        <span>
                          {permission.code}
                        </span>

                        <p>
                          {
                            permission.description
                          }
                        </p>
                      </div>


                      <button
                        type="button"
                        className="danger-button"
                        onClick={() =>
                          onRemovePermission(
                            permission.code,
                          )
                        }
                      >
                        Remove
                      </button>

                    </div>
                  ),
                )
              )}

            </div>

          </>
        )}

      </div>
    </>
  )
}