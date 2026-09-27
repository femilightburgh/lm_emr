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
  startDoctorConsultation,
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
import DoctorQueuePanel from './DoctorQueuePanel'
import DoctorCurrentEncounterCard from './DoctorCurrentEncounterCard'

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
    manualDiagnosis,
    setManualDiagnosis,
    diagnosisSearchPerformed,
    enterManualDiagnosis,
    exitManualDiagnosis,
    selectDiagnosis,
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
    manualDiagnosis,
    refreshEncounterContext,
    resetDiagnosisSearch: () => {
      setDiagnosisQuery('')
      setDiagnosisResults([])
      setManualDiagnosis('')
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

    selectedLaboratoryTestIds,
    selectedDiagnosticInvestigationId,

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

    customLaboratoryInvestigation,
    setCustomLaboratoryInvestigation,
    handleLaboratoryTestChange,
    customDiagnosticInvestigation,
    setCustomDiagnosticInvestigation,
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
  } = documentation

  const {
    loadingProgressNote,
    savingProgressNote,
    signingProgressNote,
    saveProgressNote,
    signProgressNote,
  } = clinicalDocumentation









    const [completingConsultation, setCompletingConsultation] =
      useState(false)

    const [completingDoctorReview, setCompletingDoctorReview] =
      useState(false)


















  function handleBackToDoctorQueue() {
    setError(null)
    setSuccess(null)

    setSelectedEncounter(null)
    setSelectedEpisode(null)

    setPatient(null)
    setPreviousEpisodes([])
    setCurrentEpisodeEncounters([])

    resetNursingHandoff()
    closeHistoricalViewer()
    resetEncounterContext()

    documentation.resetProgressNote()
    documentation.resetInitialClerking()
  }


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
        episode.id,
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

      let encounter: Encounter | null = null

      if (preferredTitle === 'Doctor Consultation') {
        await startDoctorConsultation(
          accessToken,
          episode.id,
        )

        const refreshedEncounters =
          await listEpisodeEncounters(
            accessToken,
            episode.id,
          )

        encounter =
          refreshedEncounters.find(
            candidate =>
              candidate.status === 'OPEN' &&
              candidate.title === 'Doctor Consultation',
          ) ?? null

        if (!encounter) {
          throw new Error(
            'Doctor Consultation was started, but the encounter could not be loaded.',
          )
        }

        setCurrentEpisodeEncounters(
          refreshedEncounters,
        )
      } else {
        encounter =
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
      documentation.progressNoteForm.objective.trim()

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
    <section className="workspace-content doctor-workspace">
      <div className="page-header">
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
        <DoctorQueuePanel
          clinicQueue={clinicQueue}
          wardQueue={wardQueue}
          selectedEpisodeId={selectedEpisode?.id ?? null}
          onSelectQueueItem={(item, source) => {
            void openDoctorQueueItem(item, source)
          }}
        />

        <DoctorCurrentEncounterCard
          selectedEncounter={selectedEncounter}
          selectedEpisode={selectedEpisode}
        />
      </div>

      {selectedEncounter && (
        <DoctorEncounterWorkspace
          selectedEncounter={selectedEncounter}
          selectedEpisode={selectedEpisode}
          accessToken={accessToken}
          onBackToQueue={handleBackToDoctorQueue}
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
          onSelectCurrentEncounter={encounter => {
            closeHistoricalViewer()
            void openEncounterView(encounter)
          }}
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
          manualDiagnosis={manualDiagnosis}
          diagnosisSearchPerformed={diagnosisSearchPerformed}
          diagnosisType={diagnosisType}
          certainty={certainty}
          searchDiagnoses={searchDiagnoses}
          selectDiagnosis={selectDiagnosis}
          enterManualDiagnosis={enterManualDiagnosis}
          exitManualDiagnosis={exitManualDiagnosis}
          setManualDiagnosis={setManualDiagnosis}
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
          selectedLaboratoryTestIds={selectedLaboratoryTestIds}
          customLaboratoryInvestigation={
            customLaboratoryInvestigation
          }
          diagnosticInvestigations={diagnosticInvestigations}
          selectedDiagnosticInvestigationId={selectedDiagnosticInvestigationId}
          customDiagnosticInvestigation={
            customDiagnosticInvestigation
          }
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
          setCustomLaboratoryInvestigation={
            setCustomLaboratoryInvestigation
          }
          handleDiagnosticInvestigationChange={handleDiagnosticInvestigationChange}
          setCustomDiagnosticInvestigation={
            setCustomDiagnosticInvestigation
          }
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
