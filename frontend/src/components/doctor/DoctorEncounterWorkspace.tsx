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
import NursingHandoffPanel from './NursingHandoffPanel'
import PatientHistoryPanel from './PatientHistoryPanel'
import DoctorPatientBanner from './DoctorPatientBanner'
import DoctorEncounterNavigation from './DoctorEncounterNavigation'
import DoctorDocumentationPanel from './DoctorDocumentationPanel'
import DoctorEncounterTimeline from './DoctorEncounterTimeline'
import DoctorEncounterCompletionPanels from './DoctorEncounterCompletionPanels'
import type { WardReviewDisposition } from './DoctorEncounterCompletionPanels'
import VitalsPanel from './VitalsPanel'
import DoctorMedicationTreatmentReview from './DoctorMedicationTreatmentReview'
import type { useDoctorDocumentation } from './useDoctorDocumentation'

type StringChangeHandler = (
  value: string,
) => void

type AsyncAction = () => Promise<void>


type CompleteWardReviewAction = (
  disposition: WardReviewDisposition,
  details: string | null,
) => Promise<void>

interface Props {
  selectedEncounter: Encounter
  selectedEpisode: Episode | null
  accessToken: string
  onBackToQueue: () => void
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
  onSelectCurrentEncounter: (
    encounter: Encounter,
  ) => void

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
  manualDiagnosis: string
  diagnosisSearchPerformed: boolean
  diagnosisType: DiagnosisType
  certainty: DiagnosisCertainty
  searchDiagnoses: (
    query: string,
  ) => Promise<void>
  enterManualDiagnosis: () => void
  exitManualDiagnosis: () => void
  setManualDiagnosis: StringChangeHandler
  selectDiagnosis: (
    concept: TerminologyConcept,
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
  selectedLaboratoryTestIds: string[]
  customLaboratoryInvestigation: string
  diagnosticInvestigations: DiagnosticInvestigation[]
  selectedDiagnosticInvestigationId: string
  customDiagnosticInvestigation: string
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
  setCustomLaboratoryInvestigation: StringChangeHandler
  handleDiagnosticInvestigationChange: StringChangeHandler
  setCustomDiagnosticInvestigation: StringChangeHandler
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

export default function DoctorEncounterWorkspace({
  selectedEncounter,
  accessToken,
  selectedEpisode,
  onBackToQueue,
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
  onSelectCurrentEncounter,
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
  manualDiagnosis,
  diagnosisSearchPerformed,
  diagnosisType,
  certainty,
  searchDiagnoses,
  enterManualDiagnosis,
  exitManualDiagnosis,
  setManualDiagnosis,
  selectDiagnosis,
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
  selectedLaboratoryTestIds,
  customLaboratoryInvestigation,
  diagnosticInvestigations,
  selectedDiagnosticInvestigationId,
  customDiagnosticInvestigation,
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
  setCustomLaboratoryInvestigation,
  handleDiagnosticInvestigationChange,
  setCustomDiagnosticInvestigation,
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
  const isDoctorReview =
    selectedEncounter.title === 'Doctor Review'

  const isWardReview =
    selectedEncounter.title === 'Ward Review'

  const encounterMode = isWardReview
    ? {
        eyebrow: 'WARD REVIEW',
        title: 'Daily inpatient review',
        description:
          'Assess the patient’s current condition and ongoing care.',
        className: 'doctor-encounter-mode--ward',
      }
    : isDoctorReview
      ? {
          eyebrow: 'DOCTOR REVIEW',
          title: 'Post-investigation review',
          description:
            'Review investigation results, reassess the patient, and finalize the clinical plan.',
          className: 'doctor-encounter-mode--review',
        }
      : {
          eyebrow: 'DOCTOR CONSULTATION',
          title: 'Outpatient consultation',
          description:
            'Assess the presenting problem, establish the diagnosis, and plan care.',
          className: 'doctor-encounter-mode--clinic',
        }

  const [wardReviewDisposition, setWardReviewDisposition] =
    useState<WardReviewDisposition>(
      'CONTINUE_ADMISSION',
    )

  const [wardReviewDetails, setWardReviewDetails] =
    useState('')

  type DoctorTab = 'OVERVIEW' | 'DOCUMENTATION' | 'ASSESSMENT' | 'ORDERS' | 'RESULTS' | 'HISTORY'

  const [activeTab, setActiveTab] =
    useState<DoctorTab>('OVERVIEW')

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
  manualDiagnosis={manualDiagnosis}
  diagnosisSearchPerformed={diagnosisSearchPerformed}

  diagnosisType={diagnosisType}
  certainty={certainty}

  onQueryChange={value =>
    void searchDiagnoses(value)
  }

  onSelect={
    selectDiagnosis
  }

  onEnterManualDiagnosis={
    enterManualDiagnosis
  }

  onExitManualDiagnosis={
    exitManualDiagnosis
  }

  onManualDiagnosisChange={
    setManualDiagnosis
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
    <DoctorDocumentationPanel
      documentation={documentation}
      progressNote={progressNote}
      selectedEncounter={selectedEncounter}
      selectedEpisode={selectedEpisode}
      loadingProgressNote={loadingProgressNote}
      savingProgressNote={savingProgressNote}
      signingProgressNote={signingProgressNote}
      admittingEpisode={admittingEpisode}
      vitalsCount={vitals.length}
      insertLatestVitals={insertLatestVitals}
      saveProgressNote={saveProgressNote}
      signProgressNote={signProgressNote}
      admitSelectedEpisode={admitSelectedEpisode}
    />
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
  selectedLaboratoryTestIds={
    selectedLaboratoryTestIds
  }
  diagnosticInvestigations={
    diagnosticInvestigations
  }
  selectedDiagnosticInvestigationId={
    selectedDiagnosticInvestigationId
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
  customLaboratoryInvestigation={
    customLaboratoryInvestigation
  }
  onCustomLaboratoryInvestigationChange={
    setCustomLaboratoryInvestigation
  }
  onDiagnosticInvestigationChange={
    handleDiagnosticInvestigationChange
  }
  customDiagnosticInvestigation={
    customDiagnosticInvestigation
  }
  onCustomDiagnosticInvestigationChange={
    setCustomDiagnosticInvestigation
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
    <DoctorEncounterTimeline
      timeline={timeline}
      loadingTimeline={loadingTimeline}
    />
  )

  return (
    <>
<DoctorEncounterNavigation
  onBackToQueue={onBackToQueue}
/>

<section
  className={`doctor-encounter-mode ${encounterMode.className}`}
>
  <div>
    <p className="eyebrow">
      {encounterMode.eyebrow}
    </p>

    <h1>
      {encounterMode.title}
    </h1>

    <p>
      {encounterMode.description}
    </p>
  </div>

  <span className="doctor-encounter-mode-badge">
    {selectedEncounter.status === 'OPEN'
      ? 'Active'
      : 'Closed'}
  </span>
</section>

<DoctorPatientBanner
  patient={patient}
  loadingPatientContext={loadingPatientContext}
  selectedEpisode={selectedEpisode}
  isWardReview={isWardReview}
/>

<div className="doctor-workspace-tabs" role="tablist" aria-label="Patient chart sections">
  {([
    ['OVERVIEW', 'Overview'],
    ['DOCUMENTATION', 'Notes'],
    ['ASSESSMENT', 'Assessment'],
    ['ORDERS', 'Orders'],
    ['RESULTS', 'Results'],
    ['HISTORY', 'History'],
  ] as const).map(([key, label]) => (
    <button
      key={key}
      type="button"
      role="tab"
      aria-selected={activeTab === key}
      className={activeTab === key ? 'doctor-workspace-tab active' : 'doctor-workspace-tab'}
      onClick={() => setActiveTab(key)}
    >
      {label}
    </button>
  ))}
</div>

<div className="doctor-tab-content">
  {activeTab === 'OVERVIEW' && (
    <div className="doctor-overview-grid">
      <div className="doctor-vitals-section">
        <VitalsPanel
          vitals={vitals}
          nursingVitals={nursingVitals}
          saving={savingVitals}
          encounterClosed={selectedEncounter.status === 'CLOSED'}
          temperature={temperature}
          heartRate={heartRate}
          respiratoryRate={respiratoryRate}
          systolicBp={systolicBp}
          diastolicBp={diastolicBp}
          spo2={spo2}
          weight={weight}
          onTemperatureChange={setTemperature}
          onHeartRateChange={setHeartRate}
          onRespiratoryRateChange={setRespiratoryRate}
          onSystolicBpChange={setSystolicBp}
          onDiastolicBpChange={setDiastolicBp}
          onSpo2Change={setSpo2}
          onWeightChange={setWeight}
          onSave={() => void saveVitals()}
        />
      </div>

      {renderDiagnosis()}

      {isWardReview && (
        <NursingHandoffPanel
          encounter={nursingEncounter}
          document={nursingDocument}
          loading={loadingNursingHandoff}
        />
      )}

      {isWardReview && selectedEpisode && (
        <DoctorMedicationTreatmentReview
          accessToken={accessToken}
          episodeId={selectedEpisode.id}
        />
      )}

      {renderTimeline()}
    </div>
  )}

  {activeTab === 'DOCUMENTATION' && renderDocumentation()}
  {activeTab === 'ASSESSMENT' && renderDiagnosis()}
  {activeTab === 'ORDERS' && renderOrders()}
  {activeTab === 'RESULTS' && renderInvestigationResults()}

  {activeTab === 'HISTORY' && (
    <>
      <PatientHistoryPanel
        currentEpisode={selectedEpisode}
        previousEpisodes={previousEpisodes}
        selectedEpisode={historicalEpisode}
        currentEpisodeEncounters={currentEpisodeEncounters}
        historicalEncounters={historicalEncounters}
        selectedHistoricalEncounter={selectedHistoricalEncounter}
        loadingCurrentEncounters={loadingPatientContext}
        loadingPreviousEpisodes={loadingPreviousEpisodes}
        loadingHistorical={loadingHistorical}
        onSelectCurrentEncounter={encounter => {
          onSelectCurrentEncounter(encounter)
        }}
        onSelectPreviousEpisode={episode => void openHistoricalEpisode(episode)}
        onSelectHistoricalEncounter={encounter => {
          if (!historicalEpisode) return
          void openHistoricalEncounter(historicalEpisode, encounter)
        }}
      />

      <HistoricalEncounterPanel
        episode={historicalEpisode}
        encounter={selectedHistoricalEncounter}
        documents={historicalDocuments}
        diagnoses={historicalDiagnoses}
        orders={historicalOrders}
        vitals={historicalVitals}
        timeline={historicalTimeline}
        loading={loadingHistorical}
        onCloseHistory={closeHistoricalViewer}
      />
    </>
  )}
</div>

<DoctorEncounterCompletionPanels
  isWardReview={isWardReview}
  selectedEncounter={selectedEncounter}
  selectedEpisode={selectedEpisode}
  progressNote={progressNote}
  closingEncounter={closingEncounter}
  wardReviewDisposition={wardReviewDisposition}
  setWardReviewDisposition={setWardReviewDisposition}
  wardReviewDetails={wardReviewDetails}
  setWardReviewDetails={setWardReviewDetails}
  wardReviewDetailsRequired={wardReviewDetailsRequired}
  wardReviewReady={wardReviewReady}
  completeWardReview={completeWardReview}
  completingConsultation={completingConsultation}
  handleCompleteConsultation={handleCompleteConsultation}
  completingDoctorReview={completingDoctorReview}
  handleCompleteDoctorReview={handleCompleteDoctorReview}
/>


    </>
  )
}
