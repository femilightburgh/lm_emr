import type { Episode } from '../../api/episodes'
import type { Encounter } from '../../api/encounters'
import type { ClinicalDocument } from '../../api/clinicalDocuments'
import type { Patient } from '../../types'

import {
  documentToIntake,
} from './nursing/documentUtils'


interface PreviousVisit {
  episode: Episode
  encounters: Encounter[]
  eventsByEncounter: Record<
    string,
    unknown[]
  >
  nursingDocumentsByEncounter: Record<
    string,
    ClinicalDocument | null
  >
}


interface Props {
  episode: Episode
  encounter: Encounter
  patient: Patient | null
  loadingPatient: boolean
  previousEpisodes: Episode[]
  loadingPreviousEpisodes: boolean
  previousVisits: PreviousVisit[]
  loadingPreviousVisits: boolean
}


function fullName(
  patient: Patient | null,
): string {
  if (!patient) return 'Patient'

  return [
    patient.first_name,
    patient.middle_name,
    patient.last_name,
  ]
    .filter(Boolean)
    .join(' ')
}


function ageFromDob(
  value: string | null | undefined,
): string {
  if (!value) return 'Age —'

  const dob = new Date(value)
  const today = new Date()

  let age =
    today.getFullYear() -
    dob.getFullYear()

  if (
    today.getMonth() < dob.getMonth() ||
    (
      today.getMonth() === dob.getMonth() &&
      today.getDate() < dob.getDate()
    )
  ) {
    age--
  }

  return `${age} years`
}


function date(
  value: string | null | undefined,
): string {
  if (!value) return '—'

  return new Date(
    value,
  ).toLocaleDateString(
    [],
    {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    },
  )
}


function dateTime(
  value: string,
): string {
  return new Date(
    value,
  ).toLocaleString(
    [],
    {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    },
  )
}


function value(
  text: string,
): string {
  return text.trim() || 'Not documented'
}


