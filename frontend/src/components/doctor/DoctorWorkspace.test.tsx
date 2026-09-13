import { render, screen } from '@testing-library/react'
import { useState } from 'react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi, beforeEach } from 'vitest'

import DoctorWorkspace from './DoctorWorkspace'

import type {
  DoctorQueueItem,
  Episode,
} from '../../api/episodes'
import type { Encounter } from '../../api/encounters'

const mocks = vi.hoisted(() => ({
  getEpisode: vi.fn(),
  getPatient: vi.fn(),
  listEpisodeEncounters: vi.fn(),
  createEncounter: vi.fn(),
  startDoctorConsultation: vi.fn(),
  completeConsultation: vi.fn(),
  completeDoctorReview: vi.fn(),

  refreshEncounterData: vi.fn(),
  resetEncounterContext: vi.fn(),
  setSelectedEncounter: vi.fn(),

  refreshDoctorQueues: vi.fn(),

  loadPreviousPatientEpisodes: vi.fn(),
  loadNursingHandoff: vi.fn(),
  resetNursingHandoff: vi.fn(),

  refreshEncounterContext: vi.fn(),

  clinicalDocumentation: {
    loadProgressNote: vi.fn(),
  },

  doctorQueue: {
    clinicQueue: [] as DoctorQueueItem[],
    wardQueue: [] as DoctorQueueItem[],
    currentStaffId: 'staff-1',
    refreshDoctorQueues: vi.fn(),
  },
}))

vi.mock('../../api/encounters', () => ({
  createEncounter: mocks.createEncounter,
  listEpisodeEncounters: mocks.listEpisodeEncounters,
}))

vi.mock('../../api/episodes', () => ({
  completeConsultation: mocks.completeConsultation,
  completeDoctorReview: mocks.completeDoctorReview,
  getEpisode: mocks.getEpisode,
  startDoctorConsultation: mocks.startDoctorConsultation,
}))

vi.mock('../../api/patients', () => ({
  getPatient: mocks.getPatient,
}))

vi.mock('./DoctorEncounterWorkspace', () => ({
  default: ({
    handleCompleteConsultation,
    handleCompleteDoctorReview,
  }: {
    handleCompleteConsultation: () => Promise<void>
    handleCompleteDoctorReview: () => Promise<void>
  }) => (
    <div data-testid="doctor-encounter-workspace">
      <button
        type="button"
        onClick={() => void handleCompleteConsultation()}
      >
        Mock Complete Consultation
      </button>

      <button
        type="button"
        onClick={() => void handleCompleteDoctorReview()}
      >
        Mock Complete Doctor Review
      </button>
    </div>
  ),
}))

vi.mock('./useDoctorEncounterContext', () => ({
  useDoctorEncounterContext: () => {
    const [selectedEncounter, setSelectedEncounterState] =
      useState<Encounter | null>(null)

    const setSelectedEncounter = (nextEncounter: Encounter | null) => {
      mocks.setSelectedEncounter(nextEncounter)
      setSelectedEncounterState(nextEncounter)
    }

    return {
      selectedEncounter,
      setSelectedEncounter,
      resetEncounterContext: mocks.resetEncounterContext,
      refreshEncounterData: mocks.refreshEncounterData,
      diagnoses: [],
      timeline: [],
      loadingTimeline: false,
      loadingDiagnoses: false,
      orders: [],
      vitals: [],
      clinicalResults: [],
      diagnosticReports: [],
      diagnosticAttachments: {},
      loadingClinicalResults: false,
      loadingOrders: false,
    }
  },
}))

vi.mock('./useDoctorPatientContext', () => ({
  useDoctorPatientContext: () => ({
    currentEpisodeEncounters: [],
    setCurrentEpisodeEncounters: vi.fn(),
    patient: null,
    setPatient: vi.fn(),
    loadingPatientContext: false,
    setLoadingPatientContext: vi.fn(),
    previousEpisodes: [],
    setPreviousEpisodes: vi.fn(),
    loadingPreviousEpisodes: false,
    loadPreviousPatientEpisodes:
      mocks.loadPreviousPatientEpisodes,
  }),
}))

vi.mock('./useDoctorQueue', () => ({
  useDoctorQueue: () => mocks.doctorQueue,
}))

vi.mock('./useDoctorDiagnosisSearch', () => ({
  useDoctorDiagnosisSearch: () => ({
    diagnosisQuery: '',
    setDiagnosisQuery: vi.fn(),
    diagnosisResults: [],
    setDiagnosisResults: vi.fn(),
    selectedDiagnosis: null,
    manualDiagnosis: '',
    setManualDiagnosis: vi.fn(),
    diagnosisSearchPerformed: false,
    enterManualDiagnosis: vi.fn(),
    exitManualDiagnosis: vi.fn(),
    selectDiagnosis: vi.fn(),
    searchDiagnoses: vi.fn(),
  }),
}))

