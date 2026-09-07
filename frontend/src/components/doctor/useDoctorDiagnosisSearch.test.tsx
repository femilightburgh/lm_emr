import { act, renderHook, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import {
  searchDiagnosisTerminology,
  type TerminologyConcept,
} from '../../api/terminology'

import { useDoctorDiagnosisSearch } from './useDoctorDiagnosisSearch'

vi.mock('../../api/terminology', () => ({
  searchDiagnosisTerminology: vi.fn(),
}))

const mockedSearchDiagnosisTerminology =
  vi.mocked(searchDiagnosisTerminology)

describe('useDoctorDiagnosisSearch', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })


  it('switches to manual diagnosis entry using the current search query', async () => {
    const { result } = renderHook(() =>
      useDoctorDiagnosisSearch({
        accessToken: 'test-token',
      }),
    )

    await act(async () => {
      await result.current.searchDiagnoses('rare clinical condition')
    })

    act(() => {
      result.current.enterManualDiagnosis()
    })

    expect(result.current.manualDiagnosis).toBe(
      'rare clinical condition',
    )
    expect(result.current.selectedDiagnosis).toBeNull()
    expect(result.current.diagnosisResults).toEqual([])
    expect(result.current.diagnosisSearchPerformed).toBe(false)
  })


  it('ignores an older search response when a newer search has started', async () => {
    let resolveMalaria:
      ((value: TerminologyConcept[]) => void) | undefined

    let resolveHypertension:
      ((value: TerminologyConcept[]) => void) | undefined

    const malaria: TerminologyConcept = {
      id: 'icd11-malaria',
      system: 'ICD-11',
      code: '1F40.Z',
      display_name: 'Malaria due to Plasmodium falciparum, unspecified',
      description: null,
      active: true,
    }

    const hypertension: TerminologyConcept = {
      id: 'icd11-hypertension',
      system: 'ICD-11',
      code: 'BA00.0',
      display_name: 'Combined diastolic and systolic hypertension',
      description: null,
      active: true,
    }

    mockedSearchDiagnosisTerminology
      .mockImplementationOnce(
        () =>
          new Promise(resolve => {
            resolveMalaria = resolve
          }),
      )
      .mockImplementationOnce(
        () =>
          new Promise(resolve => {
            resolveHypertension = resolve
          }),
      )

    const { result } = renderHook(() =>
      useDoctorDiagnosisSearch({
        accessToken: 'test-token',
      }),
    )

    let firstSearch: Promise<void>
    let secondSearch: Promise<void>

    await act(async () => {
      firstSearch = result.current.searchDiagnoses('malaria')
      secondSearch =
        result.current.searchDiagnoses('hypertension')
    })

    await act(async () => {
      resolveHypertension?.([hypertension])
      await secondSearch
    })

    expect(result.current.diagnosisResults).toEqual([
      hypertension,
    ])

    await act(async () => {
      resolveMalaria?.([malaria])
      await firstSearch
    })

    expect(result.current.diagnosisResults).toEqual([
      hypertension,
    ])
    expect(result.current.diagnosisQuery).toBe(
      'hypertension',
    )
  })

  it('searches ICD-11 terminology with the expected query and limit', async () => {
    const malaria: TerminologyConcept = {
      id: 'icd11-malaria',
      system: 'ICD-11',
      code: '1F40.Z',
      display_name: 'Malaria due to Plasmodium falciparum, unspecified',
      description: null,
      active: true,
    }

    mockedSearchDiagnosisTerminology.mockResolvedValueOnce([
      malaria,
    ])

    const { result } = renderHook(() =>
      useDoctorDiagnosisSearch({
        accessToken: 'test-token',
      }),
    )

    await act(async () => {
      await result.current.searchDiagnoses('malaria')
    })

    await waitFor(() => {
      expect(result.current.diagnosisResults).toEqual([
        malaria,
      ])
    })

    expect(
      mockedSearchDiagnosisTerminology,
    ).toHaveBeenCalledTimes(1)

    expect(
      mockedSearchDiagnosisTerminology,
    ).toHaveBeenCalledWith(
      'test-token',
      'malaria',
      {
        system: 'ICD-11',
        limit: 10,
      },
    )

    expect(result.current.diagnosisQuery).toBe('malaria')
    expect(result.current.diagnosisSearchPerformed).toBe(true)
  })
})
