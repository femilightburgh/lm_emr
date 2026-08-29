import {
  useEffect,
  useState,
} from 'react'

import {
  createEncounter,
  getEncounter,
  getEncounterTimeline,
  listEpisodeEncounters,
  type ClinicalEvent,
  type Encounter,
} from '../../api/encounters'

import {
  admitEpisode,
  completeConsultation,
  getEpisode,
  listPatientEpisodes,
  listDoctorClinicQueue,
  listDoctorWardQueue,
  type DoctorQueueItem,
  type Episode,
} from '../../api/episodes'

import {
  getPatient,
  type Patient,
} from '../../api/patients'

import {
  getCurrentStaff,
} from '../../api/staff'

import {
  createClinicalDiagnosis,
  listEncounterDiagnoses,
  type ClinicalDiagnosis,
  type DiagnosisCertainty,
  type DiagnosisType,
} from '../../api/diagnoses'

import {
  searchDiagnosisTerminology,
  type TerminologyConcept,
} from '../../api/terminology'

import {
  createClinicalDocument,
  listEncounterClinicalDocuments,
  signClinicalDocument,
  updateClinicalDocument,
  type ClinicalDocument,
} from '../../api/clinicalDocuments'

import {
  cancelClinicalOrder,
  createClinicalOrder,
  listEncounterClinicalOrders,
  type ClinicalOrder,
  type ClinicalOrderType,
} from '../../api/clinicalOrders'

import {
  listLaboratoryTests,
  type LaboratoryTest,
} from '../../api/laboratory'

import {
  listOrderClinicalResults,
  type ClinicalResult,
} from '../../api/clinicalResults'

import {
  createPrescription,
} from '../../api/prescriptions'

import {
  createVitals,
  listEncounterVitals,
  type Vitals,
} from '../../api/vitals'

import VitalsPanel from './VitalsPanel'

import ClinicalOrdersPanel from './ClinicalOrdersPanel'

import ProgressNotePanel from './ProgressNotePanel'
import NursingHandoffPanel from './NursingHandoffPanel'
import SignedClinicalDocumentSummary from './SignedClinicalDocumentSummary'
import PatientHistoryPanel from './PatientHistoryPanel'
import HistoricalEncounterPanel from './HistoricalEncounterPanel'

import DiagnosisPanel from './DiagnosisPanel'

import InitialClerkingPanel from './InitialClerkingPanel'

