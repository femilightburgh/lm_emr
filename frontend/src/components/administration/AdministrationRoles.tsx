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
    <div className="admin-panel">

      {/* ================================================================== */}
      {/* Roles                                                              */}
      {/* ================================================================== */}

      <div className="page-header">

        <div>
          <p className="eyebrow">
            ACCESS CONTROL
          </p>

          <h2>
            Roles & permissions
          </h2>

          <p>
            Define hospital roles and the permissions
            assigned to them.
          </p>
        </div>

        <button
          type="button"
          className="primary-button"
          onClick={onCreateRole}
        >
          New role
        </button>

      </div>


      {/* ================================================================== */}
      {/* Role Creation / Editing                                             */}
      {/* ================================================================== */}

      {editingRole && (
        <section className="workspace-panel">

          <div className="panel-header">

            <div>
              <p className="eyebrow">
                {editingRole
                  ? 'EDIT ROLE'
                  : 'NEW ROLE'}
              </p>

              <h3>
                {editingRole
                  ? 'Edit role'
                  : 'Create role'}
              </h3>

              <p>
                Define the role name and its purpose
                within the hospital.
              </p>
            </div>

          </div>


          <form
            className="shared-form-section"
            onSubmit={onSaveRole}
          >

            <div className="form-grid">

              <div className="form-field">
                <label htmlFor="role-name">
                  Role name
                </label>

                <input
                  id="role-name"
                  className="form-control"
                  value={roleName}
                  onChange={event =>
                    onRoleNameChange(
                      event.target.value,
                    )
                  }
                  placeholder="e.g. Nurse Manager"
                />
              </div>


              <div className="form-field">
                <label htmlFor="role-description">
                  Description
                </label>

                <input
                  id="role-description"
                  className="form-control"
                  value={roleDescription}
                  onChange={event =>
                    onRoleDescriptionChange(
                      event.target.value,
                    )
                  }
                  placeholder="Describe this role"
                />
              </div>

            </div>


            <div className="form-actions">

              <button
                type="submit"
                className="primary-button"
                disabled={savingRole}
              >
                {savingRole
                  ? 'Saving...'
                  : editingRole
                    ? 'Save Changes'
                    : 'Create Role'}
              </button>

              <button
                type="button"
                className="secondary-button"
                onClick={onBackToRoles}
                disabled={savingRole}
              >
                Cancel
              </button>

            </div>

          </form>

        </section>
      )}


      {/* ================================================================== */}
      {/* Role Directory                                                      */}
      {/* ================================================================== */}

      <section className="workspace-panel">

        <div className="panel-header">

          <div>
            <p className="eyebrow">
              ROLE DIRECTORY
            </p>

            <h3>
              Hospital roles
            </h3>

            <p>
              {roles.length}{' '}
              role
              {roles.length === 1
                ? ''
                : 's'} configured for this hospital.
            </p>
          </div>

          <span className="staff-directory-count">
            {selectedRole
              ? `Selected: ${selectedRole.name}`
              : `${roles.length} total`}
          </span>

        </div>


        {roles.length === 0 ? (
          <div className="empty-state">
            <strong>
              No roles found.
            </strong>

            <p>
              Create the first hospital role to
              configure access.
            </p>
          </div>
        ) : (
          <div className="data-table admin-roles-directory">

            <div className="
              data-table-header
              admin-roles-directory-header
            ">
              <div>
                Role
              </div>

              <div>
                Description
              </div>

              <div>
                Action
              </div>
            </div>


            {roles.map(role => (
              <div
                key={role.id}
                className="
                  data-table-row
                  admin-roles-directory-row
                "
              >

                <div className="data-table-cell">

                  <button
                    type="button"
                    className="admin-role-directory-select"
                    onClick={() =>
                      onSelectRole(role.id)
                    }
                  >
                    <strong>
                      {role.name}
                    </strong>

                    <span>
                      Role
                    </span>
                  </button>

                </div>


                <div className="data-table-cell">
                  <strong className="
                    admin-role-description
                  ">
                    {role.description ||
                      'No description provided.'}
                  </strong>
                </div>


                <div className="
                  data-table-cell
                  admin-roles-directory-action
                ">

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() =>
                      onSelectRole(role.id)
                    }
                  >
                    Select
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

              </div>
            ))}

          </div>
        )}

      </section>


      {/* ================================================================== */}
      {/* Selected Role                                                       */}
      {/* ================================================================== */}

      <section className="workspace-panel">

        <div className="panel-header">

          <div>
            <p className="eyebrow">
              ROLE DETAILS
            </p>

            <h3>
              {selectedRole
                ? selectedRole.name
                : 'Select a role'}
            </h3>

            {selectedRole && (
              <p>
                {selectedRole.description ||
                  'No description provided.'}
              </p>
            )}
          </div>

        </div>


        {!selectedRole ? (
          <div className="empty-state">
            <strong>
              No role selected.
            </strong>

            <p>
              Select a role above to manage its
              permissions.
            </p>
          </div>
        ) : (
          <div className="role-detail-actions">

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

          </div>
        )}

      </section>


      {/* ================================================================== */}
      {/* Permissions                                                         */}
      {/* ================================================================== */}

      <section className="workspace-panel">

        <div className="panel-header">

          <div>
            <p className="eyebrow">
              PERMISSIONS
            </p>

            <h3>
              {selectedRole
                ? `${selectedRole.name} permissions`
                : 'Role permissions'}
            </h3>

            <p>
              Assign or remove permissions for the
              selected role.
            </p>
          </div>

        </div>


        {!selectedRole ? (
          <div className="empty-state">
            <strong>
              Select a role first.
            </strong>

            <p>
              Permissions will appear here once
              a role is selected.
            </p>
          </div>
        ) : (
          <>

            <div className="permission-assignment">

              <select
                className="form-control"
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


            {permissions.length === 0 ? (
              <div className="empty-state">
                <strong>
                  No permissions assigned.
                </strong>

                <p>
                  Use the selector above to assign
                  a permission to this role.
                </p>
              </div>
            ) : (
              <div className="permission-list">

                {permissions.map(
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
                )}

              </div>
            )}

          </>
        )}

      </section>

    </div>
  )
}
