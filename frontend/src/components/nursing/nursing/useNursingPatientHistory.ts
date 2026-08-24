import {
  useCallback,
  useState,
} from 'react'

import {
  listPatientEpisodes,
} from '../../../api/episodes'

import {
  getEncounterTimeline,
  listEpisodeEncounters,
  type ClinicalEvent,
  type Encounter,
} from '../../../api/encounters'

import {
  getPatient,
} from '../../../api/patients'

import type {
  Episode,
} from '../../../api/episodes'

import type {
  Patient,
} from '../../../types'


export interface PreviousVisit {
  episode: Episode

  encounters: Encounter[]

  eventsByEncounter: Record<
    string,
    ClinicalEvent[]
  >
}


interface UseNursingPatientHistoryProps {
  accessToken: string

  onError: (
    message: string,
  ) => void
}


export function useNursingPatientHistory({
  accessToken,
  onError,
}: UseNursingPatientHistoryProps) {
  const [patient, setPatient] =
    useState<Patient | null>(null)

  const [loadingPatient, setLoadingPatient] =
    useState(false)

  const [previousEpisodes, setPreviousEpisodes] =
    useState<Episode[]>([])

  const [
    loadingPreviousEpisodes,
    setLoadingPreviousEpisodes,
  ] = useState(false)

  const [previousVisits, setPreviousVisits] =
    useState<PreviousVisit[]>([])

  const [
    loadingPreviousVisits,
    setLoadingPreviousVisits,
  ] = useState(false)


  const loadPatient =
    useCallback(
      async (
        patientId: string,
      ) => {
        setLoadingPatient(true)

        try {
          const result =
            await getPatient(
              accessToken,
              patientId,
            )

          setPatient(result)
        } catch (err) {
          setPatient(null)

          onError(
            err instanceof Error
              ? err.message
              : 'Unable to load patient information.',
          )
        } finally {
          setLoadingPatient(false)
        }
      },
      [
        accessToken,
        onError,
      ],
    )


  const loadPreviousVisits =
    useCallback(
      async (
        episodesToLoad: Episode[],
      ) => {
        if (
          episodesToLoad.length === 0
        ) {
          setPreviousVisits([])
          return
        }

        setLoadingPreviousVisits(true)

        try {
          const visits =
            await Promise.all(
              episodesToLoad.map(
                async episode => {
                  const encounters =
                    await listEpisodeEncounters(
                      accessToken,
                      episode.id,
                    )

                  const timelineEntries =
                    await Promise.all(
                      encounters.map(
                        async encounter => {
                          const events =
                            await getEncounterTimeline(
                              accessToken,
                              encounter.id,
                            )

                          return [
                            encounter.id,
                            events,
                          ] as const
                        },
                      ),
                    )

                  const eventsByEncounter =
                    Object.fromEntries(
                      timelineEntries,
                    )

                  return {
                    episode,
                    encounters,
                    eventsByEncounter,
                  }
                },
              ),
            )

          setPreviousVisits(
            visits,
          )
        } catch (err) {
          setPreviousVisits([])

          onError(
            err instanceof Error
              ? err.message
              : 'Unable to load previous clinical history.',
          )
        } finally {
          setLoadingPreviousVisits(false)
        }
      },
      [
        accessToken,
        onError,
      ],
    )


  const loadPreviousEpisodes =
    useCallback(
      async (
        patientId: string,
        currentEpisodeId: string,
      ) => {
        setLoadingPreviousEpisodes(true)

        try {
          const response =
            await listPatientEpisodes(
              accessToken,
              patientId,
            )

          const previous =
            response
              .filter(
                item =>
                  item.id !==
                  currentEpisodeId,
              )
              .sort(
                (a, b) =>
                  new Date(
                    b.opened_at,
                  ).getTime() -
                  new Date(
                    a.opened_at,
                  ).getTime(),
              )

          setPreviousEpisodes(
            previous,
          )

          await loadPreviousVisits(
            previous,
          )
        } catch (err) {
          setPreviousEpisodes([])

          onError(
            err instanceof Error
              ? err.message
              : 'Unable to load previous patient visits.',
          )
        } finally {
          setLoadingPreviousEpisodes(false)
        }
      },
      [
        accessToken,
        loadPreviousVisits,
        onError,
      ],
    )


  function clearPatientHistory() {
    setPatient(null)
    setPreviousEpisodes([])
    setPreviousVisits([])
  }


  return {
    patient,
    loadingPatient,

    previousEpisodes,
    loadingPreviousEpisodes,

    previousVisits,
    loadingPreviousVisits,

    loadPatient,
    loadPreviousEpisodes,
    clearPatientHistory,
  }
}
