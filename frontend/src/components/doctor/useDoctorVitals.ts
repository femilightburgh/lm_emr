/**
 * LIGHTBURGH EMR
 *
 * Doctor vital signs hook.
 *
 * Purpose
 * -------
 * Owns vital-sign entry state and persistence for the doctor workspace.
 *
 * Responsibilities
 * ----------------
 * - Maintain vital-sign entry fields.
 * - Validate vital-sign input.
 * - Save vital signs for the selected encounter.
 */

import {
  useState,
} from 'react'

import type { Encounter } from '../../api/encounters'

import {
  createVitals,
} from '../../api/vitals'

interface Props {
  accessToken: string
  selectedEncounter: Encounter | null
  refreshEncounterContext: (
    encounterId: string,
  ) => Promise<void>
  onError?: (message: string | null) => void
  onSuccess?: (message: string | null) => void
}

export function useDoctorVitals({
  accessToken,
  selectedEncounter,
  refreshEncounterContext,
  onError,
  onSuccess,
}: Props) {
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
      onError?.(
        'Enter at least one vital sign.',
      )
      return
    }

    setSavingVitals(true)
    onError?.(null)
    onSuccess?.(null)

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

      onSuccess?.(
        'Vital signs recorded.',
      )
    } catch (err) {
      onError?.(
        err instanceof Error
          ? err.message
          : 'Unable to record vital signs.',
      )
    } finally {
      setSavingVitals(false)
    }
  }

  return {
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
  }
}
