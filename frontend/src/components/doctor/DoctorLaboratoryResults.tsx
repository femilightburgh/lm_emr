import type { ClinicalOrder } from '../../api/clinicalOrders'
import type { ClinicalResult, ClinicalResultValue } from '../../api/clinicalResults'

interface Props {
  clinicalResults: ClinicalResult[]
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
    const item = orderItemId
      ? order.items.find(
          candidate =>
            candidate.id === orderItemId &&
            candidate.item_type === 'LABORATORY',
        )
      : undefined

    const testName = item?.details.test_name
    const testCode = item?.details.test_code

    if (typeof testName === 'string' && testName.trim()) {
      return testName
    }

    if (typeof testCode === 'string' && testCode.trim()) {
      return testCode
    }

    const legacyTestName = order.details.test_name
    const legacyTestCode = order.details.test_code

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

  const studyCode = order.details.study_code

  if (typeof studyCode === 'string' && studyCode.trim()) {
    return studyCode
  }

  return 'Radiology investigation'
}

function formatResultValue(value: unknown): string {
  if (value === null || value === undefined || value === '') {
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

function getAnalyteName(value: ClinicalResultValue): string {
  return (
    value.custom_analyte_name?.trim() ||
    value.analyte_name?.trim() ||
    'Unnamed analyte'
  )
}

function getAnalyteUnit(value: ClinicalResultValue): string {
  return (
    value.custom_unit?.trim() ||
    value.unit?.trim() ||
    '—'
  )
}

function getReference(value: ClinicalResultValue): string {
  const low = value.custom_reference_low ?? value.reference_low
  const high = value.custom_reference_high ?? value.reference_high

  let range = '—'

  if (low !== null && high !== null) {
    range = `${low}–${high}`
  } else if (low !== null) {
    range = `≥ ${low}`
  } else if (high !== null) {
    range = `≤ ${high}`
  }

  const text =
    value.custom_reference_text?.trim() ||
    value.reference_text?.trim()

  if (range !== '—' && text) {
    return `${range} · ${text}`
  }

  if (text) {
    return text
  }

  return range
}

function getAnalyteCode(value: ClinicalResultValue): string | null {
  return (
    value.custom_analyte_code?.trim() ||
    value.analyte_code?.trim() ||
    null
  )
}

export default function DoctorLaboratoryResults({
  clinicalResults,
  orders,
}: Props) {
  return (
    <>
      {!clinicalResults.length && (
        <p>No laboratory results recorded.</p>
      )}

      {clinicalResults.map(result => {
        const order = orders.find(
          candidate => candidate.id === result.order_id,
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
                      {new Date(order.ordered_at).toLocaleString()}
                    </span>
                  </>
                )}

                <span>
                  Recorded{' '}
                  {new Date(result.recorded_at).toLocaleString()}
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
                <span>Specimen</span>
                <strong>
                  {result.specimen ?? 'Not recorded'}
                </strong>
              </div>

              <div>
                <span>Collected</span>
                <strong>
                  {result.collected_at
                    ? new Date(result.collected_at).toLocaleString()
                    : 'Not recorded'}
                </strong>
              </div>

              <div>
                <span>Reported</span>
                <strong>
                  {result.reported_at
                    ? new Date(result.reported_at).toLocaleString()
                    : 'Not recorded'}
                </strong>
              </div>
            </div>

            <div className="clinical-result-table">
              <div className="clinical-result-table-header">
                <span>Analyte</span>
                <span>Result</span>
                <span>Unit</span>
                <span>Reference</span>
                <span>Flag</span>
              </div>

              {result.values.length === 0 ? (
                <p>No structured result values recorded.</p>
              ) : (
                result.values.map(value => {
                  const analyteCode =
                    getAnalyteCode(value)

                  return (
                    <div
                      key={value.id}
                      className="clinical-result-table-row"
                    >
                      <span>
                        <strong>
                          {getAnalyteName(value)}
                        </strong>

                        {analyteCode && (
                          <small>
                            {analyteCode}
                          </small>
                        )}
                      </span>

                      <span>
                        {formatResultValue(value.value)}
                      </span>

                      <span>
                        {getAnalyteUnit(value)}
                      </span>

                      <span>
                        {getReference(value)}
                      </span>

                      <span>
                        <span
                          className={
                            value.abnormal_flag === 'HIGH' ||
                            value.abnormal_flag === 'LOW'
                              ? 'clinical-result-flag abnormal'
                              : value.abnormal_flag === 'NORMAL'
                                ? 'clinical-result-flag normal'
                                : 'clinical-result-flag'
                          }
                        >
                          {value.abnormal_flag ?? '—'}
                        </span>
                      </span>
                    </div>
                  )
                })
              )}
            </div>

            {result.interpretation && (
              <div className="clinical-result-interpretation">
                <span>Interpretation</span>
                <p>{result.interpretation}</p>
              </div>
            )}
          </article>
        )
      })}
    </>
  )
}
