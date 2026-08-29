import {
  useMemo,
  useState,
  type FormEvent,
} from 'react'

import type {
  AdminUser,
  OnboardStaffResponse,
  Role,
} from '../../api'


interface AdministrationUsersProps {
  users: AdminUser[]
  roles: Role[]
  loading: boolean
  selectedUser: AdminUser | null

  onRefresh: () => void

  onSelectUser: (
    user: AdminUser,
  ) => void

  onCloseUser: () => void

  onAssignRole: (
    user: AdminUser,
    role: Role,
  ) => void

  onRemoveRole: (
    user: AdminUser,
    roleName: string,
  ) => void

  onOnboardStaff: (
    email: string,
    roleName: string,
  ) => Promise<OnboardStaffResponse>
}


export default function AdministrationUsers({
  users,
  roles,
  loading,
  selectedUser,
  onRefresh,
  onSelectUser,
  onCloseUser,
  onAssignRole,
  onRemoveRole,
  onOnboardStaff,
}: AdministrationUsersProps) {

  const [search, setSearch] =
    useState('')

  const [email, setEmail] =
    useState('')

  const [roleName, setRoleName] =
    useState('')

  const [submitting, setSubmitting] =
    useState(false)

  const [onboardingError, setOnboardingError] =
    useState<string | null>(null)

  const [invitation, setInvitation] =
    useState<OnboardStaffResponse | null>(
      null,
    )


  const filteredUsers =
    useMemo(() => {
      const query =
        search.trim().toLowerCase()

      if (!query) {
        return users
      }

      return users.filter(user =>
        user.email
          .toLowerCase()
          .includes(query),
      )
    }, [users, search])


  function resetInvitation() {
    setInvitation(null)
    setOnboardingError(null)
  }


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const normalizedEmail =
      email.trim().toLowerCase()

    if (!normalizedEmail) {
      setOnboardingError(
        'Email address is required.',
      )
      return
    }

    if (!roleName) {
      setOnboardingError(
        'Select an initial role.',
      )
      return
    }

    setSubmitting(true)
    setOnboardingError(null)
    setInvitation(null)

    try {
      const response =
        await onOnboardStaff(
          normalizedEmail,
          roleName,
        )

      setInvitation(response)
      setEmail('')
      setRoleName('')
    } catch {
      setOnboardingError(
        'Unable to create staff invitation.',
      )
    } finally {
      setSubmitting(false)
    }
  }


  function statusClass(
    status: string,
  ) {
    switch (
      status.toUpperCase()
    ) {
      case 'ACTIVE':
        return 'admin-status admin-status-active'

      case 'PENDING':
        return 'admin-status admin-status-pending'

      case 'LOCKED':
        return 'admin-status admin-status-locked'

      case 'INACTIVE':
        return 'admin-status admin-status-inactive'

      default:
        return 'admin-status'
    }
  }


  async function copyInvitationToken() {
    if (!invitation) {
      return
    }

    await navigator.clipboard.writeText(
      invitation.invitation_token,
    )
  }


  return (
    <div className="admin-panel">

      {/* ================================================================== */}
      {/* Header                                                             */}
      {/* ================================================================== */}

      <div className="page-header">

        <div>
          <p className="eyebrow">
            USER ACCOUNTS
          </p>

          <h2>
            Hospital users
          </h2>

          <p>
            Manage LIGHTBURGH login accounts,
            roles, and access.
          </p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={onRefresh}
          disabled={loading}
        >
          {loading
            ? 'Refreshing...'
            : 'Refresh'}
        </button>

      </div>


      {/* ================================================================== */}
      {/* Invitation                                                          */}
      {/* ================================================================== */}

      <section className="workspace-panel">

        <div className="panel-header">
          <div>
            <p className="eyebrow">
              ACCOUNT ONBOARDING
            </p>

            <h3>
              Add hospital staff
            </h3>

            <p>
              Create a pending LIGHTBURGH account
              and generate a one-time activation
              invitation.
            </p>
          </div>
        </div>


        <form
          className="shared-form-section"
          onSubmit={handleSubmit}
        >

          <div className="form-grid">

            <div className="form-field">
              <label htmlFor="staff-email">
                Work email
              </label>

              <input
                id="staff-email"
                type="email"
                className="form-control"
                value={email}
                onChange={event =>
                  setEmail(
                    event.target.value,
                  )
                }
                placeholder="staff@hospital.com"
                disabled={submitting}
              />
            </div>


            <div className="form-field">
              <label htmlFor="staff-role">
                Initial role
              </label>

              <select
                id="staff-role"
                className="form-control"
                value={roleName}
                onChange={event =>
                  setRoleName(
                    event.target.value,
                  )
                }
                disabled={submitting}
              >
                <option value="">
                  Select a role
                </option>

                {roles.map(role => (
                  <option
                    key={role.id}
                    value={role.name}
                  >
                    {role.name}
                  </option>
                ))}
              </select>
            </div>

          </div>


          {onboardingError && (
            <div className="error-state">
              {onboardingError}
            </div>
          )}


          <div className="form-actions">
            <button
              type="submit"
              className="primary-button"
              disabled={submitting}
            >
              {submitting
                ? 'Creating...'
                : 'Create invitation'}
            </button>
          </div>

        </form>

      </section>


      {/* ================================================================== */}
      {/* Invitation Result                                                   */}
      {/* ================================================================== */}

      {invitation && (
        <section className="workspace-panel">

          <div className="panel-header">

            <div>
              <p className="eyebrow">
                INVITATION
              </p>

              <h3>
                Invitation created
              </h3>

              <p>
                {invitation.user.email} has been
                added as a pending staff member.
              </p>
            </div>

          </div>


          <div className="detail-panel">

            <p>
              The invitation expires on{' '}
              {new Date(
                invitation.invitation_expires_at,
              ).toLocaleString()}.
            </p>

            <code className="admin-invitation-token">
              {invitation.invitation_token}
            </code>

            <div className="form-actions">

              <button
                type="button"
                className="primary-button"
                onClick={() =>
                  void copyInvitationToken()
                }
              >
                Copy invitation token
              </button>

              <button
                type="button"
                className="secondary-button"
                onClick={resetInvitation}
              >
                Dismiss
              </button>

            </div>

          </div>

        </section>
      )}


      {/* ================================================================== */}
      {/* Search                                                              */}
      {/* ================================================================== */}

      <section className="workspace-panel">

        <div className="admin-users-toolbar">

          <div className="admin-search">
            <input
              type="search"
              className="form-control"
              value={search}
              onChange={event =>
                setSearch(
                  event.target.value,
                )
              }
              placeholder="Search users by email..."
              aria-label="Search hospital users"
            />
          </div>

          <span className="staff-directory-count">
            {filteredUsers.length}{' '}
            {filteredUsers.length === 1
              ? 'user'
              : 'users'}
          </span>

        </div>


        {/* ================================================================ */}
        {/* Users Table                                                       */}
        {/* ================================================================ */}

        {loading ? (
          <div className="empty-state">
            <strong>
              Loading users...
            </strong>
          </div>
        ) : filteredUsers.length === 0 ? (
          <div className="empty-state">

            <strong>
              {search
                ? 'No matching users.'
                : 'No users found.'}
            </strong>

            {search && (
              <p>
                Try a different email address.
              </p>
            )}

          </div>
        ) : (
          <div className="data-table admin-users-directory">

            <div className="
              data-table-header
              admin-users-directory-header
            ">
              <div>
                User
              </div>

              <div>
                Status
              </div>

              <div>
                Roles
              </div>

              <div>
                Action
              </div>
            </div>


            {filteredUsers.map(user => (
              <div
                className="
                  data-table-row
                  admin-users-directory-row
                "
                key={user.id}
              >

                <div className="data-table-cell">
                  <strong>
                    {user.email}
                  </strong>

                  <span>
                    LIGHTBURGH account
                  </span>
                </div>


                <div className="data-table-cell">
                  <span
                    className={statusClass(
                      user.status,
                    )}
                  >
                    {user.status}
                  </span>
                </div>


                <div className="
                  data-table-cell
                  role-badges
                ">

                  {user.roles.length === 0 ? (
                    <span>
                      No roles
                    </span>
                  ) : (
                    user.roles.map(role => (
                      <span
                        className="role-badge"
                        key={role.id}
                      >
                        {role.role_name}
                      </span>
                    ))
                  )}

                </div>


                <div className="
                  data-table-cell
                  admin-users-directory-action
                ">
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() =>
                      onSelectUser(user)
                    }
                  >
                    Manage
                  </button>
                </div>

              </div>
            ))}

          </div>
        )}

      </section>


      {/* ================================================================== */}
      {/* User Manager                                                        */}
      {/* ================================================================== */}

      {selectedUser && (
        <section className="workspace-panel">

          <div className="panel-header">

            <div>
              <p className="eyebrow">
                USER ACCESS
              </p>

              <h3>
                {selectedUser.email}
              </h3>

              <p>
                Manage roles assigned to this
                LIGHTBURGH account.
              </p>
            </div>

            <button
              type="button"
              className="secondary-button"
              onClick={onCloseUser}
            >
              Close
            </button>

          </div>


          <div className="detail-panel">

            <div className="section-heading">
              <div>
                <h3>
                  Current roles
                </h3>

                <p>
                  Roles determine the capabilities
                  available to this account.
                </p>
              </div>
            </div>


            {selectedUser.roles.length === 0 ? (
              <div className="empty-state">
                <strong>
                  No active roles.
                </strong>

                <p>
                  Assign a role below to provide
                  system access.
                </p>
              </div>
            ) : (
              <div>
                {selectedUser.roles.map(role => (
                  <div
                    className="permission-item"
                    key={role.id}
                  >

                    <div>
                      <strong>
                        {role.role_name}
                      </strong>
                    </div>

                    <button
                      type="button"
                      className="danger-button"
                      onClick={() =>
                        onRemoveRole(
                          selectedUser,
                          role.role_name,
                        )
                      }
                    >
                      Remove
                    </button>

                  </div>
                ))}
              </div>
            )}


            <div className="admin-role-assignment">

              <div className="section-heading">
                <div>
                  <h3>
                    Assign role
                  </h3>

                  <p>
                    Select a role to grant its
                    configured permissions.
                  </p>
                </div>
              </div>


              <div className="inline-form">

                <select
                  className="form-control"
                  defaultValue=""
                  onChange={event => {

                    const role =
                      roles.find(
                        item =>
                          item.name ===
                          event.target.value,
                      )

                    if (role) {
                      onAssignRole(
                        selectedUser,
                        role,
                      )
                    }

                  }}
                >
                  <option value="">
                    Select a role
                  </option>

                  {roles.map(role => (
                    <option
                      value={role.name}
                      key={role.id}
                    >
                      {role.name}
                    </option>
                  ))}

                </select>

              </div>

            </div>

          </div>

        </section>
      )}

    </div>
  )
}
