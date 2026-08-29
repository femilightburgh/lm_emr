import type { ClinicalDocument } from '../../api/clinicalDocuments'
import type { ClinicalDiagnosis } from '../../api/diagnoses'
import type { ClinicalOrder } from '../../api/clinicalOrders'
import type { ClinicalEvent, Encounter } from '../../api/encounters'
import type { Episode } from '../../api/episodes'
import type { Vitals } from '../../api/vitals'


interface Props {
  episode: Episode | null
  encounter: Encounter | null

  documents: ClinicalDocument[]
  diagnoses: ClinicalDiagnosis[]
  orders: ClinicalOrder[]
  vitals: Vitals[]
  timeline: ClinicalEvent[]

  loading: boolean
  onCloseHistory: () => void
}


function formatDate(
  value: string | null | undefined,
): string {
  if (!value) {
    return '—'
  }

  return new Date(value).toLocaleString()
}


export default function HistoricalEncounterPanel({
  episode,
  encounter,
  documents,
  diagnoses,
  orders,
  vitals,
  timeline,
  loading,
  onCloseHistory,
}: Props) {
  if (!episode || !encounter) {
    return null
  }

  return (
    <section className="workspace-panel">
      <div className="panel-header">
        <div>
          <h2>Historical Encounter</h2>
          <p>
            Read-only clinical history.
          </p>
        </div>

        <span>
          {encounter.status}
        </span>
      </div>

      <div className="selected-diagnosis">
        <strong>
          {encounter.title}
        </strong>

        <span>
          {episode.episode_number}
          {' · '}
          {episode.title}
        </span>

        <span>
          Started {formatDate(
            encounter.started_at,
          )}
          {encounter.ended_at
            ? ` · ended ${formatDate(
                encounter.ended_at,
              )}`
            : ''}
        </span>
      </div>

      <div className="inline-fields">
        <button
          type="button"
          onClick={onCloseHistory}
        >
          Close History
        </button>
      </div>

      {loading && (
        <p>
          Loading historical encounter...
        </p>
      )}

      {!loading && (
        <>
          <div className="diagnosis-list">
            <h3>Documents</h3>

            {documents.length === 0 ? (
              <p>
                No clinical documents recorded.
              </p>
            ) : (
              documents.map(document => (
                <div
                  key={document.id}
                  className="list-item"
                >
                  <strong>
                    {document.document_type}
                  </strong>

                  <span>
                    {document.status}
                    {' · v'}
                    {document.version}
                    {document.signed_at
                      ? ` · signed ${formatDate(
                          document.signed_at,
                        )}`
                      : ''}
                  </span>
                </div>
              ))
            )}
          </div>

          <div className="diagnosis-list">
            <h3>Diagnoses</h3>

            {diagnoses.length === 0 ? (
              <p>
                No diagnoses recorded.
              </p>
            ) : (
              diagnoses.map(diagnosis => (
                <div
                  key={diagnosis.id}
                  className="list-item"
                >
                  <strong>
                    {diagnosis.diagnosis_name}
                  </strong>

                  <span>
                    {diagnosis.code
                      ? `${diagnosis.code} · `
                      : ''}
                    {diagnosis.diagnosis_type}
                    {' · '}
                    {diagnosis.certainty}
                  </span>
                </div>
              ))
            )}
          </div>

          <div className="diagnosis-list">
            <h3>Orders</h3>

            {orders.length === 0 ? (
              <p>
                No clinical orders recorded.
              </p>
            ) : (
              orders.map(order => (
                <div
                  key={order.id}
                  className="list-item"
                >
                  <strong>
                    {order.order_type}
                  </strong>

                  <span>
                    {order.status}
                    {' · '}
                    {order.priority}
                  </span>
                </div>
              ))
            )}
          </div>

          <div className="diagnosis-list">
            <h3>Vitals</h3>

            {vitals.length === 0 ? (
              <p>
                No vitals recorded.
              </p>
            ) : (
              vitals
                .slice()
                .sort(
                  (a, b) =>
                    new Date(
                      b.occurred_at,
                    ).getTime() -
                    new Date(
                      a.occurred_at,
                    ).getTime(),
                )
                .map(vital => (
                  <div
                    key={vital.id}
                    className="list-item"
                  >
                    <strong>
                      {formatDate(
                        vital.occurred_at,
                      )}
                    </strong>

                    <span>
                      Temp{' '}
                      {vital.payload.temperature ?? '—'}
                      {' · '}
                      BP{' '}
                      {vital.payload.systolic_bp ?? '—'}
                      /
                      {vital.payload.diastolic_bp ?? '—'}
                      {' · HR '}
                      {vital.payload.heart_rate ?? '—'}
                      {' · RR '}
                      {vital.payload.respiratory_rate ?? '—'}
                      {' · SpO₂ '}
                      {vital.payload.spo2 ?? '—'}
                    </span>
                  </div>
                ))
            )}
          </div>

          <div className="diagnosis-list">
            <h3>Timeline</h3>

            {timeline.length === 0 ? (
              <p>
                No clinical events recorded.
              </p>
            ) : (
              timeline.map(event => (
                <div
                  key={event.id}
                  className="list-item"
                >
                  <strong>
                    {event.event_type}
                  </strong>

                  <span>
                    {formatDate(
                      event.occurred_at,
                    )}
                  </span>
                </div>
              ))
            )}
          </div>
        </>
      )}
    </section>
  )
}
