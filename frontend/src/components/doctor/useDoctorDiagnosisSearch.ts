/**
 * LIGHTBURGH EMR
 *
 * Doctor Diagnosis Search Hook
 *
 * Purpose
 * -------
 * Owns diagnosis terminology search state.
 *
 * Responsibilities
 * ----------------
 * - Search ICD-11 diagnosis terminology.
 * - Track the current diagnosis search.
 * - Track the selected terminology concept.
 * - Report search errors to the parent.
 */

import {
  useRef,
  useState,
} from 'react'

import {
  searchDiagnosisTerminology,
  type TerminologyConcept,
} from '../../api/terminology'

interface Props {
  accessToken: string
  onError?: (message: string) => void
}

export function useDoctorDiagnosisSearch({
  accessToken,
  onError,
}: Props) {
  const [diagnosisQuery, setDiagnosisQuery] =
    useState('')

  const [diagnosisResults, setDiagnosisResults] =
    useState<TerminologyConcept[]>([])

  const [selectedDiagnosis, setSelectedDiagnosis] =
    useState<TerminologyConcept | null>(null)

  const [diagnosisSearchPerformed, setDiagnosisSearchPerformed] =
    useState(false)

  const [manualDiagnosis, setManualDiagnosis] =
    useState('')

  const searchRequestSequence =
    useRef(0)

  function enterManualDiagnosis() {
    searchRequestSequence.current += 1
    setSelectedDiagnosis(null)
    setDiagnosisResults([])
    setDiagnosisSearchPerformed(false)
    setManualDiagnosis(diagnosisQuery)
  }

  function selectDiagnosis(
    concept: TerminologyConcept,
  ) {
    searchRequestSequence.current += 1
    setManualDiagnosis('')
    setSelectedDiagnosis(concept)
  }

  function exitManualDiagnosis() {
    searchRequestSequence.current += 1
    setManualDiagnosis('')
    setSelectedDiagnosis(null)
    setDiagnosisQuery('')
    setDiagnosisResults([])
    setDiagnosisSearchPerformed(false)
  }

  async function searchDiagnoses(
    query: string,
  ) {
    const requestSequence =
      searchRequestSequence.current + 1

    searchRequestSequence.current =
      requestSequence

    setDiagnosisQuery(query)
    setSelectedDiagnosis(null)
    setManualDiagnosis('')

    if (!query.trim()) {
      setDiagnosisResults([])
      setDiagnosisSearchPerformed(false)
      return
    }

    setDiagnosisSearchPerformed(true)

    try {
      const results =
        await searchDiagnosisTerminology(
          accessToken,
          query,
          {
            system: 'ICD-11',
            limit: 10,
          },
        )

      if (
        searchRequestSequence.current !==
        requestSequence
      ) {
        return
      }

      setDiagnosisResults(results)
    } catch (err) {
      onError?.(
        err instanceof Error
          ? err.message
          : 'Unable to search diagnoses.',
      )
    }
  }

  return {
    diagnosisQuery,
    setDiagnosisQuery,
    diagnosisResults,
    setDiagnosisResults,
    selectedDiagnosis,
    setSelectedDiagnosis,
    manualDiagnosis,
    setManualDiagnosis,
    diagnosisSearchPerformed,
    enterManualDiagnosis,
    exitManualDiagnosis,
    selectDiagnosis,
    searchDiagnoses,
  }
}
