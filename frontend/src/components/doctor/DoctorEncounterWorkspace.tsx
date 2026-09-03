import { useState } from 'react'

import type { ClinicalEvent, Encounter } from '../../api/encounters'
import type { Episode } from '../../api/episodes'
import type { Patient } from '../../api/patients'
import type {
  ClinicalDiagnosis,
  DiagnosisCertainty,
  DiagnosisType,
} from '../../api/diagnoses'
import type { TerminologyConcept } from '../../api/terminology'
import type { ClinicalDocument } from '../../api/clinicalDocuments'
import type {
  ClinicalOrder,
  ClinicalOrderType,
} from '../../api/clinicalOrders'
import type { LaboratoryTest } from '../../api/laboratory'
import type { ClinicalResult } from '../../api/clinicalResults'
import type {
  DiagnosticInvestigation,
  DiagnosticReport,
} from '../../api/diagnostics'
import type { Vitals } from '../../api/vitals'
import type { DoctorDiagnosticAttachment } from './doctorEncounterContext'

import ClinicalOrdersPanel from './ClinicalOrdersPanel'
import DiagnosisPanel from './DiagnosisPanel'
import DoctorInvestigationResults from './DoctorInvestigationResults'
import HistoricalEncounterPanel from './HistoricalEncounterPanel'
import InitialClerkingPanel from './InitialClerkingPanel'
import NursingHandoffPanel from './NursingHandoffPanel'
import PatientHistoryPanel from './PatientHistoryPanel'
import ProgressNotePanel from './ProgressNotePanel'
import SignedClinicalDocumentSummary from './SignedClinicalDocumentSummary'
import VitalsPanel from './VitalsPanel'
import DoctorMedicationTreatmentReview from './DoctorMedicationTreatmentReview'
import type { useDoctorDocumentation } from './useDoctorDocumentation'

type StringChangeHandler = (
  value: string,
) => void

type AsyncAction = () => Promise<void>

type WardReviewDisposition =
  | 'CONTINUE_ADMISSION'
  | 'DISCHARGE'
  | 'TRANSFER'
  | 'REFERRAL'
  | 'OTHER'

type CompleteWardReviewAction = (
  disposition: WardReviewDisposition,
  details: string | null,
) => Promise<void>

interface Props {
  selectedEncounter: Encounter
  selectedEpisode: Episode | null
  accessToken: string
  patient: Patient | null
  loadingPatientContext: boolean

  previousEpisodes: Episode[]
  currentEpisodeEncounters: Encounter[]
  historicalEpisode: Episode | null
  historicalEncounters: Encounter[]
  selectedHistoricalEncounter: Encounter | null
  historicalDocuments: ClinicalDocument[]
  historicalDiagnoses: ClinicalDiagnosis[]
  historicalOrders: ClinicalOrder[]
  historicalVitals: Vitals[]
  historicalTimeline: ClinicalEvent[]
  loadingPreviousEpisodes: boolean
  loadingHistorical: boolean
  openHistoricalEncounter: (
    episode: Episode,
    encounter: Encounter,
  ) => Promise<void>
  openHistoricalEpisode: (
    episode: Episode,
  ) => Promise<void>
  closeHistoricalViewer: () => void

  nursingEncounter: Encounter | null
  nursingDocument: ClinicalDocument | null
  loadingNursingHandoff: boolean

  timeline: ClinicalEvent[]
  loadingTimeline: boolean

  documentation: ReturnType<typeof useDoctorDocumentation>

  progressNote: ClinicalDocument | null
  loadingProgressNote: boolean
  savingProgressNote: boolean
  signingProgressNote: boolean
  admittingEpisode: boolean

  clerkingComplaint: string
  clerkingComplaintDuration: string
  clerkingHistory: string
  clerkingReviewOfSystems: string
  clerkingPastMedicalHistory: string
  clerkingPastSurgicalHistory: string
  clerkingDrugHistory: string
  clerkingAllergies: string
  clerkingFamilyHistory: string
  clerkingSocialHistory: string
  clerkingPersonalHistory: string
  clerkingIdeas: string
  clerkingConcerns: string
  clerkingExpectations: string
  clerkingExamGeneral: string
  clerkingExamCardiovascular: string
  clerkingExamRespiratory: string
  clerkingExamAbdomen: string
  clerkingExamNeurological: string
  clerkingExamMusculoskeletal: string
  clerkingExamGenitourinary: string
  clerkingExamOther: string

  noteSubjective: string
  noteObjective: string
  noteWorkingDiagnosis: string
  noteDifferentials: string
  notePlan: string

