/**
 * LIGHTBURGH EMR
 *
 * Doctor Orders Hook
 *
 * Purpose
 * -------
 * Owns Doctor Workspace clinical order form state and order actions.
 *
 * Responsibilities
 * ----------------
 * - Manage clinical order and prescription form state.
 * - Create clinical orders and prescriptions.
 * - Cancel clinical orders.
 * - Resolve catalogue selections into order details.
 */

import {
  useState,
} from 'react'

import {
  cancelClinicalOrder,
  createClinicalOrder,
  type ClinicalOrderType,
} from '../../api/clinicalOrders'

import {
  createPrescription,
} from '../../api/prescriptions'

import type {
  Episode,
} from '../../api/episodes'

import type {
  Encounter,
} from '../../api/encounters'

import type {
  LaboratoryTest,
} from '../../api/laboratory'

import type {
  DiagnosticInvestigation,
} from '../../api/diagnostics'

interface Props {
  accessToken: string
  selectedEpisode: Episode | null
  selectedEncounter: Encounter | null
  laboratoryTests: LaboratoryTest[]
  diagnosticInvestigations: DiagnosticInvestigation[]
  refreshEncounterContext: (
    encounterId: string,
  ) => Promise<void>
  onError?: (message: string) => void
  onSuccess?: (message: string) => void
  clearError?: () => void
  clearSuccess?: () => void
}

