/**
 * LIGHTBURGH EMR
 *
 * Doctor Clinical Documentation Hook
 *
 * Purpose
 * -------
 * Owns the clinical document API lifecycle for the doctor workspace.
 *
 * Responsibilities
 * ----------------
 * - Load the current doctor document for an encounter.
 * - Save clinical documentation drafts.
 * - Sign clinical documentation.
 */

import {
  useState,
} from 'react'

import {
  createClinicalDocument,
  listEncounterClinicalDocuments,
  signClinicalDocument,
  updateClinicalDocument,
  type ClinicalDocument,
} from '../../api/clinicalDocuments'

import type {
  Encounter,
} from '../../api/encounters'

interface Documentation {
  progressNote: ClinicalDocument | null

  setProgressNote: (
    document: ClinicalDocument | null,
  ) => void

  loadProgressNoteContent: (
    document: ClinicalDocument,
  ) => void

  loadInitialClerkingContent: (
    document: ClinicalDocument,
  ) => void

  resetProgressNote: () => void

  resetInitialClerking: () => void

  doctorNoteDocumentType: () =>
    'INITIAL_CLERKING' | 'PROGRESS_NOTE'

  initialClerkingContent: () =>
    Record<string, unknown>

  progressNoteContent: () =>
    Record<string, unknown>
}

interface Props {
  accessToken: string
  currentStaffId: string | null
  selectedEncounter: Encounter | null
  documentation: Documentation
  refreshEncounterData: (
    encounterId: string,
  ) => Promise<void>
  onError: (message: string | null) => void
  onSuccess: (message: string | null) => void
}

export function useDoctorClinicalDocumentation({
  accessToken,
  currentStaffId,
  selectedEncounter,
  documentation,
  refreshEncounterData,
  onError,
  onSuccess,
}: Props) {
  const {
    progressNote,
    setProgressNote,
    loadProgressNoteContent,
    loadInitialClerkingContent,
    resetProgressNote,
    resetInitialClerking,
    doctorNoteDocumentType,
    initialClerkingContent,
    progressNoteContent,
  } = documentation

  const [loadingProgressNote, setLoadingProgressNote] =
    useState(false)

  const [savingProgressNote, setSavingProgressNote] =
    useState(false)

  const [signingProgressNote, setSigningProgressNote] =
    useState(false)

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

        if (
          documentType === 'INITIAL_CLERKING'
        ) {
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

        if (
          documentType === 'INITIAL_CLERKING'
        ) {
          resetInitialClerking()
        } else {
          resetProgressNote()
        }
      }
    } catch (err) {
      onError(
        err instanceof Error
          ? err.message
          : 'Unable to load progress note.',
      )
    } finally {
      setLoadingProgressNote(false)
    }
  }

  async function saveProgressNote() {
    if (!selectedEncounter) {
      return
    }

    if (
      selectedEncounter.status !== 'OPEN'
    ) {
      onError(
        'Clinical documents cannot be edited on a closed Encounter.',
      )
      return
    }

    setSavingProgressNote(true)
    onError(null)
    onSuccess(null)

    if (!currentStaffId) {
      setSavingProgressNote(false)
      onError(
        'Authenticated user does not have a Staff profile.',
      )
      return
    }

    const content =
      doctorNoteDocumentType() ===
      'INITIAL_CLERKING'
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

      await refreshEncounterData(
        selectedEncounter.id,
      )

      onSuccess(
        doctorNoteDocumentType() ===
        'INITIAL_CLERKING'
          ? 'Initial clerking draft saved.'
          : 'Progress note draft saved.',
      )
    } catch (err) {
      onError(
        err instanceof Error
          ? err.message
          : 'Unable to save progress note.',
      )
    } finally {
      setSavingProgressNote(false)
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
    onError(null)
    onSuccess(null)

    try {
      const signed =
        await signClinicalDocument(
          accessToken,
          progressNote.id,
        )

      setProgressNote(signed)

      await refreshEncounterData(
        selectedEncounter?.id ??
          signed.encounter_id,
      )

      onSuccess(
        'Progress note signed successfully.',
      )
    } catch (err) {
      onError(
        err instanceof Error
          ? err.message
          : 'Unable to sign progress note.',
      )
    } finally {
      setSigningProgressNote(false)
    }
  }

  return {
    loadingProgressNote,
    savingProgressNote,
    signingProgressNote,
    loadProgressNote,
    saveProgressNote,
    signProgressNote,
  }
}
