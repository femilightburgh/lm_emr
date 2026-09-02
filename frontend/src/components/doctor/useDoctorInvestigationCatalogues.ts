/**
 * LIGHTBURGH EMR
 *
 * Doctor Investigation Catalogues Hook
 *
 * Purpose
 * -------
 * Owns laboratory and diagnostic investigation catalogues.
 *
 * Responsibilities
 * ----------------
 * - Load laboratory tests.
 * - Load diagnostic investigations.
 * - Report catalogue loading errors to the parent.
 */

import {
  useEffect,
  useState,
} from 'react'

import {
  listLaboratoryTests,
  type LaboratoryTest,
} from '../../api/laboratory'

import {
  listDiagnosticInvestigations,
  type DiagnosticInvestigation,
} from '../../api/diagnostics'

interface Props {
  accessToken: string
  onError?: (message: string) => void
}

export function useDoctorInvestigationCatalogues({
  accessToken,
  onError,
}: Props) {
  const [laboratoryTests, setLaboratoryTests] =
    useState<LaboratoryTest[]>([])

  const [diagnosticInvestigations, setDiagnosticInvestigations] =
    useState<DiagnosticInvestigation[]>([])

  useEffect(() => {
    let cancelled = false

    async function loadInvestigationCatalogues() {
      try {
        const [
          laboratoryTestResults,
          diagnosticInvestigationResults,
        ] = await Promise.all([
          listLaboratoryTests(
            accessToken,
          ),
          listDiagnosticInvestigations(
            accessToken,
          ),
        ])

        if (!cancelled) {
          setLaboratoryTests(
            laboratoryTestResults,
          )

          setDiagnosticInvestigations(
            diagnosticInvestigationResults,
          )
        }
      } catch (err) {
        if (!cancelled) {
          onError?.(
            err instanceof Error
              ? err.message
              : 'Unable to load investigation catalogues.',
          )
        }
      }
    }

    void loadInvestigationCatalogues()

    return () => {
      cancelled = true
    }
  }, [accessToken, onError])

  return {
    laboratoryTests,
    diagnosticInvestigations,
  }
}
