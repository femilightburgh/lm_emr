import type { ClinicalDocument } from '../../api/clinicalDocuments'
import type { Encounter } from '../../api/encounters'
import type { Episode } from '../../api/episodes'

export type WardReviewDisposition =
  | 'CONTINUE_ADMISSION'
  | 'DISCHARGE'
  | 'TRANSFER'
  | 'REFERRAL'
  | 'OTHER'

interface Props {
  isWardReview: boolean
  selectedEncounter: Encounter
  selectedEpisode: Episode | null
  progressNote: ClinicalDocument | null
  closingEncounter: boolean

  wardReviewDisposition: WardReviewDisposition
  setWardReviewDisposition: (value: WardReviewDisposition) => void
  wardReviewDetails: string
  setWardReviewDetails: (value: string) => void
  wardReviewDetailsRequired: boolean
  wardReviewReady: boolean
  completeWardReview: (
    disposition: WardReviewDisposition,
    details: string | null,
  ) => Promise<void>

  completingConsultation: boolean
  handleCompleteConsultation: () => Promise<void>
  completingDoctorReview: boolean
  handleCompleteDoctorReview: () => Promise<void>
}

export default function DoctorEncounterCompletionPanels({
  isWardReview,
  selectedEncounter,
  selectedEpisode,
  progressNote,
  closingEncounter,
  wardReviewDisposition,
  setWardReviewDisposition,
  wardReviewDetails,
  setWardReviewDetails,
  wardReviewDetailsRequired,
  wardReviewReady,
  completeWardReview,
  completingConsultation,
  handleCompleteConsultation,
  completingDoctorReview,
  handleCompleteDoctorReview,
}: Props) {
  return (
    <>
      {isWardReview && selectedEncounter.status === 'OPEN' && (
        <section className="workspace-panel doctor-completion-panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">DISPOSITION</p>
              <h2>Complete Ward Review</h2>
              <p>Finalize today's inpatient review after documentation and clinical actions are complete.</p>
            </div>
          </div>
          <div className="doctor-completion-controls">
            <label>
              <span>Disposition</span>
              <select
                value={wardReviewDisposition}
                disabled={closingEncounter}
                onChange={event => {
                  const disposition = event.target.value as WardReviewDisposition
                  setWardReviewDisposition(disposition)
                  if (!['TRANSFER', 'REFERRAL', 'OTHER'].includes(disposition)) {
                    setWardReviewDetails('')
                  }
                }}
              >
                <option value="CONTINUE_ADMISSION">Continue admission</option>
                <option value="DISCHARGE">Discharge</option>
                <option value="TRANSFER">Transfer</option>
                <option value="REFERRAL">Referral</option>
                <option value="OTHER">Other</option>
              </select>
            </label>
            {wardReviewDetailsRequired && (
              <label className="doctor-completion-details">
                <span>Details</span>
                <textarea
                  rows={3}
                  value={wardReviewDetails}
                  disabled={closingEncounter}
                  onChange={event => setWardReviewDetails(event.target.value)}
                />
              </label>
            )}
            <button
              type="button"
              disabled={closingEncounter || !wardReviewReady}
              onClick={() =>
                void completeWardReview(
                  wardReviewDisposition,
                  wardReviewDetailsRequired ? wardReviewDetails.trim() : null,
                )
              }
            >
              {closingEncounter ? 'Completing...' : 'Complete Ward Review'}
            </button>
          </div>
        </section>
      )}

      {selectedEncounter.title === 'Doctor Consultation' &&
        selectedEncounter.status === 'OPEN' &&
        selectedEpisode?.status === 'OPEN' &&
        progressNote?.document_type === 'INITIAL_CLERKING' &&
        progressNote.status === 'SIGNED' && (
          <section className="workspace-panel doctor-completion-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">DISPOSITION</p>
                <h2>Consultation ready to complete</h2>
                <p>The initial clerking is signed. Complete the consultation while keeping the episode open for investigations and review.</p>
              </div>
            </div>
            <button
              type="button"
              disabled={completingConsultation}
              onClick={() => void handleCompleteConsultation()}
            >
              {completingConsultation ? 'Completing...' : 'Complete Consultation'}
            </button>
          </section>
        )}

      {selectedEncounter.title === 'Doctor Review' &&
        selectedEncounter.status === 'OPEN' &&
        selectedEpisode?.status === 'OPEN' && (
          <section className="workspace-panel doctor-completion-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">DISPOSITION</p>
                <h2>Doctor review ready to complete</h2>
                <p>Complete the review after documenting the assessment, results, and clinical plan.</p>
              </div>
            </div>
            <button
              type="button"
              disabled={completingDoctorReview}
              onClick={() => void handleCompleteDoctorReview()}
            >
              {completingDoctorReview ? 'Completing...' : 'Complete Doctor Review'}
            </button>
          </section>
        )}
    </>
  )
}
