import type { ClinicalOrder } from '../../api/clinicalOrders'
import type { DiagnosticReport } from '../../api/diagnostics'
import type { ClinicalResult } from '../../api/clinicalResults'

import type {
  DoctorDiagnosticAttachment,
} from './doctorEncounterContext'

interface Props {
  showResults: boolean
  loadingClinicalResults: boolean
  clinicalResults: ClinicalResult[]
  diagnosticReports: DiagnosticReport[]
  diagnosticAttachments: Record<
    string,
    DoctorDiagnosticAttachment[]
  >
  orders: ClinicalOrder[]
}

function getInvestigationLabel(
  order: ClinicalOrder,
): string {
  if (order.order_type === 'LABORATORY') {
    const testName = order.details.test_name
    const testCode = order.details.test_code

    if (
      typeof testName === 'string' &&
      testName.trim()
    ) {
      return testName
    }

    if (
      typeof testCode === 'string' &&
      testCode.trim()
    ) {
      return testCode
    }

    return 'Laboratory investigation'
  }

  const studyCode =
    order.details.study_code

  if (
    typeof studyCode === 'string' &&
    studyCode.trim()
  ) {
    return studyCode
  }

  return 'Radiology investigation'
}

function formatResultValue(
  value: unknown,
): string {
  if (
    value === null ||
    value === undefined
  ) {
    return '—'
  }

  if (
    typeof value === 'string' ||
    typeof value === 'number' ||
    typeof value === 'boolean'
  ) {
    return String(value)
  }

  return JSON.stringify(value)
}

