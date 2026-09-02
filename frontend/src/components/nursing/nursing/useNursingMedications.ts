import {
  useCallback,
  useState,
} from 'react'

import {
  getMedicationNursingSummary,
  recordMedicationAdministration,
  type MedicationAdministrationStatus,
  type MedicationNursingSummary,
} from '../../../api/medicationDoses'


interface UseNursingMedicationsProps {
  accessToken: string

  onError: (
    message: string,
  ) => void

  onSuccess: (
    message: string,
  ) => void
}


export function useNursingMedications({
  accessToken,
  onError,
  onSuccess,
}: UseNursingMedicationsProps) {
  const [
    medicationSummary,
    setMedicationSummary,
  ] = useState<MedicationNursingSummary | null>(
    null,
  )

  const [
    loadingMedications,
    setLoadingMedications,
  ] = useState(false)

  const [
    savingMedicationDoseId,
    setSavingMedicationDoseId,
  ] = useState<string | null>(null)


  const loadMedicationDoses =
    useCallback(
      async (
        episodeId: string,
      ) => {
        setLoadingMedications(true)

        try {
          const response =
            await getMedicationNursingSummary(
              accessToken,
              episodeId,
            )

          setMedicationSummary(
            response,
          )
        } catch (err) {
          setMedicationSummary(null)

          onError(
            err instanceof Error
              ? err.message
              : 'Unable to load medication summary.',
          )
        } finally {
          setLoadingMedications(false)
        }
      },
      [
        accessToken,
        onError,
      ],
    )


  const administerMedicationDose =
    useCallback(
      async (
        doseId: string,
        status: MedicationAdministrationStatus,
        reason?: string,
      ) => {
        setSavingMedicationDoseId(
          doseId,
        )

        try {
          await recordMedicationAdministration(
            accessToken,
            doseId,
            {
              status,
              administered_at:
                new Date().toISOString(),
              reason:
                reason?.trim() || null,
            },
          )

          onSuccess(
            'Medication administration recorded.',
          )

          return true
        } catch (err) {
          onError(
            err instanceof Error
              ? err.message
              : 'Unable to record medication administration.',
          )

          return false
        } finally {
          setSavingMedicationDoseId(
            null,
          )
        }
      },
      [
        accessToken,
        onError,
        onSuccess,
      ],
    )


  function clearMedicationDoses() {
    setMedicationSummary(null)
  }


  return {
    medicationSummary,
    loadingMedications,
    savingMedicationDoseId,
    loadMedicationDoses,
    administerMedicationDose,
    clearMedicationDoses,
  }
}