function NursingHistoryDocument({
  document,
}: {
  document: ClinicalDocument
}) {
  const intake =
    documentToIntake(
      document,
    )

  const presentingComplaint =
    value(
      intake.presenting_complaint,
    )

  return (
    <details className="nursing-history-document">
      <summary className="nursing-history-document-summary">
        <span className="nursing-history-document-title">
          <strong>
            Nursing assessment
          </strong>

          <small>
            {document.status}
            {document.signed_at
              ? ` · Signed ${dateTime(document.signed_at)}`
              : ''}
          </small>

          <span>
            {presentingComplaint}
          </span>
        </span>

        <span className="nursing-history-document-action">
          View full assessment
        </span>
      </summary>

      <div className="nursing-history-document-body">
        <div className="nursing-history-document-meta">
          <span>
            Nursing assessment
          </span>

          <span>
            {document.status}
          </span>

          {document.signed_at && (
            <span>
              Signed {dateTime(document.signed_at)}
            </span>
          )}
        </div>

        <div className="nursing-history-clinical-grid">
          <div className="nursing-history-clinical-group">
            <p className="eyebrow">
              PRESENTING PROBLEM
            </p>

            <div>
              <span>
                Presenting complaint
              </span>
              <strong>
                {value(
                  intake.presenting_complaint,
                )}
              </strong>
            </div>

            <div>
              <span>
                History of presenting complaint
              </span>
              <strong>
                {value(
                  intake.history_of_presenting_complaint,
                )}
              </strong>
            </div>
          </div>

          <div className="nursing-history-clinical-group">
            <p className="eyebrow">
              MEDICAL BACKGROUND
            </p>

            <div>
              <span>
                Known allergies
              </span>
              <strong>
                {value(
                  intake.known_allergies,
                )}
              </strong>
            </div>

            <div>
              <span>
                Allergy notes
              </span>
              <strong>
                {value(
                  intake.allergy_notes,
                )}
              </strong>
            </div>

            <div>
              <span>
                Past medical history
              </span>
              <strong>
                {value(
                  intake.past_medical_history,
                )}
              </strong>
            </div>

            <div>
              <span>
                Current medications
              </span>
              <strong>
                {value(
                  intake.current_medications,
                )}
              </strong>
            </div>

            <div>
              <span>
                Surgical history
              </span>
              <strong>
                {value(
                  intake.surgical_history,
                )}
              </strong>
            </div>
          </div>

          <div className="nursing-history-clinical-group">
            <p className="eyebrow">
              CLINICAL ASSESSMENT
            </p>

            <div>
              <span>
                General appearance
              </span>
              <strong>
                {value(
                  intake.general_appearance,
                )}
              </strong>
            </div>

            <div>
              <span>
                Level of consciousness
              </span>
              <strong>
                {value(
                  intake.level_of_consciousness,
                )}
              </strong>
            </div>

            <div>
              <span>
                Mobility
              </span>
              <strong>
                {value(
                  intake.mobility_status,
                )}
              </strong>
            </div>

            <div>
              <span>
                Pain
              </span>
              <strong>
                {[
                  intake.pain_score.trim(),
                  intake.pain_location.trim(),
                ]
                  .filter(Boolean)
                  .join(' · ') ||
                  'Not documented'}
              </strong>
            </div>
          </div>

          <div className="nursing-history-clinical-group">
            <p className="eyebrow">
              RISK & SAFETY
            </p>

            <div>
              <span>
                Fall risk
              </span>
              <strong>
                {value(
                  intake.fall_risk,
                )}
              </strong>
            </div>

            <div>
              <span>
                Pressure injury risk
              </span>
              <strong>
                {value(
                  intake.pressure_injury_risk,
                )}
              </strong>
            </div>

            <div>
              <span>
                Infection precautions
              </span>
              <strong>
                {value(
                  intake.infection_precautions,
                )}
              </strong>
            </div>
          </div>

          <div className="nursing-history-clinical-group nursing-history-clinical-wide">
            <p className="eyebrow">
              NURSING OBSERVATIONS
            </p>

            <div>
              <span>
                Nursing observations
              </span>
              <strong>
                {value(
                  intake.nursing_observations,
                )}
              </strong>
            </div>

            <div>
              <span>
                Immediate concerns
              </span>
              <strong>
                {value(
                  intake.immediate_concerns,
                )}
              </strong>
            </div>
          </div>

          <div className="nursing-history-clinical-group nursing-history-clinical-wide">
            <p className="eyebrow">
              HANDOVER
            </p>

            <div>
              <span>
                Handover notes
              </span>
              <strong>
                {value(
                  intake.handover_notes,
                )}
              </strong>
            </div>
          </div>
        </div>
      </div>
    </details>
  )
}

