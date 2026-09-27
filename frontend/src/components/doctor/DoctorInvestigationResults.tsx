import type { ClinicalOrder } from '../../api/clinicalOrders'
import type { DiagnosticReport } from '../../api/diagnostics'
import type { ClinicalResult } from '../../api/clinicalResults'
import DoctorLaboratoryResults from './DoctorLaboratoryResults'

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

      {!loadingClinicalResults && (
        <DoctorLaboratoryResults
          clinicalResults={clinicalResults}
          orders={orders}
        />
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
