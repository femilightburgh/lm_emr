import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  createClinicalOrder,
} from '../../api/clinicalOrders'

import {
  useDoctorOrders,
} from './useDoctorOrders'

vi.mock('../../api/clinicalOrders', () => ({
  cancelClinicalOrder: vi.fn(),
  createClinicalOrder: vi.fn(),
}))

vi.mock('../../api/prescriptions', () => ({
  createPrescription: vi.fn(),
}))

describe('useDoctorOrders', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    vi.mocked(createClinicalOrder).mockResolvedValue(
      {} as Awaited<ReturnType<typeof createClinicalOrder>>,
    )
  })

  it('creates one grouped laboratory order for multiple selected tests', async () => {
    const selectedEncounter = {
      id: 'encounter-1',
    } as Parameters<
      typeof useDoctorOrders
    >[0]['selectedEncounter']

    const laboratoryTests = [
      {
        id: 'lab-cbc',
        code: 'CBC',
        name: 'Full Blood Count',
      },
      {
        id: 'lab-eucr',
        code: 'EUCR',
        name: 'Electrolytes, Urea and Creatinine',
      },
      {
        id: 'lab-lft',
        code: 'LFT',
        name: 'Liver Function Test',
      },
    ] as Parameters<
      typeof useDoctorOrders
    >[0]['laboratoryTests']

    const refreshEncounterContext = vi.fn().mockResolvedValue(undefined)

    const { result } = renderHook(() =>
      useDoctorOrders({
        accessToken: 'test-token',
        selectedEpisode: null,
        selectedEncounter,
        laboratoryTests,
        diagnosticInvestigations: [],
        refreshEncounterContext,
      }),
    )

    act(() => {
      result.current.setSelectedLaboratoryTestIds([
        'lab-cbc',
        'lab-eucr',
        'lab-lft',
      ])
    })

    await act(async () => {
      await result.current.saveOrder()
    })

    expect(createClinicalOrder).toHaveBeenCalledTimes(1)

    expect(createClinicalOrder).toHaveBeenCalledWith(
      'test-token',
      {
        encounter_id: 'encounter-1',
        order_type: 'LABORATORY',
        priority: 'ROUTINE',
        details: {},
        items: [
          {
            laboratory_test_id: 'lab-cbc',
          },
          {
            laboratory_test_id: 'lab-eucr',
          },
          {
            laboratory_test_id: 'lab-lft',
          },
        ],
      },
    )

    expect(refreshEncounterContext).toHaveBeenCalledTimes(1)
    expect(refreshEncounterContext).toHaveBeenCalledWith(
      'encounter-1',
    )
  })
})