export default function NursingPatientSummary({
  episode,
  encounter,
  patient,
  loadingPatient,
  previousEpisodes,
  loadingPreviousEpisodes,
  previousVisits,
  loadingPreviousVisits,
}: Props) {
  const name =
    fullName(patient)

  return (
    <section className="nursing-patient-cockpit">
      <header className="nursing-cockpit-header">
        <div className="nursing-cockpit-identity">
          <span className="nursing-cockpit-avatar">
            {name
              .split(' ')
              .map(
                part =>
                  part.charAt(0),
              )
              .slice(0, 2)
              .join('')}
          </span>

          <div>
            <p className="eyebrow">
              PATIENT SNAPSHOT
            </p>

            <h2>
              {loadingPatient
                ? 'Loading patient…'
                : name}
            </h2>

            <p>
              {patient?.hospital_number ??
                'Hospital number —'}
              {' · '}
              {patient?.sex ??
                'Sex —'}
              {' · '}
              {ageFromDob(
                patient?.date_of_birth,
              )}
            </p>
          </div>
        </div>

        <div className="nursing-cockpit-status">
          <span className="nursing-status-pill">
            OPEN
          </span>

          <small>
            {episode.title}
          </small>

          <strong>
            {episode.episode_number}
          </strong>
        </div>
      </header>

      <div className="nursing-cockpit-alerts">
        <div>
          <span>
            Blood group
          </span>
          <strong>
            {patient?.blood_group ??
              'Not recorded'}
          </strong>
        </div>

        <div>
          <span>
            Genotype
          </span>
          <strong>
            {patient?.genotype ??
              'Not recorded'}
          </strong>
        </div>

        <div className="nursing-cockpit-alert">
          <span>
            Allergies
          </span>
          <strong>
            Review nursing intake
          </strong>
        </div>

        <div>
          <span>
            Encounter started
          </span>
          <strong>
            {dateTime(
              encounter.started_at,
            )}
          </strong>
        </div>
      </div>

      <div className="nursing-context-grid">
        <details
          open
          className="nursing-context-card"
        >
          <summary>
            <span>
              <small>
                CARE CONTEXT
              </small>
              <strong>
                Current episode
              </strong>
            </span>

            <b>
              {episode.status}
            </b>
          </summary>

          <div className="nursing-context-body">
            <div>
              <span>
                Episode
              </span>
              <strong>
                {episode.episode_number}
              </strong>
            </div>

            <div>
              <span>
                Visit
              </span>
              <strong>
                {episode.title}
              </strong>
            </div>

            <div>
              <span>
                Encounter
              </span>
              <strong>
                {encounter.title}
              </strong>
            </div>

            <div>
              <span>
                Started
              </span>
              <strong>
                {dateTime(
                  encounter.started_at,
                )}
              </strong>
            </div>
          </div>
        </details>

        <details className="nursing-context-card">
          <summary>
            <span>
              <small>
                BACKGROUND
              </small>
              <strong>
                Patient information
              </strong>
            </span>

            <b>
              View
            </b>
          </summary>

          <div className="nursing-context-body">
            <div>
              <span>
                Phone
              </span>
              <strong>
                {patient?.phone_number ??
                  '—'}
              </strong>
            </div>

            <div>
              <span>
                Next of kin
              </span>
              <strong>
                {patient?.next_of_kin_name ??
                  '—'}
              </strong>
            </div>

            <div>
              <span>
                Relationship
              </span>
              <strong>
                {patient?.next_of_kin_relationship ??
                  '—'}
              </strong>
            </div>

            <div>
              <span>
                Date of birth
              </span>
              <strong>
                {date(
                  patient?.date_of_birth,
                )}
              </strong>
            </div>
          </div>
        </details>

        <details className="nursing-context-card">
          <summary>
            <span>
              <small>
                CARE HISTORY
              </small>

              <strong>
                Previous nursing assessments
              </strong>
            </span>

            <b>
              {loadingPreviousEpisodes
                ? '…'
                : previousEpisodes.length}
            </b>
          </summary>

          <div className="nursing-history-body">
            {loadingPreviousVisits ||
            loadingPreviousEpisodes ? (
              <div className="nursing-history-empty">
                Loading nursing history…
              </div>
            ) : previousVisits.length === 0 ? (
              <div className="nursing-history-empty">
                No previous visits recorded.
              </div>
            ) : (
              previousVisits
                .slice(0, 5)
                .map(visit => {
                  const nursingDocuments =
                    visit.encounters
                      .map(
                        previousEncounter =>
                          visit
                            .nursingDocumentsByEncounter[
                              previousEncounter.id
                            ],
                      )
                      .filter(
                        (
                          document,
                        ): document is ClinicalDocument =>
                          document !== null,
                      )

                  return (
                    <details
                      key={visit.episode.id}
                      className="nursing-history-visit"
                    >
                      <summary>
                        <span>
                          <strong>
                            {visit.episode.title}
                          </strong>

                          <small>
                            {visit.episode.episode_number}
                            {' · '}
                            {date(
                              visit.episode.opened_at,
                            )}
                          </small>
                        </span>

                        <b>
                          {nursingDocuments.length}
                          {' '}
                          assessment
                          {nursingDocuments.length === 1
                            ? ''
                            : 's'}
                        </b>
                      </summary>

                      <div className="nursing-history-visit-body">
                        {nursingDocuments.length === 0 ? (
                          <div className="nursing-history-empty">
                            No signed nursing assessment was documented for this visit.
                          </div>
                        ) : (
                          nursingDocuments.map(
                            document => (
                              <NursingHistoryDocument
                                key={
                                  document.id
                                }
                                document={
                                  document
                                }
                              />
                            ),
                          )
                        )}
                      </div>
                    </details>
                  )
                })
            )}
          </div>
        </details>
      </div>
    </section>
  )
}
