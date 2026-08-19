import {
  useEffect,
  useState,
} from 'react'
import type { FormEvent } from 'react'
import AdministratorWorkspace from './components/administration/AdministratorWorkspace'
import AppShell from './app/AppShell'

import {
  createPatient,
  getCurrentUser,
  listPatients,
  login,
  refreshAccessToken,
  searchPatients,
} from './api'

import {
  clearSession,
  getAccessToken,
  getRefreshToken,
  saveSession,
} from './auth'

import type {
  AuthenticatedUser,
  CreatePatientRequest,
  LoginResponse,
  Patient,
} from './types'

import './App.css'
import ActivateAccount from './components/auth/ActivateAccount'


type WorkspaceView =
  | 'dashboard'
  | 'patients'
  | 'register'
  | 'administrator'


const emptyPatientForm: CreatePatientRequest = {
  hospital_number: '',
  first_name: '',
  last_name: '',
  middle_name: '',
  sex: 'Male',
  date_of_birth: '',
  phone_number: '',
  email: '',
  address: '',
  occupation: '',
  marital_status: null,
  religion: '',
  blood_group: null,
  genotype: null,
  next_of_kin_name: '',
  next_of_kin_relationship: null,
  next_of_kin_phone: '',
  next_of_kin_address: '',
}


