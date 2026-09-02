/**
 * LIGHTBURGH EMR
 *
 * Doctor Episode Actions Hook
 *
 * Purpose
 * -------
 * Owns episode-level lifecycle actions used by the Doctor Workspace.
 *
 * Responsibilities
 * ----------------
 * - Admit a selected episode after Initial Clerking is signed.
 * - Complete an open Ward Review with a disposition.
 * - Track episode action loading state.
 */

import {
  useState,
  type Dispatch,
  type SetStateAction,
} from 'react'

import {
  admitEpisode,
  completeWardReview as completeWardReviewRequest,
  type Episode,
  type WardReviewDisposition,
} from '../../api/episodes'

import type {
  Encounter,
} from '../../api/encounters'

interface Props {
  accessToken: string
  selectedEpisode: Episode | null
  selectedEncounter: Encounter | null
  initialClerkingSigned: boolean
  setSelectedEpisode: Dispatch<
    SetStateAction<Episode | null>
  >
  setSelectedEncounter: Dispatch<
    SetStateAction<Encounter | null>
  >
  refreshDoctorQueues: () => Promise<void>
  refreshEncounterContext: (
    encounterId: string,
  ) => Promise<void>
  onError?: (message: string) => void
  onSuccess?: (message: string) => void
  clearError?: () => void
  clearSuccess?: () => void
}

export function useDoctorEpisodeActions({
  accessToken,
  selectedEpisode,
  selectedEncounter,
  initialClerkingSigned,
  setSelectedEpisode,
  setSelectedEncounter,
  refreshDoctorQueues,
  refreshEncounterContext,
  onError,
  onSuccess,
  clearError,
  clearSuccess,
}: Props) {
  const [admittingEpisode, setAdmittingEpisode] =
    useState(false)

  const [closingEncounter, setClosingEncounter] =
    useState(false)

async function admitSelectedEpisode() {
  if (
    !selectedEpisode ||
    !selectedEncounter
  ) {
    return
  }

  if (!initialClerkingSigned) {
    onError?.(
      'Initial Clerking must be signed before admission.',
    )
    return
  }


  setAdmittingEpisode(true)
  clearError?.()
  clearSuccess?.()

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

    await refreshDoctorQueues()

    await refreshEncounterContext(
      selectedEncounter.id,
    )

    onSuccess?.(
      'Patient admitted to the ward.',
    )
  } catch (err) {
    onError?.(
      err instanceof Error
        ? err.message
        : 'Unable to admit patient.',
    )
  } finally {
    setAdmittingEpisode(false)
  }
}

async function completeWardReview(
  disposition: WardReviewDisposition,
  details: string | null,
) {
  if (
    !selectedEncounter ||
    selectedEncounter.title !== 'Ward Review' ||
    selectedEncounter.status !== 'OPEN' ||
    !selectedEpisode ||
    selectedEpisode.status !== 'ADMITTED'
  ) {
    return
  }

  setClosingEncounter(true)
  clearError?.()
  clearSuccess?.()

  try {
    const updatedEpisode = await completeWardReviewRequest(
      accessToken,
      selectedEpisode.id,
      {
        encounter_id: selectedEncounter.id,
        disposition,
        details,
      },
    )

    setSelectedEpisode(updatedEpisode)
    await refreshDoctorQueues()

    setSelectedEncounter(null)
    setSelectedEpisode(null)

    onSuccess?.(
      'Ward Review completed and encounter signed out.',
    )
  } catch (err) {
    onError?.(
      err instanceof Error
        ? err.message
        : 'Unable to complete Ward Review.',
    )
  } finally {
    setClosingEncounter(false)
  }
}

  return {
    admittingEpisode,
    admitSelectedEpisode,
    closingEncounter,
    completeWardReview,
  }
}
