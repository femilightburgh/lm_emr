import type { ClinicalEvent } from '../../api/encounters'

interface Props {
  timeline: ClinicalEvent[]
  loadingTimeline: boolean
}

const EVENT_LABELS: Record<string, string> = {
  VITALS_RECORDED: 'Vital signs recorded',
  CLINICAL_NOTE_RECORDED: 'Clinical note recorded',
  DIAGNOSIS_RECORDED: 'Diagnosis recorded',
  MEDICATION_PRESCRIBED: 'Medication prescribed',
  MEDICATION_GIVEN: 'Medication administered',
  INVESTIGATION_ORDERED: 'Investigation ordered',
  CLINICAL_ORDER_CANCELLED: 'Clinical order cancelled',
  RESULT_RECORDED: 'Result recorded',
  PROCEDURE_PERFORMED: 'Procedure performed',
  WOUND_DRESSED: 'Wound dressed',
  EPISODE_ADMITTED: 'Episode admitted',
}

function formatEventLabel(eventType: string): string {
  return (
    EVENT_LABELS[eventType] ??
    eventType.toLowerCase().replaceAll('_', ' ')
  )
}

export default function DoctorEncounterTimeline({
  timeline,
  loadingTimeline,
}: Props) {
  return (
    <section className="workspace-panel doctor-timeline-panel">
      <details>
        <summary className="doctor-context-summary">
          <div>
            <p className="eyebrow">CARE CONTEXT</p>
            <h2>Timeline</h2>
            <p>Clinical events recorded for this encounter.</p>
          </div>

          <div className="doctor-context-summary-meta">
            <span>
              {timeline.length}{' '}
              event{timeline.length === 1 ? '' : 's'}
            </span>
          </div>
        </summary>

        <div className="doctor-context-body">
          {loadingTimeline && (
            <p>Loading clinical timeline...</p>
          )}

          {!loadingTimeline && timeline.length === 0 && (
            <p>No clinical events recorded yet.</p>
          )}

          {!loadingTimeline && timeline.length > 0 && (
            <div className="doctor-timeline-list">
              {timeline.map(event => (
                <div
                  key={event.id}
                  className="doctor-timeline-item"
                >
                  <strong>
                    {formatEventLabel(event.event_type)}
                  </strong>

                  <span>
                    {new Date(event.occurred_at).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </details>
    </section>
  )
}
