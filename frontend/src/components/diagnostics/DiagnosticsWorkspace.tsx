import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  createDiagnosticReport,
  finalizeDiagnosticReport,
  listDiagnosticAttachments,
  listDiagnosticInvestigations,
  listDiagnosticQueue,
  receiveDiagnosticOrder,
  startDiagnosticOrder,
  updateDiagnosticReport,
  uploadDiagnosticAttachment,
  type DiagnosticInvestigation,
  type DiagnosticQueueItem,
  type DiagnosticReport,
  type DiagnosticReportAttachment,
} from '../../api/diagnostics'

interface Props {
  accessToken: string
}

function getInvestigation(
  order: DiagnosticQueueItem | null,
  investigations: DiagnosticInvestigation[],
): DiagnosticInvestigation | null {
  if (!order) {
    return null
  }

  const value =
    order.details.investigation_id

  if (typeof value !== 'string') {
    return null
  }

  return (
    investigations.find(
      item => item.id === value,
    ) ?? null
  )
}

function getTemplateFields(
  investigation: DiagnosticInvestigation | null,
) {
  const fields =
    investigation?.report_template?.fields

  if (!Array.isArray(fields)) {
    return []
  }

  return fields.filter(
    value =>
      typeof value === 'object' &&
      value !== null &&
      typeof (
        value as Record<string, unknown>
      ).code === 'string',
  ) as Array<Record<string, unknown>>
}

function statusLabel(
  status: DiagnosticQueueItem['status'],
): string {
  switch (status) {
    case 'REQUESTED':
      return 'Awaiting receipt'
    case 'RECEIVED':
      return 'Received'
    case 'IN_PROGRESS':
      return 'In progress'
  }
}