export function useDoctorOrders({
  accessToken,
  selectedEpisode,
  selectedEncounter,
  laboratoryTests,
  diagnosticInvestigations,
  refreshEncounterContext,
  onError,
  onSuccess,
  clearError,
  clearSuccess,
}: Props) {

const [savingOrder, setSavingOrder] =
  useState(false)

const [cancellingOrderId, setCancellingOrderId] =
  useState<string | null>(null)

const [orderType, setOrderType] =
  useState<ClinicalOrderType>('LABORATORY')

const [orderPriority, setOrderPriority] =
  useState('ROUTINE')

const [orderTestCode, setOrderTestCode] =
  useState('')

const [orderTestName, setOrderTestName] =
  useState('')

const [orderStudyCode, setOrderStudyCode] =
  useState('')

const [orderMedicationId, setOrderMedicationId] =
  useState('')

const [orderDose, setOrderDose] =
  useState('')

const [prescriptionMedicine, setPrescriptionMedicine] =
  useState('')

const [prescriptionStrength, setPrescriptionStrength] =
  useState('')

const [prescriptionDoseUnit, setPrescriptionDoseUnit] =
  useState('')

const [prescriptionRoute, setPrescriptionRoute] =
  useState('')

const [prescriptionFrequency, setPrescriptionFrequency] =
  useState('')

const [inpatientTreatmentStart, setInpatientTreatmentStart] =
  useState('')

const [inpatientFirstDose, setInpatientFirstDose] =
  useState('')

const [prescriptionDuration, setPrescriptionDuration] =
  useState('')

const [prescriptionDurationUnit, setPrescriptionDurationUnit] =
  useState('')

const [prescriptionQuantity, setPrescriptionQuantity] =
  useState('')

const [prescriptionDirections, setPrescriptionDirections] =
  useState('')

const [prescriptionIndication, setPrescriptionIndication] =
  useState('')

const [selectedLaboratoryTestIds, setSelectedLaboratoryTestIds] =
  useState<string[]>([])

const [selectedDiagnosticInvestigationId, setSelectedDiagnosticInvestigationId] =
  useState('')

const [customLaboratoryInvestigation, setCustomLaboratoryInvestigation] =
  useState('')

const [customDiagnosticInvestigation, setCustomDiagnosticInvestigation] =
  useState('')

async function cancelOrder(
  orderId: string,
) {
  setCancellingOrderId(orderId)
  clearError?.()
  clearSuccess?.()

  try {
    const cancelled =
      await cancelClinicalOrder(
        accessToken,
        orderId,
      )

    await refreshEncounterContext(
      selectedEncounter?.id ?? cancelled.encounter_id,
    )

    onSuccess?.('Clinical order cancelled.')
  } catch (err) {
    onError?.(
      err instanceof Error
        ? err.message
        : 'Unable to cancel clinical order.',
    )
  } finally {
    setCancellingOrderId(null)
  }
}




function handleLaboratoryTestChange(
  testId: string,
) {
  setSelectedLaboratoryTestIds(
    current =>
      current.includes(testId)
        ? current.filter(id => id !== testId)
        : [...current, testId],
  )

  const nextIds = selectedLaboratoryTestIds.includes(testId)
    ? selectedLaboratoryTestIds.filter(id => id !== testId)
    : [...selectedLaboratoryTestIds, testId]

  const firstTest =
    laboratoryTests.find(
      test => test.id === nextIds[0],
    )

  setOrderTestCode(firstTest?.code ?? '')
  setOrderTestName(firstTest?.name ?? '')
}


function handleDiagnosticInvestigationChange(
  investigationId: string,
) {
  setSelectedDiagnosticInvestigationId(
    investigationId,
  )
}


async function saveOrder() {
  if (!selectedEncounter) {
    return
  }

  setSavingOrder(true)
  clearError?.()
  clearSuccess?.()

  try {
    if (orderType === 'MEDICATION') {
      const medicine =
        prescriptionMedicine.trim()

      const dose =
        orderDose.trim()

      const route =
        prescriptionRoute.trim()

      const frequency =
        prescriptionFrequency.trim()

      if (!medicine) {
        onError?.(
          'Enter the medicine name.',
        )
        return
      }

      if (!dose) {
        onError?.(
          'Enter the dose.',
        )
        return
      }

      if (!route) {
        onError?.(
          'Select the administration route.',
        )
        return
      }

      if (!frequency) {
        onError?.(
          'Enter the frequency.',
        )
        return
      }

      await createPrescription(
        accessToken,
        {
          encounter_id:
            selectedEncounter.id,

          priority:
            orderPriority,

          medicine_name:
            medicine,

          strength:
            prescriptionStrength.trim() ||
            null,

          dose,

          dose_unit:
            prescriptionDoseUnit.trim() ||
            null,

          route,

          frequency,

          duration:
            prescriptionDuration.trim() ||
            null,

          duration_unit:
            prescriptionDurationUnit.trim() ||
            null,

          quantity:
            prescriptionQuantity.trim() ||
            null,

          directions:
            prescriptionDirections.trim() ||
            null,

          indication:
            prescriptionIndication.trim() ||
            null,

          start_at:
            selectedEpisode?.status === 'ADMITTED' &&
            inpatientTreatmentStart
              ? new Date(
                  inpatientTreatmentStart,
                ).toISOString()
              : null,

          first_dose_at:
            selectedEpisode?.status === 'ADMITTED' &&
            inpatientFirstDose
              ? new Date(
                  inpatientFirstDose,
                ).toISOString()
              : null,
        },
      )

      await refreshEncounterContext(
        selectedEncounter.id,
      )

      setPrescriptionMedicine('')
      setPrescriptionStrength('')
      setOrderDose('')
      setPrescriptionDoseUnit('')
      setPrescriptionRoute('')
      setPrescriptionFrequency('')
      setPrescriptionDuration('')
      setPrescriptionDurationUnit('')
      setPrescriptionQuantity('')
      setPrescriptionDirections('')
      setPrescriptionIndication('')

      onSuccess?.(
        'Prescription created successfully.',
      )

      return
    }

    let details: Record<string, unknown>

    if (orderType === 'LABORATORY') {
      const customName =
        customLaboratoryInvestigation.trim()

      if (
        selectedLaboratoryTestIds.length === 0 &&
        !customName
      ) {
        onError?.(
          'Select at least one laboratory investigation or enter a custom investigation.',
        )
        return
      }

      const selectedTests =
        selectedLaboratoryTestIds.map(testId =>
          laboratoryTests.find(
            test => test.id === testId,
          ),
        )

      if (selectedTests.some(test => !test)) {
        onError?.(
          'One or more selected laboratory investigations could not be found.',
        )
        return
      }

      const items = [
        ...selectedTests
          .filter(
            (
              selectedTest,
            ): selectedTest is LaboratoryTest =>
              selectedTest !== undefined,
          )
          .map(
            selectedTest => ({
              laboratory_test_id:
                selectedTest.id,
            }),
          ),
        ...(customName
          ? [{ custom_name: customName }]
          : []),
      ]

      await createClinicalOrder(
        accessToken,
        {
          encounter_id:
            selectedEncounter.id,

          order_type:
            orderType,

          priority:
            orderPriority,

          details: {},

          items,
        },
      )

      await refreshEncounterContext(
        selectedEncounter.id,
      )

      setOrderTestCode('')
      setOrderTestName('')
      setSelectedLaboratoryTestIds([])
      setCustomLaboratoryInvestigation('')

      onSuccess?.(
        items.length === 1
          ? 'Clinical order created.'
          : `Clinical order created with ${items.length} investigations.`,
      )

      return
    } else if (orderType === 'DIAGNOSTIC') {
      const customName =
        customDiagnosticInvestigation.trim()

      if (
        !selectedDiagnosticInvestigationId &&
        !customName
      ) {
        onError?.(
          'Select a diagnostic investigation or enter a custom investigation.',
        )
        return
      }

      const selectedInvestigation =
        selectedDiagnosticInvestigationId
          ? diagnosticInvestigations.find(
              investigation =>
                investigation.id ===
                selectedDiagnosticInvestigationId,
            )
          : undefined

      if (
        selectedDiagnosticInvestigationId &&
        !selectedInvestigation
      ) {
        onError?.(
          'Selected diagnostic investigation could not be found.',
        )
        return
      }

      details = {}

      const items = [
        ...(selectedInvestigation
          ? [
              {
                diagnostic_investigation_id:
                  selectedInvestigation.id,
              },
            ]
          : []),
        ...(customName
          ? [{ custom_name: customName }]
          : []),
      ]

      await createClinicalOrder(
        accessToken,
        {
          encounter_id:
            selectedEncounter.id,

          order_type:
            orderType,

          priority:
            orderPriority,

          details,

          items,
        },
      )

      await refreshEncounterContext(
        selectedEncounter.id,
      )

      setSelectedDiagnosticInvestigationId('')
      setCustomDiagnosticInvestigation('')

      onSuccess?.(
        items.length === 1
          ? 'Clinical order created.'
          : `Clinical order created with ${items.length} investigations.`,
      )

      return
    } else {
      details = {
        study_code:
          orderStudyCode.trim(),
      }
    }

    await createClinicalOrder(
      accessToken,
      {
        encounter_id:
          selectedEncounter.id,

        order_type:
          orderType,

        priority:
          orderPriority,

        details,
      },
    )

    await refreshEncounterContext(
      selectedEncounter.id,
    )

    setOrderTestCode('')
    setOrderTestName('')
    setOrderStudyCode('')
    setSelectedDiagnosticInvestigationId('')

    onSuccess?.(
      'Clinical order created.',
    )
  } catch (err) {
    onError?.(
      err instanceof Error
        ? err.message
        : orderType === 'MEDICATION'
          ? 'Unable to create prescription.'
          : 'Unable to create clinical order.',
    )
  } finally {
    setSavingOrder(false)
  }
}

  return {
    savingOrder,
    cancellingOrderId,

    orderType,
    setOrderType,
    orderPriority,
    setOrderPriority,

    selectedLaboratoryTestIds,
    setSelectedLaboratoryTestIds,
    selectedDiagnosticInvestigationId,
    setSelectedDiagnosticInvestigationId,

    customLaboratoryInvestigation,
    setCustomLaboratoryInvestigation,
    customDiagnosticInvestigation,
    setCustomDiagnosticInvestigation,

    orderTestCode,
    setOrderTestCode,
    orderTestName,
    setOrderTestName,
    orderMedicationId,
    setOrderMedicationId,
    orderDose,
    setOrderDose,

    prescriptionMedicine,
    setPrescriptionMedicine,
    prescriptionStrength,
    setPrescriptionStrength,
    prescriptionDoseUnit,
    setPrescriptionDoseUnit,
    prescriptionRoute,
    setPrescriptionRoute,
    prescriptionFrequency,
    setPrescriptionFrequency,

    inpatientTreatmentStart,
    setInpatientTreatmentStart,
    inpatientFirstDose,
    setInpatientFirstDose,

    prescriptionDuration,
    setPrescriptionDuration,
    prescriptionDurationUnit,
    setPrescriptionDurationUnit,
    prescriptionQuantity,
    setPrescriptionQuantity,
    prescriptionDirections,
    setPrescriptionDirections,
    prescriptionIndication,
    setPrescriptionIndication,

    handleLaboratoryTestChange,
    handleDiagnosticInvestigationChange,
    saveOrder,
    cancelOrder,
  }
}
