import {
  useCallback,
  useState,
} from 'react'

import {
  createVitals,
  listEpisodeVitals,
  type Vitals,
} from '../../../api/vitals'

import {
  INITIAL_VITALS_FORM,
} from './constants'

import type {
  VitalsFormState,
} from './types'


interface UseNursingVitalsProps {
  accessToken: string

  onError: (
    message: string,
  ) => void

  onSuccess: (
    message: string,
  ) => void
}


export function useNursingVitals({
  accessToken,
  onError,
  onSuccess,
}: UseNursingVitalsProps) {
  const [recordedVitals, setRecordedVitals] =
    useState<Vitals[]>([])

  const [loadingVitals, setLoadingVitals] =
    useState(false)

  const [savingVitals, setSavingVitals] =
    useState(false)


  const loadRecordedVitals =
    useCallback(
      async (
        episodeId: string,
      ) => {
        setLoadingVitals(true)

        try {
          const response =
            await listEpisodeVitals(
              accessToken,
              episodeId,
            )

          setRecordedVitals(
            response,
          )
        } catch (err) {
          setRecordedVitals([])

          onError(
            err instanceof Error
              ? err.message
              : 'Unable to load recorded vital signs.',
          )
        } finally {
          setLoadingVitals(false)
        }
      },
      [
        accessToken,
        onError,
      ],
    )


  async function saveVitals(
    encounterId: string,
    vitals: VitalsFormState,
  ) {
    const hasValue =
      Object.values(vitals).some(
        value =>
          value.trim() !== '',
      )

    if (!hasValue) {
      onError(
        'Enter at least one vital sign.',
      )
      return
    }

    setSavingVitals(true)

    try {
      const created =
        await createVitals(
          accessToken,
          {
            encounter_id:
              encounterId,

            occurred_at:
              new Date().toISOString(),

            temperature:
              vitals.temperature
                ? Number(
                    vitals.temperature,
                  )
                : null,

            heart_rate:
              vitals.heart_rate
                ? Number(
                    vitals.heart_rate,
                  )
                : null,

            respiratory_rate:
              vitals.respiratory_rate
                ? Number(
                    vitals.respiratory_rate,
                  )
                : null,

            systolic_bp:
              vitals.systolic_bp
                ? Number(
                    vitals.systolic_bp,
                  )
                : null,

            diastolic_bp:
              vitals.diastolic_bp
                ? Number(
                    vitals.diastolic_bp,
                  )
                : null,

            spo2:
              vitals.spo2
                ? Number(
                    vitals.spo2,
                  )
                : null,

            weight:
              vitals.weight
                ? Number(
                    vitals.weight,
                  )
                : null,
          },
        )

      setRecordedVitals(
        current => [
          ...current,
          created,
        ],
      )

      onSuccess(
        'Vitals recorded successfully.',
      )

      return created
    } catch (err) {
      onError(
        err instanceof Error
          ? err.message
          : 'Unable to record vitals.',
      )
    } finally {
      setSavingVitals(false)
    }
  }


  function resetVitals() {
    return INITIAL_VITALS_FORM
  }


  function clearRecordedVitals() {
    setRecordedVitals([])
  }


  const latestVitals =
    recordedVitals.length > 0
      ? [...recordedVitals].sort(
          (a, b) =>
            new Date(b.occurred_at).getTime() -
            new Date(a.occurred_at).getTime(),
        )[0]
      : null


  return {
    recordedVitals,
    latestVitals,
    loadingVitals,
    savingVitals,
    loadRecordedVitals,
    saveVitals,
    resetVitals,
    clearRecordedVitals,
  }
}
