import {
  useState,
} from 'react'

import {
  useDoctorEpisodeActions,
} from './useDoctorEpisodeActions'


import {
  createEncounter,
  listEpisodeEncounters,
  type Encounter,
} from '../../api/encounters'

import {
  completeConsultation,
  completeDoctorReview,
  getEpisode,
  type DoctorQueueItem,
  type Episode,
} from '../../api/episodes'

import {
  getPatient,
} from '../../api/patients'








import {
  type Vitals,
} from '../../api/vitals'

import DoctorEncounterWorkspace from './DoctorEncounterWorkspace'
import { useDoctorDocumentation } from './useDoctorDocumentation'
import {
  useDoctorClinicalDocumentation,
} from './useDoctorClinicalDocumentation'
import { useDoctorDiagnosis } from './useDoctorDiagnosis'
import { useDoctorVitals } from './useDoctorVitals'
import { useDoctorEncounterContext } from './useDoctorEncounterContext'
import { useDoctorPatientContext } from './useDoctorPatientContext'
import { useDoctorQueue } from './useDoctorQueue'
import { useDoctorDiagnosisSearch } from './useDoctorDiagnosisSearch'
import { useDoctorOrders } from './useDoctorOrders'
import { useDoctorNursingHandoff } from './useDoctorNursingHandoff'
import { useDoctorInvestigationCatalogues } from './useDoctorInvestigationCatalogues'
import { useDoctorHistory } from './useDoctorHistory'

interface Props {
  accessToken: string
}


function formatVitalsForObjective(
  vital: Vitals,
): string {
  const payload = vital.payload

  const parts: string[] = []

  if (payload.temperature != null) {
    parts.push(
      `Temp ${payload.temperature} °C`,
    )
  }

  if (payload.heart_rate != null) {
    parts.push(
      `HR ${payload.heart_rate} bpm`,
    )
  }

  if (
    payload.systolic_bp != null ||
    payload.diastolic_bp != null
  ) {
    const systolic =
      payload.systolic_bp != null
        ? payload.systolic_bp
        : '—'

    const diastolic =
      payload.diastolic_bp != null
        ? payload.diastolic_bp
        : '—'

    parts.push(
      `BP ${systolic}/${diastolic} mmHg`,
    )
  }

  if (payload.respiratory_rate != null) {
    parts.push(
      `RR ${payload.respiratory_rate}/min`,
    )
  }

  if (payload.spo2 != null) {
    parts.push(
      `SpO₂ ${payload.spo2}%`,
    )
  }

  if (payload.weight != null) {
    parts.push(
      `Wt ${payload.weight} kg`,
    )
  }

  return parts.join(' · ')
}


