/**
 * LIGHTBURGH EMR
 *
 * Doctor Queue Hook
 *
 * Purpose
 * -------
 * Owns doctor queue state and queue loading.
 *
 * Responsibilities
 * ----------------
 * - Load clinic and ward queues.
 * - Resolve the authenticated Staff profile.
 * - Refresh doctor queues after workflow actions.
 */

import {
  useEffect,
  useState,
} from 'react'

import {
  listDoctorClinicQueue,
  listDoctorWardQueue,
  type DoctorQueueItem,
} from '../../api/episodes'

import {
  getCurrentStaff,
} from '../../api/staff'

interface Props {
  accessToken: string
  onError?: (message: string) => void
}

export function useDoctorQueue({
  accessToken,
  onError,
}: Props) {
  const [clinicQueue, setClinicQueue] =
    useState<DoctorQueueItem[]>([])

  const [wardQueue, setWardQueue] =
    useState<DoctorQueueItem[]>([])

  const [currentStaffId, setCurrentStaffId] =
    useState<string | null>(null)

  const [loadingQueue, setLoadingQueue] =
    useState(false)

  async function refreshDoctorQueues() {
    const [
      clinicResults,
      wardResults,
    ] = await Promise.all([
      listDoctorClinicQueue(
        accessToken,
      ),
      listDoctorWardQueue(
        accessToken,
      ),
    ])

    setClinicQueue(
      clinicResults,
    )

    setWardQueue(
      wardResults,
    )
  }

  useEffect(() => {
    let cancelled = false

    async function loadQueue() {
      setLoadingQueue(true)

      try {
        const [
          currentStaff,
          clinicResults,
          wardResults,
        ] = await Promise.all([
          getCurrentStaff(
            accessToken,
          ),
          listDoctorClinicQueue(
            accessToken,
          ),
          listDoctorWardQueue(
            accessToken,
          ),
        ])

        if (!cancelled) {
          setCurrentStaffId(
            currentStaff.id,
          )

          setClinicQueue(
            clinicResults,
          )

          setWardQueue(
            wardResults,
          )
        }
      } catch (err) {
        if (!cancelled) {
          onError?.(
            err instanceof Error
              ? err.message
              : 'Unable to load doctor queues.',
          )
        }
      } finally {
        if (!cancelled) {
          setLoadingQueue(false)
        }
      }
    }

    void loadQueue()

    return () => {
      cancelled = true
    }
  }, [accessToken, onError])

  return {
    clinicQueue,
    wardQueue,
    currentStaffId,
    loadingQueue,
    refreshDoctorQueues,
  }
}
