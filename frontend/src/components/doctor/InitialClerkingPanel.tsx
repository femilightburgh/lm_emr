import type { ClinicalDocument } from '../../api/clinicalDocuments'


interface Props {
  document: ClinicalDocument | null
  loading: boolean
  saving: boolean
  signing: boolean

  complaint: string
  complaintDuration: string
  history: string
  reviewOfSystems: string
  pastMedicalHistory: string
  pastSurgicalHistory: string
  drugHistory: string
  allergies: string
  familyHistory: string
  socialHistory: string
  personalHistory: string

  ideas: string
  concerns: string
  expectations: string

  examGeneral: string
  examCardiovascular: string
  examRespiratory: string
  examAbdomen: string
  examNeurological: string
  examMusculoskeletal: string
  examGenitourinary: string
  examOther: string

  onComplaintChange: (value: string) => void
  onComplaintDurationChange: (value: string) => void
  onHistoryChange: (value: string) => void
  onReviewOfSystemsChange: (value: string) => void
  onPastMedicalHistoryChange: (value: string) => void
  onPastSurgicalHistoryChange: (value: string) => void
  onDrugHistoryChange: (value: string) => void
  onAllergiesChange: (value: string) => void
  onFamilyHistoryChange: (value: string) => void
  onSocialHistoryChange: (value: string) => void
  onPersonalHistoryChange: (value: string) => void

  onIdeasChange: (value: string) => void
  onConcernsChange: (value: string) => void
  onExpectationsChange: (value: string) => void

  onExamGeneralChange: (value: string) => void
  onExamCardiovascularChange: (value: string) => void
  onExamRespiratoryChange: (value: string) => void
  onExamAbdomenChange: (value: string) => void
  onExamNeurologicalChange: (value: string) => void
  onExamMusculoskeletalChange: (value: string) => void
  onExamGenitourinaryChange: (value: string) => void
  onExamOtherChange: (value: string) => void

  onSave: () => void
  onSign: () => void

  admitting: boolean
  canAdmit: boolean
  onAdmit: () => void
}