interface Props {
  accessToken: string
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

function getInvestigationLabel(
  order: ClinicalOrder,
): string {
  if (order.order_type === 'LABORATORY') {
    const testName = order.details.test_name
    const testCode = order.details.test_code

    if (typeof testName === 'string' && testName.trim()) {
      return testName
    }

    if (typeof testCode === 'string' && testCode.trim()) {
      return testCode
    }

    return 'Laboratory investigation'
  }

  const studyCode = order.details.study_code

  if (typeof studyCode === 'string' && studyCode.trim()) {
    return studyCode
  }

  return 'Radiology investigation'
}


function formatResultValue(
  value: unknown,
): string {
  if (
    value === null ||
    value === undefined
  ) {
    return '—'
  }

  if (
    typeof value === 'string' ||
    typeof value === 'number' ||
    typeof value === 'boolean'
  ) {
    return String(value)
  }

  return JSON.stringify(value)
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
  const [clinicQueue, setClinicQueue] =
    useState<DoctorQueueItem[]>([])

  const [wardQueue, setWardQueue] =
    useState<DoctorQueueItem[]>([])

  const [selectedEncounter, setSelectedEncounter] =
    useState<Encounter | null>(null)

  const [currentEpisodeEncounters, setCurrentEpisodeEncounters] =
    useState<Encounter[]>([])

  const [timeline, setTimeline] =
    useState<ClinicalEvent[]>([])

  const [loadingTimeline, setLoadingTimeline] =
    useState(false)

  const [selectedEpisode, setSelectedEpisode] =
    useState<Episode | null>(null)

  const [patient, setPatient] =
    useState<Patient | null>(null)

  const [nursingEncounter, setNursingEncounter] =
    useState<Encounter | null>(null)

  const [nursingDocument, setNursingDocument] =
    useState<ClinicalDocument | null>(null)

  const [nursingVitals, setNursingVitals] =
    useState<Vitals[]>([])

  const [loadingNursingHandoff, setLoadingNursingHandoff] =
    useState(false)

  const [currentStaffId, setCurrentStaffId] =
    useState<string | null>(null)

  const [loadingPatientContext, setLoadingPatientContext] =
    useState(false)

  const [previousEpisodes, setPreviousEpisodes] =
    useState<Episode[]>([])

  const [loadingPreviousEpisodes, setLoadingPreviousEpisodes] =
    useState(false)

  const [historicalEpisode, setHistoricalEpisode] =
    useState<Episode | null>(null)

  const [historicalEncounters, setHistoricalEncounters] =
    useState<Encounter[]>([])

  const [selectedHistoricalEncounter, setSelectedHistoricalEncounter] =
    useState<Encounter | null>(null)

  const [historicalDocuments, setHistoricalDocuments] =
    useState<ClinicalDocument[]>([])

  const [historicalDiagnoses, setHistoricalDiagnoses] =
    useState<ClinicalDiagnosis[]>([])

  const [historicalOrders, setHistoricalOrders] =
    useState<ClinicalOrder[]>([])

  const [historicalVitals, setHistoricalVitals] =
    useState<Vitals[]>([])

  const [historicalTimeline, setHistoricalTimeline] =
    useState<ClinicalEvent[]>([])

  const [loadingHistorical, setLoadingHistorical] =
    useState(false)

  const [diagnoses, setDiagnoses] =
    useState<ClinicalDiagnosis[]>([])

  const [diagnosisQuery, setDiagnosisQuery] =
    useState('')

  const [diagnosisResults, setDiagnosisResults] =
    useState<TerminologyConcept[]>([])

  const [selectedDiagnosis, setSelectedDiagnosis] =
    useState<TerminologyConcept | null>(null)

  const [diagnosisType, setDiagnosisType] =
    useState<DiagnosisType>('PROVISIONAL')

  const [certainty, setCertainty] =
    useState<DiagnosisCertainty>('POSSIBLE')

  const [, setLoadingQueue] =
    useState(false)

  const [loadingDiagnoses, setLoadingDiagnoses] =
    useState(false)

  const [savingDiagnosis, setSavingDiagnosis] =
    useState(false)

  const [progressNote, setProgressNote] =
    useState<ClinicalDocument | null>(null)

  const [noteSubjective, setNoteSubjective] =
    useState('')

  const [noteObjective, setNoteObjective] =
    useState('')

  const [noteWorkingDiagnosis, setNoteWorkingDiagnosis] =
    useState('')

  const [noteDifferentials, setNoteDifferentials] =
    useState('')

  const [notePlan, setNotePlan] =
    useState('')

  const [clerkingComplaint, setClerkingComplaint] =
    useState('')

  const [clerkingComplaintDuration, setClerkingComplaintDuration] =
    useState('')

  const [clerkingHistory, setClerkingHistory] =
    useState('')

  const [clerkingReviewOfSystems, setClerkingReviewOfSystems] =
    useState('')

  const [clerkingPastMedicalHistory, setClerkingPastMedicalHistory] =
    useState('')

  const [clerkingPastSurgicalHistory, setClerkingPastSurgicalHistory] =
    useState('')

  const [clerkingDrugHistory, setClerkingDrugHistory] =
    useState('')

  const [clerkingAllergies, setClerkingAllergies] =
    useState('')

  const [clerkingFamilyHistory, setClerkingFamilyHistory] =
    useState('')

  const [clerkingSocialHistory, setClerkingSocialHistory] =
    useState('')

  const [clerkingPersonalHistory, setClerkingPersonalHistory] =
    useState('')

  const [clerkingGynaecologicalHistory, setClerkingGynaecologicalHistory] =
    useState('')

  const [clerkingObstetricHistory, setClerkingObstetricHistory] =
    useState('')

  const [clerkingMenstrualHistory, setClerkingMenstrualHistory] =
    useState('')

  const [clerkingSexualHistory, setClerkingSexualHistory] =
    useState('')

  const [clerkingIdeas, setClerkingIdeas] =
    useState('')

  const [clerkingConcerns, setClerkingConcerns] =
    useState('')

  const [clerkingExpectations, setClerkingExpectations] =
    useState('')

  const [clerkingExamGeneral, setClerkingExamGeneral] =
    useState('')

  const [clerkingExamCardiovascular, setClerkingExamCardiovascular] =
    useState('')

  const [clerkingExamRespiratory, setClerkingExamRespiratory] =
    useState('')

  const [clerkingExamAbdomen, setClerkingExamAbdomen] =
    useState('')

  const [clerkingExamNeurological, setClerkingExamNeurological] =
    useState('')

  const [clerkingExamMusculoskeletal, setClerkingExamMusculoskeletal] =
    useState('')

  const [clerkingExamGenitourinary, setClerkingExamGenitourinary] =
    useState('')

  const [clerkingExamOther, setClerkingExamOther] =
    useState('')

  const [clerkingInvestigations, setClerkingInvestigations] =
    useState('')

  const [loadingProgressNote, setLoadingProgressNote] =
    useState(false)

  const [savingProgressNote, setSavingProgressNote] =
    useState(false)

  const [signingProgressNote, setSigningProgressNote] =
    useState(false)

  const [admittingEpisode, setAdmittingEpisode] =
    useState(false)

  const [completingConsultation, setCompletingConsultation] =
    useState(false)

  const [orders, setOrders] =
    useState<ClinicalOrder[]>([])

  const [laboratoryTests, setLaboratoryTests] =
    useState<LaboratoryTest[]>([])

  const [selectedLaboratoryTestId, setSelectedLaboratoryTestId] =
    useState('')

  const [clinicalResults, setClinicalResults] =
    useState<ClinicalResult[]>([])

  const [loadingClinicalResults, setLoadingClinicalResults] =
    useState(false)

  const [vitals, setVitals] =
    useState<Vitals[]>([])

  const [savingVitals, setSavingVitals] =
    useState(false)

  const [temperature, setTemperature] =
    useState('')

  const [heartRate, setHeartRate] =
    useState('')

  const [respiratoryRate, setRespiratoryRate] =
    useState('')

  const [systolicBp, setSystolicBp] =
    useState('')

  const [diastolicBp, setDiastolicBp] =
    useState('')

  const [spo2, setSpo2] =
    useState('')

  const [weight, setWeight] =
    useState('')

  const [loadingOrders, setLoadingOrders] =
    useState(false)

  const [savingOrder, setSavingOrder] =
    useState(false)

  const [cancellingOrderId, setCancellingOrderId] =
    useState<string | null>(null)

  const [orderType, setOrderType] =
    useState<ClinicalOrderType>('LABORATORY')

  const [orderPriority, setOrderPriority] =
    useState('ROUTINE')

  const [orderTestCode, setOrderTestCode] =
    useState('')

  const [orderTestName, setOrderTestName] =
    useState('')

  const [orderStudyCode, setOrderStudyCode] =
    useState('')

  const [orderMedicationId, setOrderMedicationId] =
    useState('')

  const [orderDose, setOrderDose] =
    useState('')

  const [prescriptionMedicine, setPrescriptionMedicine] =
    useState('')

  const [prescriptionStrength, setPrescriptionStrength] =
    useState('')

  const [prescriptionDoseUnit, setPrescriptionDoseUnit] =
    useState('')

  const [prescriptionRoute, setPrescriptionRoute] =
    useState('')

  const [prescriptionFrequency, setPrescriptionFrequency] =
    useState('')

  const [prescriptionDuration, setPrescriptionDuration] =
    useState('')

  const [prescriptionDurationUnit, setPrescriptionDurationUnit] =
    useState('')

  const [prescriptionQuantity, setPrescriptionQuantity] =
    useState('')

  const [prescriptionDirections, setPrescriptionDirections] =
    useState('')

  const [prescriptionIndication, setPrescriptionIndication] =
    useState('')

  const [error, setError] =
    useState<string | null>(null)

  const [success, setSuccess] =
    useState<string | null>(null)


  useEffect(() => {
    let cancelled = false

    async function loadDoctorQueues() {
      setLoadingQueue(true)
      setError(null)

      try {
        const currentStaff =
          await getCurrentStaff(
            accessToken,
          )

        const [
          clinicResults,
          wardResults,
          laboratoryTestResults,
        ] = await Promise.all([
          listDoctorClinicQueue(
            accessToken,
          ),
          listDoctorWardQueue(
            accessToken,
          ),
          listLaboratoryTests(
            accessToken,
          ),
        ])

        if (!cancelled) {
          setCurrentStaffId(
            currentStaff.id,
          )

          setClinicQueue(
            clinicResults,
          )

          setWardQueue(
            wardResults,
          )

          setLaboratoryTests(
            laboratoryTestResults,
          )
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Unable to load doctor queues.',
          )
        }
      } finally {
        if (!cancelled) {
          setLoadingQueue(false)
        }
      }
    }

    void loadDoctorQueues()

    return () => {
      cancelled = true
    }
  }, [accessToken])