export default function DoctorInvestigationResults({
  showResults,
  loadingClinicalResults,
  clinicalResults,
  diagnosticReports,
  diagnosticAttachments,
  orders,
}: Props) {
  if (!showResults) {
    return null
  }

  return (
    <section className="workspace-panel">
  <div className="panel-header">
    <div>
      <h2>
        Investigation Results
      </h2>

      <p>
        Results available for clinical review.
      </p>
    </div>
  </div>

  {loadingClinicalResults && (
    <p>
      Loading investigation results...
    </p>
  )}

  {!loadingClinicalResults &&
    clinicalResults.length === 0 &&
    diagnosticReports.length === 0 && (
      <p>
        No investigation results recorded.
      </p>
    )}

  {!loadingClinicalResults &&
    clinicalResults.map(
      result => {
        const order =
          orders.find(
            candidate =>
              candidate.id ===
              result.order_id,
          )

        if (!order) {
          return null
        }

        return (
          <article
            key={result.id}
            className="workspace-panel clinical-result-report"
          >
            <div className="clinical-result-report-header">
              <div>
                <strong>
                  {getInvestigationLabel(
                    order,
                  )}
                </strong>

                <span>
                  {order.order_type}
                  {' · '}
                  {order.priority}
                </span>

                <span>
                  Recorded{' '}
                  {new Date(
                    result.recorded_at,
                  ).toLocaleString()}
                </span>
              </div>

              <span className={
                result.status === 'FINAL'
                  ? 'clinical-result-status final'
                  : 'clinical-result-status draft'
              }>
                {result.status}
              </span>
            </div>

            <div className="clinical-result-report-meta">
              <div>
                <span>
                  Specimen
                </span>

                <strong>
                  {result.specimen ??
                    'Not recorded'}
                </strong>
              </div>

              <div>
                <span>
                  Collected
                </span>

                <strong>
                  {result.collected_at
                    ? new Date(
                        result.collected_at,
                      ).toLocaleString()
                    : 'Not recorded'}
                </strong>
              </div>

              <div>
                <span>
                  Reported
                </span>

                <strong>
                  {result.reported_at
                    ? new Date(
                        result.reported_at,
                      ).toLocaleString()
                    : 'Not recorded'}
                </strong>
              </div>
            </div>

            <div className="clinical-result-table">
              <div className="clinical-result-table-header">
                <span>
                  Analyte
                </span>

                <span>
                  Result
                </span>

                <span>
                  Unit
                </span>

                <span>
                  Reference
                </span>

                <span>
                  Flag
                </span>
              </div>

              {result.values.length === 0 ? (
                <p>
                  No structured result values recorded.
                </p>
              ) : (
                result.values.map(
                  value => (
                    <div
                      key={value.id}
                      className="clinical-result-table-row"
                    >
                      <span>
                        <strong>
                          {value.analyte_name}
                        </strong>

                        <small>
                          {value.analyte_code}
                        </small>
                      </span>

                      <strong>
                        {formatResultValue(
                          value.value,
                        )}
                      </strong>

                      <span>
                        {value.unit ??
                          '—'}
                      </span>

                      <span>
                        {value.reference_text ??
                          (
                            value.reference_low !== null &&
                            value.reference_high !== null
                              ? `${value.reference_low}–${value.reference_high}`
                              : value.reference_low !== null
                                ? `≥ ${value.reference_low}`
                                : value.reference_high !== null
                                  ? `≤ ${value.reference_high}`
                                  : '—'
                          )}
                      </span>

                      <span>
                        {value.abnormal_flag ??
                          '—'}
                      </span>
                    </div>
                  ),
                )
              )}
            </div>

            <div className="clinical-result-interpretation">
              <span>
                Interpretation
              </span>

              <p>
                {result.interpretation ??
                  'No interpretation recorded.'}
              </p>
            </div>
          </article>
        )
      },
    )}

  {diagnosticReports.length === 0 ? (
    <p>
      No finalized diagnostic reports recorded.
    </p>
  ) : (
    diagnosticReports.map(
      report => {
        const order =
          orders.find(
            candidate =>
              candidate.id ===
              report.order_id,
          )

        const investigationName =
          typeof order?.details
            .investigation_name ===
          'string'
            ? order.details
                .investigation_name
            : typeof order?.details
                .investigation_code ===
              'string'
              ? order.details
                  .investigation_code
              : 'Diagnostic investigation'

        return (
          <article
            key={report.id}
            className="workspace-panel clinical-result-report diagnostic-result-report"
          >
            <details className="doctor-diagnostic-report-details">
              <summary className="clinical-result-report-header doctor-diagnostic-report-summary">
                <div>
                  <strong>
                    {investigationName}
                  </strong>

                  <span>
                    DIAGNOSTIC
                    {' · '}
                    {order?.priority ??
                      'ROUTINE'}
                  </span>

                  <span>
                    Reported{' '}
                    {report.reported_at
                      ? new Date(
                          report.reported_at,
                        ).toLocaleString()
                      : 'Not recorded'}
                  </span>
                </div>

                <span className="clinical-result-status final">
                  FINAL
                </span>
              </summary>

            <div className="clinical-result-report-meta">
              <div>
                <span>
                  Category
                </span>

                <strong>
                  {report.category}
                </strong>
              </div>

              <div>
                <span>
                  Recorded
                </span>

                <strong>
                  {report.recorded_at
                    ? new Date(
                        report.recorded_at,
                      ).toLocaleString()
                    : 'Not recorded'}
                </strong>
              </div>
            </div>

            {report.findings?.trim() && (
              <div className="clinical-result-interpretation">
                <span>
                  Findings
                </span>

                <p>
                  {report.findings}
                </p>
              </div>
            )}

            {report.impression?.trim() && (
              <div className="clinical-result-interpretation">
                <span>
                  Impression
                </span>

                <p>
                  {report.impression}
                </p>
              </div>
            )}

            {report.interpretation?.trim() && (
              <div className="clinical-result-interpretation">
                <span>
                  Interpretation
                </span>

                <p>
                  {report.interpretation}
                </p>
              </div>
            )}

            {report.recommendations?.trim() && (
              <div className="clinical-result-interpretation">
                <span>
                  Recommendations
                </span>

                <p>
                  {report.recommendations}
                </p>
              </div>
            )}

            {report.measurements &&
              Object.keys(
                report.measurements,
              ).length > 0 && (
                <div className="clinical-result-report-meta diagnostic-measurement-grid">
                  {Object.entries(
                    report.measurements,
                  ).map(
                    ([key, value]) => (
                      <div key={key}>
                        <span>
                          {key.replace(
                            /_/g,
                            ' ',
                          )}
                        </span>

                        <strong>
                          {value === null ||
                          value === undefined
                            ? '—'
                            : typeof value ===
                                'object'
                              ? JSON.stringify(
                                  value,
                                )
                              : String(
                                  value,
                                )}
                        </strong>
                      </div>
                    ),
                  )}
                </div>
              )}

            {diagnosticAttachments[report.id]
              ?.length > 0 && (
              <div className="diagnostic-doctor-attachments">
                <div>
                  <span className="diagnostic-doctor-section-label">
                    Attachments
                  </span>

                  <p className="diagnostic-doctor-attachments-help">
                    Supporting diagnostic images and documents.
                  </p>
                </div>

                <div className="diagnostic-doctor-attachment-list">
                  {diagnosticAttachments[
                    report.id
                  ].map(
                    attachment => {
                      const isImage =
                        attachment.content_type.startsWith(
                          'image/',
                        )

                      const isPdf =
                        attachment.content_type ===
                        'application/pdf'

                      return (
                        <div
                          key={
                            attachment.id
                          }
                          className="diagnostic-doctor-attachment"
                        >
                          {isImage ? (
                            <a
                              href={
                                attachment.url
                              }
                              target="_blank"
                              rel="noreferrer"
                              className="diagnostic-doctor-image-link"
                            >
                              <img
                                src={
                                  attachment.url
                                }
                                alt={
                                  attachment.description ??
                                  attachment.file_name
                                }
                                className="diagnostic-doctor-image"
                              />
                            </a>
                          ) : (
                            <div className="diagnostic-doctor-file">
                              <strong>
                                {
                                  attachment.file_name
                                }
                              </strong>

                              {attachment.description && (
                                <span>
                                  {
                                    attachment.description
                                  }
                                </span>
                              )}

                              {isPdf && (
                                <a
                                  href={
                                    attachment.url
                                  }
                                  target="_blank"
                                  rel="noreferrer"
                                >
                                  Open PDF
                                </a>
                              )}
                            </div>
                          )}

                          {isImage &&
                            attachment.description && (
                              <span>
                                {
                                  attachment.description
                                }
                              </span>
                            )}
                        </div>
                      )
                    },
                  )}
                </div>
              </div>
            )}
            </details>
          </article>
        )
      },
    )
  )}
</section>
  )
}
