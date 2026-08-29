import type { ClinicalDocument } from '../../api/clinicalDocuments'


interface Props {
  noteTitle: string
  progressNote: ClinicalDocument | null
  encounterClosed: boolean
  loading: boolean
  saving: boolean
  signing: boolean

  subjective: string
  objective: string
  workingDiagnosis: string
  differentials: string
  plan: string

  onSubjectiveChange: (value: string) => void
  onObjectiveChange: (value: string) => void
  onWorkingDiagnosisChange: (value: string) => void
  onDifferentialsChange: (value: string) => void
  onPlanChange: (value: string) => void

  onInsertLatestVitals: () => void
  hasVitals: boolean

  onSave: () => void
  onSign: () => void
}


export default function ProgressNotePanel({
  progressNote,
  encounterClosed,
  loading,
  saving,
  signing,

  subjective,
  objective,
  workingDiagnosis,
  differentials,
  plan,

  onSubjectiveChange,
  onObjectiveChange,
  onWorkingDiagnosisChange,
  onDifferentialsChange,
  onPlanChange,

  onInsertLatestVitals,
  hasVitals,

  onSave,
  onSign,
  noteTitle,
}: Props) {
  const signed =
    progressNote?.status === 'SIGNED'

  const readOnly =
    signed || encounterClosed

  return (
    <section className="workspace-panel doctor-progress-note">
      <div className="panel-header">
        <div>
          <p className="eyebrow">
            CLINICAL DOCUMENTATION
          </p>

          <h2>
            {noteTitle}
          </h2>

          <p>
            Document the current clinical assessment and plan.
          </p>
        </div>

        {progressNote && (
          <span>
            {progressNote.status}
            {' · '}
            v{progressNote.version}
          </span>
        )}
      </div>

      {loading && (
        <div className="doctor-note-loading">
          Loading {noteTitle.toLowerCase()}...
        </div>
      )}

      {!loading && (
        <div className="doctor-note-form">
          <section className="doctor-note-section">
            <div className="doctor-note-section-heading">
              <span>
                S
              </span>

              <div>
                <strong>
                  Subjective
                </strong>

                <small>
                  What the patient reports
                </small>
              </div>
            </div>

            <textarea
              rows={6}
              value={subjective}
              disabled={readOnly}
              onChange={event =>
                onSubjectiveChange(
                  event.target.value,
                )
              }
              placeholder="Patient-reported symptoms, concerns, and relevant history."
            />
          </section>

          <section className="doctor-note-section">
            <div className="doctor-note-section-heading">
              <span>
                O
              </span>

              <div>
                <strong>
                  Objective
                </strong>

                <small>
                  Examination findings and observations
                </small>
              </div>

              <button
                type="button"
                className="doctor-note-inline-action"
                disabled={
                  signed ||
                  !hasVitals
                }
                onClick={onInsertLatestVitals}
              >
                Insert latest vitals
              </button>
            </div>

            <textarea
              rows={6}
              value={objective}
              disabled={readOnly}
              onChange={event =>
                onObjectiveChange(
                  event.target.value,
                )
              }
              placeholder="Examination findings, observations, and relevant results."
            />
          </section>

          <section className="doctor-note-section">
            <div className="doctor-note-section-heading">
              <span>
                A
              </span>

              <div>
                <strong>
                  Assessment
                </strong>

                <small>
                  Clinical impression and differentials
                </small>
              </div>
            </div>

            <label className="doctor-note-field">
              <span>
                Working diagnosis
              </span>

              <input
                value={workingDiagnosis}
                disabled={readOnly}
                onChange={event =>
                  onWorkingDiagnosisChange(
                    event.target.value,
                  )
                }
                placeholder="Primary working diagnosis"
              />
            </label>

            <label className="doctor-note-field">
              <span>
                Differentials
              </span>

              <textarea
                rows={4}
                value={differentials}
                disabled={readOnly}
                onChange={event =>
                  onDifferentialsChange(
                    event.target.value,
                  )
                }
                placeholder="One differential diagnosis per line"
              />
            </label>
          </section>

          <section className="doctor-note-section">
            <div className="doctor-note-section-heading">
              <span>
                P
              </span>

              <div>
                <strong>
                  Plan
                </strong>

                <small>
                  Treatment, investigations, and follow-up
                </small>
              </div>
            </div>

            <textarea
              rows={7}
              value={plan}
              disabled={readOnly}
              onChange={event =>
                onPlanChange(
                  event.target.value,
                )
              }
              placeholder="Treatment, investigations, follow-up, and next steps."
            />
          </section>

          <div className="doctor-note-actions">
            <button
              type="button"
              disabled={
                saving ||
                signing ||
                readOnly
              }
              onClick={onSave}
            >
              {saving
                ? 'Saving...'
                : 'Save Draft'}
            </button>

            <button
              type="button"
              className="primary-button"
              disabled={
                signing ||
                saving ||
                !progressNote ||
                progressNote.status !== 'DRAFT' ||
                encounterClosed
              }
              onClick={onSign}
            >
              {signing
                ? 'Signing...'
                : 'Sign Note'}
            </button>
          </div>
        </div>
      )}
    </section>
  )
}
