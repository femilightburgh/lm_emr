import type { ClinicalDocument } from '../../api/clinicalDocuments'


function textValue(
  content: Record<string, unknown>,
  key: string,
): string {
  const value = content[key]

  if (typeof value === 'string') {
    return value.trim() || 'Not documented'
  }

  if (typeof value === 'number') {
    return String(value)
  }

  return 'Not documented'
}


function listValue(
  content: Record<string, unknown>,
  key: string,
): string {
  const value = content[key]

  if (!Array.isArray(value)) {
    return 'Not documented'
  }

  const items = value
    .filter(
      item =>
        typeof item === 'string' &&
        item.trim(),
    )
    .map(item => item.trim())

  return items.length > 0
    ? items.join(', ')
    : 'Not documented'
}


function complaintValue(
  content: Record<string, unknown>,
): string {
  const complaints =
    content.presenting_complaints

  if (!Array.isArray(complaints)) {
    return 'Not documented'
  }

  const values = complaints
    .filter(
      item =>
        item &&
        typeof item === 'object' &&
        !Array.isArray(item),
    )
    .map(item => {
      const record =
        item as Record<string, unknown>

      const complaint =
        typeof record.complaint === 'string'
          ? record.complaint.trim()
          : ''

      const duration =
        typeof record.duration === 'string'
          ? record.duration.trim()
          : ''

      if (!complaint) {
        return ''
      }

      return duration
        ? `${complaint} (${duration})`
        : complaint
    })
    .filter(Boolean)

  return values.length > 0
    ? values.join(', ')
    : 'Not documented'
}


function Section({
  title,
  children,
  wide = false,
}: {
  title: string
  children: React.ReactNode
  wide?: boolean
}) {
  return (
    <section
      className={
        `doctor-history-doctor-section${
          wide
            ? ' doctor-history-doctor-section-wide'
            : ''
        }`
      }
    >
      <p className="eyebrow">
        {title}
      </p>

      <div className="doctor-history-doctor-fields">
        {children}
      </div>
    </section>
  )
}


function Field({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <div className="doctor-history-doctor-field">
      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>
    </div>
  )
}


function InitialClerkingViewer({
  document,
}: {
  document: ClinicalDocument
}) {
  const content = document.content

  const assessment =
    content.assessment &&
    typeof content.assessment === 'object' &&
    !Array.isArray(content.assessment)
      ? content.assessment as Record<string, unknown>
      : {}

  return (
    <>
      <Section title="PRESENTING PROBLEM">
        <Field
          label="Presenting complaint"
          value={complaintValue(content)}
        />

        <Field
          label="History of presenting complaint"
          value={textValue(
            content,
            'history_of_presenting_complaint',
          )}
        />
      </Section>

      <Section title="REVIEW OF SYSTEMS">
        <Field
          label="Review of systems"
          value={textValue(
            content,
            'review_of_systems',
          )}
        />
      </Section>

      <Section title="MEDICAL BACKGROUND">
        <Field
          label="Past medical history"
          value={textValue(
            content,
            'past_medical_history',
          )}
        />

        <Field
          label="Past surgical history"
          value={textValue(
            content,
            'past_surgical_history',
          )}
        />

        <Field
          label="Drug history"
          value={textValue(
            content,
            'drug_history',
          )}
        />

        <Field
          label="Allergies"
          value={textValue(
            content,
            'allergies',
          )}
        />

        <Field
          label="Family history"
          value={textValue(
            content,
            'family_history',
          )}
        />

        <Field
          label="Social history"
          value={textValue(
            content,
            'social_history',
          )}
        />

        <Field
          label="Personal history"
          value={textValue(
            content,
            'personal_history',
          )}
        />
      </Section>

      <Section title="PATIENT PERSPECTIVE">
        <Field
          label="Ideas"
          value={textValue(
            content,
            'ideas',
          )}
        />

        <Field
          label="Concerns"
          value={textValue(
            content,
            'concerns',
          )}
        />

        <Field
          label="Expectations"
          value={textValue(
            content,
            'expectations',
          )}
        />

        <Field
          label="Patient perspective"
          value={textValue(
            content,
            'patient_perspective',
          )}
        />
      </Section>

      <Section title="WOMEN'S HEALTH">
        <Field
          label="Gynaecological history"
          value={textValue(
            content,
            'gynaecological_history',
          )}
        />

        <Field
          label="Obstetric history"
          value={textValue(
            content,
            'obstetric_history',
          )}
        />

        <Field
          label="Menstrual history"
          value={textValue(
            content,
            'menstrual_history',
          )}
        />

        <Field
          label="Sexual history"
          value={textValue(
            content,
            'sexual_history',
          )}
        />
      </Section>

      <Section
        title="EXAMINATION"
        wide
      >
        <Field
          label="General examination"
          value={textValue(
            content,
            'exam_general',
          )}
        />

        <Field
          label="Cardiovascular"
          value={textValue(
            content,
            'exam_cardiovascular',
          )}
        />

        <Field
          label="Respiratory"
          value={textValue(
            content,
            'exam_respiratory',
          )}
        />

        <Field
          label="Abdomen"
          value={textValue(
            content,
            'exam_abdomen',
          )}
        />

        <Field
          label="Neurological"
          value={textValue(
            content,
            'exam_neurological',
          )}
        />

        <Field
          label="Musculoskeletal"
          value={textValue(
            content,
            'exam_musculoskeletal',
          )}
        />

        <Field
          label="Genitourinary"
          value={textValue(
            content,
            'exam_genitourinary',
          )}
        />

        <Field
          label="Other examination"
          value={textValue(
            content,
            'exam_other',
          )}
        />

        <Field
          label="Examination"
          value={textValue(
            content,
            'examination',
          )}
        />
      </Section>

      <Section title="ASSESSMENT">
        <Field
          label="Working diagnosis"
          value={textValue(
            assessment,
            'working_diagnosis',
          )}
        />

        <Field
          label="Differentials"
          value={listValue(
            assessment,
            'differentials',
          )}
        />
      </Section>

      <Section title="INVESTIGATION PLAN">
        <Field
          label="Investigations"
          value={listValue(
            content,
            'investigations',
          )}
        />
      </Section>

      <Section title="PLAN">
        <Field
          label="Management plan"
          value={textValue(
            content,
            'plan',
          )}
        />
      </Section>
    </>
  )
}