vi.mock('./useDoctorDiagnosis', () => ({
  useDoctorDiagnosis: () => ({
    diagnosisType: 'PROVISIONAL',
    setDiagnosisType: vi.fn(),
    certainty: 'POSSIBLE',
    setCertainty: vi.fn(),
    savingDiagnosis: false,
    saveDiagnosis: vi.fn(),
  }),
}))

vi.mock('./useDoctorNursingHandoff', () => ({
  useDoctorNursingHandoff: () => ({
    nursingEncounter: null,
    nursingDocument: null,
    nursingVitals: [],
    loadingNursingHandoff: false,
    resetNursingHandoff: mocks.resetNursingHandoff,
    loadNursingHandoff: mocks.loadNursingHandoff,
  }),
}))

vi.mock('./useDoctorInvestigationCatalogues', () => ({
  useDoctorInvestigationCatalogues: () => ({
    laboratoryTests: [],
    diagnosticInvestigations: [],
  }),
}))

vi.mock('./useDoctorOrders', () => ({
  useDoctorOrders: () => ({
    savingOrder: false,
    cancellingOrderId: null,
    orderType: 'LABORATORY',
    setOrderType: vi.fn(),
    orderPriority: 'ROUTINE',
    setOrderPriority: vi.fn(),
    selectedLaboratoryTestId: '',
    selectedDiagnosticInvestigationId: '',
    orderTestCode: '',
    setOrderTestCode: vi.fn(),
    orderTestName: '',
    setOrderTestName: vi.fn(),
    orderMedicationId: '',
    setOrderMedicationId: vi.fn(),
    orderDose: '',
    setOrderDose: vi.fn(),
    prescriptionMedicine: '',
    setPrescriptionMedicine: vi.fn(),
    prescriptionStrength: '',
    setPrescriptionStrength: vi.fn(),
    prescriptionDoseUnit: '',
    setPrescriptionDoseUnit: vi.fn(),
    prescriptionRoute: '',
    setPrescriptionRoute: vi.fn(),
    prescriptionFrequency: '',
    setPrescriptionFrequency: vi.fn(),
    inpatientTreatmentStart: '',
    setInpatientTreatmentStart: vi.fn(),
    inpatientFirstDose: '',
    setInpatientFirstDose: vi.fn(),
    prescriptionDuration: '',
    setPrescriptionDuration: vi.fn(),
    prescriptionDurationUnit: '',
    setPrescriptionDurationUnit: vi.fn(),
    prescriptionQuantity: '',
    setPrescriptionQuantity: vi.fn(),
    prescriptionDirections: '',
    setPrescriptionDirections: vi.fn(),
    prescriptionIndication: '',
    setPrescriptionIndication: vi.fn(),
    handleLaboratoryTestChange: vi.fn(),
    handleDiagnosticInvestigationChange: vi.fn(),
    saveOrder: vi.fn(),
    cancelOrder: vi.fn(),
  }),
}))

vi.mock('./useDoctorHistory', () => ({
  useDoctorHistory: () => ({
    historicalEpisode: null,
    historicalEncounters: [],
    selectedHistoricalEncounter: null,
    historicalDocuments: [],
    historicalDiagnoses: [],
    historicalOrders: [],
    historicalVitals: [],
    historicalTimeline: [],
    loadingHistorical: false,
    openHistoricalEncounter: vi.fn(),
    openHistoricalEpisode: vi.fn(),
    closeHistoricalViewer: vi.fn(),
  }),
}))

vi.mock('./useDoctorDocumentation', () => ({
  useDoctorDocumentation: () => ({
    progressNote: null,
    initialClerking: {},
    progressNoteForm: {
      subjective: '',
      objective: '',
      workingDiagnosis: '',
      differentials: '',
      plan: '',
    },
    doctorNoteDocumentType: () => 'PROGRESS_NOTE',
    updateInitialClerking: vi.fn(),
    updateProgressNote: vi.fn(),
    resetProgressNote: vi.fn(),
    resetInitialClerking: vi.fn(),
  }),
}))

vi.mock('./useDoctorClinicalDocumentation', () => ({
  useDoctorClinicalDocumentation: () => ({
    loadingProgressNote: false,
    savingProgressNote: false,
    signingProgressNote: false,
    saveProgressNote: vi.fn(),
    signProgressNote: vi.fn(),
    loadProgressNote:
      mocks.clinicalDocumentation.loadProgressNote,
  }),
}))

