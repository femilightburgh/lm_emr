import {
  useMemo,
  useState,
  type FormEvent,
} from 'react'

import type {
  AdminUser,
  Staff,
} from '../../api'

import type {
  EmploymentStatus,
  EmploymentType,
  Gender,
  Profession,
} from '../../types'


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


interface Props {
  hospitalId: string

  staff: Staff[]
  users: AdminUser[]

  loading: boolean

  onRefresh: () => void

  onLinkUser: (
    staff: Staff,
    userId: string,
  ) => Promise<void>

  onCreateStaff: (
    payload: CreateStaffPayload,
  ) => Promise<void>
}


interface FormState {
  staffNumber: string

  firstName: string
  middleName: string
  lastName: string

  gender: Gender

  dateOfBirth: string

  phoneNumber: string
  email: string

  profession: Profession

  employmentStatus: EmploymentStatus

  employmentType: EmploymentType

  dateEmployed: string
}


const INITIAL_FORM: FormState = {
  staffNumber: '',

  firstName: '',
  middleName: '',
  lastName: '',

  gender: 'Female',

  dateOfBirth: '',

  phoneNumber: '',
  email: '',

  profession: 'Receptionist',

  employmentStatus: 'Active',

  employmentType: 'Full Time',

  dateEmployed: '',
}


const PROFESSIONS: Profession[] = [
  'Doctor',
  'Nurse',
  'Pharmacist',
  'Laboratory Scientist',
  'Radiographer',
  'Physiotherapist',
  'Dietitian',
  'Dentist',
  'Receptionist',
  'Records Officer',
  'Accountant',
  'Administrator',
  'IT Support',
  'Other',
]


const EMPLOYMENT_STATUSES:
  EmploymentStatus[] = [
    'Active',
    'On Leave',
    'Suspended',
    'Resigned',
    'Retired',
    'Terminated',
  ]


const EMPLOYMENT_TYPES:
  EmploymentType[] = [
    'Full Time',
    'Part Time',
    'Contract',
    'Locum',
    'Intern',
    'Resident',
    'Visiting',
  ]


