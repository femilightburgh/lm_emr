import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import DoctorEncounterWorkspace from './DoctorEncounterWorkspace'

vi.mock('./ClinicalOrdersPanel', () => ({
  default: () => (
    <div data-testid="clinical-orders-panel">
      Clinical Orders
    </div>
  ),
}))

vi.mock('./DiagnosisPanel', () => ({
  default: ({ title }: { title: string }) => (
    <div data-testid="diagnosis-panel">
      {title}
    </div>
  ),
}))

vi.mock('./DoctorInvestigationResults', () => ({
  default: () => (
    <div data-testid="investigation-results">
      Investigation Results
    </div>
  ),
}))

vi.mock('./HistoricalEncounterPanel', () => ({
  default: () => (
    <div data-testid="historical-encounter-panel">
      Historical Encounter
    </div>
  ),
}))

vi.mock('./InitialClerkingPanel', () => ({
  default: () => (
    <div data-testid="initial-clerking-panel">
      Initial Clerking
    </div>
  ),
}))

vi.mock('./NursingHandoffPanel', () => ({
  default: () => (
    <div data-testid="nursing-handoff-panel">
      Nursing Handoff
    </div>
  ),
}))

vi.mock('./PatientHistoryPanel', () => ({
  default: () => (
    <div data-testid="patient-history-panel">
      Patient History
    </div>
  ),
}))

vi.mock('./ProgressNotePanel', () => ({
  default: () => (
    <div data-testid="progress-note-panel">
      Progress Note
    </div>
  ),
}))

vi.mock('./SignedClinicalDocumentSummary', () => ({
  default: () => (
    <div data-testid="signed-document-summary">
      Signed Document
    </div>
  ),
}))

vi.mock('./VitalsPanel', () => ({
  default: () => (
    <div data-testid="vitals-panel">
      Vitals
    </div>
  ),
}))

vi.mock('./DoctorMedicationTreatmentReview', () => ({
  default: () => (
    <div data-testid="medication-treatment-review">
      Medication & Treatment Review
    </div>
  ),
}))

type WorkspaceProps = React.ComponentProps<
  typeof DoctorEncounterWorkspace
>

function createEncounter(
  title: string,
  status: 'OPEN' | 'CLOSED' = 'OPEN',
): WorkspaceProps['selectedEncounter'] {
  return {
    id: `encounter-${title.replaceAll(' ', '-').toLowerCase()}`,
    title,
    status,
  } as WorkspaceProps['selectedEncounter']
}

function createEpisode(
  status: 'OPEN' | 'ADMITTED' = 'OPEN',
): NonNullable<WorkspaceProps['selectedEpisode']> {
  return {
    id: 'episode-1',
    episode_number: 'EP-001',
    status,
  } as NonNullable<WorkspaceProps['selectedEpisode']>
}

function createDocumentation(
  documentType: 'INITIAL_CLERKING' | 'PROGRESS_NOTE' = 'PROGRESS_NOTE',
): WorkspaceProps['documentation'] {
  const emptyInitialClerking = {
    complaint: '',
    complaintDuration: '',
    history: '',
    reviewOfSystems: '',
    pastMedicalHistory: '',
    pastSurgicalHistory: '',
    drugHistory: '',
    allergies: '',
    familyHistory: '',
    socialHistory: '',
    personalHistory: '',
    gynaecologicalHistory: '',
    obstetricHistory: '',
    menstrualHistory: '',
    sexualHistory: '',
    ideas: '',
    concerns: '',
    expectations: '',
    examGeneral: '',
    examCardiovascular: '',
    examRespiratory: '',
    examAbdomen: '',
    examNeurological: '',
    examMusculoskeletal: '',
    examGenitourinary: '',
    examOther: '',
    investigations: '',
  }

  const emptyProgressNoteForm = {
    subjective: '',
    objective: '',
    workingDiagnosis: '',
    differentials: '',
    plan: '',
  }

  return {
    progressNote: null,
    setProgressNote: () => {},

    initialClerking: emptyInitialClerking,
    progressNoteForm: emptyProgressNoteForm,

    updateInitialClerking: () => {},
    updateProgressNote: () => {},

    resetInitialClerking: () => {},
    resetProgressNote: () => {},

    loadProgressNoteContent: () => {},
    loadInitialClerkingContent: () => {},

    initialClerkingContent: () => ({}),
    progressNoteContent: () => ({}),

    doctorNoteDocumentType: () => documentType,
  }
}

