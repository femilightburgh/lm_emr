import {
  useEffect,
  useState,
  type FormEvent,
} from 'react'

import {
  checkInEpisode,
  createEpisode,
  createPatient,
  listPatientEpisodes,
  listPatients,
  searchPatients,
} from '../../api'

import type {
  CreatePatientRequest,
  Patient,
} from '../../types'

import type { Episode } from '../../api'
import PatientRegistration from './PatientRegistration'
import PatientDetails from './PatientDetails'
import PatientList from './PatientList'


interface Props {
  accessToken: string
  onDashboard: () => void
}


type ReceptionView =
  | 'patients'
  | 'register'


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


export default function ReceptionWorkspace({
  accessToken,
  onDashboard,
}: Props) {
  // ==========================================================================
  // View
  // ==========================================================================

  const [view, setView] =
    useState<ReceptionView>('patients')


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


  function openPatients() {
    setView('patients')
    setSelectedPatient(null)
    setPatientEpisodes([])
    setSearchQuery('')

    void loadPatients()
  }


  function openRegistration() {
    setView('register')
    setRegistrationError(null)
    setRegistrationSuccess(null)
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
  }, [])


  // ==========================================================================
  // Registration view
  // ==========================================================================

    if (view === 'register') {
    return (
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
        onViewPatients={openPatients}
        onDashboard={onDashboard}
      />
    )
  }


  // ==========================================================================
  // Patient view
  // ==========================================================================

  return (
    <section className="workspace-content">

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