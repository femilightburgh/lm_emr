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
 * - Search ICD-10-CM diagnosis terminology.
 * - Track the current diagnosis search.
 * - Track the selected terminology concept.
 * - Report search errors to the parent.
 */

import {
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

  async function searchDiagnoses(
    query: string,
  ) {
    setDiagnosisQuery(query)
    setSelectedDiagnosis(null)

    if (!query.trim()) {
      setDiagnosisResults([])
      return
    }

    try {
      const results =
        await searchDiagnosisTerminology(
          accessToken,
          query,
          {
            system: 'ICD-10-CM',
            limit: 10,
          },
        )

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
    searchDiagnoses,
  }
}
