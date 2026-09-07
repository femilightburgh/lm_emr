import { renderHook, act, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import {
  createClinicalDiagnosis,
  type CreateClinicalDiagnosisRequest,
} from '../../api/diagnoses'

import type { Encounter } from '../../api/encounters'
import type { TerminologyConcept } from '../../api/terminology'

import { useDoctorDiagnosis } from './useDoctorDiagnosis'

vi.mock('../../api/diagnoses', () => ({
  createClinicalDiagnosis: vi.fn(),
}))

const mockedCreateClinicalDiagnosis =
  vi.mocked(createClinicalDiagnosis)

describe('useDoctorDiagnosis', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })


  it('persists a manual diagnosis without an ICD-11 code', async () => {
    const encounter = {
      id: 'encounter-456',
    } as Encounter

    const refreshEncounterContext = vi.fn()
      .mockResolvedValue(undefined)

    const resetDiagnosisSearch = vi.fn()

    mockedCreateClinicalDiagnosis.mockResolvedValueOnce(
      {} as Awaited<ReturnType<typeof createClinicalDiagnosis>>,
    )

    const { result } = renderHook(() =>
      useDoctorDiagnosis({
        accessToken: 'test-token',
        selectedEncounter: encounter,
        selectedDiagnosis: null,
        manualDiagnosis: 'Acute febrile illness',
        refreshEncounterContext,
        resetDiagnosisSearch,
      }),
    )

    await act(async () => {
      await result.current.saveDiagnosis()
    })

    expect(mockedCreateClinicalDiagnosis).toHaveBeenCalledTimes(1)

    expect(
      mockedCreateClinicalDiagnosis,
    ).toHaveBeenCalledWith(
      'test-token',
      {
        encounter_id: 'encounter-456',
        diagnosis_name: 'Acute febrile illness',
        code_system: null,
        code: null,
        diagnosis_type: 'PROVISIONAL',
        certainty: 'POSSIBLE',
      },
    )

    expect(
      refreshEncounterContext,
    ).toHaveBeenCalledWith('encounter-456')

    expect(
      resetDiagnosisSearch,
    ).toHaveBeenCalledTimes(1)
  })


  it('reports a diagnosis persistence error without resetting the entry', async () => {
    const encounter = {
      id: 'encounter-error',
    } as Encounter

    const malaria: TerminologyConcept = {
      id: 'icd11-malaria',
      system: 'ICD-11',
      code: '1F40.Z',
      display_name: 'Malaria due to Plasmodium falciparum, unspecified',
      description: null,
      active: true,
    }

    const refreshEncounterContext = vi.fn()
      .mockResolvedValue(undefined)

    const resetDiagnosisSearch = vi.fn()

    const onError = vi.fn()
    const onSuccess = vi.fn()

    mockedCreateClinicalDiagnosis.mockRejectedValueOnce(
      new Error('Unable to record diagnosis.'),
    )

    const { result } = renderHook(() =>
      useDoctorDiagnosis({
        accessToken: 'test-token',
        selectedEncounter: encounter,
        selectedDiagnosis: malaria,
        manualDiagnosis: '',
        refreshEncounterContext,
        resetDiagnosisSearch,
        onError,
        onSuccess,
      }),
    )

    await act(async () => {
      await result.current.saveDiagnosis()
    })

    expect(onError).toHaveBeenCalledWith(
      'Unable to record diagnosis.',
    )

    expect(
      refreshEncounterContext,
    ).not.toHaveBeenCalled()

    expect(
      resetDiagnosisSearch,
    ).not.toHaveBeenCalled()

    expect(onSuccess).not.toHaveBeenCalledWith(
      'Diagnosis recorded.',
    )

    expect(result.current.savingDiagnosis).toBe(false)
  })

  it('persists a selected ICD-11 diagnosis with its terminology code', async () => {
    const encounter = {
      id: 'encounter-123',
    } as Encounter

    const malaria: TerminologyConcept = {
      id: 'icd11-malaria',
      system: 'ICD-11',
      code: '1F40.Z',
      display_name: 'Malaria due to Plasmodium falciparum, unspecified',
      description: null,
      active: true,
    }

    const refreshEncounterContext = vi.fn()
      .mockResolvedValue(undefined)

    const resetDiagnosisSearch = vi.fn()

    const onSuccess = vi.fn()

    mockedCreateClinicalDiagnosis.mockResolvedValueOnce(
      {} as Awaited<ReturnType<typeof createClinicalDiagnosis>>,
    )

    const { result } = renderHook(() =>
      useDoctorDiagnosis({
        accessToken: 'test-token',
        selectedEncounter: encounter,
        selectedDiagnosis: malaria,
        manualDiagnosis: '',
        refreshEncounterContext,
        resetDiagnosisSearch,
        onSuccess,
      }),
    )

    await act(async () => {
      await result.current.saveDiagnosis()
    })

    const expectedPayload: CreateClinicalDiagnosisRequest = {
      encounter_id: 'encounter-123',
      diagnosis_name:
        'Malaria due to Plasmodium falciparum, unspecified',
      code_system: 'ICD-11',
      code: '1F40.Z',
      diagnosis_type: 'PROVISIONAL',
      certainty: 'POSSIBLE',
    }

    expect(mockedCreateClinicalDiagnosis).toHaveBeenCalledTimes(1)
    expect(mockedCreateClinicalDiagnosis).toHaveBeenCalledWith(
      'test-token',
      expectedPayload,
    )

    await waitFor(() => {
      expect(refreshEncounterContext).toHaveBeenCalledWith(
        'encounter-123',
      )
    })

    expect(resetDiagnosisSearch).toHaveBeenCalledTimes(1)
    expect(onSuccess).toHaveBeenCalledWith(
      'Diagnosis recorded.',
    )
    expect(result.current.savingDiagnosis).toBe(false)
  })
})