  setClerkingComplaint: StringChangeHandler
  setClerkingComplaintDuration: StringChangeHandler
  setClerkingHistory: StringChangeHandler
  setClerkingReviewOfSystems: StringChangeHandler
  setClerkingPastMedicalHistory: StringChangeHandler
  setClerkingPastSurgicalHistory: StringChangeHandler
  setClerkingDrugHistory: StringChangeHandler
  setClerkingAllergies: StringChangeHandler
  setClerkingFamilyHistory: StringChangeHandler
  setClerkingSocialHistory: StringChangeHandler
  setClerkingPersonalHistory: StringChangeHandler
  setClerkingIdeas: StringChangeHandler
  setClerkingConcerns: StringChangeHandler
  setClerkingExpectations: StringChangeHandler
  setClerkingExamGeneral: StringChangeHandler
  setClerkingExamCardiovascular: StringChangeHandler
  setClerkingExamRespiratory: StringChangeHandler
  setClerkingExamAbdomen: StringChangeHandler
  setClerkingExamNeurological: StringChangeHandler
  setClerkingExamMusculoskeletal: StringChangeHandler
  setClerkingExamGenitourinary: StringChangeHandler
  setClerkingExamOther: StringChangeHandler

  setNoteSubjective: StringChangeHandler
  setNoteObjective: StringChangeHandler
  setNoteWorkingDiagnosis: StringChangeHandler
  setNoteDifferentials: StringChangeHandler
  setNotePlan: StringChangeHandler

  insertLatestVitals: () => void
  saveProgressNote: AsyncAction
  signProgressNote: AsyncAction
  admitSelectedEpisode: AsyncAction
  closingEncounter: boolean
  completeWardReview: CompleteWardReviewAction
  vitals: Vitals[]
  nursingVitals: Vitals[]
  savingVitals: boolean
  temperature: string
  heartRate: string
  respiratoryRate: string
  systolicBp: string
  diastolicBp: string
  spo2: string
  weight: string
  setTemperature: StringChangeHandler
  setHeartRate: StringChangeHandler
  setRespiratoryRate: StringChangeHandler
  setSystolicBp: StringChangeHandler
  setDiastolicBp: StringChangeHandler
  setSpo2: StringChangeHandler
  setWeight: StringChangeHandler
  saveVitals: AsyncAction

  diagnoses: ClinicalDiagnosis[]
  loadingDiagnoses: boolean
  savingDiagnosis: boolean
  diagnosisQuery: string
  diagnosisResults: TerminologyConcept[]
  selectedDiagnosis: TerminologyConcept | null
  diagnosisType: DiagnosisType
  certainty: DiagnosisCertainty
  searchDiagnoses: (
    query: string,
  ) => Promise<void>
  setSelectedDiagnosis: (
    value: TerminologyConcept | null,
  ) => void
  setDiagnosisType: (
    value: DiagnosisType,
  ) => void
  setCertainty: (
    value: DiagnosisCertainty,
  ) => void
  saveDiagnosis: AsyncAction

  orders: ClinicalOrder[]
  clinicalResults: ClinicalResult[]
  loadingOrders: boolean
  savingOrder: boolean
  cancellingOrderId: string | null
  inpatientTreatmentStart: string
  inpatientFirstDose: string
  orderType: ClinicalOrderType
  orderPriority: string
  laboratoryTests: LaboratoryTest[]
  selectedLaboratoryTestId: string
  diagnosticInvestigations: DiagnosticInvestigation[]
  selectedDiagnosticInvestigationId: string
  orderTestCode: string
  orderTestName: string
  orderMedicationId: string
  orderDose: string
  prescriptionMedicine: string
  prescriptionStrength: string
  prescriptionDoseUnit: string
  prescriptionRoute: string
  prescriptionFrequency: string
  prescriptionDuration: string
  prescriptionDurationUnit: string
  prescriptionQuantity: string
  prescriptionDirections: string
  prescriptionIndication: string
  setInpatientTreatmentStart: StringChangeHandler
  setInpatientFirstDose: StringChangeHandler
  setOrderType: (
    value: ClinicalOrderType,
  ) => void
  setOrderPriority: StringChangeHandler
  handleLaboratoryTestChange: StringChangeHandler
  handleDiagnosticInvestigationChange: StringChangeHandler
  setOrderTestCode: StringChangeHandler
  setOrderTestName: StringChangeHandler
  setOrderMedicationId: StringChangeHandler
  setOrderDose: StringChangeHandler
  setPrescriptionMedicine: StringChangeHandler
  setPrescriptionStrength: StringChangeHandler
  setPrescriptionDoseUnit: StringChangeHandler
  setPrescriptionRoute: StringChangeHandler
  setPrescriptionFrequency: StringChangeHandler
  setPrescriptionDuration: StringChangeHandler
  setPrescriptionDurationUnit: StringChangeHandler
  setPrescriptionQuantity: StringChangeHandler
  setPrescriptionDirections: StringChangeHandler
  setPrescriptionIndication: StringChangeHandler
  saveOrder: AsyncAction
  cancelOrder: (
    orderId: string,
  ) => Promise<void>