export default function InitialClerkingPanel({
  document,
  loading,
  saving,
  signing,

  complaint,
  complaintDuration,
  history,
  reviewOfSystems,
  pastMedicalHistory,
  pastSurgicalHistory,
  drugHistory,
  allergies,
  familyHistory,
  socialHistory,
  personalHistory,

  ideas,
  concerns,
  expectations,

  examGeneral,
  examCardiovascular,
  examRespiratory,
  examAbdomen,
  examNeurological,
  examMusculoskeletal,
  examGenitourinary,
  examOther,

  onComplaintChange,
  onComplaintDurationChange,
  onHistoryChange,
  onReviewOfSystemsChange,
  onPastMedicalHistoryChange,
  onPastSurgicalHistoryChange,
  onDrugHistoryChange,
  onAllergiesChange,
  onFamilyHistoryChange,
  onSocialHistoryChange,
  onPersonalHistoryChange,

  onIdeasChange,
  onConcernsChange,
  onExpectationsChange,

  onExamGeneralChange,
  onExamCardiovascularChange,
  onExamRespiratoryChange,
  onExamAbdomenChange,
  onExamNeurologicalChange,
  onExamMusculoskeletalChange,
  onExamGenitourinaryChange,
  onExamOtherChange,

  onSave,
  onSign,

  admitting,
  canAdmit,
  onAdmit,
}: Props) {
  const signed =
    document?.status === 'SIGNED'

  return (
    <section className="workspace-panel doctor-clerking-panel">
      <div className="panel-header">
        <div>
          <h2>Initial Clerking</h2>
          <p>
            Document the patient's initial clinical assessment.
          </p>
        </div>

        {document && (
          <span>
            {document.status}
            {' · '}
            v{document.version}
          </span>
        )}
      </div>

      {loading && (
        <p>Loading initial clerking...</p>
      )}

      {!loading && (
        <>
          <details
            className="doctor-clerking-section"
            open
          >
            <summary>
              <span>
                Presenting Complaint
              </span>
            </summary>

            <div className="doctor-clerking-section-body">
              <div className="inline-fields">
                <label>
                  Complaint
                  <input
                    value={complaint}
                    disabled={signed}
                    onChange={event =>
                      onComplaintChange(
                        event.target.value,
                      )
                    }
                    placeholder="e.g. Fever"
                  />
                </label>

                <label>
                  Duration
                  <input
                    value={complaintDuration}
                    disabled={signed}
                    onChange={event =>
                      onComplaintDurationChange(
                        event.target.value,
                      )
                    }
                    placeholder="e.g. 3 days"
                  />
                </label>
              </div>

              <label>
                History of Presenting Complaint
                <textarea
                  rows={5}
                  value={history}
                  disabled={signed}
                  onChange={event =>
                    onHistoryChange(
                      event.target.value,
                    )
                  }
                />
              </label>

              <label>
                Review of Systems
                <textarea
                  rows={4}
                  value={reviewOfSystems}
                  disabled={signed}
                  onChange={event =>
                    onReviewOfSystemsChange(
                      event.target.value,
                    )
                  }
                />
              </label>
            </div>
          </details>

          <details className="doctor-clerking-section">
            <summary>
              <span>
                Past History
              </span>
            </summary>

            <div className="doctor-clerking-section-body">

          <label>
            Past Medical History
            <textarea
              rows={4}
              value={pastMedicalHistory}
              disabled={signed}
              onChange={event =>
                onPastMedicalHistoryChange(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Past Surgical History
            <textarea
              rows={4}
              value={pastSurgicalHistory}
              disabled={signed}
              onChange={event =>
                onPastSurgicalHistoryChange(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Drug History
            <textarea
              rows={4}
              value={drugHistory}
              disabled={signed}
              onChange={event =>
                onDrugHistoryChange(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Allergies
            <textarea
              rows={3}
              value={allergies}
              disabled={signed}
              onChange={event =>
                onAllergiesChange(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Family History
            <textarea
              rows={3}
              value={familyHistory}
              disabled={signed}
              onChange={event =>
                onFamilyHistoryChange(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Social History
            <textarea
              rows={3}
              value={socialHistory}
              disabled={signed}
              onChange={event =>
                onSocialHistoryChange(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Personal History
            <textarea
              rows={3}
              value={personalHistory}
              disabled={signed}
              onChange={event =>
                onPersonalHistoryChange(
                  event.target.value,
                )
              }
            />
          </label>

            </div>
          </details>

          <details className="doctor-clerking-section">
            <summary>
              <span>
                Patient Perspective
              </span>
            </summary>

            <div className="doctor-clerking-section-body">

          <label>
            Ideas
            <textarea
              rows={3}
              value={ideas}
              disabled={signed}
              onChange={event =>
                onIdeasChange(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Concerns
            <textarea
              rows={3}
              value={concerns}
              disabled={signed}
              onChange={event =>
                onConcernsChange(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Expectations
            <textarea
              rows={3}
              value={expectations}
              disabled={signed}
              onChange={event =>
                onExpectationsChange(
                  event.target.value,
                )
              }
            />
          </label>

            </div>
          </details>

          <details className="doctor-clerking-section">
            <summary>
              <span>
                Examination
              </span>
            </summary>

            <div className="doctor-clerking-section-body">

          <label>
            General
            <textarea
              rows={3}
              value={examGeneral}
              disabled={signed}
              onChange={event =>
                onExamGeneralChange(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Cardiovascular
            <textarea
              rows={3}
              value={examCardiovascular}
              disabled={signed}
              onChange={event =>
                onExamCardiovascularChange(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Respiratory
            <textarea
              rows={3}
              value={examRespiratory}
              disabled={signed}
              onChange={event =>
                onExamRespiratoryChange(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Abdomen
            <textarea
              rows={3}
              value={examAbdomen}
              disabled={signed}
              onChange={event =>
                onExamAbdomenChange(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Neurological
            <textarea
              rows={3}
              value={examNeurological}
              disabled={signed}
              onChange={event =>
                onExamNeurologicalChange(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Musculoskeletal
            <textarea
              rows={3}
              value={examMusculoskeletal}
              disabled={signed}
              onChange={event =>
                onExamMusculoskeletalChange(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Genitourinary
            <textarea
              rows={3}
              value={examGenitourinary}
              disabled={signed}
              onChange={event =>
                onExamGenitourinaryChange(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Other
            <textarea
              rows={3}
              value={examOther}
              disabled={signed}
              onChange={event =>
                onExamOtherChange(
                  event.target.value,
                )
              }
            />
          </label>

            </div>
          </details>

          <div className="doctor-clerking-actions">
            <button
              type="button"
              disabled={
                saving ||
                signing ||
                signed
              }
              onClick={onSave}
            >
              {saving
                ? 'Saving...'
                : 'Save Draft'}
            </button>

            <button
              type="button"
              disabled={
                signing ||
                saving ||
                !document ||
                document.status !== 'DRAFT'
              }
              onClick={onSign}
            >
              {signing
                ? 'Signing...'
                : 'Sign Note'}
            </button>

            <button
              type="button"
              disabled={
                !canAdmit ||
                admitting ||
                signing ||
                saving
              }
              onClick={onAdmit}
            >
              {admitting
                ? 'Admitting...'
                : 'Admit to Ward'}
            </button>
          </div>
        </>
      )}
    </section>
  )
}
