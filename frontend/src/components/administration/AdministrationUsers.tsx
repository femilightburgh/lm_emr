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

      <div className="admin-panel-header">

        <div>
          <p className="eyebrow">
            USERS
          </p>

          <h3>
            Hospital users
          </h3>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={onRefresh}
          disabled={loading}
        >
          Refresh
        </button>

      </div>


      {/* ================================================================== */}
      {/* Add Staff                                                          */}
      {/* ================================================================== */}

      <div className="admin-onboarding-card">

        <h4>
          Add hospital staff
        </h4>

        <p>
          Create a pending staff account and
          generate a one-time activation
          invitation.
        </p>


        <form
          className="admin-onboarding-form"
          onSubmit={handleSubmit}
        >

          <div className="admin-field">

            <label htmlFor="staff-email">
              Work email
            </label>

            <input
              id="staff-email"
              type="email"
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


          <div className="admin-field">

            <label htmlFor="staff-role">
              Initial role
            </label>

            <select
              id="staff-role"
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


          <button
            type="submit"
            className="primary-button"
            disabled={submitting}
          >
            {submitting
              ? 'Creating...'
              : 'Create invitation'}
          </button>

        </form>


        {onboardingError && (
          <div className="admin-form-error">
            {onboardingError}
          </div>
        )}

      </div>


      {/* ================================================================== */}
      {/* Invitation Result                                                 */}
      {/* ================================================================== */}

      {invitation && (
        <div className="admin-invitation">

          <h4>
            Invitation created
          </h4>

          <p>
            {invitation.user.email} has been
            added as a pending staff member.
          </p>

          <p>
            The invitation expires on{' '}
            {new Date(
              invitation.invitation_expires_at,
            ).toLocaleString()}.
          </p>


          <code className="admin-invitation-token">
            {invitation.invitation_token}
          </code>


          <div className="admin-invitation-actions">

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
      )}


      {/* ================================================================== */}
      {/* Search                                                             */}
      {/* ================================================================== */}

      <div className="admin-users-toolbar">

        <div className="admin-search">

          <input
            type="search"
            value={search}
            onChange={event =>
              setSearch(
                event.target.value,
              )
            }
            placeholder="Search staff by email..."
            aria-label="Search hospital users"
          />

        </div>

        <span>
          {filteredUsers.length}{' '}
          {filteredUsers.length === 1
            ? 'user'
            : 'users'}
        </span>

      </div>


      {/* ================================================================== */}
      {/* Users Table                                                        */}
      {/* ================================================================== */}

      {loading ? (
        <div className="admin-empty">
          Loading users...
        </div>
      ) : filteredUsers.length === 0 ? (
        <div className="admin-empty">
          <strong>
            {search
              ? 'No matching users.'
              : 'No users found.'}
          </strong>
        </div>
      ) : (
        <div className="admin-table">

          <div className="admin-table-header">
            <span>
              Email
            </span>

            <span>
              Status
            </span>

            <span>
              Roles
            </span>

            <span>
              Action
            </span>
          </div>


          {filteredUsers.map(user => (
            <div
              className="admin-table-row"
              key={user.id}
            >

              <strong>
                {user.email}
              </strong>


              <span
                className={statusClass(
                  user.status,
                )}
              >
                {user.status}
              </span>


              <span className="role-badges">

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

              </span>


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
          ))}

        </div>
      )}


      {/* ================================================================== */}
      {/* User Manager                                                       */}
      {/* ================================================================== */}

      {selectedUser && (
        <div className="admin-user-manager">

          <div className="admin-panel-header">

            <div>

              <p className="eyebrow">
                USER ACCESS
              </p>

              <h3>
                {selectedUser.email}
              </h3>

            </div>


            <button
              type="button"
              className="secondary-button"
              onClick={onCloseUser}
            >
              Close
            </button>

          </div>


          <div className="current-roles">

            <h4>
              Current roles
            </h4>


            {selectedUser.roles.length === 0 ? (
              <p>
                No active roles.
              </p>
            ) : (
              selectedUser.roles.map(role => (
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
              ))
            )}

          </div>


          <div className="admin-role-assignment">

            <h4>
              Assign role
            </h4>

            <div className="inline-form">

              <select
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
      )}

    </div>
  )
}