  completingConsultation: boolean
  handleCompleteConsultation: AsyncAction

  completingDoctorReview: boolean
  handleCompleteDoctorReview: AsyncAction

  loadingClinicalResults: boolean
  diagnosticReports: DiagnosticReport[]
  diagnosticAttachments: Record<
    string,
    DoctorDiagnosticAttachment[]
  >
}

const EVENT_LABELS: Record<string, string> = {
  VITALS_RECORDED: 'Vital signs recorded',
  CLINICAL_NOTE_RECORDED: 'Clinical note recorded',
  DIAGNOSIS_RECORDED: 'Diagnosis recorded',
  MEDICATION_PRESCRIBED: 'Medication prescribed',
  MEDICATION_GIVEN: 'Medication administered',
  INVESTIGATION_ORDERED: 'Investigation ordered',
  CLINICAL_ORDER_CANCELLED: 'Clinical order cancelled',
  RESULT_RECORDED: 'Result recorded',
  PROCEDURE_PERFORMED: 'Procedure performed',
  WOUND_DRESSED: 'Wound dressed',
  EPISODE_ADMITTED: 'Episode admitted',
}


function formatEventLabel(
  eventType: string,
): string {
  return (
    EVENT_LABELS[eventType] ??
    eventType
      .toLowerCase()
      .replaceAll('_', ' ')
  )
}



