/**
 * LIGHTBURGH EMR
 *
 * Doctor patient context hook.
 *
 * Purpose
 * -------
 * Owns patient and episode history context used by the doctor workspace.
 *
 * Responsibilities
 * ----------------
 * - Maintain the selected patient's context data.
 * - Maintain current episode encounters.
 * - Load previous patient episodes.
 */

import {
  useState,
} from 'react'

import type { Encounter } from '../../api/encounters'
import type { Episode } from '../../api/episodes'
import type { Patient } from '../../api/patients'

import {
  loadPatientHistory,
} from './doctorPatientHistory'

interface Props {
  accessToken: string
  onError?: (message: string) => void
}

export function useDoctorPatientContext({
  accessToken,
  onError,
}: Props) {
  const [currentEpisodeEncounters, setCurrentEpisodeEncounters] =
    useState<Encounter[]>([])

  const [patient, setPatient] =
    useState<Patient | null>(null)

  const [loadingPatientContext, setLoadingPatientContext] =
    useState(false)

  const [previousEpisodes, setPreviousEpisodes] =
    useState<Episode[]>([])

  const [loadingPreviousEpisodes, setLoadingPreviousEpisodes] =
    useState(false)

  async function loadPreviousPatientEpisodes(
    patientId: string,
    currentEpisodeId: string,
  ) {
    setLoadingPreviousEpisodes(true)

    try {
      const episodes =
        await loadPatientHistory(
          accessToken,
          patientId,
        )

      setPreviousEpisodes(
   episodes.filter(
     episode =>
       episode.id !== currentEpisodeId,
   ),
 )
    } catch (err) {
      setPreviousEpisodes([])

      onError?.(
        err instanceof Error
          ? err.message
          : 'Unable to load previous encounters.',
      )
    } finally {
      setLoadingPreviousEpisodes(false)
    }
  }

  return {
    currentEpisodeEncounters,
    setCurrentEpisodeEncounters,

    patient,
    setPatient,

    loadingPatientContext,
    setLoadingPatientContext,

    previousEpisodes,
    setPreviousEpisodes,

    loadingPreviousEpisodes,
    setLoadingPreviousEpisodes,

    loadPreviousPatientEpisodes,
  }
}