function ProgressNoteViewer({
  document,
}: {
  document: ClinicalDocument
}) {
  const content = document.content

  const assessment =
    content.assessment &&
    typeof content.assessment === 'object' &&
    !Array.isArray(content.assessment)
      ? content.assessment as Record<string, unknown>
      : {}

  return (
    <>
      <Section title="SUBJECTIVE">
        <Field
          label="Subjective"
          value={textValue(
            content,
            'subjective',
          )}
        />
      </Section>

      <Section title="OBJECTIVE">
        <Field
          label="Objective"
          value={textValue(
            content,
            'objective',
          )}
        />
      </Section>

      <Section title="ASSESSMENT">
        <Field
          label="Working diagnosis"
          value={textValue(
            assessment,
            'working_diagnosis',
          )}
        />

        <Field
          label="Differentials"
          value={listValue(
            assessment,
            'differentials',
          )}
        />
      </Section>

      <Section title="PLAN">
        <Field
          label="Management plan"
          value={textValue(
            content,
            'plan',
          )}
        />
      </Section>
    </>
  )
}


export default function HistoricalDoctorDocumentViewer({
  document,
}: {
  document: ClinicalDocument
}) {
  if (
    document.status !== 'SIGNED' &&
    document.status !== 'AMENDED'
  ) {
    return (
      <section className="doctor-history-doctor-document">
        <header className="doctor-history-doctor-document-header">
          <div>
            <p className="eyebrow">
              CLINICAL DOCUMENT
            </p>

            <h3>
              {document.document_type}
            </h3>

            <p>
              This document is not signed and is not
              available as a historical clinical record.
            </p>
          </div>
        </header>
      </section>
    )
  }

  const title =
    document.document_type ===
      'INITIAL_CLERKING'
      ? 'Initial Clerking'
      : 'Progress Note'

  return (
    <section className="doctor-history-doctor-document">
      <header className="doctor-history-doctor-document-header">
        <div>
          <p className="eyebrow">
            SIGNED CLINICAL DOCUMENT
          </p>

          <h3>
            {title}
          </h3>

          <p>
            Read-only clinical record · v{document.version}
          </p>
        </div>

        <span className="doctor-history-status doctor-history-status-complete">
          {document.status}
        </span>
      </header>

      <div className="doctor-history-doctor-grid">
        {document.document_type ===
        'INITIAL_CLERKING' ? (
          <InitialClerkingViewer
            document={document}
          />
        ) : (
          <ProgressNoteViewer
            document={document}
          />
        )}
      </div>
    </section>
  )
}