vi.mock('./useDoctorVitals', () => ({
  useDoctorVitals: () => ({
    savingVitals: false,
    temperature: '',
    setTemperature: vi.fn(),
    heartRate: '',
    setHeartRate: vi.fn(),
    respiratoryRate: '',
    setRespiratoryRate: vi.fn(),
    systolicBp: '',
    setSystolicBp: vi.fn(),
    diastolicBp: '',
    setDiastolicBp: vi.fn(),
    spo2: '',
    setSpo2: vi.fn(),
    weight: '',
    setWeight: vi.fn(),
    saveVitals: vi.fn(),
  }),
}))

vi.mock('./useDoctorEpisodeActions', () => ({
  useDoctorEpisodeActions: () => ({
    admittingEpisode: false,
    admitSelectedEpisode: vi.fn(),
    closingEncounter: false,
    completeWardReview: vi.fn(),
  }),
}))

function episode(
  flow_status: string = 'OPEN',
): Episode {
  return {
    id: 'episode-1',
    patient_id: 'patient-1',
    episode_number: 'EP-001',
    status: 'OPEN',
    flow_status,
  } as Episode
}

function encounter(
  title: string,
  id = `encounter-${title.toLowerCase().replaceAll(' ', '-')}`,
): Encounter {
  return {
    id,
    episode_id: 'episode-1',
    title,
    status: 'OPEN',
  } as Encounter
}

const patient = {
  id: 'patient-1',
  first_name: 'Test',
  last_name: 'Patient',
  middle_name: null,
  hospital_number: 'H001',
  date_of_birth: '1990-01-01',
  sex: 'MALE',
}

const clinicItem = {
  id: 'episode-1',
  patient_id: 'patient-1',
  patient_name: 'Test Patient',
  hospital_number: 'H001',
  episode_number: 'EP-001',
  title: 'Clinic',
  status: 'OPEN' as const,
  flow_status: 'ROUTED' as const,
  managing_doctor_id: 'staff-1',
  checked_in_at: null,
  routed_at: null,
}

const wardItem = {
  id: 'episode-1',
  patient_id: 'patient-1',
  patient_name: 'Test Patient',
  hospital_number: 'H001',
  episode_number: 'EP-001',
  title: 'Ward',
  status: 'ADMITTED' as const,
  flow_status: 'ROUTED' as const,
  managing_doctor_id: 'staff-1',
  checked_in_at: null,
  routed_at: null,
}

