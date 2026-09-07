import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

import DiagnosisPanel from './DiagnosisPanel'

import type { TerminologyConcept } from '../../api/terminology'

describe('DiagnosisPanel', () => {

  it('allows the clinician to enter a diagnosis manually when no ICD-11 result is suitable', async () => {
    const user = userEvent.setup()

    const onEnterManualDiagnosis = vi.fn()

    render(
      <DiagnosisPanel
        diagnoses={[]}
        loading={false}
        saving={false}
        encounterClosed={false}
        eyebrow="ASSESSMENT"
        title="Assessment History"
        description="Record the clinician's current assessment."
        query="rare clinical condition"
        results={[]}
        selected={null}
        manualDiagnosis=""
        diagnosisSearchPerformed={true}
        diagnosisType="PROVISIONAL"
        certainty="SUSPECTED"
        onQueryChange={vi.fn()}
        onSelect={vi.fn()}
        onEnterManualDiagnosis={onEnterManualDiagnosis}
        onExitManualDiagnosis={vi.fn()}
        onManualDiagnosisChange={vi.fn()}
        onDiagnosisTypeChange={vi.fn()}
        onCertaintyChange={vi.fn()}
        onSave={vi.fn()}
      />,
    )

    expect(
      screen.getByText('No suitable ICD-11 diagnoses found.'),
    ).toBeInTheDocument()

    const manualButton = screen.getByRole('button', {
      name: 'Enter diagnosis manually',
    })

    expect(manualButton).toBeEnabled()

    await user.click(manualButton)

    expect(onEnterManualDiagnosis).toHaveBeenCalledTimes(1)
  })
  it('allows the clinician to select an ICD-11 diagnosis from search results', async () => {
    const user = userEvent.setup()

    const malaria: TerminologyConcept = {
      id: 'icd11-malaria',
      system: 'ICD-11',
      code: '1F40.Z',
      display_name: 'Malaria due to Plasmodium falciparum, unspecified',
      description: null,
      active: true,
    }

    const onSelect = vi.fn()

    render(
      <DiagnosisPanel
        diagnoses={[]}
        loading={false}
        saving={false}
        encounterClosed={false}
        eyebrow="ASSESSMENT"
        title="Assessment History"
        description="Record the clinician's current assessment."
        query="malaria"
        results={[malaria]}
        selected={null}
        manualDiagnosis=""
        diagnosisSearchPerformed={true}
        diagnosisType="PROVISIONAL"
        certainty="SUSPECTED"
        onQueryChange={vi.fn()}
        onSelect={onSelect}
        onEnterManualDiagnosis={vi.fn()}
        onExitManualDiagnosis={vi.fn()}
        onManualDiagnosisChange={vi.fn()}
        onDiagnosisTypeChange={vi.fn()}
        onCertaintyChange={vi.fn()}
        onSave={vi.fn()}
      />,
    )

    expect(
      screen.getByText(
        'Malaria due to Plasmodium falciparum, unspecified',
      ),
    ).toBeInTheDocument()

    expect(
      screen.getByText('ICD-11 · 1F40.Z'),
    ).toBeInTheDocument()

    await user.click(
      screen.getByRole('button', {
        name: /Malaria due to Plasmodium falciparum, unspecified/,
      }),
    )

    expect(onSelect).toHaveBeenCalledTimes(1)
    expect(onSelect).toHaveBeenCalledWith(malaria)
  })
})
