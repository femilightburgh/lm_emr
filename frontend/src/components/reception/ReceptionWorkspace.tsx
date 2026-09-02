import {
  useEffect,
  useState,
  type FormEvent,
} from 'react'

import {
  checkInEpisode,
  createEpisode,
  createPatient,
  getReceptionOverview,
  getReceptionPatientFlow,
  listPatientEpisodes,
  listPatients,
  searchPatients,
} from '../../api'

import type {
  CreatePatientRequest,
  Patient,
} from '../../types'

import type {
  Episode,
  ReceptionOverview,
  ReceptionPatientFlowItem,
} from '../../api'
import PatientRegistration from './PatientRegistration'
import PatientDetails from './PatientDetails'
import PatientList from './PatientList'


interface Props {
  accessToken: string
  onDashboard: () => void
}


type ReceptionView =
  | 'overview'
  | 'register'
  | 'patients'
  | 'flow'


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


interface ReceptionNavigationProps {
  view: ReceptionView
  onOverview: () => void
  onRegister: () => void
  onFindPatient: () => void
  onPatientFlow: () => void
}


function ReceptionNavigation({
  view,
  onOverview,
  onRegister,
  onFindPatient,
  onPatientFlow,
}: ReceptionNavigationProps) {
  return (
    <nav
      className="reception-workspace-navigation"
      aria-label="Reception workspace"
    >
      <button
        type="button"
        className={
          view === 'overview'
            ? 'reception-tab active'
            : 'reception-tab'
        }
        onClick={onOverview}
      >
        Overview
      </button>

      <button
        type="button"
        className={
          view === 'register'
            ? 'reception-tab active'
            : 'reception-tab'
        }
        onClick={onRegister}
      >
        Register Patient
      </button>

      <button
        type="button"
        className={
          view === 'patients'
            ? 'reception-tab active'
            : 'reception-tab'
        }
        onClick={onFindPatient}
      >
        Find Patient
      </button>

      <button
        type="button"
        className={
          view === 'flow'
            ? 'reception-tab active'
            : 'reception-tab'
        }
        onClick={onPatientFlow}
      >
        Patient Flow
      </button>
    </nav>
  )
}


function getPatientFlowLabel(
  item: ReceptionPatientFlowItem,
): string {
  if (item.status === 'ADMITTED') {
    return 'On admission'
  }

  switch (item.flow_status) {
    case 'AWAITING_CHECK_IN':
      return 'Awaiting check-in'

    case 'WAITING_FOR_NURSING':
      return 'Waiting for nurse'

    case 'NURSING_IN_PROGRESS':
      return 'With nurse'

    case 'ROUTED':
      return 'With clinical team'

    case 'AWAITING_INVESTIGATIONS':
      return 'Awaiting investigations'

    case 'AWAITING_REVIEW':
      return 'Waiting for doctor review'

    default:
      return 'In progress'
  }
}


function formatPatientFlowTime(
  value: string | null,
): string {
  if (!value) {
    return '—'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return '—'
  }

  return date.toLocaleTimeString(
    [],
    {
      hour: 'numeric',
      minute: '2-digit',
    },
  )
}