  function resetHistoricalEpisode() {
    setHistoricalEpisode(null)
    setHistoricalEncounters([])
    setSelectedHistoricalEncounter(null)
    setHistoricalDocuments([])
    setHistoricalDiagnoses([])
    setHistoricalOrders([])
    setHistoricalVitals([])
    setHistoricalTimeline([])
  }


  function resetNursingHandoff() {
    setNursingEncounter(null)
    setNursingDocument(null)
    setNursingVitals([])
  }


  async function openHistoricalEpisode(
    episode: Episode,
  ) {
    setLoadingHistorical(true)
    setError(null)

    try {
      const encounters =
        await listEpisodeEncounters(
          accessToken,
          episode.id,
        )

      setHistoricalEpisode(
        episode,
      )

      setHistoricalEncounters(
        encounters,
      )

      setHistoricalDocuments([])
      setHistoricalDiagnoses([])
      setHistoricalOrders([])
      setHistoricalVitals([])
      setHistoricalTimeline([])

      const firstEncounter =
        encounters[0] ?? null

      if (firstEncounter) {
        await openHistoricalEncounter(
          episode,
          firstEncounter,
        )
      } else {
        setSelectedHistoricalEncounter(null)
      }
    } catch (err) {
      resetHistoricalEpisode()

      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load previous encounter history.',
      )
    } finally {
      setLoadingHistorical(false)
    }
  }


  async function openHistoricalEncounter(
    episode: Episode,
    encounter: Encounter,
  ) {
    setHistoricalEpisode(
      episode,
    )

    setLoadingHistorical(true)
    setError(null)

    try {
      const [
        documents,
        diagnoses,
        orders,
        vitals,
        timeline,
      ] = await Promise.all([
        listEncounterClinicalDocuments(
          accessToken,
          encounter.id,
        ),
        listEncounterDiagnoses(
          accessToken,
          encounter.id,
        ),
        listEncounterClinicalOrders(
          accessToken,
          encounter.id,
        ),
        listEncounterVitals(
          accessToken,
          encounter.id,
        ),
        getEncounterTimeline(
          accessToken,
          encounter.id,
        ),
      ])

      setSelectedHistoricalEncounter(
        encounter,
      )

      setHistoricalDocuments(
        documents,
      )

      setHistoricalDiagnoses(
        diagnoses,
      )

      setHistoricalOrders(
        orders,
      )

      setHistoricalVitals(
        vitals,
      )

      setHistoricalTimeline(
        timeline,
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load historical encounter.',
      )
    } finally {
      setLoadingHistorical(false)
    }
  }


  async function loadPreviousPatientEpisodes(
    patientId: string,
  ) {
    setLoadingPreviousEpisodes(true)

    try {
      const episodes =
        await listPatientEpisodes(
          accessToken,
          patientId,
        )

      setPreviousEpisodes(episodes)
    } catch (err) {
      setPreviousEpisodes([])

      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load previous encounters.',
      )
    } finally {
      setLoadingPreviousEpisodes(false)
    }
  }


  async function loadNursingHandoff(
    encounters: Encounter[],
  ) {
    setLoadingNursingHandoff(true)

    try {
      const nursingEncounters =
        encounters
          .filter(
            encounter =>
              encounter.title === 'Nursing Intake',
          )
          .sort(
            (a, b) =>
              new Date(b.started_at).getTime() -
              new Date(a.started_at).getTime(),
          )

      const nursing =
        nursingEncounters[0] ?? null

      if (!nursing) {
        resetNursingHandoff()
        return
      }

      setNursingEncounter(nursing)

      const [
        documents,
        vitals,
      ] = await Promise.all([
        listEncounterClinicalDocuments(
          accessToken,
          nursing.id,
        ),
        listEncounterVitals(
          accessToken,
          nursing.id,
        ),
      ])

      const signedNursingDocument =
        documents
          .filter(
            document =>
              document.document_type ===
                'NURSING_INTAKE' &&
              document.status === 'SIGNED',
          )
          .sort(
            (a, b) =>
              b.version - a.version,
          )[0] ?? null

      setNursingDocument(
        signedNursingDocument,
      )

      setNursingVitals(vitals)
    } catch (err) {
      resetNursingHandoff()

      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load nursing handoff.',
      )
    } finally {
      setLoadingNursingHandoff(false)
    }
  }


  async function openDoctorQueueItem(
    item: DoctorQueueItem,
    mode: 'CLINIC' | 'WARD',
  ) {
    setError(null)
    resetNursingHandoff()
    setPreviousEpisodes([])
    setCurrentEpisodeEncounters([])
    resetHistoricalEpisode()
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

    setLoadingDiagnoses(true)
    setLoadingTimeline(true)
    setLoadingOrders(true)
    setLoadingClinicalResults(true)
    try {
      const [
        encounterResult,
        diagnosisResults,
        timelineResults,
        orderResults,
        vitalResults,
      ] = await Promise.all([
        getEncounter(
          accessToken,
          encounterId,
        ),
        listEncounterDiagnoses(
          accessToken,
          encounterId,
        ),
        getEncounterTimeline(
          accessToken,
          encounterId,
        ),
        listEncounterClinicalOrders(
          accessToken,
          encounterId,
        ),
        listEncounterVitals(
          accessToken,
          encounterId,
        ),
      ])

      setSelectedEncounter(
        encounterResult,
      )

      setDiagnoses(diagnosisResults)
      setTimeline(timelineResults)
      setOrders(orderResults)
      setVitals(vitalResults)

      const investigationOrders =
        orderResults.filter(
          order =>
            order.order_type === 'LABORATORY' ||
            order.order_type === 'RADIOLOGY',
        )

      const resultGroups =
        await Promise.all(
          investigationOrders.map(
            order =>
              listOrderClinicalResults(
                accessToken,
                order.id,
              ),
          ),
        )

      setClinicalResults(
        resultGroups.flat(),
      )

      await loadProgressNote(
        encounterId,
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to refresh encounter context.',
      )
    } finally {
      setLoadingDiagnoses(false)
      setLoadingTimeline(false)
      setLoadingOrders(false)
      setLoadingClinicalResults(false)
    }
  }


  async function openEncounterView(
    encounter: Encounter,
  ) {
    setSelectedEncounter(encounter)
    setDiagnoses([])
    setTimeline([])
    setOrders([])
    setClinicalResults([])
    setVitals([])
    resetProgressNote()
    resetInitialClerking()
    setError(null)

    await refreshEncounterContext(
      encounter.id,
    )
  }


  function resetInitialClerking() {
    setClerkingComplaint('')
    setClerkingComplaintDuration('')
    setClerkingHistory('')
    setClerkingReviewOfSystems('')
    setClerkingPastMedicalHistory('')
    setClerkingPastSurgicalHistory('')
    setClerkingDrugHistory('')
    setClerkingAllergies('')
    setClerkingFamilyHistory('')
    setClerkingSocialHistory('')
    setClerkingPersonalHistory('')
    setClerkingGynaecologicalHistory('')
    setClerkingObstetricHistory('')
    setClerkingMenstrualHistory('')
    setClerkingSexualHistory('')
    setClerkingIdeas('')
    setClerkingConcerns('')
    setClerkingExpectations('')
    setClerkingExamGeneral('')
    setClerkingExamCardiovascular('')
    setClerkingExamRespiratory('')
    setClerkingExamAbdomen('')
    setClerkingExamNeurological('')
    setClerkingExamMusculoskeletal('')
    setClerkingExamGenitourinary('')
    setClerkingExamOther('')
    setClerkingInvestigations('')
  }


  function resetProgressNote() {
    setProgressNote(null)
    setNoteSubjective('')
    setNoteObjective('')
    setNoteWorkingDiagnosis('')
    setNoteDifferentials('')
    setNotePlan('')
  }


  function loadProgressNoteContent(
    document: ClinicalDocument,
  ) {
    const content = document.content

    setNoteSubjective(
      typeof content.subjective === 'string'
        ? content.subjective
        : '',
    )

    setNoteObjective(
      typeof content.objective === 'string'
        ? content.objective
        : '',
    )

    const assessment =
      content.assessment

    if (
      assessment &&
      typeof assessment === 'object' &&
      !Array.isArray(assessment)
    ) {
      const assessmentRecord =
        assessment as Record<string, unknown>

      setNoteWorkingDiagnosis(
        typeof assessmentRecord.working_diagnosis === 'string'
          ? assessmentRecord.working_diagnosis
          : '',
      )

      const differentials =
        assessmentRecord.differentials

      setNoteDifferentials(
        Array.isArray(differentials)
          ? differentials.join('\n')
          : '',
      )
    } else {
      setNoteWorkingDiagnosis('')
      setNoteDifferentials('')
    }

    setNotePlan(
      typeof content.plan === 'string'
        ? content.plan
        : '',
    )
  }


  function loadInitialClerkingContent(
    document: ClinicalDocument,
  ) {
    const content = document.content

    const presentingComplaints =
      Array.isArray(content.presenting_complaints)
        ? content.presenting_complaints
        : []

    const firstComplaint =
      presentingComplaints[0]

    if (
      firstComplaint &&
      typeof firstComplaint === 'object' &&
      !Array.isArray(firstComplaint)
    ) {
      const complaintRecord =
        firstComplaint as Record<string, unknown>

      setClerkingComplaint(
        typeof complaintRecord.complaint === 'string'
          ? complaintRecord.complaint
          : '',
      )

      setClerkingComplaintDuration(
        typeof complaintRecord.duration === 'string'
          ? complaintRecord.duration
          : '',
      )
    } else {
      setClerkingComplaint('')
      setClerkingComplaintDuration('')
    }

    const readString = (
      source: Record<string, unknown>,
      key: string,
    ) =>
      typeof source[key] === 'string'
        ? source[key] as string
        : ''

    setClerkingHistory(
      readString(
        content,
        'history_of_presenting_complaint',
      ),
    )

    setClerkingReviewOfSystems(
      readString(
        content,
        'review_of_systems',
      ),
    )

    setClerkingPastMedicalHistory(
      readString(
        content,
        'past_medical_history',
      ),
    )

    setClerkingPastSurgicalHistory(
      readString(
        content,
        'past_surgical_history',
      ),
    )

    setClerkingDrugHistory(
      readString(
        content,
        'drug_history',
      ),
    )

    setClerkingAllergies(
      readString(
        content,
        'allergies',
      ),
    )

    setClerkingFamilyHistory(
      readString(
        content,
        'family_history',
      ),
    )

    setClerkingSocialHistory(
      readString(
        content,
        'social_history',
      ),
    )

    setClerkingPersonalHistory(
      readString(
        content,
        'personal_history',
      ),
    )

    setClerkingGynaecologicalHistory(
      readString(
        content,
        'gynaecological_history',
      ),
    )

    setClerkingObstetricHistory(
      readString(
        content,
        'obstetric_history',
      ),
    )

    setClerkingMenstrualHistory(
      readString(
        content,
        'menstrual_history',
      ),
    )

    setClerkingSexualHistory(
      readString(
        content,
        'sexual_history',
      ),
    )

    const perspective =
      content.patient_perspective

    if (
      perspective &&
      typeof perspective === 'object' &&
      !Array.isArray(perspective)
    ) {
      const perspectiveRecord =
        perspective as Record<string, unknown>

      setClerkingIdeas(
        readString(
          perspectiveRecord,
          'ideas',
        ),
      )

      setClerkingConcerns(
        readString(
          perspectiveRecord,
          'concerns',
        ),
      )

      setClerkingExpectations(
        readString(
          perspectiveRecord,
          'expectations',
        ),
      )
    } else {
      setClerkingIdeas('')
      setClerkingConcerns('')
      setClerkingExpectations('')
    }

    const examination =
      content.examination

    if (
      examination &&
      typeof examination === 'object' &&
      !Array.isArray(examination)
    ) {
      const examinationRecord =
        examination as Record<string, unknown>

      setClerkingExamGeneral(
        readString(
          examinationRecord,
          'general',
        ),
      )

      setClerkingExamCardiovascular(
        readString(
          examinationRecord,
          'cardiovascular',
        ),
      )

      setClerkingExamRespiratory(
        readString(
          examinationRecord,
          'respiratory',
        ),
      )

      setClerkingExamAbdomen(
        readString(
          examinationRecord,
          'abdomen',
        ),
      )

      setClerkingExamNeurological(
        readString(
          examinationRecord,
          'neurological',
        ),
      )

      setClerkingExamMusculoskeletal(
        readString(
          examinationRecord,
          'musculoskeletal',
        ),
      )

      setClerkingExamGenitourinary(
        readString(
          examinationRecord,
          'genitourinary',
        ),
      )

      setClerkingExamOther(
        readString(
          examinationRecord,
          'other',
        ),
      )
    } else {
      setClerkingExamGeneral('')
      setClerkingExamCardiovascular('')
      setClerkingExamRespiratory('')
      setClerkingExamAbdomen('')
      setClerkingExamNeurological('')
      setClerkingExamMusculoskeletal('')
      setClerkingExamGenitourinary('')
      setClerkingExamOther('')
    }

    const assessment =
      content.assessment

    if (
      assessment &&
      typeof assessment === 'object' &&
      !Array.isArray(assessment)
    ) {
      const assessmentRecord =
        assessment as Record<string, unknown>

      setNoteWorkingDiagnosis(
        readString(
          assessmentRecord,
          'working_diagnosis',
        ),
      )

      const differentials =
        assessmentRecord.differentials

      setNoteDifferentials(
        Array.isArray(differentials)
          ? differentials
              .filter(
                item =>
                  typeof item === 'string',
              )
              .join('\n')
          : '',
      )
    } else {
      setNoteWorkingDiagnosis('')
      setNoteDifferentials('')
    }

    const investigations =
      Array.isArray(content.investigations)
        ? content.investigations
            .filter(
              item =>
                typeof item === 'string',
            )
            .join('\n')
        : ''

    setClerkingInvestigations(
      investigations,
    )

  }


  function initialClerkingContent():
    Record<string, unknown> {
    const examination = {
      general:
        clerkingExamGeneral.trim() || null,
      cardiovascular:
        clerkingExamCardiovascular.trim() || null,
      respiratory:
        clerkingExamRespiratory.trim() || null,
      abdomen:
        clerkingExamAbdomen.trim() || null,
      neurological:
        clerkingExamNeurological.trim() || null,
      musculoskeletal:
        clerkingExamMusculoskeletal.trim() || null,
      genitourinary:
        clerkingExamGenitourinary.trim() || null,
      other:
        clerkingExamOther.trim() || null,
    }

    const patientPerspective = {
      ideas:
        clerkingIdeas.trim() || null,
      concerns:
        clerkingConcerns.trim() || null,
      expectations:
        clerkingExpectations.trim() || null,
    }

    return {
      presenting_complaints: [
        {
          complaint:
            clerkingComplaint.trim() || 'Not documented',
          duration:
            clerkingComplaintDuration.trim() || 'Not documented',
        },
      ],

      history_of_presenting_complaint:
        clerkingHistory.trim() || null,

      review_of_systems:
        clerkingReviewOfSystems.trim() || null,

      past_medical_history:
        clerkingPastMedicalHistory.trim() || null,

      past_surgical_history:
        clerkingPastSurgicalHistory.trim() || null,

      drug_history:
        clerkingDrugHistory.trim() || null,

      allergies:
        clerkingAllergies.trim() || null,

      family_history:
        clerkingFamilyHistory.trim() || null,

      social_history:
        clerkingSocialHistory.trim() || null,

      personal_history:
        clerkingPersonalHistory.trim() || null,

      gynaecological_history:
        clerkingGynaecologicalHistory.trim() || null,

      obstetric_history:
        clerkingObstetricHistory.trim() || null,

      menstrual_history:
        clerkingMenstrualHistory.trim() || null,

      sexual_history:
        clerkingSexualHistory.trim() || null,

      patient_perspective:
        patientPerspective,

      examination,

      assessment: {
        working_diagnosis:
          noteWorkingDiagnosis.trim() || null,

        differentials:
          noteDifferentials
            .split('\n')
            .map(item => item.trim())
            .filter(Boolean),
      },

      investigations:
        clerkingInvestigations
          .split('\n')
          .map(item => item.trim())
          .filter(Boolean),

      plan:
        notePlan.trim() || null,
    }
  }


  function progressNoteContent(): Record<string, unknown> {
    return {
      subjective:
        noteSubjective.trim() || null,

      objective:
        noteObjective.trim() || null,

      assessment: {
        working_diagnosis:
          noteWorkingDiagnosis.trim() || null,

        differentials:
          noteDifferentials
            .split('\n')
            .map(item => item.trim())
            .filter(Boolean),
      },

      plan:
        notePlan.trim() || null,
    }
  }


  function doctorNoteDocumentType():
    | 'INITIAL_CLERKING'
    | 'PROGRESS_NOTE' {
    return selectedEpisode?.status === 'ADMITTED'
      ? 'PROGRESS_NOTE'
      : 'INITIAL_CLERKING'
  }


  async function loadProgressNote(
    encounterId: string,
  ) {
    setLoadingProgressNote(true)

    try {
      const documents =
        await listEncounterClinicalDocuments(
          accessToken,
          encounterId,
        )

      const documentType =
        doctorNoteDocumentType()

      const candidates =
        documents.filter(
          document =>
            document.document_type === documentType,
        )

      const latest =
        candidates.sort(
          (a, b) => b.version - a.version,
        )[0] ?? null

      if (latest) {
        setProgressNote(latest)

        if (documentType === 'INITIAL_CLERKING') {
          loadInitialClerkingContent(
            latest,
          )
        } else {
          loadProgressNoteContent(
            latest,
          )
        }
      } else {
        setProgressNote(null)

        if (documentType === 'INITIAL_CLERKING') {
          resetInitialClerking()
        } else {
          resetProgressNote()
        }
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load progress note.',
      )
    } finally {
      setLoadingProgressNote(false)
    }
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

    setNoteObjective(current => {
      const trimmed = current.trim()

      return trimmed
        ? `${trimmed}

Vitals: ${formatted}`
        : `Vitals: ${formatted}`
    })

    setSuccess(
      'Latest vitals added to Objective.',
    )
  }


  async function saveProgressNote() {
    if (!selectedEncounter) {
      return
    }

    if (selectedEncounter.status !== 'OPEN') {
      setError(
        'Clinical documents cannot be edited on a closed Encounter.',
      )
      return
    }

    setSavingProgressNote(true)
    setError(null)
    setSuccess(null)

    if (!currentStaffId) {
      setSavingProgressNote(false)
      setError(
        'Authenticated user does not have a Staff profile.',
      )
      return
    }

    const content =
      doctorNoteDocumentType() === 'INITIAL_CLERKING'
        ? initialClerkingContent()
        : progressNoteContent()

    try {
      let saved: ClinicalDocument

      if (
        progressNote &&
        progressNote.status === 'DRAFT'
      ) {
        saved =
          await updateClinicalDocument(
            accessToken,
            progressNote.id,
            currentStaffId,
            content,
          )
      } else {
        saved =
          await createClinicalDocument(
            accessToken,
            {
              encounter_id:
                selectedEncounter.id,

              document_type:
                doctorNoteDocumentType(),

              authored_by:
                currentStaffId,

              content,
            },
          )
      }

      setProgressNote(saved)

      if (
        saved.document_type ===
        'INITIAL_CLERKING'
      ) {
        loadInitialClerkingContent(
          saved,
        )
      } else {
        loadProgressNoteContent(
          saved,
        )
      }

      await refreshEncounterContext(
        selectedEncounter.id,
      )

      setSuccess(
        doctorNoteDocumentType() === 'INITIAL_CLERKING'
          ? 'Initial clerking draft saved.'
          : 'Progress note draft saved.',
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to save progress note.',
      )
    } finally {
      setSavingProgressNote(false)
    }
  }


  function closeHistoricalViewer() {
    resetHistoricalEpisode()
  }


  async function admitSelectedEpisode() {
    if (
      !selectedEpisode ||
      !selectedEncounter
    ) {
      return
    }

    if (
      progressNote?.document_type !==
      'INITIAL_CLERKING' ||
      progressNote.status !== 'SIGNED'
    ) {
      setError(
        'Initial Clerking must be signed before admission.',
      )
      return
    }

    setAdmittingEpisode(true)
    setError(null)
    setSuccess(null)

    try {
      const admitted =
        await admitEpisode(
          accessToken,
          selectedEpisode.id,
          selectedEncounter.id,
        )

      setSelectedEpisode(
        admitted,
      )

      const [
        clinicResults,
        wardResults,
      ] = await Promise.all([
        listDoctorClinicQueue(
          accessToken,
        ),
        listDoctorWardQueue(
          accessToken,
        ),
      ])

      setClinicQueue(
        clinicResults,
      )

      setWardQueue(
        wardResults,
      )

      await refreshEncounterContext(
        selectedEncounter.id,
      )

      setSuccess(
        'Patient admitted to the ward.',
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to admit patient.',
      )
    } finally {
      setAdmittingEpisode(false)
    }
  }


  async function handleOrderInvestigations() {
    if (
      !selectedEpisode ||
      !selectedEncounter
    ) {
      return
    }

    const investigationOrders =
      orders.filter(
        order =>
          order.order_type === 'LABORATORY' ||
          order.order_type === 'RADIOLOGY',
      )

    if (investigationOrders.length === 0) {
      setError(
        'Add at least one laboratory or radiology order before completing the consultation.',
      )
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
              'ORDER_INVESTIGATIONS',
          },
        )

      setSelectedEpisode(
        updatedEpisode,
      )

      await refreshEncounterContext(
        selectedEncounter.id,
      )

      const [
        clinicResults,
        wardResults,
      ] = await Promise.all([
        listDoctorClinicQueue(
          accessToken,
        ),
        listDoctorWardQueue(
          accessToken,
        ),
      ])

      setClinicQueue(
        clinicResults,
      )

      setWardQueue(
        wardResults,
      )

      setSuccess(
        'Consultation completed. Patient is awaiting investigations.',
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


  async function signProgressNote() {
    if (
      !progressNote ||
      progressNote.status !== 'DRAFT'
    ) {
      return
    }

    setSigningProgressNote(true)
    setError(null)
    setSuccess(null)

    try {
      const signed =
        await signClinicalDocument(
          accessToken,
          progressNote.id,
        )

      setProgressNote(signed)

      await refreshEncounterContext(
        selectedEncounter?.id ?? signed.encounter_id,
      )

      setSuccess(
        'Progress note signed successfully.',
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to sign progress note.',
      )
    } finally {
      setSigningProgressNote(false)
    }
  }


  async function searchDiagnoses(
    query: string,
  ) {
    setDiagnosisQuery(query)
    setSelectedDiagnosis(null)

    if (!query.trim()) {
      setDiagnosisResults([])
      return
    }

    try {
      const results =
        await searchDiagnosisTerminology(
          accessToken,
          query,
          {
            system: 'ICD-10-CM',
            limit: 10,
          },
        )

      setDiagnosisResults(results)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to search diagnoses.',
      )
    }
  }


  async function saveVitals() {
    if (!selectedEncounter) {
      return
    }

    const numericValue = (
      value: string,
    ): number | undefined => {
      const trimmed = value.trim()

      if (!trimmed) {
        return undefined
      }

      const parsed = Number(trimmed)

      return Number.isFinite(parsed)
        ? parsed
        : undefined
    }

    const payload = {
      encounter_id:
        selectedEncounter.id,

      occurred_at:
        new Date().toISOString(),

      temperature:
        numericValue(temperature),

      heart_rate:
        numericValue(heartRate),

      respiratory_rate:
        numericValue(respiratoryRate),

      systolic_bp:
        numericValue(systolicBp),

      diastolic_bp:
        numericValue(diastolicBp),

      spo2:
        numericValue(spo2),

      weight:
        numericValue(weight),
    }

    const measurements = [
      payload.temperature,
      payload.heart_rate,
      payload.respiratory_rate,
      payload.systolic_bp,
      payload.diastolic_bp,
      payload.spo2,
      payload.weight,
    ]

    if (
      measurements.every(
        value => value === undefined,
      )
    ) {
      setError(
        'Enter at least one vital sign.',
      )
      return
    }

    setSavingVitals(true)
    setError(null)
    setSuccess(null)

    try {
      await createVitals(
        accessToken,
        payload,
      )

      await refreshEncounterContext(
        selectedEncounter.id,
      )

      setTemperature('')
      setHeartRate('')
      setRespiratoryRate('')
      setSystolicBp('')
      setDiastolicBp('')
      setSpo2('')
      setWeight('')

      setSuccess('Vital signs recorded.')
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to record vital signs.',
      )
    } finally {
      setSavingVitals(false)
    }
  }


  async function cancelOrder(
    orderId: string,
  ) {
    setCancellingOrderId(orderId)
    setError(null)
    setSuccess(null)

    try {
      const cancelled =
        await cancelClinicalOrder(
          accessToken,
          orderId,
        )

      await refreshEncounterContext(
        selectedEncounter?.id ?? cancelled.encounter_id,
      )

      setSuccess('Clinical order cancelled.')
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to cancel clinical order.',
      )
    } finally {
      setCancellingOrderId(null)
    }
  }




  function handleLaboratoryTestChange(
    testId: string,
  ) {
    setSelectedLaboratoryTestId(testId)

    if (!testId) {
      setOrderTestCode('')
      setOrderTestName('')
      return
    }

    const test =
      laboratoryTests.find(
        candidate =>
          candidate.id === testId,
      )

    if (!test) {
      setOrderTestCode('')
      setOrderTestName('')
      return
    }

    setOrderTestCode(test.code)
    setOrderTestName(test.name)
  }


  async function saveOrder() {
    if (!selectedEncounter) {
      return
    }

    setSavingOrder(true)
    setError(null)
    setSuccess(null)

    try {
      if (orderType === 'MEDICATION') {
        const medicine =
          prescriptionMedicine.trim()

        const dose =
          orderDose.trim()

        const route =
          prescriptionRoute.trim()

        const frequency =
          prescriptionFrequency.trim()

        if (!medicine) {
          setError(
            'Enter the medicine name.',
          )
          return
        }

        if (!dose) {
          setError(
            'Enter the dose.',
          )
          return
        }

        if (!route) {
          setError(
            'Select the administration route.',
          )
          return
        }

        if (!frequency) {
          setError(
            'Enter the frequency.',
          )
          return
        }

        await createPrescription(
          accessToken,
          {
            encounter_id:
              selectedEncounter.id,

            priority:
              orderPriority,

            medicine_name:
              medicine,

            strength:
              prescriptionStrength.trim() ||
              null,

            dose,

            dose_unit:
              prescriptionDoseUnit.trim() ||
              null,

            route,

            frequency,

            duration:
              prescriptionDuration.trim() ||
              null,

            duration_unit:
              prescriptionDurationUnit.trim() ||
              null,

            quantity:
              prescriptionQuantity.trim() ||
              null,

            directions:
              prescriptionDirections.trim() ||
              null,

            indication:
              prescriptionIndication.trim() ||
              null,
          },
        )

        await refreshEncounterContext(
          selectedEncounter.id,
        )

        setPrescriptionMedicine('')
        setPrescriptionStrength('')
        setOrderDose('')
        setPrescriptionDoseUnit('')
        setPrescriptionRoute('')
        setPrescriptionFrequency('')
        setPrescriptionDuration('')
        setPrescriptionDurationUnit('')
        setPrescriptionQuantity('')
        setPrescriptionDirections('')
        setPrescriptionIndication('')

        setSuccess(
          'Prescription created successfully.',
        )

        return
      }

      let details: Record<string, unknown>

      if (orderType === 'LABORATORY') {
        if (!selectedLaboratoryTestId) {
          setError(
            'Select a laboratory investigation from the catalogue.',
          )
          return
        }

        const selectedTest =
          laboratoryTests.find(
            test =>
              test.id === selectedLaboratoryTestId,
          )

        if (!selectedTest) {
          setError(
            'Selected laboratory investigation could not be found.',
          )
          return
        }

        details = {
          test_code:
            selectedTest.code,

          test_name:
            selectedTest.name,
        }
      } else {
        details = {
          study_code:
            orderStudyCode.trim(),
        }
      }

      await createClinicalOrder(
        accessToken,
        {
          encounter_id:
            selectedEncounter.id,

          order_type:
            orderType,

          priority:
            orderPriority,

          details,
        },
      )

      await refreshEncounterContext(
        selectedEncounter.id,
      )

      setOrderTestCode('')
      setOrderTestName('')
      setOrderStudyCode('')

      setSuccess(
        'Clinical order created.',
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : orderType === 'MEDICATION'
            ? 'Unable to create prescription.'
            : 'Unable to create clinical order.',
      )
    } finally {
      setSavingOrder(false)
    }
  }


  async function saveDiagnosis() {
    if (
      !selectedEncounter ||
      !selectedDiagnosis
    ) {
      return
    }

    setSavingDiagnosis(true)
    setError(null)
    setSuccess(null)

    try {
      await createClinicalDiagnosis(
        accessToken,
        {
            encounter_id:
              selectedEncounter.id,
            diagnosis_name:
              selectedDiagnosis.display_name,
            code_system:
              selectedDiagnosis.system,
            code:
              selectedDiagnosis.code,
            diagnosis_type:
              diagnosisType,
            certainty,
          },
        )

      await refreshEncounterContext(
        selectedEncounter.id,
      )

      setDiagnosisQuery('')
      setDiagnosisResults([])
      setSelectedDiagnosis(null)

      setSuccess('Diagnosis recorded.')
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to record diagnosis.',
      )
    } finally {
      setSavingDiagnosis(false)
    }
  }


  return (
    <section className="doctor-workspace">
      <div className="workspace-header">
        <div>
          <p className="eyebrow">
            Clinical workspace
          </p>
          <h1>Doctor Workspace</h1>
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
        <>
          <section className="doctor-patient-banner">
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

          <NursingHandoffPanel
            encounter={nursingEncounter}
            document={nursingDocument}
            loading={loadingNursingHandoff}
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

          {doctorNoteDocumentType() === 'INITIAL_CLERKING' ? (
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

              workingDiagnosis={
                noteWorkingDiagnosis
              }
              differentials={
                noteDifferentials
              }
              investigations={
                clerkingInvestigations
              }
              plan={notePlan}

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

              onWorkingDiagnosisChange={
                setNoteWorkingDiagnosis
              }
              onDifferentialsChange={
                setNoteDifferentials
              }
              onInvestigationsChange={
                setClerkingInvestigations
              }
              onPlanChange={
                setNotePlan
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

          <DiagnosisPanel
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

          </div>

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

            orderType={orderType}
            orderPriority={orderPriority}

            laboratoryTests={
              laboratoryTests
            }
            selectedLaboratoryTestId={
              selectedLaboratoryTestId
            }
            orderTestCode={
              orderTestCode
            }
            orderTestName={
              orderTestName
            }
            orderStudyCode={
              orderStudyCode
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
            onOrderTestCodeChange={
              setOrderTestCode
            }
            onOrderTestNameChange={
              setOrderTestName
            }
            onOrderStudyCodeChange={
              setOrderStudyCode
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
                      'SIGNED' ||
                    !orders.some(
                      order =>
                        order.order_type ===
                          'LABORATORY' ||
                        order.order_type ===
                          'RADIOLOGY',
                    )
                  }
                  onClick={() =>
                    void handleOrderInvestigations()
                  }
                >
                  {completingConsultation
                    ? 'Completing...'
                    : 'Order Investigations & Complete Consultation'}
                </button>
              </section>
            )}

          {selectedEncounter.title ===
            'Doctor Review' && (
              <section className="workspace-panel">
                <div className="panel-header">
                  <div>
                    <h2>
                      Investigation Results
                    </h2>

                    <p>
                      Results available for clinical review.
                    </p>
                  </div>
                </div>

                {loadingClinicalResults && (
                  <p>
                    Loading investigation results...
                  </p>
                )}

                {!loadingClinicalResults &&
                  clinicalResults.length === 0 && (
                    <p>
                      No investigation results recorded.
                    </p>
                  )}

                {!loadingClinicalResults &&
                  clinicalResults.map(
                    result => {
                      const order =
                        orders.find(
                          candidate =>
                            candidate.id ===
                            result.order_id,
                        )

                      if (!order) {
                        return null
                      }

                      return (
                        <article
                          key={result.id}
                          className="workspace-panel clinical-result-report"
                        >
                          <div className="clinical-result-report-header">
                            <div>
                              <strong>
                                {getInvestigationLabel(
                                  order,
                                )}
                              </strong>

                              <span>
                                {order.order_type}
                                {' · '}
                                {order.priority}
                              </span>

                              <span>
                                Recorded{' '}
                                {new Date(
                                  result.recorded_at,
                                ).toLocaleString()}
                              </span>
                            </div>

                            <span className={
                              result.status === 'FINAL'
                                ? 'clinical-result-status final'
                                : 'clinical-result-status draft'
                            }>
                              {result.status}
                            </span>
                          </div>

                          <div className="clinical-result-report-meta">
                            <div>
                              <span>
                                Specimen
                              </span>

                              <strong>
                                {result.specimen ??
                                  'Not recorded'}
                              </strong>
                            </div>

                            <div>
                              <span>
                                Collected
                              </span>

                              <strong>
                                {result.collected_at
                                  ? new Date(
                                      result.collected_at,
                                    ).toLocaleString()
                                  : 'Not recorded'}
                              </strong>
                            </div>

                            <div>
                              <span>
                                Reported
                              </span>

                              <strong>
                                {result.reported_at
                                  ? new Date(
                                      result.reported_at,
                                    ).toLocaleString()
                                  : 'Not recorded'}
                              </strong>
                            </div>
                          </div>

                          <div className="clinical-result-table">
                            <div className="clinical-result-table-header">
                              <span>
                                Analyte
                              </span>

                              <span>
                                Result
                              </span>

                              <span>
                                Unit
                              </span>

                              <span>
                                Reference
                              </span>

                              <span>
                                Flag
                              </span>
                            </div>

                            {result.values.length === 0 ? (
                              <p>
                                No structured result values recorded.
                              </p>
                            ) : (
                              result.values.map(
                                value => (
                                  <div
                                    key={value.id}
                                    className="clinical-result-table-row"
                                  >
                                    <span>
                                      <strong>
                                        {value.analyte_name}
                                      </strong>

                                      <small>
                                        {value.analyte_code}
                                      </small>
                                    </span>

                                    <strong>
                                      {formatResultValue(
                                        value.value,
                                      )}
                                    </strong>

                                    <span>
                                      {value.unit ??
                                        '—'}
                                    </span>

                                    <span>
                                      {value.reference_text ??
                                        (
                                          value.reference_low !== null &&
                                          value.reference_high !== null
                                            ? `${value.reference_low}–${value.reference_high}`
                                            : value.reference_low !== null
                                              ? `≥ ${value.reference_low}`
                                              : value.reference_high !== null
                                                ? `≤ ${value.reference_high}`
                                                : '—'
                                        )}
                                    </span>

                                    <span>
                                      {value.abnormal_flag ??
                                        '—'}
                                    </span>
                                  </div>
                                ),
                              )
                            )}
                          </div>

                          <div className="clinical-result-interpretation">
                            <span>
                              Interpretation
                            </span>

                            <p>
                              {result.interpretation ??
                                'No interpretation recorded.'}
                            </p>
                          </div>
                        </article>
                      )
                    },
                  )}
              </section>
            )}

        </>
      )}
    </section>
  )
}
