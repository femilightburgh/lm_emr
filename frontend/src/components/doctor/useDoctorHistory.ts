/**
 * LIGHTBURGH EMR
 *
 * Doctor History Hook
 *
 * Purpose
 * -------
 * Owns historical encounter viewer state and loading.
 *
 * Responsibilities
 * ----------------
 * - Load historical episode encounters.
 * - Load historical encounter context.
 * - Manage historical viewer state.
 * - Report history loading errors to the parent.
 */

import {
  useState,
} from 'react'

import {
  listEpisodeEncounters,
  type ClinicalEvent,
  type Encounter,
} from '../../api/encounters'

import type {
  Episode,
} from '../../api/episodes'

import type {
  ClinicalDiagnosis,
} from '../../api/diagnoses'

import type {
  ClinicalDocument,
} from '../../api/clinicalDocuments'

import type {
  ClinicalOrder,
} from '../../api/clinicalOrders'

import type {
  Vitals,
} from '../../api/vitals'

import {
  loadHistoricalEncounterContext,
} from './doctorPatientHistory'

interface Props {
  accessToken: string
  onError?: (message: string) => void
  clearError?: () => void
}

export function useDoctorHistory({
  accessToken,
  onError,
  clearError,
}: Props) {
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

  async function openHistoricalEpisode(
    episode: Episode,
  ) {
    setLoadingHistorical(true)
    clearError?.()

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

      onError?.(
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
    clearError?.()

    try {
      const context =
        await loadHistoricalEncounterContext(
          accessToken,
          encounter,
        )

      setSelectedHistoricalEncounter(
        context.encounter,
      )

      setHistoricalDocuments(
        context.documents,
      )

      setHistoricalDiagnoses(
        context.diagnoses,
      )

      setHistoricalOrders(
        context.orders,
      )

      setHistoricalVitals(
        context.vitals,
      )

      setHistoricalTimeline(
        context.timeline,
      )
    } catch (err) {
      onError?.(
        err instanceof Error
          ? err.message
          : 'Unable to load historical encounter.',
      )
    } finally {
      setLoadingHistorical(false)
    }
  }

  function closeHistoricalViewer() {
    resetHistoricalEpisode()
  }

  return {
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
  }
}