function createProps(
  title: string,
  status: 'OPEN' | 'CLOSED' = 'OPEN',
): WorkspaceProps {
  const noop = () => {}
  const asyncNoop = async () => {}

  return {
    selectedEncounter: createEncounter(title, status),
    selectedEpisode: createEpisode(),
    accessToken: 'test-token',
    onBackToQueue: noop,
    onSelectCurrentEncounter: noop,
    patient: {
      first_name: 'Test',
      middle_name: null,
      last_name: 'Patient',
      hospital_number: 'H001',
      date_of_birth: '1990-01-01',
      sex: 'MALE',
    } as WorkspaceProps['patient'],
    loadingPatientContext: false,

    previousEpisodes: [],
    currentEpisodeEncounters: [],
    historicalEpisode: null,
    historicalEncounters: [],
    selectedHistoricalEncounter: null,
    historicalDocuments: [],
    historicalDiagnoses: [],
    historicalOrders: [],
    historicalVitals: [],
    historicalTimeline: [],
    loadingPreviousEpisodes: false,
    loadingHistorical: false,
    openHistoricalEncounter: asyncNoop,
    openHistoricalEpisode: asyncNoop,
    closeHistoricalViewer: noop,

    nursingEncounter: null,
    nursingDocument: null,
    loadingNursingHandoff: false,

    timeline: [],
    loadingTimeline: false,

    documentation: createDocumentation(),

    progressNote: null,
    loadingProgressNote: false,
    savingProgressNote: false,
    signingProgressNote: false,
    admittingEpisode: false,

    insertLatestVitals: noop,
    saveProgressNote: asyncNoop,
    signProgressNote: asyncNoop,
    admitSelectedEpisode: asyncNoop,
    closingEncounter: false,
    completeWardReview: asyncNoop,

    vitals: [],
    nursingVitals: [],
    savingVitals: false,
    temperature: '',
    heartRate: '',
    respiratoryRate: '',
    systolicBp: '',
    diastolicBp: '',
    spo2: '',
    weight: '',
    setTemperature: noop,
    setHeartRate: noop,
    setRespiratoryRate: noop,
    setSystolicBp: noop,
    setDiastolicBp: noop,
    setSpo2: noop,
    setWeight: noop,
    saveVitals: asyncNoop,

    diagnoses: [],
    loadingDiagnoses: false,
    savingDiagnosis: false,
    diagnosisQuery: '',
    diagnosisResults: [],
    selectedDiagnosis: null,
    manualDiagnosis: '',
    diagnosisSearchPerformed: false,
    diagnosisType: 'PROVISIONAL',
    certainty: 'SUSPECTED',
    searchDiagnoses: asyncNoop,
    enterManualDiagnosis: noop,
    exitManualDiagnosis: noop,
    setManualDiagnosis: noop,
    selectDiagnosis: noop,
    setDiagnosisType: noop,
    setCertainty: noop,
    saveDiagnosis: asyncNoop,

    orders: [],
    clinicalResults: [],
    loadingOrders: false,
    savingOrder: false,
    cancellingOrderId: null,
    inpatientTreatmentStart: '',
    inpatientFirstDose: '',
    orderType: 'LABORATORY',
    orderPriority: 'ROUTINE',
    laboratoryTests: [],
    selectedLaboratoryTestIds: [],
      customLaboratoryInvestigation: '',
    diagnosticInvestigations: [],
    selectedDiagnosticInvestigationId: '',
      customDiagnosticInvestigation: '',
    orderMedicationId: '',
    orderDose: '',
    prescriptionMedicine: '',
    prescriptionStrength: '',
    prescriptionDoseUnit: '',
    prescriptionRoute: '',
    prescriptionFrequency: '',
    prescriptionDuration: '',
    prescriptionDurationUnit: '',
    prescriptionQuantity: '',
    prescriptionDirections: '',
    prescriptionIndication: '',
    setInpatientTreatmentStart: noop,
    setInpatientFirstDose: noop,
    setOrderType: noop,
    setOrderPriority: noop,
    handleLaboratoryTestChange: noop,
      setCustomLaboratoryInvestigation: noop,
    handleDiagnosticInvestigationChange: noop,
      setCustomDiagnosticInvestigation: noop,
    setOrderMedicationId: noop,
    setOrderDose: noop,
    setPrescriptionMedicine: noop,
    setPrescriptionStrength: noop,
    setPrescriptionDoseUnit: noop,
    setPrescriptionRoute: noop,
    setPrescriptionFrequency: noop,
    setPrescriptionDuration: noop,
    setPrescriptionDurationUnit: noop,
    setPrescriptionQuantity: noop,
    setPrescriptionDirections: noop,
    setPrescriptionIndication: noop,
    saveOrder: asyncNoop,
    cancelOrder: asyncNoop,

    completingConsultation: false,
    handleCompleteConsultation: asyncNoop,

    completingDoctorReview: false,
    handleCompleteDoctorReview: asyncNoop,

    loadingClinicalResults: false,
    diagnosticReports: [],
    diagnosticAttachments: {},
  }
}

