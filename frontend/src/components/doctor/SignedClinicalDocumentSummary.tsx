import type { ClinicalDocument } from '../../api/clinicalDocuments'


interface Props {
  document: ClinicalDocument | null
}


function stringValue(
  content: Record<string, unknown>,
  key: string,
): string {
  const value = content[key]

  return typeof value === 'string'
    ? value.trim()
    : ''
}


function listValue(
  content: Record<string, unknown>,
  key: string,
): string[] {
  const value = content[key]

  return Array.isArray(value)
    ? value.filter(
        item => typeof item === 'string',
      ) as string[]
    : []
}


function displayValue(
  value: string,
): string {
  return value || 'Not recorded'
}


function SummaryRow({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <div className="doctor-signed-document-row">
      <span>
        {label}
      </span>

      <strong>
        {displayValue(value)}
      </strong>
    </div>
  )
}


export default function SignedClinicalDocumentSummary({
  document,
}: Props) {
  if (
    !document ||
    document.status !== 'SIGNED'
  ) {
    return null
  }

  const content =
    document.content

  const assessment =
    content.assessment

  const assessmentRecord =
    assessment &&
    typeof assessment === 'object' &&
    !Array.isArray(assessment)
      ? assessment as Record<string, unknown>
      : {}

  const isInitialClerking =
    document.document_type ===
    'INITIAL_CLERKING'

  const workingDiagnosis =
    stringValue(
      assessmentRecord,
      'working_diagnosis',
    )

  const differentials =
    listValue(
      assessmentRecord,
      'differentials',
    )

  const investigations =
    listValue(
      content,
      'investigations',
    )

  const subjective =
    stringValue(
      content,
      'subjective',
    )

  const objective =
    stringValue(
      content,
      'objective',
    )

  const plan =
    stringValue(
      content,
      'plan',
    )

  const presentingComplaints =
    Array.isArray(
      content.presenting_complaints,
    )
      ? content.presenting_complaints.filter(
          item =>
            item &&
            typeof item === 'object' &&
            !Array.isArray(item),
        ) as Array<Record<string, unknown>>
      : []

  const presentingComplaintText =
    presentingComplaints
      .map(
        complaint => {
          const name =
            typeof complaint.complaint === 'string'
              ? complaint.complaint
              : ''

          const duration =
            typeof complaint.duration === 'string'
              ? complaint.duration
              : ''

          return duration
            ? `${name} (${duration})`
            : name
        },
      )
      .filter(Boolean)
      .join(', ')

  const history =
    stringValue(
      content,
      'history_of_presenting_complaint',
    )

  const patientPerspective = (() => {
    const perspective =
      content.patient_perspective

    if (
      !perspective ||
      typeof perspective !== 'object' ||
      Array.isArray(perspective)
    ) {
      return 'Not recorded'
    }

    const record =
      perspective as Record<string, unknown>

    return [
      typeof record.ideas === 'string'
        ? `Ideas: ${record.ideas}`
        : '',
      typeof record.concerns === 'string'
        ? `Concerns: ${record.concerns}`
        : '',
      typeof record.expectations === 'string'
        ? `Expectations: ${record.expectations}`
        : '',
    ]
      .filter(Boolean)
      .join(' · ') || 'Not recorded'
  })()

  const examination = (() => {
    const examination =
      content.examination

    if (
      !examination ||
      typeof examination !== 'object' ||
      Array.isArray(examination)
    ) {
      return 'Not recorded'
    }

    const record =
      examination as Record<string, unknown>

    return [
      ['General', record.general],
      ['Cardiovascular', record.cardiovascular],
      ['Respiratory', record.respiratory],
      ['Abdomen', record.abdomen],
      ['Neurological', record.neurological],
      ['Musculoskeletal', record.musculoskeletal],
      ['Genitourinary', record.genitourinary],
      ['Other', record.other],
    ]
      .filter(
        ([, value]) =>
          typeof value === 'string' &&
          value.trim(),
      )
      .map(
        ([label, value]) =>
          `${label}: ${value}`,
      )
      .join(' · ') || 'Not recorded'
  })()

  return (
    <section className="workspace-panel doctor-signed-document">
      <details>
        <summary className="doctor-signed-document-summary">
          <div>
            <p className="eyebrow">
              SIGNED DOCUMENTATION
            </p>

            <h2>
              {isInitialClerking
                ? 'Signed Initial Clerking'
                : 'Signed Progress Note'}
            </h2>

            <p>
              Read-only clinical record.
            </p>
          </div>

          <div className="doctor-signed-document-meta">
            <span>
              SIGNED · v{document.version}
            </span>
          </div>
        </summary>

        <div className="doctor-signed-document-body">
          <div className="doctor-signed-document-preview">
            {isInitialClerking ? (
              <>
                <SummaryRow
                  label="Presenting complaint"
                  value={
                    presentingComplaintText
                  }
                />

                <SummaryRow
                  label="History"
                  value={history}
                />
              </>
            ) : (
              <>
                <SummaryRow
                  label="Subjective"
                  value={subjective}
                />

                <SummaryRow
                  label="Objective"
                  value={objective}
                />
              </>
            )}

            <SummaryRow
              label="Working diagnosis"
              value={workingDiagnosis}
            />

            <SummaryRow
              label="Differentials"
              value={
                differentials.length > 0
                  ? differentials.join(', ')
                  : ''
              }
            />

            {isInitialClerking && (
              <SummaryRow
                label="Investigations"
                value={
                  investigations.length > 0
                    ? investigations.join(', ')
                    : ''
                }
              />
            )}

            <SummaryRow
              label="Plan"
              value={plan}
            />
          </div>

          <details className="doctor-signed-document-full">
            <summary>
              View complete signed document
            </summary>

            <div className="doctor-signed-document-full-body">
              {isInitialClerking ? (
                <>
                  <SummaryRow
                    label="Review of systems"
                    value={
                      stringValue(
                        content,
                        'review_of_systems',
                      )
                    }
                  />

                  <SummaryRow
                    label="Past medical history"
                    value={
                      stringValue(
                        content,
                        'past_medical_history',
                      )
                    }
                  />

                  <SummaryRow
                    label="Past surgical history"
                    value={
                      stringValue(
                        content,
                        'past_surgical_history',
                      )
                    }
                  />

                  <SummaryRow
                    label="Drug history"
                    value={
                      stringValue(
                        content,
                        'drug_history',
                      )
                    }
                  />

                  <SummaryRow
                    label="Allergies"
                    value={
                      stringValue(
                        content,
                        'allergies',
                      )
                    }
                  />

                  <SummaryRow
                    label="Family history"
                    value={
                      stringValue(
                        content,
                        'family_history',
                      )
                    }
                  />

                  <SummaryRow
                    label="Social history"
                    value={
                      stringValue(
                        content,
                        'social_history',
                      )
                    }
                  />

                  <SummaryRow
                    label="Personal history"
                    value={
                      stringValue(
                        content,
                        'personal_history',
                      )
                    }
                  />

                  <SummaryRow
                    label="Gynaecological history"
                    value={
                      stringValue(
                        content,
                        'gynaecological_history',
                      )
                    }
                  />

                  <SummaryRow
                    label="Obstetric history"
                    value={
                      stringValue(
                        content,
                        'obstetric_history',
                      )
                    }
                  />

                  <SummaryRow
                    label="Menstrual history"
                    value={
                      stringValue(
                        content,
                        'menstrual_history',
                      )
                    }
                  />

                  <SummaryRow
                    label="Sexual history"
                    value={
                      stringValue(
                        content,
                        'sexual_history',
                      )
                    }
                  />

                  <SummaryRow
                    label="Patient perspective"
                    value={patientPerspective}
                  />

                  <SummaryRow
                    label="Examination"
                    value={examination}
                  />
                </>
              ) : (
                <>
                  <SummaryRow
                    label="Subjective"
                    value={subjective}
                  />

                  <SummaryRow
                    label="Objective"
                    value={objective}
                  />
                </>
              )}
            </div>
          </details>
        </div>
      </details>
    </section>
  )
}