function App() {
  // ==========================================================================
  // Authentication
  // ==========================================================================

  const [hospitalCode, setHospitalCode] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const [session, setSession] =
    useState<LoginResponse | null>(null)

  const [user, setUser] =
    useState<AuthenticatedUser | null>(null)

  const [initializing, setInitializing] =
    useState(true)

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)


  // ==========================================================================
  // Workspace
  // ==========================================================================

  const [view, setView] =
    useState<WorkspaceView>('dashboard')

  const [patients, setPatients] =
    useState<Patient[]>([])

  const [patientCount, setPatientCount] =
    useState(0)

  const [patientLoading, setPatientLoading] =
    useState(false)

  const [patientError, setPatientError] =
    useState<string | null>(null)

  const [searchQuery, setSearchQuery] =
    useState('')

  const [selectedPatient, setSelectedPatient] =
    useState<Patient | null>(null)


  // ==========================================================================
  // Registration
  // ==========================================================================

  const [patientForm, setPatientForm] =
    useState<CreatePatientRequest>(
      emptyPatientForm,
    )

  const [registrationLoading, setRegistrationLoading] =
    useState(false)

  const [registrationError, setRegistrationError] =
    useState<string | null>(null)

  const [registrationSuccess, setRegistrationSuccess] =
    useState<Patient | null>(null)


  // ==========================================================================
  // Session Restoration
  // ==========================================================================

  useEffect(() => {
    async function restoreSession() {
      const accessToken = getAccessToken()
      const refreshToken = getRefreshToken()

      if (!accessToken || !refreshToken) {
        setInitializing(false)
        return
      }

      try {
        const currentUser =
          await getCurrentUser(accessToken)

        setSession({
          access_token: accessToken,
          refresh_token: refreshToken,
          token_type: 'bearer',
        })

        setUser(currentUser)
      } catch {
        try {
          const refreshed =
            await refreshAccessToken(
              refreshToken,
            )

          const currentUser =
            await getCurrentUser(
              refreshed.access_token,
            )

          saveSession(
            refreshed,
            currentUser,
          )

          setSession(refreshed)
          setUser(currentUser)
        } catch {
          clearSession()
          setSession(null)
          setUser(null)
        }
      } finally {
        setInitializing(false)
      }
    }

    restoreSession()
  }, [])


  // ==========================================================================
  // Login
  // ==========================================================================

  async function handleLogin(
    event: FormEvent,
  ) {
    event.preventDefault()

    setLoading(true)
    setError(null)

    try {
      const response =
        await login({
          hospital_code:
            hospitalCode.trim(),
          email:
            email.trim(),
          password,
        })

      const currentUser =
        await getCurrentUser(
          response.access_token,
        )

      saveSession(
        response,
        currentUser,
      )

      setSession(response)
      setUser(currentUser)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to sign in.',
      )
    } finally {
      setLoading(false)
    }
  }


  // ==========================================================================
  // Sign Out
  // ==========================================================================

  function handleSignOut() {
    clearSession()

    setSession(null)
    setUser(null)

    setHospitalCode('')
    setEmail('')
    setPassword('')

    setView('dashboard')
    setPatients([])
    setSelectedPatient(null)
  }


  // ==========================================================================
  // Patient Loading
  // ==========================================================================

  async function loadPatients(
    query = '',
  ) {
    if (!session) {
      return
    }

    setPatientLoading(true)
    setPatientError(null)

    try {
      const response =
        query.trim()
          ? await searchPatients(
              session.access_token,
              query,
            )
          : await listPatients(
              session.access_token,
            )

      setPatients(response.items)
      setPatientCount(response.total)
    } catch (err) {
      setPatientError(
        err instanceof Error
          ? err.message
          : 'Unable to load patients.',
      )
    } finally {
      setPatientLoading(false)
    }
  }


  async function handlePatientSearch(
    event: FormEvent,
  ) {
    event.preventDefault()

    await loadPatients(searchQuery)
  }


  function openPatients() {
    setView('patients')
    setSelectedPatient(null)
    setSearchQuery('')

    void loadPatients()
  }


  function openDashboard() {
    setView('dashboard')
    setSelectedPatient(null)
  }


  function openRegistration() {
    setView('register')
    setRegistrationError(null)
    setRegistrationSuccess(null)
  }


  // ==========================================================================
  // Patient Registration
  // ==========================================================================

  function updatePatientField(
    field: keyof CreatePatientRequest,
    value: string | null,
  ) {
    setPatientForm(
      current => ({
        ...current,
        [field]: value,
      }),
    )
  }


  async function handleRegistration(
    event: FormEvent,
  ) {
    event.preventDefault()

    if (!session) {
      return
    }

    setRegistrationLoading(true)
    setRegistrationError(null)
    setRegistrationSuccess(null)

    try {
      const response =
        await createPatient(
          session.access_token,
          {
            ...patientForm,

            hospital_number:
              patientForm.hospital_number.trim(),

            first_name:
              patientForm.first_name.trim(),

            last_name:
              patientForm.last_name.trim(),

            middle_name:
              patientForm.middle_name?.trim() || null,

            phone_number:
              patientForm.phone_number?.trim() || null,

            email:
              patientForm.email?.trim() || null,

            address:
              patientForm.address?.trim() || null,

            occupation:
              patientForm.occupation?.trim() || null,

            religion:
              patientForm.religion?.trim() || null,

            next_of_kin_name:
              patientForm.next_of_kin_name?.trim() || null,

            next_of_kin_phone:
              patientForm.next_of_kin_phone?.trim() || null,

            next_of_kin_address:
              patientForm.next_of_kin_address?.trim() || null,
          },
        )

      setRegistrationSuccess(response)

      setPatientForm({
        ...emptyPatientForm,
      })
    } catch (err) {
      setRegistrationError(
        err instanceof Error
          ? err.message
          : 'Unable to register patient.',
      )
    } finally {
      setRegistrationLoading(false)
    }
  }


  // ==========================================================================
  // Initialization Screen
  // ==========================================================================

  if (initializing) {
    return (
      <main className="login-shell">
        <section className="login-card loading-card">
          <div className="brand">
            LIGHTBURGH
          </div>

          <h1>Loading...</h1>

          <p className="login-subtitle">
            Restoring your session.
          </p>
        </section>
      </main>
    )
  }


  if (
    window.location.pathname === '/activate'
  ) {
    return (
      <ActivateAccount
        onActivated={() => {
          window.history.pushState(
            {},
            '',
            '/',
          )

          window.location.reload()
        }}
      />
    )
  }


  // ==========================================================================
  // Login Screen
  // ==========================================================================

  if (!session || !user) {
    return (
      <main className="login-shell">
        <section className="login-card">

          <div className="brand">
            LIGHTBURGH
          </div>

          <div className="workspace-name">
            Hospital Information System
          </div>

          <div className="login-heading">
            <p className="eyebrow">
              STAFF ACCESS
            </p>

            <h1>
              Sign in
            </h1>

            <p className="login-subtitle">
              Sign in to access your hospital workspace.
            </p>
          </div>

          {error && (
            <div className="login-error">
              {error}
            </div>
          )}

          <form
            className="login-form"
            onSubmit={handleLogin}
          >
            <label>
              Hospital code

              <input
                type="text"
                value={hospitalCode}
                onChange={event =>
                  setHospitalCode(
                    event.target.value,
                  )
                }
                placeholder="e.g. WTH001"
                autoComplete="organization"
                required
              />
            </label>

            <label>
              Email

              <input
                type="email"
                value={email}
                onChange={event =>
                  setEmail(
                    event.target.value,
                  )
                }
                placeholder="you@hospital.com"
                autoComplete="email"
                required
              />
            </label>

            <label>
              Password

              <input
                type="password"
                value={password}
                onChange={event =>
                  setPassword(
                    event.target.value,
                  )
                }
                placeholder="Enter your password"
                autoComplete="current-password"
                required
              />
            </label>

            <button
              type="submit"
              className="primary-button"
              disabled={loading}
            >
              {loading
                ? 'Signing in...'
                : 'Sign in'}
            </button>
          </form>

        </section>
      </main>
    )
  }


  // ==========================================================================
  // Authenticated Workspace
  // ==========================================================================

  const isReceptionist =
    user.roles?.includes('Receptionist') ?? false

  const isAdministrator =
    user.roles?.includes('Administrator') ?? false

  return (
    <AppShell
      user={user}
      view={view}
      isReceptionist={isReceptionist}
      isAdministrator={isAdministrator}
      onDashboard={openDashboard}
      onPatients={openPatients}
      onRegistration={openRegistration}
      onAdministrator={() =>
        setView('administrator')
      }
      onSignOut={handleSignOut}
    >


        {/* ================================================================= */}
        {/* Dashboard                                                         */}
        {/* ================================================================= */}

        {view === 'dashboard' && (
          <section className="workspace-content">

            <div className="welcome-panel">

              <div>
                <p className="eyebrow">
                  TODAY'S WORKSPACE
                </p>

                <h2>
                  Welcome to reception.
                </h2>

                <p>
                  Search for an existing patient or
                  register a new patient to begin
                  their journey through LIGHTBURGH.
                </p>
              </div>

              <button
                type="button"
                className="primary-button dashboard-action"
                onClick={openRegistration}
              >
                Register patient
              </button>

            </div>


            <div className="dashboard-grid">

              <article className="stat-card">
                <span>
                  Patients
                </span>

                <strong>
                  {patientCount}
                </strong>

                <button
                  type="button"
                  onClick={openPatients}
                >
                  View patients
                </button>
              </article>

              <article className="action-card">

                <p className="eyebrow">
                  QUICK SEARCH
                </p>

                <h3>
                  Find a patient
                </h3>

                <form
                  className="quick-search"
                  onSubmit={async event => {
                    event.preventDefault()

                    setView('patients')

                    await loadPatients(
                      searchQuery,
                    )
                  }}
                >
                  <input
                    type="search"
                    value={searchQuery}
                    onChange={event =>
                      setSearchQuery(
                        event.target.value,
                      )
                    }
                    placeholder="Search by patient name"
                  />

                  <button
                    type="submit"
                    className="secondary-button"
                  >
                    Search
                  </button>
                </form>

              </article>

            </div>

          </section>
        )}


        {/* ================================================================= */}
        {/* Patients                                                          */}
        {/* ================================================================= */}

        {view === 'patients' && (
          <section className="workspace-content">

            <div className="section-toolbar">

              <form
                className="patient-search"
                onSubmit={handlePatientSearch}
              >
                <input
                  type="search"
                  value={searchQuery}
                  onChange={event =>
                    setSearchQuery(
                      event.target.value,
                    )
                  }
                  placeholder="Search patients by name"
                />

                <button
                  type="submit"
                  className="secondary-button"
                  disabled={patientLoading}
                >
                  {patientLoading
                    ? 'Searching...'
                    : 'Search'}
                </button>
              </form>

              <button
                type="button"
                className="primary-button"
                onClick={openRegistration}
              >
                Register patient
              </button>

            </div>

            {patientError && (
              <div className="login-error">
                {patientError}
              </div>
            )}

            {patientLoading && (
              <div className="empty-state">
                Loading patients...
              </div>
            )}

            {!patientLoading &&
              patients.length === 0 && (
                <div className="empty-state">
                  <strong>
                    No patients found.
                  </strong>

                  <span>
                    Search again or register a new
                    patient.
                  </span>
                </div>
              )}

            {!patientLoading &&
              patients.length > 0 && (
                <div className="patient-table">

                  <div className="patient-table-header">
                    <span>Hospital number</span>
                    <span>Patient</span>
                    <span>Sex</span>
                    <span>Date of birth</span>
                    <span>Phone</span>
                  </div>

                  {patients.map(patient => (
                    <button
                      type="button"
                      className="patient-row"
                      key={patient.id}
                      onClick={() =>
                        setSelectedPatient(
                          patient,
                        )
                      }
                    >
                      <span>
                        <strong>
                          {patient.hospital_number}
                        </strong>
                      </span>

                      <span>
                        {patient.last_name},{' '}
                        {patient.first_name}{' '}
                        {patient.middle_name ?? ''}
                      </span>

                      <span>
                        {patient.sex}
                      </span>

                      <span>
                        {patient.date_of_birth}
                      </span>

                      <span>
                        {patient.phone_number ?? '—'}
                      </span>
                    </button>
                  ))}

                </div>
              )}


            {selectedPatient && (
              <div className="patient-detail-card">

                <div className="detail-header">

                  <div>
                    <p className="eyebrow">
                      PATIENT
                    </p>

                    <h2>
                      {selectedPatient.first_name}{' '}
                      {selectedPatient.last_name}
                    </h2>

                    <span>
                      {
                        selectedPatient
                          .hospital_number
                      }
                    </span>
                  </div>

                  <button
                    type="button"
                    className="close-button"
                    onClick={() =>
                      setSelectedPatient(null)
                    }
                  >
                    Close
                  </button>

                </div>

                <div className="detail-grid">

                  <div>
                    <span>Sex</span>
                    <strong>
                      {selectedPatient.sex}
                    </strong>
                  </div>

                  <div>
                    <span>Date of birth</span>
                    <strong>
                      {selectedPatient.date_of_birth}
                    </strong>
                  </div>

                  <div>
                    <span>Phone</span>
                    <strong>
                      {selectedPatient.phone_number ?? '—'}
                    </strong>
                  </div>

                  <div>
                    <span>Email</span>
                    <strong>
                      {selectedPatient.email ?? '—'}
                    </strong>
                  </div>

                  <div>
                    <span>Blood group</span>
                    <strong>
                      {selectedPatient.blood_group ?? '—'}
                    </strong>
                  </div>

                  <div>
                    <span>Genotype</span>
                    <strong>
                      {selectedPatient.genotype ?? '—'}
                    </strong>
                  </div>

                </div>

              </div>
            )}

          </section>
        )}


        {/* ================================================================= */}
        {/* Registration                                                       */}
        {/* ================================================================= */}

        {view === 'register' && (
          <section className="workspace-content">

            {registrationSuccess ? (
              <div className="registration-success">

                <div className="success-mark">
                  ✓
                </div>

                <p className="eyebrow">
                  PATIENT REGISTERED
                </p>

                <h2>
                  {registrationSuccess.first_name}{' '}
                  {registrationSuccess.last_name}
                </h2>

                <p>
                  The patient has been registered
                  successfully.
                </p>

                <div className="registration-number">
                  <span>
                    Hospital number
                  </span>

                  <strong>
                    {
                      registrationSuccess
                        .hospital_number
                    }
                  </strong>
                </div>

                <div className="registration-actions">

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() => {
                      setRegistrationSuccess(null)
                      setPatientForm({
                        ...emptyPatientForm,
                      })
                    }}
                  >
                    Register another
                  </button>

                  <button
                    type="button"
                    className="primary-button"
                    onClick={() => {
                      setRegistrationSuccess(null)
                      openPatients()
                    }}
                  >
                    View patients
                  </button>

                </div>

              </div>
            ) : (
              <form
                className="registration-form"
                onSubmit={handleRegistration}
              >

                <div className="form-section">

                  <div className="form-section-heading">
                    <p className="eyebrow">
                      IDENTIFICATION
                    </p>

                    <h2>
                      Patient information
                    </h2>

                    <p>
                      Enter the patient's hospital
                      identification and demographic
                      information.
                    </p>
                  </div>

                  <div className="form-grid">

                    <label>
                      Hospital number
                      <input
                        value={
                          patientForm.hospital_number
                        }
                        onChange={event =>
                          updatePatientField(
                            'hospital_number',
                            event.target.value,
                          )
                        }
                        required
                      />
                    </label>

                    <label>
                      First name
                      <input
                        value={
                          patientForm.first_name
                        }
                        onChange={event =>
                          updatePatientField(
                            'first_name',
                            event.target.value,
                          )
                        }
                        required
                      />
                    </label>

                    <label>
                      Last name
                      <input
                        value={
                          patientForm.last_name
                        }
                        onChange={event =>
                          updatePatientField(
                            'last_name',
                            event.target.value,
                          )
                        }
                        required
                      />
                    </label>

                    <label>
                      Middle name
                      <input
                        value={
                          patientForm.middle_name ?? ''
                        }
                        onChange={event =>
                          updatePatientField(
                            'middle_name',
                            event.target.value,
                          )
                        }
                      />
                    </label>

                    <label>
                      Sex
                      <select
                        value={patientForm.sex}
                        onChange={event =>
                          updatePatientField(
                            'sex',
                            event.target.value,
                          )
                        }
                        required
                      >
                        <option value="Male">
                          Male
                        </option>

                        <option value="Female">
                          Female
                        </option>
                      </select>
                    </label>

                    <label>
                      Date of birth
                      <input
                        type="date"
                        value={
                          patientForm.date_of_birth
                        }
                        onChange={event =>
                          updatePatientField(
                            'date_of_birth',
                            event.target.value,
                          )
                        }
                        required
                      />
                    </label>

                  </div>

                </div>


                <div className="form-section">

                  <div className="form-section-heading">
                    <p className="eyebrow">
                      CONTACT
                    </p>

                    <h2>
                      Contact information
                    </h2>
                  </div>

                  <div className="form-grid">

                    <label>
                      Phone number
                      <input
                        type="tel"
                        value={
                          patientForm.phone_number ?? ''
                        }
                        onChange={event =>
                          updatePatientField(
                            'phone_number',
                            event.target.value,
                          )
                        }
                      />
                    </label>

                    <label>
                      Email
                      <input
                        type="email"
                        value={
                          patientForm.email ?? ''
                        }
                        onChange={event =>
                          updatePatientField(
                            'email',
                            event.target.value,
                          )
                        }
                      />
                    </label>

                    <label className="wide-field">
                      Address
                      <input
                        value={
                          patientForm.address ?? ''
                        }
                        onChange={event =>
                          updatePatientField(
                            'address',
                            event.target.value,
                          )
                        }
                      />
                    </label>

                    <label>
                      Occupation
                      <input
                        value={
                          patientForm.occupation ?? ''
                        }
                        onChange={event =>
                          updatePatientField(
                            'occupation',
                            event.target.value,
                          )
                        }
                      />
                    </label>

                    <label>
                      Marital status
                      <select
                        value={
                          patientForm.marital_status ?? ''
                        }
                        onChange={event =>
                          updatePatientField(
                            'marital_status',
                            event.target.value || null,
                          )
                        }
                      >
                        <option value="">
                          Not specified
                        </option>

                        <option value="Single">
                          Single
                        </option>

                        <option value="Married">
                          Married
                        </option>

                        <option value="Divorced">
                          Divorced
                        </option>

                        <option value="Widowed">
                          Widowed
                        </option>

                        <option value="Separated">
                          Separated
                        </option>
                      </select>
                    </label>

                    <label>
                      Religion
                      <input
                        value={
                          patientForm.religion ?? ''
                        }
                        onChange={event =>
                          updatePatientField(
                            'religion',
                            event.target.value,
                          )
                        }
                      />
                    </label>

                  </div>

                </div>


                <div className="form-section">

                  <div className="form-section-heading">
                    <p className="eyebrow">
                      HEALTH INFORMATION
                    </p>

                    <h2>
                      Clinical demographics
                    </h2>
                  </div>

                  <div className="form-grid">

                    <label>
                      Blood group
                      <select
                        value={
                          patientForm.blood_group ?? ''
                        }
                        onChange={event =>
                          updatePatientField(
                            'blood_group',
                            event.target.value || null,
                          )
                        }
                      >
                        <option value="">
                          Not specified
                        </option>

                        <option value="A+">A+</option>
                        <option value="A-">A-</option>
                        <option value="B+">B+</option>
                        <option value="B-">B-</option>
                        <option value="AB+">AB+</option>
                        <option value="AB-">AB-</option>
                        <option value="O+">O+</option>
                        <option value="O-">O-</option>
                        <option value="Unknown">
                          Unknown
                        </option>
                      </select>
                    </label>

                    <label>
                      Genotype
                      <select
                        value={
                          patientForm.genotype ?? ''
                        }
                        onChange={event =>
                          updatePatientField(
                            'genotype',
                            event.target.value || null,
                          )
                        }
                      >
                        <option value="">
                          Not specified
                        </option>

                        <option value="AA">AA</option>
                        <option value="AS">AS</option>
                        <option value="AC">AC</option>
                        <option value="SS">SS</option>
                        <option value="SC">SC</option>
                        <option value="CC">CC</option>
                        <option value="Unknown">
                          Unknown
                        </option>
                      </select>
                    </label>

                  </div>

                </div>


                <div className="form-section">

                  <div className="form-section-heading">
                    <p className="eyebrow">
                      NEXT OF KIN
                    </p>

                    <h2>
                      Emergency contact
                    </h2>
                  </div>

                  <div className="form-grid">

                    <label>
                      Name
                      <input
                        value={
                          patientForm.next_of_kin_name ?? ''
                        }
                        onChange={event =>
                          updatePatientField(
                            'next_of_kin_name',
                            event.target.value,
                          )
                        }
                      />
                    </label>

                    <label>
                      Relationship
                      <select
                        value={
                          patientForm.next_of_kin_relationship ?? ''
                        }
                        onChange={event =>
                          updatePatientField(
                            'next_of_kin_relationship',
                            event.target.value || null,
                          )
                        }
                      >
                        <option value="">
                          Not specified
                        </option>

                        <option value="Spouse">
                          Spouse
                        </option>

                        <option value="Father">
                          Father
                        </option>

                        <option value="Mother">
                          Mother
                        </option>

                        <option value="Son">
                          Son
                        </option>

                        <option value="Daughter">
                          Daughter
                        </option>

                        <option value="Brother">
                          Brother
                        </option>

                        <option value="Sister">
                          Sister
                        </option>

                        <option value="Uncle">
                          Uncle
                        </option>

                        <option value="Aunt">
                          Aunt
                        </option>

                        <option value="Grandparent">
                          Grandparent
                        </option>

                        <option value="Grandchild">
                          Grandchild
                        </option>

                        <option value="Friend">
                          Friend
                        </option>

                        <option value="Employer">
                          Employer
                        </option>

                        <option value="Guardian">
                          Guardian
                        </option>

                        <option value="Other">
                          Other
                        </option>
                      </select>
                    </label>

                    <label>
                      Phone number
                      <input
                        type="tel"
                        value={
                          patientForm.next_of_kin_phone ?? ''
                        }
                        onChange={event =>
                          updatePatientField(
                            'next_of_kin_phone',
                            event.target.value,
                          )
                        }
                      />
                    </label>

                    <label>
                      Address
                      <input
                        value={
                          patientForm.next_of_kin_address ?? ''
                        }
                        onChange={event =>
                          updatePatientField(
                            'next_of_kin_address',
                            event.target.value,
                          )
                        }
                      />
                    </label>

                  </div>

                </div>


                {registrationError && (
                  <div className="login-error">
                    {registrationError}
                  </div>
                )}


                <div className="form-actions">

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={openDashboard}
                  >
                    Cancel
                  </button>

                  <button
                    type="submit"
                    className="primary-button"
                    disabled={registrationLoading}
                  >
                    {registrationLoading
                      ? 'Registering...'
                      : 'Register patient'}
                  </button>

                </div>

              </form>
            )}

          </section>
         
          )}
          {view === 'administrator' &&
          isAdministrator && (
            <AdministratorWorkspace
              accessToken={session.access_token}
              currentUserEmail={user.email}
            />
          )}

        </AppShell>
  )
}


export default App