export default function DoctorWorkspace({
  accessToken,
}: Props) {


  const {
    selectedEncounter,
    setSelectedEncounter,
    resetEncounterContext,
    refreshEncounterData,
    diagnoses,
    timeline,
    loadingTimeline,
    loadingDiagnoses,
    orders,
    vitals,
    clinicalResults,
    diagnosticReports,
    diagnosticAttachments,
    loadingClinicalResults,
    loadingOrders,
  } = useDoctorEncounterContext(
    accessToken,
  )

  const [error, setError] =
    useState<string | null>(null)

  const [success, setSuccess] =
    useState<string | null>(null)

  const [selectedEpisode, setSelectedEpisode] =
    useState<Episode | null>(null)

  const {
    currentEpisodeEncounters,
    setCurrentEpisodeEncounters,

    patient,
    setPatient,

    loadingPatientContext,
    setLoadingPatientContext,

    previousEpisodes,
    setPreviousEpisodes,

    loadingPreviousEpisodes,

    loadPreviousPatientEpisodes,
  } = useDoctorPatientContext({
    accessToken,
    onError: setError,
  })

  const {
    diagnosisQuery,
    setDiagnosisQuery,
    diagnosisResults,
    setDiagnosisResults,
    selectedDiagnosis,
    setSelectedDiagnosis,
    searchDiagnoses,
  } = useDoctorDiagnosisSearch({
    accessToken,
    onError: setError,
  })

  const {
    diagnosisType,
    setDiagnosisType,
    certainty,
    setCertainty,
    savingDiagnosis,
    saveDiagnosis,
  } = useDoctorDiagnosis({
    accessToken,
    selectedEncounter,
    selectedDiagnosis,
    refreshEncounterContext,
    resetDiagnosisSearch: () => {
      setDiagnosisQuery('')
      setDiagnosisResults([])
      setSelectedDiagnosis(null)
    },
    onError: setError,
    onSuccess: setSuccess,
  })

  const {
    nursingEncounter,
    nursingDocument,
    nursingVitals,
    loadingNursingHandoff,
    resetNursingHandoff,
    loadNursingHandoff,
  } = useDoctorNursingHandoff({
    accessToken,
    onError: setError,
  })

  const {
    laboratoryTests,
    diagnosticInvestigations,
  } = useDoctorInvestigationCatalogues({
    accessToken,
    onError: setError,
  })

  const {
    clinicQueue,
    wardQueue,
    currentStaffId,
    refreshDoctorQueues,
  } = useDoctorQueue({
    accessToken,
  })

  const {
    savingOrder,
    cancellingOrderId,

    orderType,
    setOrderType,
    orderPriority,
    setOrderPriority,

    selectedLaboratoryTestId,
    selectedDiagnosticInvestigationId,

    orderTestCode,
    setOrderTestCode,
    orderTestName,
    setOrderTestName,
    orderMedicationId,
    setOrderMedicationId,
    orderDose,
    setOrderDose,

    prescriptionMedicine,
    setPrescriptionMedicine,
    prescriptionStrength,
    setPrescriptionStrength,
    prescriptionDoseUnit,
    setPrescriptionDoseUnit,
    prescriptionRoute,
    setPrescriptionRoute,
    prescriptionFrequency,
    setPrescriptionFrequency,

    inpatientTreatmentStart,
    setInpatientTreatmentStart,
    inpatientFirstDose,
    setInpatientFirstDose,

    prescriptionDuration,
    setPrescriptionDuration,
    prescriptionDurationUnit,
    setPrescriptionDurationUnit,
    prescriptionQuantity,
    setPrescriptionQuantity,
    prescriptionDirections,
    setPrescriptionDirections,
    prescriptionIndication,
    setPrescriptionIndication,

    handleLaboratoryTestChange,
    handleDiagnosticInvestigationChange,
    saveOrder,
    cancelOrder,
  } = useDoctorOrders({
    accessToken,
    selectedEpisode,
    selectedEncounter,
    laboratoryTests,
    diagnosticInvestigations,
    refreshEncounterContext,
    onError: setError,
    onSuccess: setSuccess,
    clearError: () => setError(null),
    clearSuccess: () => setSuccess(null),
  })

  const {
    historicalEpisode,
    historicalEncounters,
    selectedHistoricalEncounter,
    historicalDocuments,
    historicalDiagnoses,
    historicalOrders,
    historicalVitals,
    historicalTimeline,
    loadingHistorical,
    openHistoricalEncounter,
    openHistoricalEpisode,
    closeHistoricalViewer,
  } = useDoctorHistory({
    accessToken,
    onError: setError,
    clearError: () => setError(null),
  })

  const documentation =
    useDoctorDocumentation(
      selectedEpisode?.status,
    )

  const clinicalDocumentation =
    useDoctorClinicalDocumentation({
      accessToken,
      currentStaffId,
      selectedEncounter,
      documentation,
      refreshEncounterData,
      onError: setError,
      onSuccess: setSuccess,
    })


  const {
    savingVitals,

    temperature,
    setTemperature,

    heartRate,
    setHeartRate,

    respiratoryRate,
    setRespiratoryRate,

    systolicBp,
    setSystolicBp,

    diastolicBp,
    setDiastolicBp,

    spo2,
    setSpo2,

    weight,
    setWeight,

    saveVitals,
  } = useDoctorVitals({
    accessToken,
    selectedEncounter,
    refreshEncounterContext,
    onError: setError,
    onSuccess: setSuccess,
  })


  const {
    progressNote,
    initialClerking,
    progressNoteForm,
  } = documentation

  const {
    loadingProgressNote,
    savingProgressNote,
    signingProgressNote,
    saveProgressNote,
    signProgressNote,
  } = clinicalDocumentation


  const noteSubjective =
    progressNoteForm.subjective

  const noteObjective =
    progressNoteForm.objective

  const noteWorkingDiagnosis =
    progressNoteForm.workingDiagnosis

  const noteDifferentials =
    progressNoteForm.differentials

  const notePlan =
    progressNoteForm.plan

  const clerkingComplaint =
    initialClerking.complaint

  const clerkingComplaintDuration =
    initialClerking.complaintDuration

  const clerkingHistory =
    initialClerking.history

  const clerkingReviewOfSystems =
    initialClerking.reviewOfSystems

  const clerkingPastMedicalHistory =
    initialClerking.pastMedicalHistory

  const clerkingPastSurgicalHistory =
    initialClerking.pastSurgicalHistory

  const clerkingDrugHistory =
    initialClerking.drugHistory

  const clerkingAllergies =
    initialClerking.allergies

  const clerkingFamilyHistory =
    initialClerking.familyHistory

  const clerkingSocialHistory =
    initialClerking.socialHistory

  const clerkingPersonalHistory =
    initialClerking.personalHistory

  const clerkingIdeas =
    initialClerking.ideas

  const clerkingConcerns =
    initialClerking.concerns

  const clerkingExpectations =
    initialClerking.expectations

  const clerkingExamGeneral =
    initialClerking.examGeneral

  const clerkingExamCardiovascular =
    initialClerking.examCardiovascular

  const clerkingExamRespiratory =
    initialClerking.examRespiratory

  const clerkingExamAbdomen =
    initialClerking.examAbdomen

  const clerkingExamNeurological =
    initialClerking.examNeurological

  const clerkingExamMusculoskeletal =
    initialClerking.examMusculoskeletal

  const clerkingExamGenitourinary =
    initialClerking.examGenitourinary

  const clerkingExamOther =
    initialClerking.examOther

  const setClerkingComplaint =
    (value: string) =>
      documentation.updateInitialClerking(
        'complaint',
        value,
      )

  const setClerkingComplaintDuration =
    (value: string) =>
      documentation.updateInitialClerking(
        'complaintDuration',
        value,
      )

  const setClerkingHistory =
    (value: string) =>
      documentation.updateInitialClerking(
        'history',
        value,
      )

  const setClerkingReviewOfSystems =
    (value: string) =>
      documentation.updateInitialClerking(
        'reviewOfSystems',
        value,
      )

  const setClerkingPastMedicalHistory =
    (value: string) =>
      documentation.updateInitialClerking(
        'pastMedicalHistory',
        value,
      )

  const setClerkingPastSurgicalHistory =
    (value: string) =>
      documentation.updateInitialClerking(
        'pastSurgicalHistory',
        value,
      )

  const setClerkingDrugHistory =
    (value: string) =>
      documentation.updateInitialClerking(
        'drugHistory',
        value,
      )

  const setClerkingAllergies =
    (value: string) =>
      documentation.updateInitialClerking(
        'allergies',
        value,
      )

  const setClerkingFamilyHistory =
    (value: string) =>
      documentation.updateInitialClerking(
        'familyHistory',
        value,
      )

  const setClerkingSocialHistory =
    (value: string) =>
      documentation.updateInitialClerking(
        'socialHistory',
        value,
      )

  const setClerkingPersonalHistory =
    (value: string) =>
      documentation.updateInitialClerking(
        'personalHistory',
        value,
      )

  const setClerkingIdeas =
    (value: string) =>
      documentation.updateInitialClerking(
        'ideas',
        value,
      )

  const setClerkingConcerns =
    (value: string) =>
      documentation.updateInitialClerking(
        'concerns',
        value,
      )

  const setClerkingExpectations =
    (value: string) =>
      documentation.updateInitialClerking(
        'expectations',
        value,
      )

  const setClerkingExamGeneral =
    (value: string) =>
      documentation.updateInitialClerking(
        'examGeneral',
        value,
      )

  const setClerkingExamCardiovascular =
    (value: string) =>
      documentation.updateInitialClerking(
        'examCardiovascular',
        value,
      )

  const setClerkingExamRespiratory =
    (value: string) =>
      documentation.updateInitialClerking(
        'examRespiratory',
        value,
      )

  const setClerkingExamAbdomen =
    (value: string) =>
      documentation.updateInitialClerking(
        'examAbdomen',
        value,
      )

  const setClerkingExamNeurological =
    (value: string) =>
      documentation.updateInitialClerking(
        'examNeurological',
        value,
      )

  const setClerkingExamMusculoskeletal =
    (value: string) =>
      documentation.updateInitialClerking(
        'examMusculoskeletal',
        value,
      )

  const setClerkingExamGenitourinary =
    (value: string) =>
      documentation.updateInitialClerking(
        'examGenitourinary',
        value,
      )

  const setClerkingExamOther =
    (value: string) =>
      documentation.updateInitialClerking(
        'examOther',
        value,
      )

  const setNoteSubjective =
    (value: string) =>
      documentation.updateProgressNote(
        'subjective',
        value,
      )

  const setNoteObjective =
    (value: string) =>
      documentation.updateProgressNote(
        'objective',
        value,
      )

  const setNoteWorkingDiagnosis =
    (value: string) =>
      documentation.updateProgressNote(
        'workingDiagnosis',
        value,
      )

  const setNoteDifferentials =
    (value: string) =>
      documentation.updateProgressNote(
        'differentials',
        value,
      )

  const setNotePlan =
    (value: string) =>
      documentation.updateProgressNote(
        'plan',
        value,
      )






    const [completingConsultation, setCompletingConsultation] =
      useState(false)

    const [completingDoctorReview, setCompletingDoctorReview] =
      useState(false)


















  async function openDoctorQueueItem(
    item: DoctorQueueItem,
    mode: 'CLINIC' | 'WARD',
  ) {
    setError(null)
    resetNursingHandoff()
    setPreviousEpisodes([])
    setCurrentEpisodeEncounters([])
    closeHistoricalViewer()
    setLoadingPatientContext(true)

    try {
      const episode = await getEpisode(
        accessToken,
        item.id,
      )

      setSelectedEpisode(
        episode,
      )

      const patientRecord =
        await getPatient(
          accessToken,
          episode.patient_id,
        )

      setPatient(
        patientRecord,
      )

      await loadPreviousPatientEpisodes(
        episode.patient_id,
      )

      const encounters =
        await listEpisodeEncounters(
          accessToken,
          episode.id,
        )

      await loadNursingHandoff(
        encounters,
      )

      setCurrentEpisodeEncounters(
        encounters,
      )

      const preferredTitle =
        mode === 'WARD'
          ? 'Ward Review'
          : episode.flow_status ===
              'AWAITING_REVIEW'
            ? 'Doctor Review'
            : 'Doctor Consultation'

      let encounter =
        encounters.find(
          candidate =>
            candidate.status === 'OPEN' &&
            candidate.title === preferredTitle,
        ) ?? null

      if (!encounter) {
        if (!currentStaffId) {
          throw new Error(
            'Authenticated user does not have a Staff profile.',
          )
        }

        encounter =
          await createEncounter(
            accessToken,
            {
              episode_id: episode.id,
              staff_id: currentStaffId,
              title: preferredTitle,
            },
          )
      }

      await openEncounterView(
        encounter,
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to open patient encounter.',
      )
    } finally {
      setLoadingPatientContext(false)
    }
  }


  async function refreshEncounterContext(
    encounterId: string,
  ) {
    setError(null)

    try {
      await refreshEncounterData(
        encounterId,
      )

      await clinicalDocumentation.loadProgressNote(
        encounterId,
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to refresh encounter context.',
      )
    }
  }


  async function openEncounterView(
    encounter: Encounter,
  ) {
    setSelectedEncounter(encounter)
    resetEncounterContext()
    documentation.resetProgressNote()
    documentation.resetInitialClerking()
    setError(null)

    await refreshEncounterContext(
      encounter.id,
    )
  }


                


  function insertLatestVitals() {
    const latest =
      [...vitals]
        .sort(
          (a, b) =>
            new Date(b.occurred_at).getTime() -
            new Date(a.occurred_at).getTime(),
        )[0]

    if (!latest) {
      setError(
        'No recorded vitals are available.',
      )
      return
    }

    const formatted =
      formatVitalsForObjective(latest)

    if (!formatted) {
      return
    }

    const trimmed =
      noteObjective.trim()

    documentation.updateProgressNote(
      'objective',
      trimmed
        ? `${trimmed}

Vitals: ${formatted}`
        : `Vitals: ${formatted}`,
    )

    setSuccess(
      'Latest vitals added to Objective.',
    )
  }


  



  const {
    admittingEpisode,
    admitSelectedEpisode,
    closingEncounter,
    completeWardReview,
  } = useDoctorEpisodeActions({
    accessToken,
    selectedEpisode,
    selectedEncounter,
    initialClerkingSigned:
      progressNote?.document_type ===
        'INITIAL_CLERKING' &&
      progressNote.status === 'SIGNED',
    setSelectedEpisode,
    setSelectedEncounter,
    refreshDoctorQueues,
    refreshEncounterContext,
    onError: setError,
    onSuccess: setSuccess,
    clearError: () => setError(null),
    clearSuccess: () => setSuccess(null),
  })

  async function handleCompleteConsultation() {
    if (
      !selectedEpisode ||
      !selectedEncounter
    ) {
      return
    }

    setCompletingConsultation(true)
    setError(null)
    setSuccess(null)

    try {
      const updatedEpisode =
        await completeConsultation(
          accessToken,
          selectedEpisode.id,
          {
            encounter_id:
              selectedEncounter.id,
            disposition:
              'COMPLETE',
          },
        )

      setSelectedEpisode(
        updatedEpisode,
      )

      await refreshEncounterContext(
        selectedEncounter.id,
      )

      await refreshDoctorQueues()

      setSuccess(
        'Consultation completed.',
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to complete consultation.',
      )
    } finally {
      setCompletingConsultation(false)
    }
  }


  async function handleCompleteDoctorReview() {
    if (
      !selectedEpisode ||
      !selectedEncounter ||
      selectedEncounter.title !== 'Doctor Review'
    ) {
      return
    }

    setCompletingDoctorReview(true)
    setError(null)
    setSuccess(null)

    try {
      const updatedEpisode =
        await completeDoctorReview(
          accessToken,
          selectedEpisode.id,
          {
            encounter_id:
              selectedEncounter.id,
          },
        )

      setSelectedEpisode(
        updatedEpisode,
      )

      await refreshEncounterContext(
        selectedEncounter.id,
      )

      await refreshDoctorQueues()

      setSuccess(
        'Doctor Review completed.',
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to complete Doctor Review.',
      )
    } finally {
      setCompletingDoctorReview(false)
    }
  }


  





  return (
    <section className="doctor-workspace">
      <div className="workspace-header">
        <div>
          <p className="eyebrow">
            Clinical workspace
          </p>

          <h1>
            Doctor Workspace
          </h1>

          <p>
            Open a patient encounter and record
            the clinical assessment.
          </p>
        </div>
      </div>

      {error && (
        <div className="alert error">
          {error}
        </div>
      )}

      {success && (
        <div className="alert success">
          {success}
        </div>
      )}

      <div className="doctor-workspace-top">
        <section
          className={
            selectedEpisode
              ? 'workspace-panel doctor-queue-panel compact'
              : 'workspace-panel doctor-queue-panel'
          }
        >
          <details
            open={!selectedEpisode}
          >
            <summary className="doctor-queue-summary">
              <div>
                <p className="eyebrow">
                  MY QUEUE
                </p>

                <h2>
                  Doctor Queue
                </h2>

                <p>
                  Patients currently requiring your attention.
                </p>
              </div>

              <span>
                {clinicQueue.length + wardQueue.length}
              </span>
            </summary>

            <div className="doctor-queue-sections">
              <div className="doctor-queue-section">
                <div className="doctor-queue-section-header">
                  <strong>
                    Clinic
                  </strong>

                  <span>
                    {clinicQueue.length}
                  </span>
                </div>

                {clinicQueue.length === 0 ? (
                  <p className="doctor-queue-empty">
                    No patients waiting for assessment.
                  </p>
                ) : (
                  <div className="doctor-queue-list">
                    {clinicQueue.map(item => (
                      <button
                        key={item.id}
                        type="button"
                        className={
                          selectedEpisode?.id === item.id
                            ? 'doctor-queue-item active'
                            : 'doctor-queue-item'
                        }
                        onClick={() =>
                          void openDoctorQueueItem(
                            item,
                            'CLINIC',
                          )
                        }
                      >
                        <span>
                          <strong>
                            {item.patient_name}
                          </strong>

                          <small>
                            {item.hospital_number}
                          </small>
                        </span>

                        <small>
                          {item.title}
                        </small>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <div className="doctor-queue-divider" />

              <div className="doctor-queue-section">
                <div className="doctor-queue-section-header">
                  <strong>
                    Ward
                  </strong>

                  <span>
                    {wardQueue.length}
                  </span>
                </div>

                {wardQueue.length === 0 ? (
                  <p className="doctor-queue-empty">
                    No admitted patients assigned to you.
                  </p>
                ) : (
                  <div className="doctor-queue-list">
                    {wardQueue.map(item => (
                      <button
                        key={item.id}
                        type="button"
                        className={
                          selectedEpisode?.id === item.id
                            ? 'doctor-queue-item active'
                            : 'doctor-queue-item'
                        }
                        onClick={() =>
                          void openDoctorQueueItem(
                            item,
                            'WARD',
                          )
                        }
                      >
                        <span>
                          <strong>
                            {item.patient_name}
                          </strong>

                          <small>
                            {item.hospital_number}
                          </small>
                        </span>

                        <small>
                          {item.title}
                        </small>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </details>
        </section>

        <section className="workspace-panel doctor-current-encounter">
          <div className="panel-header">
            <div>
              <p className="eyebrow">
                CURRENT ENCOUNTER
              </p>

              <h2>
                {selectedEncounter
                  ? selectedEncounter.title
                  : 'No encounter selected'}
              </h2>

              <p>
                {selectedEncounter
                  ? 'Active clinical encounter.'
                  : 'Select a patient from your queue to begin.'}
              </p>
            </div>

            {selectedEncounter && (
              <span>
                {selectedEncounter.status}
              </span>
            )}
          </div>

          {selectedEncounter ? (
            <div className="doctor-encounter-context">
              <div>
                <span>
                  Episode
                </span>

                <strong>
                  {selectedEpisode?.episode_number ?? '—'}
                </strong>
              </div>

              <div>
                <span>
                  Episode status
                </span>

                <strong>
                  {selectedEpisode?.status ?? '—'}
                </strong>
              </div>
            </div>
          ) : (
            <div className="doctor-encounter-empty">
              <p>
                No encounter selected.
              </p>
            </div>
          )}
        </section>
      </div>

      {selectedEncounter && (
        <DoctorEncounterWorkspace
          selectedEncounter={selectedEncounter}
          selectedEpisode={selectedEpisode}
          accessToken={accessToken}
          patient={patient}
          loadingPatientContext={loadingPatientContext}
          previousEpisodes={previousEpisodes}
          currentEpisodeEncounters={currentEpisodeEncounters}
          historicalEpisode={historicalEpisode}
          historicalEncounters={historicalEncounters}
          selectedHistoricalEncounter={selectedHistoricalEncounter}
          historicalDocuments={historicalDocuments}
          historicalDiagnoses={historicalDiagnoses}
          historicalOrders={historicalOrders}
          historicalVitals={historicalVitals}
          historicalTimeline={historicalTimeline}
          loadingPreviousEpisodes={loadingPreviousEpisodes}
          loadingHistorical={loadingHistorical}
          openHistoricalEncounter={openHistoricalEncounter}
          openHistoricalEpisode={openHistoricalEpisode}
          closeHistoricalViewer={closeHistoricalViewer}
          nursingEncounter={nursingEncounter}
          nursingDocument={nursingDocument}
          loadingNursingHandoff={loadingNursingHandoff}
          timeline={timeline}
          loadingTimeline={loadingTimeline}
          documentation={documentation}
          progressNote={progressNote}
          loadingProgressNote={loadingProgressNote}
          savingProgressNote={savingProgressNote}
          signingProgressNote={signingProgressNote}
          admittingEpisode={admittingEpisode}
          clerkingComplaint={clerkingComplaint}
          clerkingComplaintDuration={clerkingComplaintDuration}
          clerkingHistory={clerkingHistory}
          clerkingReviewOfSystems={clerkingReviewOfSystems}
          clerkingPastMedicalHistory={clerkingPastMedicalHistory}
          clerkingPastSurgicalHistory={clerkingPastSurgicalHistory}
          clerkingDrugHistory={clerkingDrugHistory}
          clerkingAllergies={clerkingAllergies}
          clerkingFamilyHistory={clerkingFamilyHistory}
          clerkingSocialHistory={clerkingSocialHistory}
          clerkingPersonalHistory={clerkingPersonalHistory}
          clerkingIdeas={clerkingIdeas}
          clerkingConcerns={clerkingConcerns}
          clerkingExpectations={clerkingExpectations}
          clerkingExamGeneral={clerkingExamGeneral}
          clerkingExamCardiovascular={clerkingExamCardiovascular}
          clerkingExamRespiratory={clerkingExamRespiratory}
          clerkingExamAbdomen={clerkingExamAbdomen}
          clerkingExamNeurological={clerkingExamNeurological}
          clerkingExamMusculoskeletal={clerkingExamMusculoskeletal}
          clerkingExamGenitourinary={clerkingExamGenitourinary}
          clerkingExamOther={clerkingExamOther}
          noteSubjective={noteSubjective}
          noteObjective={noteObjective}
          noteWorkingDiagnosis={noteWorkingDiagnosis}
          noteDifferentials={noteDifferentials}
          notePlan={notePlan}
          setClerkingComplaint={setClerkingComplaint}
          setClerkingComplaintDuration={setClerkingComplaintDuration}
          setClerkingHistory={setClerkingHistory}
          setClerkingReviewOfSystems={setClerkingReviewOfSystems}
          setClerkingPastMedicalHistory={setClerkingPastMedicalHistory}
          setClerkingPastSurgicalHistory={setClerkingPastSurgicalHistory}
          setClerkingDrugHistory={setClerkingDrugHistory}
          setClerkingAllergies={setClerkingAllergies}
          setClerkingFamilyHistory={setClerkingFamilyHistory}
          setClerkingSocialHistory={setClerkingSocialHistory}
          setClerkingPersonalHistory={setClerkingPersonalHistory}
          setClerkingIdeas={setClerkingIdeas}
          setClerkingConcerns={setClerkingConcerns}
          setClerkingExpectations={setClerkingExpectations}
          setClerkingExamGeneral={setClerkingExamGeneral}
          setClerkingExamCardiovascular={setClerkingExamCardiovascular}
          setClerkingExamRespiratory={setClerkingExamRespiratory}
          setClerkingExamAbdomen={setClerkingExamAbdomen}
          setClerkingExamNeurological={setClerkingExamNeurological}
          setClerkingExamMusculoskeletal={setClerkingExamMusculoskeletal}
          setClerkingExamGenitourinary={setClerkingExamGenitourinary}
          setClerkingExamOther={setClerkingExamOther}
          setNoteSubjective={setNoteSubjective}
          setNoteObjective={setNoteObjective}
          setNoteWorkingDiagnosis={setNoteWorkingDiagnosis}
          setNoteDifferentials={setNoteDifferentials}
          setNotePlan={setNotePlan}
          insertLatestVitals={insertLatestVitals}
          saveProgressNote={saveProgressNote}
          signProgressNote={signProgressNote}
          admitSelectedEpisode={admitSelectedEpisode}
          vitals={vitals}
          nursingVitals={nursingVitals}
          savingVitals={savingVitals}
          temperature={temperature}
          heartRate={heartRate}
          respiratoryRate={respiratoryRate}
          systolicBp={systolicBp}
          diastolicBp={diastolicBp}
          spo2={spo2}
          weight={weight}
          setTemperature={setTemperature}
          setHeartRate={setHeartRate}
          setRespiratoryRate={setRespiratoryRate}
          setSystolicBp={setSystolicBp}
          setDiastolicBp={setDiastolicBp}
          setSpo2={setSpo2}
          setWeight={setWeight}
          saveVitals={saveVitals}
          diagnoses={diagnoses}
          loadingDiagnoses={loadingDiagnoses}
          savingDiagnosis={savingDiagnosis}
          diagnosisQuery={diagnosisQuery}
          diagnosisResults={diagnosisResults}
          selectedDiagnosis={selectedDiagnosis}
          diagnosisType={diagnosisType}
          certainty={certainty}
          searchDiagnoses={searchDiagnoses}
          setSelectedDiagnosis={setSelectedDiagnosis}
          setDiagnosisType={setDiagnosisType}
          setCertainty={setCertainty}
          saveDiagnosis={saveDiagnosis}
          orders={orders}
          clinicalResults={clinicalResults}
          loadingOrders={loadingOrders}
          savingOrder={savingOrder}
          cancellingOrderId={cancellingOrderId}
          inpatientTreatmentStart={inpatientTreatmentStart}
          inpatientFirstDose={inpatientFirstDose}
          orderType={orderType}
          orderPriority={orderPriority}
          laboratoryTests={laboratoryTests}
          selectedLaboratoryTestId={selectedLaboratoryTestId}
          diagnosticInvestigations={diagnosticInvestigations}
          selectedDiagnosticInvestigationId={selectedDiagnosticInvestigationId}
          orderTestCode={orderTestCode}
          orderTestName={orderTestName}
          orderMedicationId={orderMedicationId}
          orderDose={orderDose}
          prescriptionMedicine={prescriptionMedicine}
          prescriptionStrength={prescriptionStrength}
          prescriptionDoseUnit={prescriptionDoseUnit}
          prescriptionRoute={prescriptionRoute}
          prescriptionFrequency={prescriptionFrequency}
          prescriptionDuration={prescriptionDuration}
          prescriptionDurationUnit={prescriptionDurationUnit}
          prescriptionQuantity={prescriptionQuantity}
          prescriptionDirections={prescriptionDirections}
          prescriptionIndication={prescriptionIndication}
          setInpatientTreatmentStart={setInpatientTreatmentStart}
          setInpatientFirstDose={setInpatientFirstDose}
          setOrderType={setOrderType}
          setOrderPriority={setOrderPriority}
          handleLaboratoryTestChange={handleLaboratoryTestChange}
          handleDiagnosticInvestigationChange={handleDiagnosticInvestigationChange}
          setOrderTestCode={setOrderTestCode}
          setOrderTestName={setOrderTestName}
          setOrderMedicationId={setOrderMedicationId}
          setOrderDose={setOrderDose}
          setPrescriptionMedicine={setPrescriptionMedicine}
          setPrescriptionStrength={setPrescriptionStrength}
          setPrescriptionDoseUnit={setPrescriptionDoseUnit}
          setPrescriptionRoute={setPrescriptionRoute}
          setPrescriptionFrequency={setPrescriptionFrequency}
          setPrescriptionDuration={setPrescriptionDuration}
          setPrescriptionDurationUnit={setPrescriptionDurationUnit}
          setPrescriptionQuantity={setPrescriptionQuantity}
          setPrescriptionDirections={setPrescriptionDirections}
          setPrescriptionIndication={setPrescriptionIndication}
          saveOrder={saveOrder}
          cancelOrder={cancelOrder}
          completingConsultation={completingConsultation}
          handleCompleteConsultation={handleCompleteConsultation}
          completingDoctorReview={completingDoctorReview}
          handleCompleteDoctorReview={handleCompleteDoctorReview}
          closingEncounter={closingEncounter}
          completeWardReview={completeWardReview}
          loadingClinicalResults={loadingClinicalResults}
          diagnosticReports={diagnosticReports}
          diagnosticAttachments={diagnosticAttachments}
        />
      )}
    </section>
  )
}