export default function ReceptionWorkspace({
  accessToken,
  onDashboard,
}: Props) {
  // ==========================================================================
  // View
  // ==========================================================================

  const [view, setView] =
    useState<ReceptionView>('overview')


  // ==========================================================================
  // Patients
  // ==========================================================================

  const [patients, setPatients] =
    useState<Patient[]>([])

  const [patientLoading, setPatientLoading] =
    useState(false)

  const [patientError, setPatientError] =
    useState<string | null>(null)

  const [searchQuery, setSearchQuery] =
    useState('')

  const [selectedPatient, setSelectedPatient] =
    useState<Patient | null>(null)


  // ==========================================================================
  // Episodes
  // ==========================================================================

  const [patientEpisodes, setPatientEpisodes] =
    useState<Episode[]>([])

  const [episodeLoading, setEpisodeLoading] =
    useState(false)

  const [episodeError, setEpisodeError] =
    useState<string | null>(null)

  const [episodeActionLoading, setEpisodeActionLoading] =
    useState(false)


  // ==========================================================================
  // Reception Overview
  // ==========================================================================

  const [receptionOverview, setReceptionOverview] =
    useState<ReceptionOverview | null>(null)

  const [overviewLoading, setOverviewLoading] =
    useState(false)

  const [overviewError, setOverviewError] =
    useState<string | null>(null)


  // ==========================================================================
  // Patient Flow
  // ==========================================================================

  const [patientFlow, setPatientFlow] =
    useState<ReceptionPatientFlowItem[]>([])

  const [patientFlowLoading, setPatientFlowLoading] =
    useState(false)

  const [patientFlowError, setPatientFlowError] =
    useState<string | null>(null)


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
  // Reception Overview Loading
  // ==========================================================================

  async function loadReceptionOverview() {
    setOverviewLoading(true)
    setOverviewError(null)

    try {
      const overview =
        await getReceptionOverview(
          accessToken,
        )

      setReceptionOverview(
        overview,
      )
    } catch (err) {
      setOverviewError(
        err instanceof Error
          ? err.message
          : 'Unable to load Reception overview.',
      )
    } finally {
      setOverviewLoading(false)
    }
  }


  // ==========================================================================
  // Patient Flow Loading
  // ==========================================================================

  async function loadPatientFlow() {
    setPatientFlowLoading(true)
    setPatientFlowError(null)

    try {
      const response =
        await getReceptionPatientFlow(
          accessToken,
        )

      setPatientFlow(
        response.items,
      )
    } catch (err) {
      setPatientFlowError(
        err instanceof Error
          ? err.message
          : 'Unable to load patient flow.',
      )
    } finally {
      setPatientFlowLoading(false)
    }
  }


  // ==========================================================================
  // Patient loading
  // ==========================================================================

  async function loadPatients(
    query = '',
  ) {
    setPatientLoading(true)
    setPatientError(null)

    try {
      const response =
        query.trim()
          ? await searchPatients(
              accessToken,
              query,
            )
          : await listPatients(
              accessToken,
            )

      setPatients(response.items)
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


  async function loadPatientEpisodes(
    patientId: string,
  ) {
    setEpisodeLoading(true)
    setEpisodeError(null)

    try {
      const episodes =
        await listPatientEpisodes(
          accessToken,
          patientId,
        )

      setPatientEpisodes(episodes)
    } catch (err) {
      setEpisodeError(
        err instanceof Error
          ? err.message
          : 'Unable to load patient visits.',
      )
    } finally {
      setEpisodeLoading(false)
    }
  }


  async function selectPatient(
    patient: Patient,
  ) {
    setSelectedPatient(patient)
    setPatientEpisodes([])
    setEpisodeError(null)

    await loadPatientEpisodes(patient.id)
  }


  async function handlePatientSearch(
    event: FormEvent,
  ) {
    event.preventDefault()

    await loadPatients(searchQuery)
  }


  function openRegistration() {
    setView('register')
    setRegistrationError(null)
    setRegistrationSuccess(null)
  }


  function openFindPatient() {
    setView('patients')
    setSelectedPatient(null)
    setPatientEpisodes([])
    setSearchQuery('')

    void loadPatients()
  }


  function openPatientFlow() {
    setView('flow')
    void loadPatientFlow()
  }


  function openOverview() {
    setView('overview')
    void loadReceptionOverview()
  }


  // ==========================================================================
  // Episode workflow
  // ==========================================================================

  function hasActiveEpisode() {
    return patientEpisodes.some(
      episode =>
        episode.status === 'OPEN' ||
        episode.status === 'ADMITTED',
    )
  }


  async function handleStartVisit() {
    if (
      !selectedPatient ||
      hasActiveEpisode()
    ) {
      return
    }

    setEpisodeActionLoading(true)
    setEpisodeError(null)

    try {
      const episode =
        await createEpisode(
          accessToken,
          {
            patient_id:
              selectedPatient.id,
            title:
              'Outpatient visit',
          },
        )

      setPatientEpisodes(
        current => [
          episode,
          ...current,
        ],
      )
    } catch (err) {
      setEpisodeError(
        err instanceof Error
          ? err.message
          : 'Unable to start patient visit.',
      )
    } finally {
      setEpisodeActionLoading(false)
    }
  }


  async function handleCheckIn(
    episode: Episode,
  ) {
    setEpisodeActionLoading(true)
    setEpisodeError(null)

    try {
      const updated =
        await checkInEpisode(
          accessToken,
          episode.id,
        )

      setPatientEpisodes(
        current =>
          current.map(item =>
            item.id === updated.id
              ? updated
              : item,
          ),
      )
    } catch (err) {
      setEpisodeError(
        err instanceof Error
          ? err.message
          : 'Unable to check in patient.',
      )
    } finally {
      setEpisodeActionLoading(false)
    }
  }


  // ==========================================================================
  // Registration
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

    setRegistrationLoading(true)
    setRegistrationError(null)
    setRegistrationSuccess(null)

    try {
      const response =
        await createPatient(
          accessToken,
          patientForm,
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
  // Initialization
  // ==========================================================================

  useEffect(() => {
    void loadPatients()
    void loadReceptionOverview()
  }, [])


  // ==========================================================================
  // Registration view
  // ==========================================================================

    if (view === 'register') {
    return (
      <section className="workspace-content">

        <ReceptionNavigation
          view={view}
          onOverview={openOverview}
          onRegister={openRegistration}
          onFindPatient={openFindPatient}
          onPatientFlow={openPatientFlow}
        />

        <PatientRegistration
          patientForm={patientForm}
          registrationLoading={registrationLoading}
          registrationError={registrationError}
          registrationSuccess={registrationSuccess}
          onChange={updatePatientField}
          onSubmit={handleRegistration}
          onRegisterAnother={() => {
            setRegistrationSuccess(null)
            setPatientForm({
              ...emptyPatientForm,
            })
          }}
          onViewPatients={openFindPatient}
          onDashboard={onDashboard}
        />

      </section>
    )
  }


  if (view === 'overview') {
    return (
      <section className="workspace-content">

        <ReceptionNavigation
          view={view}
          onOverview={openOverview}
          onRegister={openRegistration}
          onFindPatient={openFindPatient}
          onPatientFlow={openPatientFlow}
        />

        <div className="reception-overview">
          <div className="panel-header">
            <div>
              <p className="eyebrow">
                RECEPTION
              </p>

              <h2>
                Overview
              </h2>

              <p>
                Patient registration, check-in,
                and hospital flow at a glance.
              </p>
            </div>
          </div>

          <div className="reception-overview-actions">
            <button
              type="button"
              className="primary-button"
              onClick={openRegistration}
            >
              Register patient
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={openFindPatient}
            >
              Find patient
            </button>
          </div>

          <div className="reception-overview-grid">
            <article className="reception-stat-card">
              <span>Total patients</span>

              <strong>
                {overviewLoading
                  ? '—'
                  : receptionOverview?.total_patients ?? '—'}
              </strong>

              <small>
                Hospital-wide registered patients
              </small>
            </article>

            <article className="reception-stat-card">
              <span>On admission</span>

              <strong>
                {overviewLoading
                  ? '—'
                  : receptionOverview?.currently_admitted ?? '—'}
              </strong>

              <small>
                Patients currently on admission
              </small>
            </article>

            <article className="reception-stat-card">
              <span>Checked in today</span>

              <strong>
                {overviewLoading
                  ? '—'
                  : receptionOverview?.checked_in_today ?? '—'}
              </strong>

              <small>
                Patients checked in today
              </small>
            </article>
          </div>

          <section className="reception-activity-panel">
            <div className="reception-activity-header">
              <div>
                <p className="eyebrow">
                  TODAY'S PATIENT ACTIVITY
                </p>

                <h3>
                  Patient activity
                </h3>
              </div>
            </div>

            {overviewError ? (
              <div className="reception-overview-note">
                <strong>
                  Unable to load patient activity
                </strong>

                <p>
                  {overviewError}
                </p>
              </div>
            ) : (
              <div className="reception-activity-list">
                <div className="reception-activity-row">
                  <span>
                    Waiting for nursing
                  </span>

                  <strong>
                    {overviewLoading
                      ? '—'
                      : receptionOverview?.waiting_for_nursing ?? '—'}
                  </strong>
                </div>

                <div className="reception-activity-row">
                  <span>
                    Nursing in progress
                  </span>

                  <strong>
                    {overviewLoading
                      ? '—'
                      : receptionOverview?.nursing_in_progress ?? '—'}
                  </strong>
                </div>

                <div className="reception-activity-row">
                  <span>
                    Routed to care
                  </span>

                  <strong>
                    {overviewLoading
                      ? '—'
                      : receptionOverview?.routed ?? '—'}
                  </strong>
                </div>

                <div className="reception-activity-row">
                  <span>
                    Awaiting investigations
                  </span>

                  <strong>
                    {overviewLoading
                      ? '—'
                      : receptionOverview?.awaiting_investigations ?? '—'}
                  </strong>
                </div>

                <div className="reception-activity-row">
                  <span>
                    Awaiting review
                  </span>

                  <strong>
                    {overviewLoading
                      ? '—'
                      : receptionOverview?.awaiting_review ?? '—'}
                  </strong>
                </div>
              </div>
            )}
          </section>
        </div>

      </section>
    )
  }


  if (view === 'flow') {
    return (
      <section className="workspace-content">

        <ReceptionNavigation
          view={view}
          onOverview={openOverview}
          onRegister={openRegistration}
          onFindPatient={openFindPatient}
          onPatientFlow={openPatientFlow}
        />

        <div className="reception-flow-panel">
          <div className="reception-flow-header">
            <div>
              <p className="eyebrow">
                PATIENT FLOW
              </p>

              <h2>
                Patient flow
              </h2>

              <p>
                See where active patients are in
                their current episode of care.
              </p>
            </div>

            <button
              type="button"
              className="secondary-button"
              onClick={() =>
                void loadPatientFlow()
              }
              disabled={patientFlowLoading}
            >
              {patientFlowLoading
                ? 'Refreshing...'
                : 'Refresh'}
            </button>
          </div>

          {patientFlowError && (
            <div className="reception-overview-note">
              <strong>
                Unable to load patient flow
              </strong>

              <p>
                {patientFlowError}
              </p>
            </div>
          )}

          {patientFlowLoading &&
          patientFlow.length === 0 ? (
            <div className="reception-flow-empty">
              <p>
                Loading patient flow...
              </p>
            </div>
          ) : patientFlow.length === 0 ? (
            <div className="reception-flow-empty">
              <p>
                No active patients are currently
                in the workflow.
              </p>
            </div>
          ) : (
            <div className="reception-flow-table-wrapper">
              <table className="reception-flow-table">
                <thead>
                  <tr>
                    <th>
                      Patient
                    </th>

                    <th>
                      Hospital number
                    </th>

                    <th>
                      Visit
                    </th>

                    <th>
                      Current state
                    </th>

                    <th>
                      Time
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {patientFlow.map(
                    item => (
                      <tr key={item.id}>
                        <td>
                          <strong>
                            {item.patient_name}
                          </strong>
                        </td>

                        <td>
                          {item.hospital_number}
                        </td>

                        <td>
                          {item.title}
                        </td>

                          <td>
                            <div className="reception-flow-location">

                              <span className="reception-flow-state">
                                {getPatientFlowLabel(
                                  item,
                                )}
                              </span>

                              {item.professional_name && (
                                <strong className="reception-flow-professional">
                                  {item.professional_role
                                    ? `${item.professional_role} · `
                                    : ''}
                                  {item.professional_name}
                                </strong>
                              )}

                              {item.department_name && (
                                <span className="reception-flow-department">
                                  {item.department_name}
                                </span>
                              )}

                            </div>
                          </td>

                        <td>
                          {formatPatientFlowTime(
                            item.checked_in_at ??
                              item.opened_at,
                          )}
                        </td>
                      </tr>
                    ),
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </section>
    )
  }


  // ==========================================================================
  // Find Patient view
  // ==========================================================================

  return (
    <section className="workspace-content">

      <ReceptionNavigation
        view={view}
        onOverview={openOverview}
        onRegister={openRegistration}
        onFindPatient={openFindPatient}
        onPatientFlow={openPatientFlow}
      />

      <PatientList
        patients={patients}
        searchQuery={searchQuery}
        patientLoading={patientLoading}
        patientError={patientError}
        onSearchQueryChange={setSearchQuery}
        onSearch={handlePatientSearch}
        onRegisterPatient={openRegistration}
        onSelectPatient={patient =>
            void selectPatient(patient)
        }
        />


       {selectedPatient && (
        <PatientDetails
            patient={selectedPatient}
            episodes={patientEpisodes}
            episodeLoading={episodeLoading}
            episodeError={episodeError}
            episodeActionLoading={episodeActionLoading}
            hasActiveEpisode={hasActiveEpisode}
            onClose={() => {
            setSelectedPatient(null)
            setPatientEpisodes([])
            setEpisodeError(null)
            }}
            onStartVisit={() =>
            void handleStartVisit()
            }
            onCheckIn={episode =>
            void handleCheckIn(episode)
            }
        />
        )}
    </section>
  )
}