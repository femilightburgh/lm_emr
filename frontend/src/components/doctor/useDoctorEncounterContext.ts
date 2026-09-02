/**
 * LIGHTBURGH EMR
 *
 * Doctor Encounter Context Hook
 *
 * Purpose
 * -------
 * Owns encounter-level clinical context state and loading.
 *
 * Responsibilities
 * ----------------
 * - Hold the selected encounter and clinical context.
 * - Load encounter-level clinical data.
 * - Reset encounter context when switching encounters.
 */

import { useState } from 'react'

import type { ClinicalEvent, Encounter } from '../../api/encounters'
import type { ClinicalDiagnosis } from '../../api/diagnoses'
import type { ClinicalOrder } from '../../api/clinicalOrders'
import type { Vitals } from '../../api/vitals'
import type { ClinicalResult } from '../../api/clinicalResults'
import type { DiagnosticReport } from '../../api/diagnostics'

import {
  loadDoctorEncounterContext,
  type DoctorDiagnosticAttachment,
} from './doctorEncounterContext'

export function useDoctorEncounterContext(
  accessToken: string,
) {
  const [selectedEncounter, setSelectedEncounter] =
    useState<Encounter | null>(null)

  const [diagnoses, setDiagnoses] =
    useState<ClinicalDiagnosis[]>([])

  const [timeline, setTimeline] =
    useState<ClinicalEvent[]>([])

  const [orders, setOrders] =
    useState<ClinicalOrder[]>([])

  const [vitals, setVitals] =
    useState<Vitals[]>([])

  const [clinicalResults, setClinicalResults] =
    useState<ClinicalResult[]>([])

  const [diagnosticReports, setDiagnosticReports] =
    useState<DiagnosticReport[]>([])

  const [diagnosticAttachments, setDiagnosticAttachments] =
    useState<
      Record<
        string,
        DoctorDiagnosticAttachment[]
      >
    >({})

  const [loadingTimeline, setLoadingTimeline] =
    useState(false)

  const [loadingDiagnoses, setLoadingDiagnoses] =
    useState(false)

  const [loadingOrders, setLoadingOrders] =
    useState(false)

  const [loadingClinicalResults, setLoadingClinicalResults] =
    useState(false)

  function resetEncounterContext() {
    setSelectedEncounter(null)
    setDiagnoses([])
    setTimeline([])
    setOrders([])
    setVitals([])
    setClinicalResults([])
    setDiagnosticReports([])
    setDiagnosticAttachments({})
  }

  async function refreshEncounterData(
    encounterId: string,
  ) {
    setLoadingDiagnoses(true)
    setLoadingTimeline(true)
    setLoadingOrders(true)
    setLoadingClinicalResults(true)

    try {
      const context =
        await loadDoctorEncounterContext(
          accessToken,
          encounterId,
        )

      setSelectedEncounter(
        context.encounter,
      )

      setDiagnoses(
        context.diagnoses,
      )

      setTimeline(
        context.timeline,
      )

      setOrders(
        context.orders,
      )

      setVitals(
        context.vitals,
      )

      setClinicalResults(
        context.clinicalResults,
      )

      setDiagnosticReports(
        context.diagnosticReports,
      )

      setDiagnosticAttachments(
        context.diagnosticAttachments,
      )
    } finally {
      setLoadingDiagnoses(false)
      setLoadingTimeline(false)
      setLoadingOrders(false)
      setLoadingClinicalResults(false)
    }
  }

  return {
    selectedEncounter,
    setSelectedEncounter,
    resetEncounterContext,
    refreshEncounterData,
    diagnoses,
    timeline,
    loadingTimeline,
    loadingDiagnoses,
    orders,
    vitals,
    clinicalResults,
    diagnosticReports,
    diagnosticAttachments,
    loadingClinicalResults,
    loadingOrders,
  }
}