describe('DoctorEncounterWorkspace orchestration', () => {
  it('renders the consultation workflow sections in the non-ward branch', async () => {
    render(
      <DoctorEncounterWorkspace
        {...createProps('Doctor Consultation')}
      />,
    )

    expect(
      screen.getByTestId('vitals-panel'),
    ).toBeInTheDocument()

    expect(
      screen.getByTestId('diagnosis-panel'),
    ).toHaveTextContent('Initial Assessment')

    expect(
      screen.getByText('Timeline'),
    ).toBeInTheDocument()

    expect(
      screen.queryByTestId('nursing-handoff-panel'),
    ).not.toBeInTheDocument()

    expect(
      screen.queryByTestId('medication-treatment-review'),
    ).not.toBeInTheDocument()

    const user = userEvent.setup()

    await user.click(
      screen.getByRole('tab', {
        name: 'Notes',
      }),
    )

    expect(
      screen.getByTestId('progress-note-panel'),
    ).toBeInTheDocument()

    await user.click(
      screen.getByRole('tab', {
        name: 'Orders',
      }),
    )

    expect(
      screen.getByTestId('clinical-orders-panel'),
    ).toBeInTheDocument()

    await user.click(
      screen.getByRole('tab', {
        name: 'Results',
      }),
    )

    expect(
      screen.getByTestId('investigation-results'),
    ).toBeInTheDocument()

    await user.click(
      screen.getByRole('tab', {
        name: 'History',
      }),
    )

    expect(
      screen.getByTestId('patient-history-panel'),
    ).toBeInTheDocument()
  })

  it('renders the complete ward review clinical composition', async () => {
    render(
      <DoctorEncounterWorkspace
        {...createProps('Ward Review')}
      />,
    )

    expect(
      screen.getByTestId('diagnosis-panel'),
    ).toHaveTextContent('Clinical Assessment')

    expect(
      screen.getByTestId('nursing-handoff-panel'),
    ).toBeInTheDocument()

    expect(
      screen.getByTestId('medication-treatment-review'),
    ).toBeInTheDocument()

    expect(
      screen.getByText('Timeline'),
    ).toBeInTheDocument()

    const user = userEvent.setup()

    await user.click(
      screen.getByRole('tab', {
        name: 'Notes',
      }),
    )

    expect(
      screen.getByTestId('progress-note-panel'),
    ).toBeInTheDocument()

    await user.click(
      screen.getByRole('tab', {
        name: 'Orders',
      }),
    )

    expect(
      screen.getByTestId('clinical-orders-panel'),
    ).toBeInTheDocument()

    await user.click(
      screen.getByRole('tab', {
        name: 'Results',
      }),
    )

    expect(
      screen.getByTestId('investigation-results'),
    ).toBeInTheDocument()
  })

  it('requires disposition details before completing a ward review', async () => {
    const props = createProps('Ward Review')

    const completeWardReview = vi.fn(async () => {})
    props.completeWardReview = completeWardReview

    render(
      <DoctorEncounterWorkspace {...props} />,
    )

    const completeButton =
      screen.getByRole('button', {
        name: 'Complete Ward Review',
      })

    expect(completeButton).toBeEnabled()

    const disposition = screen.getByRole(
      'combobox',
      { name: 'Disposition' },
    )

    const user = userEvent.setup()

    await user.selectOptions(
      disposition,
      'TRANSFER',
    )

    expect(
      screen.getByRole('textbox', {
        name: 'Details',
      }),
    ).toBeInTheDocument()

    expect(completeButton).toBeDisabled()

    await user.type(
      screen.getByRole('textbox', {
        name: 'Details',
      }),
      'Transfer to cardiology service.',
    )

    expect(completeButton).toBeEnabled()

    await user.click(completeButton)

    expect(completeWardReview).toHaveBeenCalledWith(
      'TRANSFER',
      'Transfer to cardiology service.',
    )
  })

  it('does not render ward review completion for a closed ward encounter', () => {
    render(
      <DoctorEncounterWorkspace
        {...createProps('Ward Review', 'CLOSED')}
      />,
    )

    expect(
      screen.queryByRole('button', {
        name: 'Complete Ward Review',
      }),
    ).not.toBeInTheDocument()
  })

  it('renders consultation completion only for a signed initial clerking', () => {
    const props = createProps('Doctor Consultation')

    props.progressNote = {
      document_type: 'INITIAL_CLERKING',
      status: 'SIGNED',
    } as WorkspaceProps['progressNote']

    render(
      <DoctorEncounterWorkspace {...props} />,
    )

    expect(
      screen.getByRole('button', {
        name: 'Complete Consultation',
      }),
    ).toBeInTheDocument()
  })

  it('does not render consultation completion for an unsigned initial clerking', () => {
    const props = createProps('Doctor Consultation')

    props.progressNote = {
      document_type: 'INITIAL_CLERKING',
      status: 'DRAFT',
    } as WorkspaceProps['progressNote']

    render(
      <DoctorEncounterWorkspace {...props} />,
    )

    expect(
      screen.queryByRole('button', {
        name: 'Complete Consultation',
      }),
    ).not.toBeInTheDocument()
  })

  it('calls the doctor review completion action when the review is open', async () => {
    const props = createProps('Doctor Review')

    const handleCompleteDoctorReview =
      vi.fn(async () => {})

    props.handleCompleteDoctorReview =
      handleCompleteDoctorReview

    render(
      <DoctorEncounterWorkspace {...props} />,
    )

    const completeButton =
      screen.getByRole('button', {
        name: 'Complete Doctor Review',
      })

    const user = userEvent.setup()
    await user.click(completeButton)

    expect(
      handleCompleteDoctorReview,
    ).toHaveBeenCalledTimes(1)
  })

  it('uses Initial Clerking documentation when the documentation hook selects it', async () => {
    const props = createProps('Doctor Consultation')

    props.documentation =
      createDocumentation('INITIAL_CLERKING')

    render(
      <DoctorEncounterWorkspace {...props} />,
    )

    const user = userEvent.setup()

    await user.click(
      screen.getByRole('tab', {
        name: 'Notes',
      }),
    )

    expect(
      screen.getByTestId('initial-clerking-panel'),
    ).toBeInTheDocument()

    expect(
      screen.queryByTestId('progress-note-panel'),
    ).not.toBeInTheDocument()
  })
})