describe('DoctorWorkspace workflow controller', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    mocks.doctorQueue.clinicQueue = []
    mocks.doctorQueue.wardQueue = []
    mocks.doctorQueue.currentStaffId = 'staff-1'

    mocks.getEpisode.mockResolvedValue(episode())
    mocks.getPatient.mockResolvedValue(patient)
      mocks.listEpisodeEncounters.mockResolvedValue([])
    mocks.startDoctorConsultation.mockResolvedValue(
      episode(),
    )
    mocks.createEncounter.mockImplementation(
      async (
        _token: string,
        payload: {
          title: string
        },
      ) => encounter(payload.title),
    )

    mocks.loadPreviousPatientEpisodes.mockResolvedValue(undefined)
    mocks.loadNursingHandoff.mockResolvedValue(undefined)
    mocks.refreshEncounterData.mockResolvedValue(undefined)
    mocks.refreshDoctorQueues.mockResolvedValue(undefined)
    mocks.clinicalDocumentation.loadProgressNote
      .mockResolvedValue(undefined)

    mocks.completeConsultation.mockResolvedValue(
      episode('ROUTED'),
    )
    mocks.completeDoctorReview.mockResolvedValue(
      episode('ROUTED'),
    )
  })

  it('creates a Doctor Consultation when no open clinic encounter exists', async () => {
    mocks.doctorQueue.clinicQueue = [clinicItem]
    mocks.listEpisodeEncounters
      .mockResolvedValueOnce([])
      .mockResolvedValue(encounter('Doctor Consultation'))

    const user = userEvent.setup()

    render(
      <DoctorWorkspace accessToken="test-token" />,
    )

    await user.click(
      screen.getByRole('button', {
        name: /Test PatientH001Clinic/,
      }),
    )

    expect(mocks.startDoctorConsultation).toHaveBeenCalledWith(
      'test-token',
      'episode-1',
    )

    expect(mocks.createEncounter).not.toHaveBeenCalled()
  })

  it('creates a Doctor Review when the episode is awaiting review', async () => {
    mocks.doctorQueue.clinicQueue = [clinicItem]
    mocks.getEpisode.mockResolvedValue(
      episode('AWAITING_REVIEW'),
    )

    const user = userEvent.setup()

    render(
      <DoctorWorkspace accessToken="test-token" />,
    )

    await user.click(
      screen.getByRole('button', {
        name: /Test PatientH001Clinic/,
      }),
    )

    expect(mocks.createEncounter).toHaveBeenCalledWith(
      'test-token',
      {
        episode_id: 'episode-1',
        staff_id: 'staff-1',
        title: 'Doctor Review',
      },
    )
  })

  it('creates a Ward Review when a ward queue item is opened', async () => {
    mocks.doctorQueue.wardQueue = [wardItem]

    const user = userEvent.setup()

    render(
      <DoctorWorkspace accessToken="test-token" />,
    )

    await user.click(
      screen.getByRole('button', {
        name: /Test PatientH001Ward/,
      }),
    )

    expect(mocks.createEncounter).toHaveBeenCalledWith(
      'test-token',
      {
        episode_id: 'episode-1',
        staff_id: 'staff-1',
        title: 'Ward Review',
      },
    )
  })

  it('reuses an existing open preferred encounter instead of creating another', async () => {
    mocks.doctorQueue.clinicQueue = [clinicItem]

    const existing = encounter('Doctor Consultation', 'existing-1')

    mocks.listEpisodeEncounters.mockResolvedValue([
      existing,
    ])

    const user = userEvent.setup()

    render(
      <DoctorWorkspace accessToken="test-token" />,
    )

    await user.click(
      screen.getByRole('button', {
        name: /Test PatientH001Clinic/,
      }),
    )

    expect(mocks.createEncounter).not.toHaveBeenCalled()
    expect(mocks.setSelectedEncounter).toHaveBeenCalledWith(
      existing,
    )
    expect(
      mocks.clinicalDocumentation.loadProgressNote,
    ).toHaveBeenCalledWith('existing-1')
  })

  it('completes the consultation and refreshes the clinical workspace', async () => {
    mocks.doctorQueue.clinicQueue = [clinicItem]

    const selected = encounter(
      'Doctor Consultation',
      'consultation-1',
    )

    mocks.listEpisodeEncounters.mockResolvedValue([
      selected,
    ])

    const updatedEpisode = episode('ROUTED')
    mocks.completeConsultation.mockResolvedValue(
      updatedEpisode,
    )

    const user = userEvent.setup()

    render(
      <DoctorWorkspace accessToken="test-token" />,
    )

    await user.click(
      screen.getByRole('button', {
        name: /Test PatientH001Clinic/,
      }),
    )

    await user.click(
      screen.getByRole('button', {
        name: 'Mock Complete Consultation',
      }),
    )

    expect(mocks.completeConsultation).toHaveBeenCalledWith(
      'test-token',
      'episode-1',
      {
        encounter_id: 'consultation-1',
        disposition: 'COMPLETE',
      },
    )

    expect(
      mocks.refreshEncounterData,
    ).toHaveBeenCalledWith('consultation-1')

    expect(
      mocks.doctorQueue.refreshDoctorQueues,
    ).toHaveBeenCalled()

    expect(
      screen.getByText('Consultation completed.'),
    ).toBeInTheDocument()
  })

  it('completes a Doctor Review and refreshes the clinical workspace', async () => {
    mocks.doctorQueue.clinicQueue = [clinicItem]

    const selected = encounter(
      'Doctor Review',
      'review-1',
    )

    mocks.getEpisode.mockResolvedValue(
      episode('AWAITING_REVIEW'),
    )

    mocks.listEpisodeEncounters.mockResolvedValue([
      selected,
    ])

    const user = userEvent.setup()

    render(
      <DoctorWorkspace accessToken="test-token" />,
    )

    await user.click(
      screen.getByRole('button', {
        name: /Test PatientH001Clinic/,
      }),
    )

    await user.click(
      screen.getByRole('button', {
        name: 'Mock Complete Doctor Review',
      }),
    )

    expect(
      mocks.completeDoctorReview,
    ).toHaveBeenCalledWith(
      'test-token',
      'episode-1',
      {
        encounter_id: 'review-1',
      },
    )

    expect(
      mocks.refreshEncounterData,
    ).toHaveBeenCalledWith('review-1')

    expect(
      mocks.doctorQueue.refreshDoctorQueues,
    ).toHaveBeenCalled()

    expect(
      screen.getByText('Doctor Review completed.'),
    ).toBeInTheDocument()
  })
})
