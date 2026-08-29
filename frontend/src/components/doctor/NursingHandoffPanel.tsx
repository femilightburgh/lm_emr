import type { ClinicalDocument } from '../../api/clinicalDocuments'
import type { Encounter } from '../../api/encounters'


interface Props {
  encounter: Encounter | null
  document: ClinicalDocument | null
  loading: boolean
}


function contentString(
  content: Record<string, unknown>,
  key: string,
): string {
  const value = content[key]

  return typeof value === 'string'
    ? value.trim()
    : ''
}


function contentList(
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


function formatDate(
  value: string | null | undefined,
): string {
  if (!value) {
    return 'Not available'
  }

  return new Date(value).toLocaleString()
}


function displayValue(
  value: string,
  emptyLabel = 'Not recorded',
): string {
  return value || emptyLabel
}


export default function NursingHandoffPanel({
  encounter,
  document,
  loading,
}: Props) {
  const content =
    document?.content ?? {}

  const allergies =
    contentList(
      content,
      'known_allergies',
    )

  const medications =
    contentList(
      content,
      'current_medications',
    )

  const presentingComplaint =
    contentString(
      content,
      'presenting_complaint',
    )

  const history =
    contentString(
      content,
      'history_of_presenting_complaint',
    )

  const generalAppearance =
    contentString(
      content,
      'general_appearance',
    )

  const consciousness =
    contentString(
      content,
      'level_of_consciousness',
    )

  const painScore =
    content.pain_score != null
      ? String(content.pain_score)
      : ''

  const painLocation =
    contentString(
      content,
      'pain_location',
    )

  const immediateConcerns =
    contentString(
      content,
      'immediate_concerns',
    )

  const nursingObservations =
    contentString(
      content,
      'nursing_observations',
    )

  const handoverNotes =
    contentString(
      content,
      'handover_notes',
    )

  const allergyNotes =
    contentString(
      content,
      'allergy_notes',
    )

  return (
    <section className="workspace-panel doctor-nursing-intake">
      <details>
        <summary className="doctor-context-summary">
          <div>
            <p className="eyebrow">
              CARE CONTEXT
            </p>

            <h2>
              Nursing Intake
            </h2>

            <p>
              Nursing information recorded before the doctor review.
            </p>
          </div>

          <div className="doctor-context-summary-meta">
            {document && (
              <span>
                Signed · v{document.version}
              </span>
            )}

            {encounter && (
              <span>
                {formatDate(
                  encounter.started_at,
                )}
              </span>
            )}
          </div>
        </summary>

        <div className="doctor-context-body">

      {loading && (
        <p>Loading nursing handoff...</p>
      )}

      {!loading && !document && (
        <p>
          No signed Nursing Intake is available for this episode.
        </p>
      )}

      {!loading && document && (
        <>
          <div className="diagnosis-list">
            <h3>Clinical summary</h3>

            <div className="list-item">
              <strong>Presenting complaint</strong>
              <span>
                {displayValue(
                  presentingComplaint,
                )}
              </span>
            </div>

            <div className="list-item">
              <strong>History</strong>
              <span>
                {displayValue(
                  history,
                )}
              </span>
            </div>

            <div className="list-item">
              <strong>Allergies</strong>
              <span>
                {allergies.length > 0
                  ? allergies.join(', ')
                  : allergyNotes ||
                    'None recorded'}
              </span>
            </div>

            <div className="list-item">
              <strong>Current medications</strong>
              <span>
                {medications.length > 0
                  ? medications.join(', ')
                  : 'None recorded'}
              </span>
            </div>

            <div className="list-item">
              <strong>General appearance</strong>
              <span>
                {displayValue(
                  generalAppearance,
                )}
              </span>
            </div>

            <div className="list-item">
              <strong>Consciousness</strong>
              <span>
                {displayValue(
                  consciousness,
                )}
              </span>
            </div>

            <div className="list-item">
              <strong>Pain</strong>
              <span>
                {painScore
                  ? `${painScore}/10`
                  : 'Not recorded'}
                {painLocation
                  ? ` · ${painLocation}`
                  : ''}
              </span>
            </div>

            {(immediateConcerns ||
              nursingObservations ||
              handoverNotes) && (
              <div className="list-item">
                <strong>Nursing concerns</strong>
                <span>
                  {immediateConcerns ||
                    nursingObservations ||
                    handoverNotes}
                </span>
              </div>
            )}
          </div>

          <details>
            <summary>
              View full nursing assessment
            </summary>

            <div className="diagnosis-list">
              <div className="list-item">
                <strong>
                  Fall risk
                </strong>
                <span>
                  {displayValue(
                    contentString(
                      content,
                      'fall_risk',
                    ),
                    'Not assessed',
                  )}
                </span>
              </div>

              <div className="list-item">
                <strong>
                  Pressure injury risk
                </strong>
                <span>
                  {displayValue(
                    contentString(
                      content,
                      'pressure_injury_risk',
                    ),
                    'Not assessed',
                  )}
                </span>
              </div>

              <div className="list-item">
                <strong>
                  Infection precautions
                </strong>
                <span>
                  {displayValue(
                    contentString(
                      content,
                      'infection_precautions',
                    ),
                    'None recorded',
                  )}
                </span>
              </div>

              <div className="list-item">
                <strong>
                  Surgical history
                </strong>
                <span>
                  {displayValue(
                    contentString(
                      content,
                      'surgical_history',
                    ),
                  )}
                </span>
              </div>

              <div className="list-item">
                <strong>
                  Past medical history
                </strong>
                <span>
                  {displayValue(
                    contentString(
                      content,
                      'past_medical_history',
                    ),
                  )}
                </span>
              </div>

              <div className="list-item">
                <strong>
                  Nursing observations
                </strong>
                <span>
                  {displayValue(
                    nursingObservations,
                    'None recorded',
                  )}
                </span>
              </div>

              <div className="list-item">
                <strong>
                  Immediate concerns
                </strong>
                <span>
                  {displayValue(
                    immediateConcerns,
                    'None recorded',
                  )}
                </span>
              </div>

              <div className="list-item">
                <strong>
                  Handover notes
                </strong>
                <span>
                  {displayValue(
                    handoverNotes,
                    'None recorded',
                  )}
                </span>
              </div>
            </div>
          </details>
        </>
      )}
        </div>
      </details>
    </section>
  )
}
