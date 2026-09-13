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
  order: ClinicalOrder | undefined,
  orderItemId: string | null,
): string {
  if (!order) {
    return 'Laboratory investigation'
  }

  if (order.order_type === 'LABORATORY') {
    const item =
      orderItemId
        ? order.items.find(
            candidate =>
              candidate.id === orderItemId &&
              candidate.item_type === 'LABORATORY',
          )
        : undefined

    const testName =
      item?.details.test_name

    const testCode =
      item?.details.test_code

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

    const legacyTestName =
      order.details.test_name

    const legacyTestCode =
      order.details.test_code

    if (
      typeof legacyTestName === 'string' &&
      legacyTestName.trim()
    ) {
      return legacyTestName
    }

    if (
      typeof legacyTestCode === 'string' &&
      legacyTestCode.trim()
    ) {
      return legacyTestCode
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
                        result.order_item_id,
                      )}
                    </strong>

                    {order && (
                      <>
                        <span>
                          {order.order_type}
                          {' · '}
                          {order.priority}
                        </span>

                        <span>
                          Ordered{' '}
                          {new Date(
                            order.ordered_at,
                          ).toLocaleString()}
                        </span>
                      </>
                    )}

                    <span>
                      Recorded{' '}
                      {new Date(
                        result.recorded_at,
                      ).toLocaleString()}
                    </span>
                  </div>

                  <span
                    className={
                      result.status === 'FINAL'
                        ? 'clinical-result-status final'
                        : 'clinical-result-status draft'
                    }
                  >
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
                          </span>

                          <span>
                            {formatResultValue(
                              value.value,
                            )}
                          </span>

                          <span>
                            {value.unit ?? '—'}
                          </span>

                          <span>
                            {value.reference_text ??
                              (
                                value.reference_low !== null &&
                                value.reference_high !== null
                                  ? `${value.reference_low}–${value.reference_high}`
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

                {result.interpretation && (
                  <div className="clinical-result-interpretation">
                    <span>
                      Interpretation
                    </span>

                    <p>
                      {result.interpretation}
                    </p>
                  </div>
                )}
              </article>
            )
          },
        )}

      {diagnosticReports.length > 0 && (
        <div className="clinical-diagnostic-reports">
          <h3>
            Diagnostic Reports
          </h3>

          {diagnosticReports.map(
            report => {
              const order =
                orders.find(
                  candidate =>
                    candidate.id ===
                    report.order_id,
                )

              const attachments =
                diagnosticAttachments[
                  report.id
                ] ?? []

              return (
                <article
                  key={report.id}
                  className="workspace-panel clinical-result-report"
                >
                  <div className="clinical-result-report-header">
                    <div>
                      <strong>
                        {order
                          ? getInvestigationLabel(
                              order,
                              null,
                            )
                          : 'Diagnostic investigation'}
                      </strong>

                      {order && (
                        <span>
                          {order.order_type}
                          {' · '}
                          {order.priority}
                        </span>
                      )}

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
                  </div>

                  <div className="clinical-result-interpretation">
                    <span>
                      Report
                    </span>

                    {report.findings && (
                      <p>
                        <strong>Findings:</strong>{' '}
                        {report.findings}
                      </p>
                    )}

                    {report.impression && (
                      <p>
                        <strong>Impression:</strong>{' '}
                        {report.impression}
                      </p>
                    )}

                    {report.interpretation && (
                      <p>
                        <strong>Interpretation:</strong>{' '}
                        {report.interpretation}
                      </p>
                    )}

                    {report.recommendations && (
                      <p>
                        <strong>Recommendations:</strong>{' '}
                        {report.recommendations}
                      </p>
                    )}
                  </div>

                  {attachments.length > 0 && (
                    <div className="clinical-diagnostic-attachments">
                      <strong>
                        Attachments
                      </strong>

                      {attachments.map(
                        attachment => (
                          <a
                            key={attachment.id}
                            href={attachment.url}
                            target="_blank"
                            rel="noreferrer"
                          >
                            {attachment.file_name}
                          </a>
                        ),
                      )}
                    </div>
                  )}
                </article>
              )
            },
          )}
        </div>
      )}
    </section>
  )
}