export default function DoctorEncounterWorkspace({
  selectedEncounter,
  accessToken,
  selectedEpisode,
  patient,
  loadingPatientContext,
  previousEpisodes,
  currentEpisodeEncounters,
  historicalEpisode,
  historicalEncounters,
  selectedHistoricalEncounter,
  historicalDocuments,
  historicalDiagnoses,
  historicalOrders,
  historicalVitals,
  historicalTimeline,
  loadingPreviousEpisodes,
  loadingHistorical,
  openHistoricalEncounter,
  openHistoricalEpisode,
  closeHistoricalViewer,
  nursingEncounter,
  nursingDocument,
  loadingNursingHandoff,
  timeline,
  loadingTimeline,
  documentation,
  progressNote,
  loadingProgressNote,
  savingProgressNote,
  signingProgressNote,
  admittingEpisode,
  clerkingComplaint,
  clerkingComplaintDuration,
  clerkingHistory,
  clerkingReviewOfSystems,
  clerkingPastMedicalHistory,
  clerkingPastSurgicalHistory,
  clerkingDrugHistory,
  clerkingAllergies,
  clerkingFamilyHistory,
  clerkingSocialHistory,
  clerkingPersonalHistory,
  clerkingIdeas,
  clerkingConcerns,
  clerkingExpectations,
  clerkingExamGeneral,
  clerkingExamCardiovascular,
  clerkingExamRespiratory,
  clerkingExamAbdomen,
  clerkingExamNeurological,
  clerkingExamMusculoskeletal,
  clerkingExamGenitourinary,
  clerkingExamOther,
  noteSubjective,
  noteObjective,
  noteWorkingDiagnosis,
  noteDifferentials,
  notePlan,
  setClerkingComplaint,
  setClerkingComplaintDuration,
  setClerkingHistory,
  setClerkingReviewOfSystems,
  setClerkingPastMedicalHistory,
  setClerkingPastSurgicalHistory,
  setClerkingDrugHistory,
  setClerkingAllergies,
  setClerkingFamilyHistory,
  setClerkingSocialHistory,
  setClerkingPersonalHistory,
  setClerkingIdeas,
  setClerkingConcerns,
  setClerkingExpectations,
  setClerkingExamGeneral,
  setClerkingExamCardiovascular,
  setClerkingExamRespiratory,
  setClerkingExamAbdomen,
  setClerkingExamNeurological,
  setClerkingExamMusculoskeletal,
  setClerkingExamGenitourinary,
  setClerkingExamOther,
  setNoteSubjective,
  setNoteObjective,
  setNoteWorkingDiagnosis,
  setNoteDifferentials,
  setNotePlan,
  insertLatestVitals,
  saveProgressNote,
  signProgressNote,
  admitSelectedEpisode,
  closingEncounter,
  completeWardReview,
  vitals,
  nursingVitals,
  savingVitals,
  temperature,
  heartRate,
  respiratoryRate,
  systolicBp,
  diastolicBp,
  spo2,
  weight,
  setTemperature,
  setHeartRate,
  setRespiratoryRate,
  setSystolicBp,
  setDiastolicBp,
  setSpo2,
  setWeight,
  saveVitals,
  diagnoses,
  loadingDiagnoses,
  savingDiagnosis,
  diagnosisQuery,
  diagnosisResults,
  selectedDiagnosis,
  diagnosisType,
  certainty,
  searchDiagnoses,
  setSelectedDiagnosis,
  setDiagnosisType,
  setCertainty,
  saveDiagnosis,
  orders,
  clinicalResults,
  loadingOrders,
  savingOrder,
  cancellingOrderId,
  inpatientTreatmentStart,
  inpatientFirstDose,
  orderType,
  orderPriority,
  laboratoryTests,
  selectedLaboratoryTestId,
  diagnosticInvestigations,
  selectedDiagnosticInvestigationId,
  orderTestCode,
  orderTestName,
  orderMedicationId,
  orderDose,
  prescriptionMedicine,
  prescriptionStrength,
  prescriptionDoseUnit,
  prescriptionRoute,
  prescriptionFrequency,
  prescriptionDuration,
  prescriptionDurationUnit,
  prescriptionQuantity,
  prescriptionDirections,
  prescriptionIndication,
  setInpatientTreatmentStart,
  setInpatientFirstDose,
  setOrderType,
  setOrderPriority,
  handleLaboratoryTestChange,
  handleDiagnosticInvestigationChange,
  setOrderTestCode,
  setOrderTestName,
  setOrderMedicationId,
  setOrderDose,
  setPrescriptionMedicine,
  setPrescriptionStrength,
  setPrescriptionDoseUnit,
  setPrescriptionRoute,
  setPrescriptionFrequency,
  setPrescriptionDuration,
  setPrescriptionDurationUnit,
  setPrescriptionQuantity,
  setPrescriptionDirections,
  setPrescriptionIndication,
  saveOrder,
  cancelOrder,
  completingConsultation,
  handleCompleteConsultation,
  completingDoctorReview,
  handleCompleteDoctorReview,
  loadingClinicalResults,
  diagnosticReports,
  diagnosticAttachments,
}: Props) {
  const isWardReview =
    selectedEncounter.title === 'Ward Review'

  const [wardReviewDisposition, setWardReviewDisposition] =
    useState<WardReviewDisposition>(
      'CONTINUE_ADMISSION',
    )

  const [wardReviewDetails, setWardReviewDetails] =
    useState('')

  const wardReviewDetailsRequired =
    wardReviewDisposition === 'TRANSFER' ||
    wardReviewDisposition === 'REFERRAL' ||
    wardReviewDisposition === 'OTHER'

  const wardReviewReady =
    !wardReviewDetailsRequired ||
    wardReviewDetails.trim().length > 0


  const renderDiagnosis = () => (
<DiagnosisPanel
  eyebrow={
    isWardReview
      ? 'CLINICAL ASSESSMENT'
      : 'INITIAL ASSESSMENT'
  }
  title={
    isWardReview
      ? 'Clinical Assessment'
      : 'Initial Assessment'
  }
  description={
    isWardReview
      ? 'Review and update the patient\'s current diagnoses and clinical assessment.'
      : 'Record the working, provisional, and differential diagnoses that guide the investigation plan.'
  }

  diagnoses={diagnoses}
  loading={loadingDiagnoses}
  saving={savingDiagnosis}
  encounterClosed={
    selectedEncounter.status === 'CLOSED'
  }

  query={diagnosisQuery}
  results={diagnosisResults}
  selected={selectedDiagnosis}

  diagnosisType={diagnosisType}
  certainty={certainty}

  onQueryChange={value =>
    void searchDiagnoses(value)
  }

  onSelect={
    setSelectedDiagnosis
  }

  onDiagnosisTypeChange={
    setDiagnosisType
  }

  onCertaintyChange={
    setCertainty
  }

  onSave={() =>
    void saveDiagnosis()
  }
/>
  )


  const renderDocumentation = () => (
<div className="doctor-documentation-section">
  <div className="doctor-section-heading">
    <p className="eyebrow">
      DOCUMENTATION
    </p>

    <h2>
      Clinical Documentation
    </h2>

    <p>
      Record and review the current clinical documentation.
    </p>
  </div>

{documentation.doctorNoteDocumentType() === 'INITIAL_CLERKING' ? (
  <InitialClerkingPanel
    document={progressNote}
    loading={loadingProgressNote}
    saving={savingProgressNote}
    signing={signingProgressNote}

    complaint={clerkingComplaint}
    complaintDuration={
      clerkingComplaintDuration
    }
    history={clerkingHistory}
    reviewOfSystems={
      clerkingReviewOfSystems
    }
    pastMedicalHistory={
      clerkingPastMedicalHistory
    }
    pastSurgicalHistory={
      clerkingPastSurgicalHistory
    }
    drugHistory={clerkingDrugHistory}
    allergies={clerkingAllergies}
    familyHistory={clerkingFamilyHistory}
    socialHistory={clerkingSocialHistory}
    personalHistory={clerkingPersonalHistory}

    ideas={clerkingIdeas}
    concerns={clerkingConcerns}
    expectations={
      clerkingExpectations
    }

    examGeneral={clerkingExamGeneral}
    examCardiovascular={
      clerkingExamCardiovascular
    }
    examRespiratory={
      clerkingExamRespiratory
    }
    examAbdomen={clerkingExamAbdomen}
    examNeurological={
      clerkingExamNeurological
    }
    examMusculoskeletal={
      clerkingExamMusculoskeletal
    }
    examGenitourinary={
      clerkingExamGenitourinary
    }
    examOther={clerkingExamOther}

    onComplaintChange={
      setClerkingComplaint
    }
    onComplaintDurationChange={
      setClerkingComplaintDuration
    }
    onHistoryChange={
      setClerkingHistory
    }
    onReviewOfSystemsChange={
      setClerkingReviewOfSystems
    }
    onPastMedicalHistoryChange={
      setClerkingPastMedicalHistory
    }
    onPastSurgicalHistoryChange={
      setClerkingPastSurgicalHistory
    }
    onDrugHistoryChange={
      setClerkingDrugHistory
    }
    onAllergiesChange={
      setClerkingAllergies
    }
    onFamilyHistoryChange={
      setClerkingFamilyHistory
    }
    onSocialHistoryChange={
      setClerkingSocialHistory
    }
    onPersonalHistoryChange={
      setClerkingPersonalHistory
    }

    onIdeasChange={
      setClerkingIdeas
    }
    onConcernsChange={
      setClerkingConcerns
    }
    onExpectationsChange={
      setClerkingExpectations
    }

    onExamGeneralChange={
      setClerkingExamGeneral
    }
    onExamCardiovascularChange={
      setClerkingExamCardiovascular
    }
    onExamRespiratoryChange={
      setClerkingExamRespiratory
    }
    onExamAbdomenChange={
      setClerkingExamAbdomen
    }
    onExamNeurologicalChange={
      setClerkingExamNeurological
    }
    onExamMusculoskeletalChange={
      setClerkingExamMusculoskeletal
    }
    onExamGenitourinaryChange={
      setClerkingExamGenitourinary
    }
    onExamOtherChange={
      setClerkingExamOther
    }

    onSave={() =>
      void saveProgressNote()
    }
    onSign={() =>
      void signProgressNote()
    }

    admitting={admittingEpisode}
    canAdmit={
      Boolean(
        progressNote &&
        progressNote.document_type ===
          'INITIAL_CLERKING' &&
        progressNote.status === 'SIGNED' &&
        selectedEpisode?.status === 'OPEN',
      )
    }
    onAdmit={() =>
      void admitSelectedEpisode()
    }
  />
) : (
  <ProgressNotePanel
    noteTitle="Progress Note"

    progressNote={progressNote}
    encounterClosed={
      selectedEncounter.status === 'CLOSED'
    }
    loading={loadingProgressNote}
    saving={savingProgressNote}
    signing={signingProgressNote}

    subjective={noteSubjective}
    objective={noteObjective}
    workingDiagnosis={
      noteWorkingDiagnosis
    }
    differentials={
      noteDifferentials
    }
    plan={notePlan}

    onSubjectiveChange={
      setNoteSubjective
    }
    onObjectiveChange={
      setNoteObjective
    }
    onWorkingDiagnosisChange={
      setNoteWorkingDiagnosis
    }
    onDifferentialsChange={
      setNoteDifferentials
    }
    onPlanChange={
      setNotePlan
    }

    onInsertLatestVitals={
      insertLatestVitals
    }
    hasVitals={
      vitals.length > 0
    }

    onSave={() =>
      void saveProgressNote()
    }
    onSign={() =>
      void signProgressNote()
    }
  />
)}

<SignedClinicalDocumentSummary
  document={progressNote}
/>

</div>
  )


  const renderInvestigationResults = () => (
<DoctorInvestigationResults
  showResults={
    selectedEncounter.title ===
      'Doctor Consultation' ||
    selectedEncounter.title ===
      'Doctor Review' ||
    selectedEncounter.title ===
      'Ward Review'
  }
  loadingClinicalResults={
    loadingClinicalResults
  }
  clinicalResults={clinicalResults}
  diagnosticReports={
    diagnosticReports
  }
  diagnosticAttachments={
    diagnosticAttachments
  }
  orders={orders}
/>
  )


  const renderOrders = () => (
<ClinicalOrdersPanel
  orders={orders}
  clinicalResults={clinicalResults}
  loading={loadingOrders}
  saving={savingOrder}
  cancellingOrderId={
    cancellingOrderId
  }
  encounterClosed={
    selectedEncounter.status === 'CLOSED'
  }
  inpatientMedication={
    selectedEpisode?.status === 'ADMITTED'
  }

  inpatientTreatmentStart={
    inpatientTreatmentStart
  }

  inpatientFirstDose={
    inpatientFirstDose
  }

  onInpatientTreatmentStartChange={
    setInpatientTreatmentStart
  }

  onInpatientFirstDoseChange={
    setInpatientFirstDose
  }



  orderType={orderType}

  orderPriority={orderPriority}

  laboratoryTests={
    laboratoryTests
  }
  selectedLaboratoryTestId={
    selectedLaboratoryTestId
  }
  diagnosticInvestigations={
    diagnosticInvestigations
  }
  selectedDiagnosticInvestigationId={
    selectedDiagnosticInvestigationId
  }
  orderTestCode={
    orderTestCode
  }
  orderTestName={
    orderTestName
  }
  orderMedicationId={
    orderMedicationId
  }
  orderDose={
    orderDose
  }

  prescriptionMedicine={
    prescriptionMedicine
  }
  prescriptionStrength={
    prescriptionStrength
  }
  prescriptionDoseUnit={
    prescriptionDoseUnit
  }
  prescriptionRoute={
    prescriptionRoute
  }
  prescriptionFrequency={
    prescriptionFrequency
  }
  prescriptionDuration={
    prescriptionDuration
  }
  prescriptionDurationUnit={
    prescriptionDurationUnit
  }
  prescriptionQuantity={
    prescriptionQuantity
  }
  prescriptionDirections={
    prescriptionDirections
  }
  prescriptionIndication={
    prescriptionIndication
  }

  onOrderTypeChange={
    setOrderType
  }
  onOrderPriorityChange={
    setOrderPriority
  }
  onLaboratoryTestChange={
    handleLaboratoryTestChange
  }
  onDiagnosticInvestigationChange={
    handleDiagnosticInvestigationChange
  }
  onOrderTestCodeChange={
    setOrderTestCode
  }
  onOrderTestNameChange={
    setOrderTestName
  }
  onOrderMedicationIdChange={
    setOrderMedicationId
  }
  onOrderDoseChange={
    setOrderDose
  }

  onPrescriptionMedicineChange={
    setPrescriptionMedicine
  }
  onPrescriptionStrengthChange={
    setPrescriptionStrength
  }
  onPrescriptionDoseUnitChange={
    setPrescriptionDoseUnit
  }
  onPrescriptionRouteChange={
    setPrescriptionRoute
  }
  onPrescriptionFrequencyChange={
    setPrescriptionFrequency
  }
  onPrescriptionDurationChange={
    setPrescriptionDuration
  }
  onPrescriptionDurationUnitChange={
    setPrescriptionDurationUnit
  }
  onPrescriptionQuantityChange={
    setPrescriptionQuantity
  }
  onPrescriptionDirectionsChange={
    setPrescriptionDirections
  }
  onPrescriptionIndicationChange={
    setPrescriptionIndication
  }

  onSave={() =>
    void saveOrder()
  }

  onCancel={orderId =>
    void cancelOrder(orderId)
  }
/>
  )


  const renderTimeline = () => (
<section className="workspace-panel doctor-timeline-panel">
  <details>
    <summary className="doctor-context-summary">
      <div>
        <p className="eyebrow">
          CARE CONTEXT
        </p>

        <h2>
          Timeline
        </h2>

        <p>
          Clinical events recorded for this encounter.
        </p>
      </div>

      <div className="doctor-context-summary-meta">
        <span>
          {timeline.length}
          {' '}
          event
          {timeline.length === 1
            ? ''
            : 's'}
        </span>
      </div>
    </summary>

    <div className="doctor-context-body">
      {loadingTimeline && (
        <p>
          Loading clinical timeline...
        </p>
      )}

      {!loadingTimeline &&
        timeline.length === 0 && (
          <p>
            No clinical events recorded yet.
          </p>
        )}

      {!loadingTimeline &&
        timeline.length > 0 && (
          <div className="doctor-timeline-list">
            {timeline.map(event => (
              <div
                key={event.id}
                className="doctor-timeline-item"
              >
                <strong>
                  {formatEventLabel(
                    event.event_type,
                  )}
                </strong>

                <span>
                  {new Date(
                    event.occurred_at,
                  ).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        )}
    </div>
  </details>
</section>
  )

  return (
    <>
<section
  className={`doctor-encounter-mode ${
    isWardReview
      ? 'doctor-encounter-mode--ward'
      : 'doctor-encounter-mode--clinic'
  }`}
>
  <div>
    <p className="eyebrow">
      {isWardReview
        ? 'WARD REVIEW'
        : 'DOCTOR CONSULTATION'}
    </p>

    <h1>
      {isWardReview
        ? 'Daily inpatient review'
        : 'Outpatient consultation'}
    </h1>

    <p>
      {isWardReview
        ? 'Assess the patient’s current condition and ongoing care.'
        : 'Assess the presenting problem, establish the diagnosis, and plan care.'}
    </p>
  </div>

  <span className="doctor-encounter-mode-badge">
    {selectedEncounter.status === 'OPEN'
      ? 'Active'
      : 'Closed'}
  </span>
</section>

<section className={`doctor-patient-banner ${
  isWardReview
    ? 'doctor-patient-banner--ward'
    : 'doctor-patient-banner--clinic'
}`}>
  {loadingPatientContext ? (
    <div className="doctor-patient-banner-loading">
      Loading patient information...
    </div>
  ) : patient ? (
    <>
      <div className="doctor-patient-identity">
        <div className="doctor-patient-avatar">
          {patient.first_name.charAt(0)}
          {patient.last_name.charAt(0)}
        </div>

        <div>
          <p className="eyebrow">
            PATIENT
          </p>

          <h2>
            {patient.first_name}{' '}
            {patient.middle_name
              ? `${patient.middle_name} `
              : ''}
            {patient.last_name}
          </h2>

          <p>
            {patient.hospital_number}
          </p>
        </div>
      </div>

      <div className="doctor-patient-details">
        <div>
          <span>Date of birth</span>
          <strong>
            {patient.date_of_birth}
          </strong>
        </div>

        <div>
          <span>Sex</span>
          <strong>
            {patient.sex}
          </strong>
        </div>

        {selectedEpisode && (
          <div>
            <span>Episode</span>
            <strong>
              {selectedEpisode.episode_number}
            </strong>
          </div>
        )}

        {selectedEpisode && (
          <div>
            <span>Status</span>
            <strong>
              {selectedEpisode.status}
            </strong>
          </div>
        )}
      </div>
    </>
  ) : (
    <div className="doctor-patient-banner-loading">
      Patient information unavailable.
    </div>
  )}
</section>

<PatientHistoryPanel
  currentEpisode={
    selectedEpisode
  }

  previousEpisodes={
    previousEpisodes
  }

  selectedEpisode={
    historicalEpisode
  }

  currentEpisodeEncounters={
    currentEpisodeEncounters
  }

  historicalEncounters={
    historicalEncounters
  }

  selectedHistoricalEncounter={
    selectedHistoricalEncounter
  }

  loadingCurrentEncounters={
    loadingPatientContext
  }

  loadingPreviousEpisodes={
    loadingPreviousEpisodes
  }

  loadingHistorical={
    loadingHistorical
  }

  onSelectCurrentEncounter={
    encounter => {
      if (
        encounter.id ===
        selectedEncounter?.id
      ) {
        return
      }

      if (!selectedEpisode) {
        return
      }

      void openHistoricalEncounter(
        selectedEpisode,
        encounter,
      )
    }
  }

  onSelectPreviousEpisode={
    episode =>
      void openHistoricalEpisode(
        episode,
      )
  }

  onSelectHistoricalEncounter={
    encounter => {
      if (!historicalEpisode) {
        return
      }

      void openHistoricalEncounter(
        historicalEpisode,
        encounter,
      )
    }
  }
/>

<HistoricalEncounterPanel
  episode={historicalEpisode}
  encounter={
    selectedHistoricalEncounter
  }
  documents={historicalDocuments}
  diagnoses={historicalDiagnoses}
  orders={historicalOrders}
  vitals={historicalVitals}
  timeline={historicalTimeline}
  loading={loadingHistorical}
  onCloseHistory={
    closeHistoricalViewer
  }
/>

<div className="doctor-vitals-section">
  <VitalsPanel
  vitals={vitals}
  nursingVitals={nursingVitals}
  saving={savingVitals}
  encounterClosed={
    selectedEncounter.status === 'CLOSED'
  }
  temperature={temperature}
  heartRate={heartRate}
  respiratoryRate={respiratoryRate}
  systolicBp={systolicBp}
  diastolicBp={diastolicBp}
  spo2={spo2}
  weight={weight}
  onTemperatureChange={
    setTemperature
  }
  onHeartRateChange={
    setHeartRate
  }
  onRespiratoryRateChange={
    setRespiratoryRate
  }
  onSystolicBpChange={
    setSystolicBp
  }
  onDiastolicBpChange={
    setDiastolicBp
  }
  onSpo2Change={
    setSpo2
  }
  onWeightChange={
    setWeight
  }
  onSave={() =>
    void saveVitals()
  }
/>

</div>

{isWardReview ? (
  <>
    {renderDiagnosis()}

    <NursingHandoffPanel
      encounter={nursingEncounter}
      document={nursingDocument}
      loading={loadingNursingHandoff}
    />

    {selectedEpisode && (
      <DoctorMedicationTreatmentReview
        accessToken={accessToken}
        episodeId={selectedEpisode.id}
      />
    )}

    {renderInvestigationResults()}

    {renderTimeline()}

    {renderDocumentation()}

    {renderOrders()}
  </>
) : (
  <>
    {renderDocumentation()}

    {renderDiagnosis()}

    {renderOrders()}

    {renderInvestigationResults()}
  </>
)}

{selectedEncounter.title ===
  'Ward Review' &&
  selectedEncounter.status ===
    'OPEN' && (
    <section className="workspace-panel">
      <div className="panel-header">
        <div>
          <h2>
            Complete Ward Review
          </h2>
          <p>
            Record the patient's disposition after
            documentation, review, and clinical actions
            are finished.
          </p>
        </div>
      </div>

      <div className="doctor-note-field">
        <label>
          <span>Disposition</span>

          <select
            value={wardReviewDisposition}
            disabled={closingEncounter}
            onChange={event => {
              const disposition =
                event.target.value as WardReviewDisposition

              setWardReviewDisposition(
                disposition,
              )

              if (
                disposition !== 'TRANSFER' &&
                disposition !== 'REFERRAL' &&
                disposition !== 'OTHER'
              ) {
                setWardReviewDetails('')
              }
            }}
          >
            <option value="CONTINUE_ADMISSION">
              Continue admission
            </option>

            <option value="DISCHARGE">
              Discharge
            </option>

            <option value="TRANSFER">
              Transfer
            </option>

            <option value="REFERRAL">
              Referral
            </option>

            <option value="OTHER">
              Other
            </option>
          </select>
        </label>
      </div>

      {wardReviewDetailsRequired && (
        <div className="doctor-note-field">
          <label>
            <span>Details</span>

            <textarea
              rows={5}
              value={wardReviewDetails}
              disabled={closingEncounter}
              onChange={event =>
                setWardReviewDetails(
                  event.target.value,
                )
              }
              placeholder={
                wardReviewDisposition === 'TRANSFER'
                  ? 'Receiving facility, service, or transfer details.'
                  : wardReviewDisposition === 'REFERRAL'
                    ? 'Referral destination, specialty, or referral details.'
                    : 'Provide details for this disposition.'
              }
            />
          </label>
        </div>
      )}

      <button
        type="button"
        disabled={
          closingEncounter ||
          !wardReviewReady
        }
        onClick={() =>
          void completeWardReview(
            wardReviewDisposition,
            wardReviewDetailsRequired
              ? wardReviewDetails.trim()
              : null,
          )
        }
      >
        {closingEncounter
          ? 'Completing...'
          : 'Complete Ward Review'}
      </button>
    </section>
  )}

{selectedEncounter.title ===
  'Doctor Consultation' &&
  selectedEncounter.status ===
    'OPEN' &&
  selectedEpisode?.status ===
    'OPEN' &&
  progressNote?.document_type ===
    'INITIAL_CLERKING' &&
  progressNote.status ===
    'SIGNED' && (
    <section className="workspace-panel">
      <div className="panel-header">
        <div>
          <h2>
            Consultation Completion
          </h2>

          <p>
            Complete this consultation while keeping the episode open for investigation and review.
          </p>
        </div>
      </div>

      <button
        type="button"
        disabled={
          completingConsultation ||
          progressNote?.document_type !==
            'INITIAL_CLERKING' ||
          progressNote.status !==
            'SIGNED'
        }
        onClick={() =>
          void handleCompleteConsultation()
        }
      >
        {completingConsultation
          ? 'Completing...'
          : 'Complete Consultation'}
      </button>
    </section>
  )}

{selectedEncounter.title ===
  'Doctor Review' &&
  selectedEncounter.status ===
    'OPEN' &&
  selectedEpisode?.status ===
    'OPEN' && (
    <section className="workspace-panel">
      <div className="panel-header">
        <div>
          <h2>
            Doctor Review Completion
          </h2>

          <p>
            Complete this review after documenting the assessment, results, and clinical plan.
          </p>
        </div>
      </div>

      <button
        type="button"
        disabled={
          completingDoctorReview
        }
        onClick={() =>
          void handleCompleteDoctorReview()
        }
      >
        {completingDoctorReview
          ? 'Completing...'
          : 'Complete Doctor Review'}
      </button>
    </section>
  )}

    </>
  )
}
