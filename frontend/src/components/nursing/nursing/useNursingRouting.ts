import {
  useCallback,
  useState,
} from 'react'

import {
  listDepartments,
  type Department,
} from '../../../api/departments'

import {
  routeEpisode,
} from '../../../api/episodes'


interface UseNursingRoutingProps {
  accessToken: string

  onError: (
    message: string,
  ) => void

  onSuccess: (
    message: string,
  ) => void
}


export function useNursingRouting({
  accessToken,
  onError,
  onSuccess,
}: UseNursingRoutingProps) {
  const [
    departments,
    setDepartments,
  ] = useState<Department[]>([])

  const [
    loadingDepartments,
    setLoadingDepartments,
  ] = useState(false)

  const [
    selectedDepartmentId,
    setSelectedDepartmentId,
  ] = useState('')

  const [
    patientRouted,
    setPatientRouted,
  ] = useState(false)

  const [
    routingPatient,
    setRoutingPatient,
  ] = useState(false)


  const loadDepartments =
    useCallback(
      async (
        hospitalId: string,
      ) => {
        setLoadingDepartments(true)
        onError('')

        try {
          const response =
            await listDepartments(
              accessToken,
              hospitalId,
            )

          const activeClinicalDepartments =
            response.filter(
              department =>
                department.status ===
                  'Active' &&
                department.category ===
                  'Clinical',
            )

          setDepartments(
            activeClinicalDepartments,
          )
        } catch (err) {
          setDepartments([])

          onError(
            err instanceof Error
              ? err.message
              : 'Unable to load hospital departments.',
          )
        } finally {
          setLoadingDepartments(false)
        }
      },
      [
        accessToken,
        onError,
      ],
    )


  async function routePatient(
    episodeId: string,
  ) {
    if (!selectedDepartmentId) {
      onError(
        'Select a department before routing the patient.',
      )
      return null
    }

    setRoutingPatient(true)
    onError('')

    try {
      const updated =
        await routeEpisode(
          accessToken,
          episodeId,
          selectedDepartmentId,
        )

      const department =
        departments.find(
          item =>
            item.id ===
            selectedDepartmentId,
        )

      setPatientRouted(true)

      onSuccess(
        department
          ? `Patient routed successfully to ${department.name}.`
          : 'Patient routed successfully.',
      )

      return updated
    } catch (err) {
      onError(
        err instanceof Error
          ? err.message
          : 'Unable to route patient.',
      )

      return null
    } finally {
      setRoutingPatient(false)
    }
  }


  function resetRouting() {
    setDepartments([])
    setSelectedDepartmentId('')
    setPatientRouted(false)
  }


  function clearSelection() {
    setSelectedDepartmentId('')
  }


  return {
    departments,
    loadingDepartments,
    selectedDepartmentId,
    patientRouted,
    routingPatient,

    loadDepartments,
    routePatient,

    setSelectedDepartmentId,

    resetRouting,
    clearSelection,
  }
}
