/**
 * LIGHTBURGH EMR
 *
 * Doctor Nursing Handoff Hook
 *
 * Purpose
 * -------
 * Owns nursing handoff state and loading.
 *
 * Responsibilities
 * ----------------
 * - Resolve the latest Nursing Intake encounter.
 * - Load the signed nursing intake document.
 * - Load nursing vitals.
 * - Report loading errors to the parent.
 */

import {
  useState,
} from 'react'

import type {
  Encounter,
} from '../../api/encounters'

import {
  listEncounterClinicalDocuments,
  type ClinicalDocument,
} from '../../api/clinicalDocuments'

import {
  listEncounterVitals,
  type Vitals,
} from '../../api/vitals'

interface Props {
  accessToken: string
  onError?: (message: string) => void
}

export function useDoctorNursingHandoff({
  accessToken,
  onError,
}: Props) {
  const [nursingEncounter, setNursingEncounter] =
    useState<Encounter | null>(null)

  const [nursingDocument, setNursingDocument] =
    useState<ClinicalDocument | null>(null)

  const [nursingVitals, setNursingVitals] =
    useState<Vitals[]>([])

  const [loadingNursingHandoff, setLoadingNursingHandoff] =
    useState(false)

  function resetNursingHandoff() {
    setNursingEncounter(null)
    setNursingDocument(null)
    setNursingVitals([])
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

      onError?.(
        err instanceof Error
          ? err.message
          : 'Unable to load nursing handoff.',
      )
    } finally {
      setLoadingNursingHandoff(false)
    }
  }

  return {
    nursingEncounter,
    nursingDocument,
    nursingVitals,
    loadingNursingHandoff,
    resetNursingHandoff,
    loadNursingHandoff,
  }
}