export default function DiagnosticsWorkspace({
  accessToken,
}: Props) {
  const [orders, setOrders] =
    useState<DiagnosticQueueItem[]>([])

  const [investigations, setInvestigations] =
    useState<DiagnosticInvestigation[]>([])

  const [selectedOrder, setSelectedOrder] =
    useState<DiagnosticQueueItem | null>(null)

  const [report, setReport] =
    useState<DiagnosticReport | null>(null)

  const [attachments, setAttachments] =
    useState<DiagnosticReportAttachment[]>([])

  const [findings, setFindings] = useState('')
  const [impression, setImpression] = useState('')
  const [interpretation, setInterpretation] =
    useState('')
  const [recommendations, setRecommendations] =
    useState('')

  const [measurements, setMeasurements] =
    useState<Record<string, unknown>>({})

  const [loading, setLoading] =
    useState(true)

  const [working, setWorking] =
    useState(false)

  const [uploading, setUploading] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)

  const [success, setSuccess] =
    useState<string | null>(null)

  const selectedInvestigation =
    useMemo(
      () =>
        getInvestigation(
          selectedOrder,
          investigations,
        ),
      [selectedOrder, investigations],
    )

  async function loadWorkspace() {
    setLoading(true)
    setError(null)

    try {
      const [queue, catalogue] =
        await Promise.all([
          listDiagnosticQueue(accessToken),
          listDiagnosticInvestigations(accessToken),
        ])

      setOrders(queue)
      setInvestigations(catalogue)

      setSelectedOrder(current => {
        if (
          current &&
          queue.some(
            item => item.id === current.id,
          )
        ) {
          return (
            queue.find(
              item => item.id === current.id,
            ) ?? null
          )
        }

        return queue[0] ?? null
      })
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load diagnostics.',
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadWorkspace()
  }, [accessToken])

  useEffect(() => {
    setReport(null)
    setAttachments([])
    setFindings('')
    setImpression('')
    setInterpretation('')
    setRecommendations('')
    setMeasurements({})
    setSuccess(null)
  }, [selectedOrder?.id])

  useEffect(() => {
    if (!report) {
      return
    }

    setFindings(report.findings ?? '')
    setImpression(report.impression ?? '')
    setInterpretation(
      report.interpretation ?? '',
    )
    setRecommendations(
      report.recommendations ?? '',
    )
    setMeasurements(
      report.measurements ?? {},
    )
  }, [report?.id])

  useEffect(() => {
    if (!report) {
      return
    }

    void listDiagnosticAttachments(
      accessToken,
      report.id,
    )
      .then(setAttachments)
      .catch(err => {
        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load attachments.',
        )
      })
  }, [accessToken, report?.id])

  async function handleReceive() {
    if (!selectedOrder) {
      return
    }

    setWorking(true)
    setError(null)

    try {
      await receiveDiagnosticOrder(
        accessToken,
        selectedOrder.id,
      )
      await loadWorkspace()
      setSuccess('Diagnostic order received.')
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to receive order.',
      )
    } finally {
      setWorking(false)
    }
  }

  async function handleStart() {
    if (!selectedOrder) {
      return
    }

    setWorking(true)
    setError(null)

    try {
      await startDiagnosticOrder(
        accessToken,
        selectedOrder.id,
      )
      await loadWorkspace()
      setSuccess(
        'Diagnostic investigation started.',
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to start investigation.',
      )
    } finally {
      setWorking(false)
    }
  }

  async function ensureDraftReport() {
    if (report) {
      return report
    }

    if (!selectedOrder) {
      throw new Error(
        'No diagnostic order selected.',
      )
    }

    if (!selectedInvestigation) {
      throw new Error(
        'Investigation definition could not be found.',
      )
    }

    const created =
      await createDiagnosticReport(
        accessToken,
        {
          order_id: selectedOrder.id,
          investigation_id:
            selectedInvestigation.id,
          category:
            selectedInvestigation.category,
          findings,
          impression,
          interpretation,
          recommendations,
          measurements,
        },
      )

    setReport(created)

    return created
  }

  async function handleSaveDraft() {
    setWorking(true)
    setError(null)

    try {
      const current =
        await ensureDraftReport()

      const updated =
        await updateDiagnosticReport(
          accessToken,
          current.id,
          {
            findings,
            impression,
            interpretation,
            recommendations,
            measurements,
          },
        )

      setReport(updated)
      setSuccess('Diagnostic report saved.')
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to save report.',
      )
    } finally {
      setWorking(false)
    }
  }

  async function handleFinalize() {
    setWorking(true)
    setError(null)

    try {
      const current =
        await ensureDraftReport()

      const updated =
        await updateDiagnosticReport(
          accessToken,
          current.id,
          {
            findings,
            impression,
            interpretation,
            recommendations,
            measurements,
          },
        )

      const finalized =
        await finalizeDiagnosticReport(
          accessToken,
          updated.id,
        )

      setReport(finalized)
      setSuccess(
        'Diagnostic report finalized.',
      )

      await loadWorkspace()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to finalize report.',
      )
    } finally {
      setWorking(false)
    }
  }

  async function handleUpload(
    file: File,
  ) {
    if (!report) {
      return
    }

    setUploading(true)
    setError(null)

    try {
      const attachment =
        await uploadDiagnosticAttachment(
          accessToken,
          report.id,
          file,
        )

      setAttachments(current => [
        ...current,
        attachment,
      ])

      setSuccess(
        `${file.name} uploaded successfully.`,
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to upload attachment.',
      )
    } finally {
      setUploading(false)
    }
  }

  if (loading) {
    return (
      <section className="diagnostics-page">
        <div className="diagnostics-empty">
          Loading diagnostics...
        </div>
      </section>
    )
  }

  return (
    <section className="diagnostics-page">
      <header className="diagnostics-page-header">
        <div>
          <p className="eyebrow">
            CLINICAL DIAGNOSTICS
          </p>
          <h1>Diagnostics</h1>
          <p>
            Investigations, reporting and diagnostic attachments.
          </p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={() => void loadWorkspace()}
        >
          Refresh
        </button>
      </header>

      {error && (
        <div className="alert error-alert">
          {error}
        </div>
      )}

      {success && (
        <div className="alert success-alert">
          {success}
        </div>
      )}

      <div className="diagnostics-shell">
        <aside className="diagnostics-queue">
          <div className="diagnostics-queue-header">
            <div>
              <span className="eyebrow">
                WORKLIST
              </span>
              <h2>Pending investigations</h2>
            </div>
            <strong>{orders.length}</strong>
          </div>

          {orders.length === 0 ? (
            <div className="diagnostics-empty">
              No diagnostic orders are currently awaiting attention.
            </div>
          ) : (
            orders.map(order => {
              const investigation =
                getInvestigation(
                  order,
                  investigations,
                )

              return (
                <button
                  key={order.id}
                  type="button"
                  className={
                    selectedOrder?.id === order.id
                      ? 'diagnostic-queue-item active'
                      : 'diagnostic-queue-item'
                  }
                  onClick={() =>
                    setSelectedOrder(order)
                  }
                >
                  <strong>
                    {investigation?.name ??
                      String(
                        order.details.investigation_name ??
                          'Diagnostic Investigation',
                      )}
                  </strong>

                  <span>
                    {order.patient_name}
                  </span>

                  <small>
                    {order.hospital_number}
                    {' · '}
                    {order.priority}
                  </small>

                  <em>
                    {statusLabel(order.status)}
                  </em>
                </button>
              )
            })
          )}
        </aside>

        <main className="diagnostics-content">
          {!selectedOrder ? (
            <div className="diagnostics-empty">
              Select an investigation from the worklist.
            </div>
          ) : (
            <>
              <section className="diagnostic-order-card">
                <div>
                  <span>Patient</span>
                  <strong>
                    {selectedOrder.patient_name}
                  </strong>
                </div>

                <div>
                  <span>Hospital No.</span>
                  <strong>
                    {selectedOrder.hospital_number}
                  </strong>
                </div>

                <div>
                  <span>Investigation</span>
                  <strong>
                    {selectedInvestigation?.name ??
                      'Diagnostic Investigation'}
                  </strong>
                </div>

                <div>
                  <span>Category</span>
                  <strong>
                    {selectedInvestigation?.category ??
                      String(
                        selectedOrder.details
                          .diagnostic_category ??
                          '',
                      )}
                  </strong>
                </div>

                <div>
                  <span>Ordered by</span>
                  <strong>
                    {selectedOrder.ordering_clinician_name}
                  </strong>
                </div>
              </section>

              <section className="diagnostic-action-bar">
                {selectedOrder.status ===
                  'REQUESTED' && (
                  <button
                    type="button"
                    className="primary-button"
                    disabled={working}
                    onClick={() =>
                      void handleReceive()
                    }
                  >
                    Receive Order
                  </button>
                )}

                {selectedOrder.status ===
                  'RECEIVED' && (
                  <button
                    type="button"
                    className="primary-button"
                    disabled={working}
                    onClick={() =>
                      void handleStart()
                    }
                  >
                    Start Investigation
                  </button>
                )}

                {selectedOrder.status ===
                  'IN_PROGRESS' && (
                  <span className="diagnostic-status">
                    Investigation in progress
                  </span>
                )}
              </section>

              {selectedOrder.status ===
                'IN_PROGRESS' && (
                <section className="diagnostic-report-card">
                  <header>
                    <div>
                      <span className="eyebrow">
                        REPORT
                      </span>

                      <h2>
                        {selectedInvestigation?.name ??
                          'Diagnostic Report'}
                      </h2>
                    </div>

                    {report && (
                      <span
                        className={
                          report.status === 'FINAL'
                            ? 'diagnostic-status final'
                            : 'diagnostic-status draft'
                        }
                      >
                        {report.status}
                      </span>
                    )}
                  </header>

                  <div className="diagnostic-form">
                    <label>
                      <span>Findings</span>
                      <textarea
                        rows={7}
                        value={findings}
                        disabled={
                          report?.status === 'FINAL'
                        }
                        onChange={event =>
                          setFindings(
                            event.target.value,
                          )
                        }
                      />
                    </label>

                    <label>
                      <span>Impression</span>
                      <textarea
                        rows={5}
                        value={impression}
                        disabled={
                          report?.status === 'FINAL'
                        }
                        onChange={event =>
                          setImpression(
                            event.target.value,
                          )
                        }
                      />
                    </label>

                    <label>
                      <span>Interpretation</span>
                      <textarea
                        rows={5}
                        value={interpretation}
                        disabled={
                          report?.status === 'FINAL'
                        }
                        onChange={event =>
                          setInterpretation(
                            event.target.value,
                          )
                        }
                      />
                    </label>

                    <label>
                      <span>Recommendations</span>
                      <textarea
                        rows={4}
                        value={recommendations}
                        disabled={
                          report?.status === 'FINAL'
                        }
                        onChange={event =>
                          setRecommendations(
                            event.target.value,
                          )
                        }
                      />
                    </label>

                    {getTemplateFields(
                      selectedInvestigation,
                    ).length > 0 && (
                      <section className="diagnostic-measurements">
                        <div>
                          <span className="eyebrow">
                            STRUCTURED DATA
                          </span>
                          <h3>Measurements</h3>
                        </div>

                        {getTemplateFields(
                          selectedInvestigation,
                        ).map(field => {
                          const code =
                            String(field.code)

                          const label =
                            typeof field.label ===
                            'string'
                              ? field.label
                              : code

                          const unit =
                            typeof field.unit ===
                            'string'
                              ? field.unit
                              : ''

                          const type =
                            typeof field.type ===
                            'string'
                              ? field.type
                              : 'TEXT'

                          return (
                            <label key={code}>
                              <span>
                                {label}
                                {unit
                                  ? ` (${unit})`
                                  : ''}
                              </span>

                              <input
                                type={
                                  type ===
                                  'NUMBER'
                                    ? 'number'
                                    : 'text'
                                }
                                disabled={
                                  report?.status ===
                                  'FINAL'
                                }
                                value={
                                  measurements[code] == null
                                    ? ''
                                    : String(
                                        measurements[code],
                                      )
                                }
                                onChange={event => {
                                  const value =
                                    type ===
                                    'NUMBER'
                                      ? event
                                          .target
                                          .value === ''
                                        ? ''
                                        : Number(
                                            event
                                              .target
                                              .value,
                                          )
                                      : event
                                          .target
                                          .value

                                  setMeasurements(
                                    current => ({
                                      ...current,
                                      [code]: value,
                                    }),
                                  )
                                }}
                              />
                            </label>
                          )
                        })}
                      </section>
                    )}

                    {report && (
                      <section className="diagnostic-attachments">
                        <div>
                          <span className="eyebrow">
                            FILES
                          </span>
                          <h3>Attachments</h3>
                          <p>
                            Upload the diagnostic image,
                            PDF or supporting document.
                          </p>
                        </div>

                        {report.status ===
                          'DRAFT' && (
                          <label className="upload-button">
                            {uploading
                              ? 'Uploading...'
                              : 'Upload image / PDF'}

                            <input
                              type="file"
                              accept=".pdf,image/png,image/jpeg"
                              hidden
                              disabled={
                                uploading
                              }
                              onChange={event => {
                                const file =
                                  event.target
                                    .files?.[0]

                                event.target.value =
                                  ''

                                if (file) {
                                  void handleUpload(
                                    file,
                                  )
                                }
                              }}
                            />
                          </label>
                        )}

                        {attachments.length >
                          0 && (
                          <div className="diagnostic-attachment-list">
                            {attachments.map(
                              attachment => (
                                <a
                                  key={
                                    attachment.id
                                  }
                                  href={`/api/v1/diagnostics/attachments/${attachment.id}`}
                                  target="_blank"
                                  rel="noreferrer"
                                >
                                  <strong>
                                    {
                                      attachment.file_name
                                    }
                                  </strong>
                                  <small>
                                    {
                                      attachment.content_type
                                    }
                                  </small>
                                </a>
                              ),
                            )}
                          </div>
                        )}
                      </section>
                    )}

                    <div className="diagnostic-report-actions">
                      {(!report ||
                        report.status ===
                          'DRAFT') && (
                        <>
                          <button
                            type="button"
                            className="secondary-button"
                            disabled={working}
                            onClick={() =>
                              void handleSaveDraft()
                            }
                          >
                            Save Draft
                          </button>

                          <button
                            type="button"
                            className="primary-button"
                            disabled={working}
                            onClick={() =>
                              void handleFinalize()
                            }
                          >
                            Finalize Report
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </section>
              )}
            </>
          )}
        </main>
      </div>
    </section>
  )
}
