import {
  useCallback,
  useEffect,
  useState,
} from 'react'

import {
  listNursingQueue,
  type Episode,
} from '../../../api/episodes'

import {
  getPatient,
} from '../../../api/patients'


interface UseNursingQueueProps {
  accessToken: string

  onError: (
    message: string,
  ) => void
}


export function useNursingQueue({
  accessToken,
  onError,
}: UseNursingQueueProps) {
  const [episodes, setEpisodes] =
    useState<Episode[]>([])

  const [patientNames, setPatientNames] =
    useState<Record<string, string>>({})

  const [loading, setLoading] =
    useState(true)


  const loadQueue =
    useCallback(
      async () => {
        setLoading(true)
        onError('')

        try {
          const response =
            await listNursingQueue(
              accessToken,
            )

          const uniquePatientIds = [
            ...new Set(
              response.map(
                episode =>
                  episode.patient_id,
              ),
            ),
          ]

          const patientResults =
            await Promise.all(
              uniquePatientIds.map(
                async patientId => {
                  const patient =
                    await getPatient(
                      accessToken,
                      patientId,
                    )

                  const name = [
                    patient.first_name,
                    patient.middle_name,
                    patient.last_name,
                  ]
                    .filter(Boolean)
                    .join(' ')

                  return [
                    patientId,
                    name,
                  ] as const
                },
              ),
            )

          setPatientNames(
            Object.fromEntries(
              patientResults,
            ),
          )

          setEpisodes(
            response,
          )
        } catch (err) {
          setEpisodes([])
          setPatientNames({})

          onError(
            err instanceof Error
              ? err.message
              : 'Unable to load the nursing queue.',
          )
        } finally {
          setLoading(false)
        }
      },
      [
        accessToken,
        onError,
      ],
    )


  useEffect(() => {
    void loadQueue()
  }, [loadQueue])


  return {
    episodes,
    patientNames,
    loading,
    loadQueue,
    setEpisodes,
  }
}