export default function AdministrationStaff({
  hospitalId,
  staff,
  users,
  loading,
  onRefresh,
  onLinkUser,
  onCreateStaff,
}: Props) {
  const [
    showCreateForm,
    setShowCreateForm,
  ] = useState(false)

  const [
    form,
    setForm,
  ] = useState<FormState>(
    INITIAL_FORM,
  )

  const [
    creating,
    setCreating,
  ] = useState(false)

  const [
    createError,
    setCreateError,
  ] = useState<string | null>(null)

  const [
    selectedUsers,
    setSelectedUsers,
  ] = useState<
    Record<string, string>
  >({})

  const [
    linkingStaffId,
    setLinkingStaffId,
  ] = useState<string | null>(
    null,
  )


  // ==========================================================================
  // Available user accounts
  // ==========================================================================

  const availableUsers = useMemo(
    () =>
      users.filter(
        user =>
          !user.is_superuser &&
          user.status !== 'inactive',
      ),
    [users],
  )


  // ==========================================================================
  // Form helpers
  // ==========================================================================

  function updateForm<
    K extends keyof FormState,
  >(
    field: K,
    value: FormState[K],
  ) {
    setForm(current => ({
      ...current,
      [field]: value,
    }))
  }


  function resetForm() {
    setForm({
      ...INITIAL_FORM,

      dateEmployed:
        new Date()
          .toISOString()
          .slice(0, 10),
    })

    setCreateError(null)
  }


  function openCreateForm() {
    resetForm()
    setShowCreateForm(true)
  }


  function closeCreateForm() {
    setShowCreateForm(false)
    setCreateError(null)
  }


  // ==========================================================================
  // Create Staff
  // ==========================================================================

  async function handleCreateStaff(
    event: FormEvent<HTMLFormElement>,
  ) {
    console.log('CREATE STAFF SUBMITTED')
    event.preventDefault()

    setCreateError(null)

    if (!hospitalId) {
      setCreateError(
        'Hospital ID is missing.',
      )
      return
    }

    if (!form.staffNumber.trim()) {
      setCreateError(
        'Staff number is required.',
      )
      return
    }

    if (!form.firstName.trim()) {
      setCreateError(
        'First name is required.',
      )
      return
    }

    if (!form.lastName.trim()) {
      setCreateError(
        'Last name is required.',
      )
      return
    }

    if (!form.dateOfBirth) {
      setCreateError(
        'Date of birth is required.',
      )
      return
    }

    if (!form.dateEmployed) {
      setCreateError(
        'Date employed is required.',
      )
      return
    }

    console.log('CREATE STAFF VALIDATION PASSED')
    console.log('CREATE STAFF PAYLOAD', {
        hospital_id: hospitalId,
        staff_number: form.staffNumber,
        first_name: form.firstName,
        last_name: form.lastName,
        gender: form.gender,
        date_of_birth: form.dateOfBirth,
        profession: form.profession,
        employment_status: form.employmentStatus,
        employment_type: form.employmentType,
        date_employed: form.dateEmployed,
    })

    setCreating(true)

    try {
    await onCreateStaff({
        hospital_id: hospitalId,

        staff_number:
          form.staffNumber.trim(),

        first_name:
          form.firstName.trim(),

        middle_name:
          form.middleName.trim() ||
          null,

        last_name:
          form.lastName.trim(),

        gender:
          form.gender,

        date_of_birth:
          form.dateOfBirth,

        phone_number:
          form.phoneNumber.trim() ||
          null,

        email:
          form.email.trim() ||
          null,

        profession:
          form.profession,

        employment_status:
          form.employmentStatus,

        employment_type:
          form.employmentType,

        date_employed:
          form.dateEmployed,
      })

      resetForm()

      setShowCreateForm(false)
    } catch (err) {
      setCreateError(
        err instanceof Error
          ? err.message
          : 'Unable to create staff profile.',
      )
    } finally {
      setCreating(false)
    }
  }


  // ==========================================================================
  // User linking
  // ==========================================================================

  function getSelectedUserId(
    staffId: string,
  ): string {
    return (
      selectedUsers[staffId] ?? ''
    )
  }


  function handleUserSelection(
    staffId: string,
    userId: string,
    ) {
    console.log(
        'USER SELECTED',
        {
        staffId,
        userId,
        },
    )

    setSelectedUsers(current => ({
        ...current,
        [staffId]: userId,
    }))
    }


  async function handleLinkUser(
    member: Staff,
    ) {
    console.log(
        'LINK BUTTON CLICKED',
        {
        staffId: member.id,
        selectedUserId:
            getSelectedUserId(member.id),
        },
    )

    const userId =
        getSelectedUserId(member.id)

    if (!userId) {
      return
    }

    setLinkingStaffId(member.id)

    try {
      await onLinkUser(
        member,
        userId,
      )

      setSelectedUsers(current => {
        const next = {
          ...current,
        }

        delete next[member.id]

        return next
      })
    } finally {
      setLinkingStaffId(null)
    }
  }


  // ==========================================================================
  // Render
  // ==========================================================================

  return (
    <section className="admin-panel">

      {/* ==================================================================== */}
      {/* Header                                                               */}
      {/* ==================================================================== */}

      <div className="admin-panel-header">

        <div>
          <p className="eyebrow">
            STAFF
          </p>

          <h3>
            Hospital staff
          </h3>

          <p>
            Create staff profiles and link
            them to hospital user accounts.
          </p>
        </div>


        <div>
          <button
            type="button"
            className="primary-button"
            onClick={
              showCreateForm
                ? closeCreateForm
                : openCreateForm
            }
          >
            {showCreateForm
              ? 'Cancel'
              : 'Add Staff'}
          </button>


          <button
            type="button"
            className="secondary-button"
            onClick={onRefresh}
            disabled={loading}
          >
            {loading
              ? 'Loading...'
              : 'Refresh'}
          </button>
        </div>

      </div>


      {/* ==================================================================== */}
      {/* Create Staff Form                                                    */}
      {/* ==================================================================== */}

      {showCreateForm && (
        <form
          className="admin-onboarding-card"
          onSubmit={
            handleCreateStaff
          }
        >

          <div>
            <p className="eyebrow">
              NEW STAFF PROFILE
            </p>

            <h4>
              Add hospital staff
            </h4>

            <p>
              Create the staff profile first,
              then link the person's user
              account.
            </p>
          </div>


          {createError && (
            <div className="admin-error">
              {createError}
            </div>
          )}


          <div className="admin-onboarding-form">

            {/* Staff Number */}

            <label>
              Staff number

              <input
                type="text"
                value={
                  form.staffNumber
                }
                onChange={event =>
                  updateForm(
                    'staffNumber',
                    event.target.value,
                  )
                }
                placeholder="e.g. WTH-REC-001"
                required
              />
            </label>


            {/* First Name */}

            <label>
              First name

              <input
                type="text"
                value={
                  form.firstName
                }
                onChange={event =>
                  updateForm(
                    'firstName',
                    event.target.value,
                  )
                }
                required
              />
            </label>


            {/* Middle Name */}

            <label>
              Middle name

              <input
                type="text"
                value={
                  form.middleName
                }
                onChange={event =>
                  updateForm(
                    'middleName',
                    event.target.value,
                  )
                }
              />
            </label>


            {/* Last Name */}

            <label>
              Last name

              <input
                type="text"
                value={
                  form.lastName
                }
                onChange={event =>
                  updateForm(
                    'lastName',
                    event.target.value,
                  )
                }
                required
              />
            </label>


            {/* Gender */}

            <label>
              Gender

              <select
                value={form.gender}
                onChange={event =>
                  updateForm(
                    'gender',
                    event.target.value as Gender,
                  )
                }
              >
                <option value="Female">
                  Female
                </option>

                <option value="Male">
                  Male
                </option>
              </select>
            </label>


            {/* Date of Birth */}

            <label>
              Date of birth

              <input
                type="date"
                value={
                  form.dateOfBirth
                }
                onChange={event =>
                  updateForm(
                    'dateOfBirth',
                    event.target.value,
                  )
                }
                required
              />
            </label>


            {/* Phone */}

            <label>
              Phone number

              <input
                type="tel"
                value={
                  form.phoneNumber
                }
                onChange={event =>
                  updateForm(
                    'phoneNumber',
                    event.target.value,
                  )
                }
              />
            </label>


            {/* Email */}

            <label>
              Email

              <input
                type="email"
                value={form.email}
                onChange={event =>
                  updateForm(
                    'email',
                    event.target.value,
                  )
                }
              />
            </label>


            {/* Profession */}

            <label>
              Profession

              <select
                value={
                  form.profession
                }
                onChange={event =>
                  updateForm(
                    'profession',
                    event.target.value as Profession,
                  )
                }
              >
                {PROFESSIONS.map(
                  profession => (
                    <option
                      key={profession}
                      value={profession}
                    >
                      {profession}
                    </option>
                  ),
                )}
              </select>
            </label>


            {/* Employment Status */}

            <label>
              Employment status

              <select
                value={
                  form.employmentStatus
                }
                onChange={event =>
                  updateForm(
                    'employmentStatus',
                    event.target.value as EmploymentStatus,
                  )
                }
              >
                {EMPLOYMENT_STATUSES.map(
                  status => (
                    <option
                      key={status}
                      value={status}
                    >
                      {status}
                    </option>
                  ),
                )}
              </select>
            </label>


            {/* Employment Type */}

            <label>
              Employment type

              <select
                value={
                  form.employmentType
                }
                onChange={event =>
                  updateForm(
                    'employmentType',
                    event.target.value as EmploymentType,
                  )
                }
              >
                {EMPLOYMENT_TYPES.map(
                  employmentType => (
                    <option
                      key={employmentType}
                      value={employmentType}
                    >
                      {employmentType}
                    </option>
                  ),
                )}
              </select>
            </label>


            {/* Date Employed */}

            <label>
              Date employed

              <input
                type="date"
                value={
                  form.dateEmployed
                }
                onChange={event =>
                  updateForm(
                    'dateEmployed',
                    event.target.value,
                  )
                }
                required
              />
            </label>

          </div>


          <div>
            <button
              type="submit"
              className="primary-button"
              disabled={creating}
            >
              {creating
                ? 'Creating...'
                : 'Create Staff'}
            </button>
          </div>

        </form>
      )}


      {/* ==================================================================== */}
      {/* Staff List                                                           */}
      {/* ==================================================================== */}

      {loading &&
      staff.length === 0 ? (
        <div className="admin-empty-state">
          Loading staff...
        </div>
      ) : staff.length === 0 ? (
        <div className="admin-empty-state">
          No staff profiles found.
        </div>
      ) : (
        <div className="admin-staff-list">

          {staff.map(member => {

            const linkedUser =
              users.find(
                user =>
                  user.id ===
                  member.user_account_id,
              )


            const selectedUserId =
              getSelectedUserId(
                member.id,
              )


            const isLinking =
              linkingStaffId ===
              member.id


            return (
              <article
                key={member.id}
                className="admin-staff-card"
              >

                {/* ======================================================== */}
                {/* Staff Details                                             */}
                {/* ======================================================== */}

                <div className="admin-staff-details">

                  <div>
                    <strong>
                      {member.first_name}{' '}

                      {member.middle_name
                        ? `${member.middle_name} `
                        : ''}

                      {member.last_name}
                    </strong>


                    <p>
                      Staff number:{' '}
                      {member.staff_number}
                    </p>


                    <p>
                      {member.email ??
                        'No email recorded'}
                    </p>

                  </div>


                  <div>

                    {member.user_account_id ? (
                      <span>
                        Linked to:{' '}

                        {linkedUser?.email ??
                          member.user_account_id}
                      </span>
                    ) : (
                      <span>
                        No user account linked
                      </span>
                    )}

                  </div>

                </div>


                {/* ======================================================== */}
                {/* Link User Account                                        */}
                {/* ======================================================== */}

                {!member.user_account_id && (
                  <div className="admin-staff-link">

                    <select
                      value={
                        selectedUserId
                      }
                      onChange={event =>
                        handleUserSelection(
                          member.id,
                          event.target.value,
                        )
                      }
                      disabled={isLinking}
                    >

                      <option value="">
                        Select user account
                      </option>


                      {availableUsers.map(
                        user => (
                          <option
                            key={user.id}
                            value={user.id}
                          >
                            {user.email}
                          </option>
                        ),
                      )}

                    </select>


                    <button
                      type="button"
                      className="primary-button"
                      disabled={
                        !selectedUserId ||
                        isLinking
                      }
                      onClick={() =>
                        void handleLinkUser(
                          member,
                        )
                      }
                    >
                      {isLinking
                        ? 'Linking...'
                        : 'Link account'}
                    </button>

                  </div>
                )}

              </article>
            )
          })}

        </div>
      )}

    </section>
  )
}