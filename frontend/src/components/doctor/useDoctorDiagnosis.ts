/**
 * LIGHTBURGH EMR
 *
 * Doctor Diagnosis Hook
 *
 * Purpose
 * -------
 * Owns diagnosis classification and persistence for the doctor workspace.
 *
 * Responsibilities
 * ----------------
 * - Maintain diagnosis type and certainty.
 * - Save a selected diagnosis to the current encounter.
 * - Refresh encounter context after persistence.
 */

import {
  useState,
} from 'react'

import type { Encounter } from '../../api/encounters'
import {
  createClinicalDiagnosis,
  type DiagnosisCertainty,
  type DiagnosisType,
} from '../../api/diagnoses'
import type { TerminologyConcept } from '../../api/terminology'

interface Props {
  accessToken: string
  selectedEncounter: Encounter | null
  selectedDiagnosis: TerminologyConcept | null
  manualDiagnosis: string
  refreshEncounterContext: (
    encounterId: string,
  ) => Promise<void>
  resetDiagnosisSearch: () => void
  onError?: (message: string | null) => void
  onSuccess?: (message: string | null) => void
}

export function useDoctorDiagnosis({
  accessToken,
  selectedEncounter,
  selectedDiagnosis,
  manualDiagnosis,
  refreshEncounterContext,
  resetDiagnosisSearch,
  onError,
  onSuccess,
}: Props) {
  const [diagnosisType, setDiagnosisType] =
    useState<DiagnosisType>('PROVISIONAL')

  const [certainty, setCertainty] =
    useState<DiagnosisCertainty>('POSSIBLE')

  const [savingDiagnosis, setSavingDiagnosis] =
    useState(false)

  async function saveDiagnosis() {
    const manualDiagnosisName =
      manualDiagnosis.trim()

    if (
      !selectedEncounter ||
      (!selectedDiagnosis &&
        !manualDiagnosisName)
    ) {
      return
    }

    setSavingDiagnosis(true)
    onError?.(null)
    onSuccess?.(null)

    try {
      await createClinicalDiagnosis(
        accessToken,
        {
          encounter_id:
            selectedEncounter.id,

          diagnosis_name:
            selectedDiagnosis
              ? selectedDiagnosis.display_name
              : manualDiagnosisName,

          code_system:
            selectedDiagnosis
              ? selectedDiagnosis.system
              : null,

          code:
            selectedDiagnosis
              ? selectedDiagnosis.code
              : null,

          diagnosis_type:
            diagnosisType,

          certainty,
        },
      )

      await refreshEncounterContext(
        selectedEncounter.id,
      )

      resetDiagnosisSearch()

      onSuccess?.(
        'Diagnosis recorded.',
      )
    } catch (err) {
      onError?.(
        err instanceof Error
          ? err.message
          : 'Unable to record diagnosis.',
      )
    } finally {
      setSavingDiagnosis(false)
    }
  }

  return {
    diagnosisType,
    setDiagnosisType,

    certainty,
    setCertainty,

    savingDiagnosis,

    saveDiagnosis,
  }
}
