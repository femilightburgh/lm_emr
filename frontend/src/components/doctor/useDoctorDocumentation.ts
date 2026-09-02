import {
  useCallback,
  useState,
} from 'react'

import type { ClinicalDocument } from '../../api/clinicalDocuments'

export interface InitialClerkingForm {
  complaint: string
  complaintDuration: string
  history: string
  reviewOfSystems: string
  pastMedicalHistory: string
  pastSurgicalHistory: string
  drugHistory: string
  allergies: string
  familyHistory: string
  socialHistory: string
  personalHistory: string
  gynaecologicalHistory: string
  obstetricHistory: string
  menstrualHistory: string
  sexualHistory: string
  ideas: string
  concerns: string
  expectations: string
  examGeneral: string
  examCardiovascular: string
  examRespiratory: string
  examAbdomen: string
  examNeurological: string
  examMusculoskeletal: string
  examGenitourinary: string
  examOther: string
  investigations: string
}

export interface ProgressNoteForm {
  subjective: string
  objective: string
  workingDiagnosis: string
  differentials: string
  plan: string
}

const emptyInitialClerking: InitialClerkingForm = {
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

const emptyProgressNote: ProgressNoteForm = {
  subjective: '',
  objective: '',
  workingDiagnosis: '',
  differentials: '',
  plan: '',
}

export function useDoctorDocumentation(
  episodeStatus: string | null | undefined,
) {
  const [progressNote, setProgressNote] =
    useState<ClinicalDocument | null>(null)

  const [initialClerking, setInitialClerking] =
    useState<InitialClerkingForm>(
      emptyInitialClerking,
    )

  const [progressNoteForm, setProgressNoteForm] =
    useState<ProgressNoteForm>(
      emptyProgressNote,
    )

  const updateInitialClerking =
    useCallback(
      <K extends keyof InitialClerkingForm>(
        field: K,
        value: InitialClerkingForm[K],
      ) => {
        setInitialClerking(current => ({
          ...current,
          [field]: value,
        }))
      },
      [],
    )

  const updateProgressNote =
    useCallback(
      <K extends keyof ProgressNoteForm>(
        field: K,
        value: ProgressNoteForm[K],
      ) => {
        setProgressNoteForm(current => ({
          ...current,
          [field]: value,
        }))
      },
      [],
    )

  const resetInitialClerking =
    useCallback(() => {
      setInitialClerking(emptyInitialClerking)
    }, [])

  const resetProgressNote =
    useCallback(() => {
      setProgressNote(null)
      setProgressNoteForm(emptyProgressNote)
    }, [])

  const loadProgressNoteContent =
    useCallback(
      (document: ClinicalDocument) => {
        const content = document.content

        let workingDiagnosis = ''
        let differentials = ''

        const assessment = content.assessment

        if (
          assessment &&
          typeof assessment === 'object' &&
          !Array.isArray(assessment)
        ) {
          const assessmentRecord =
            assessment as Record<string, unknown>

          workingDiagnosis =
            typeof assessmentRecord.working_diagnosis === 'string'
              ? assessmentRecord.working_diagnosis
              : ''

          const values =
            assessmentRecord.differentials

          differentials =
            Array.isArray(values)
              ? values.join('\\n')
              : ''
        }

        setProgressNoteForm({
          subjective:
            typeof content.subjective === 'string'
              ? content.subjective
              : '',
          objective:
            typeof content.objective === 'string'
              ? content.objective
              : '',
          workingDiagnosis,
          differentials,
          plan:
            typeof content.plan === 'string'
              ? content.plan
              : '',
        })
      },
      [],
    )

  const loadInitialClerkingContent =
    useCallback(
      (document: ClinicalDocument) => {
        const content = document.content

        const readString = (
          source: Record<string, unknown>,
          key: string,
        ) =>
          typeof source[key] === 'string'
            ? source[key] as string
            : ''

        const next: InitialClerkingForm = {
          ...emptyInitialClerking,
        }

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

          next.complaint =
            typeof complaintRecord.complaint === 'string'
              ? complaintRecord.complaint
              : ''

          next.complaintDuration =
            typeof complaintRecord.duration === 'string'
              ? complaintRecord.duration
              : ''
        }

        next.history = readString(
          content,
          'history_of_presenting_complaint',
        )

        next.reviewOfSystems =
          readString(content, 'review_of_systems')

        next.pastMedicalHistory =
          readString(content, 'past_medical_history')

        next.pastSurgicalHistory =
          readString(content, 'past_surgical_history')

        next.drugHistory =
          readString(content, 'drug_history')

        next.allergies =
          readString(content, 'allergies')

        next.familyHistory =
          readString(content, 'family_history')

        next.socialHistory =
          readString(content, 'social_history')

        next.personalHistory =
          readString(content, 'personal_history')

        next.gynaecologicalHistory =
          readString(
            content,
            'gynaecological_history',
          )

        next.obstetricHistory =
          readString(
            content,
            'obstetric_history',
          )

        next.menstrualHistory =
          readString(
            content,
            'menstrual_history',
          )

        next.sexualHistory =
          readString(
            content,
            'sexual_history',
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

          next.ideas =
            readString(
              perspectiveRecord,
              'ideas',
            )

          next.concerns =
            readString(
              perspectiveRecord,
              'concerns',
            )

          next.expectations =
            readString(
              perspectiveRecord,
              'expectations',
            )
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

          next.examGeneral =
            readString(
              examinationRecord,
              'general',
            )

          next.examCardiovascular =
            readString(
              examinationRecord,
              'cardiovascular',
            )

          next.examRespiratory =
            readString(
              examinationRecord,
              'respiratory',
            )

          next.examAbdomen =
            readString(
              examinationRecord,
              'abdomen',
            )

          next.examNeurological =
            readString(
              examinationRecord,
              'neurological',
            )

          next.examMusculoskeletal =
            readString(
              examinationRecord,
              'musculoskeletal',
            )

          next.examGenitourinary =
            readString(
              examinationRecord,
              'genitourinary',
            )

          next.examOther =
            readString(
              examinationRecord,
              'other',
            )
        }

        next.investigations =
          Array.isArray(content.investigations)
            ? content.investigations
                .filter(
                  item =>
                    typeof item === 'string',
                )
                .join('\\n')
            : ''

        setInitialClerking(next)

        const assessment =
          content.assessment

        if (
          assessment &&
          typeof assessment === 'object' &&
          !Array.isArray(assessment)
        ) {
          const assessmentRecord =
            assessment as Record<string, unknown>

          setProgressNoteForm(current => ({
            ...current,
            workingDiagnosis:
              typeof assessmentRecord.working_diagnosis === 'string'
                ? assessmentRecord.working_diagnosis
                : '',
            differentials:
              Array.isArray(
                assessmentRecord.differentials,
              )
                ? assessmentRecord.differentials
                    .filter(
                      item =>
                        typeof item === 'string',
                    )
                    .join('\\n')
                : '',
          }))
        }
      },
      [],
    )

  const initialClerkingContent =
    useCallback((): Record<string, unknown> => {
      const examination = {
        general:
          initialClerking.examGeneral.trim() || null,
        cardiovascular:
          initialClerking.examCardiovascular.trim() || null,
        respiratory:
          initialClerking.examRespiratory.trim() || null,
        abdomen:
          initialClerking.examAbdomen.trim() || null,
        neurological:
          initialClerking.examNeurological.trim() || null,
        musculoskeletal:
          initialClerking.examMusculoskeletal.trim() || null,
        genitourinary:
          initialClerking.examGenitourinary.trim() || null,
        other:
          initialClerking.examOther.trim() || null,
      }

      const patientPerspective = {
        ideas:
          initialClerking.ideas.trim() || null,
        concerns:
          initialClerking.concerns.trim() || null,
        expectations:
          initialClerking.expectations.trim() || null,
      }

      return {
        presenting_complaints: [
          {
            complaint:
              initialClerking.complaint.trim() ||
              'Not documented',
            duration:
              initialClerking.complaintDuration.trim() ||
              'Not documented',
          },
        ],

        history_of_presenting_complaint:
          initialClerking.history.trim() || null,

        review_of_systems:
          initialClerking.reviewOfSystems.trim() || null,

        past_medical_history:
          initialClerking.pastMedicalHistory.trim() || null,

        past_surgical_history:
          initialClerking.pastSurgicalHistory.trim() || null,

        drug_history:
          initialClerking.drugHistory.trim() || null,

        allergies:
          initialClerking.allergies.trim() || null,

        family_history:
          initialClerking.familyHistory.trim() || null,

        social_history:
          initialClerking.socialHistory.trim() || null,

        personal_history:
          initialClerking.personalHistory.trim() || null,

        gynaecological_history:
          initialClerking.gynaecologicalHistory.trim() ||
          null,

        obstetric_history:
          initialClerking.obstetricHistory.trim() || null,

        menstrual_history:
          initialClerking.menstrualHistory.trim() || null,

        sexual_history:
          initialClerking.sexualHistory.trim() || null,

        patient_perspective:
          patientPerspective,

        examination,

        assessment: {
          working_diagnosis:
            progressNoteForm.workingDiagnosis.trim() ||
            null,

          differentials:
            progressNoteForm.differentials
              .split('\\n')
              .map(item => item.trim())
              .filter(Boolean),
        },

        investigations:
          initialClerking.investigations
            .split('\\n')
            .map(item => item.trim())
            .filter(Boolean),

        plan:
          progressNoteForm.plan.trim() || null,
      }
    }, [
      initialClerking,
      progressNoteForm,
    ])

  const progressNoteContent =
    useCallback((): Record<string, unknown> => ({
      subjective:
        progressNoteForm.subjective.trim() || null,

      objective:
        progressNoteForm.objective.trim() || null,

      assessment: {
        working_diagnosis:
          progressNoteForm.workingDiagnosis.trim() ||
          null,

        differentials:
          progressNoteForm.differentials
            .split('\\n')
            .map(item => item.trim())
            .filter(Boolean),
      },

      plan:
        progressNoteForm.plan.trim() || null,
    }), [progressNoteForm])

  const doctorNoteDocumentType =
    useCallback(
      ():
        | 'INITIAL_CLERKING'
        | 'PROGRESS_NOTE' =>
        episodeStatus === 'ADMITTED'
          ? 'PROGRESS_NOTE'
          : 'INITIAL_CLERKING',
      [episodeStatus],
    )

  return {
    progressNote,
    setProgressNote,

    initialClerking,
    progressNoteForm,

    updateInitialClerking,
    updateProgressNote,

    resetInitialClerking,
    resetProgressNote,

    loadProgressNoteContent,
    loadInitialClerkingContent,

    initialClerkingContent,
    progressNoteContent,

    doctorNoteDocumentType,
  }
}
