import {
  useEffect,
  useRef,
  useState,
} from 'react'

import {
  createClinicalResult,
  finalizeClinicalResult,
  listOrderClinicalResults,
  updateClinicalResult,
} from '../../api/clinicalResults'

import {
  listLaboratoryQueue,
  listLaboratoryTests,
  receiveLaboratoryOrderItem,
  startLaboratoryOrderItem,
  type LaboratoryQueueItem,
  type LaboratoryTest,
} from '../../api/laboratory'

import type {
  ClinicalOrderItem,
} from '../../api/clinicalOrders'

interface Props {
  accessToken: string
}


interface ResultValue {
  analyteId: string
  value: string
}


function getLaboratoryTestForItem(
  item: ClinicalOrderItem | null,
  laboratoryTests: LaboratoryTest[],
): LaboratoryTest | null {
  if (!item || item.item_type !== 'LABORATORY') {
    return null
  }

  if (item.laboratory_test_id) {
    const testById =
      laboratoryTests.find(
        test =>
          test.id === item.laboratory_test_id,
      )

    if (testById) {
      return testById
    }
  }

  const code =
    typeof item.details.test_code === 'string'
      ? item.details.test_code.trim().toUpperCase()
      : ''

  const name =
    typeof item.details.test_name === 'string'
      ? item.details.test_name.trim().toUpperCase()
      : ''

  return (
    laboratoryTests.find(
      test =>
        test.code.toUpperCase() === code ||
        test.name.toUpperCase() === name,
    ) ?? null
  )
}


function getLaboratoryStatusLabel(
  status: ClinicalOrderItem['status'],
): string {
  const labels: Record<
    ClinicalOrderItem['status'],
    string
  > = {
    REQUESTED: 'Awaiting receipt',
    RECEIVED: 'Received',
    IN_PROGRESS: 'Processing',
    COMPLETED: 'Completed',
    CANCELLED: 'Cancelled',
  }

  return labels[status]
}


function getInvestigationName(
  order: LaboratoryQueueItem,
): string {
  const testName =
    order.details.test_name

  if (
    order.order_type === 'LABORATORY' &&
    typeof testName === 'string' &&
    testName.trim()
  ) {
    return testName
  }

  const testCode =
    order.details.test_code

  if (
    order.order_type === 'LABORATORY' &&
    typeof testCode === 'string' &&
    testCode.trim()
  ) {
    return testCode
  }

  return 'Laboratory Investigation'
}


interface LaboratoryPatientGroup {
  key: string
  patient_id: string
  patient_name: string
  hospital_number: string
  episode_number: string
  orders: LaboratoryQueueItem[]
}


function groupLaboratoryOrders(
  orders: LaboratoryQueueItem[],
): LaboratoryPatientGroup[] {
  const groups = new Map<
    string,
    LaboratoryPatientGroup
  >()

  for (const order of orders) {
    const key =
      `${order.patient_id}:${order.episode_number}`

    const existing = groups.get(key)

    if (existing) {
      existing.orders.push(order)
      continue
    }

    groups.set(
      key,
      {
        key,
        patient_id: order.patient_id,
        patient_name: order.patient_name,
        hospital_number: order.hospital_number,
        episode_number: order.episode_number,
        orders: [order],
      },
    )
  }

  return Array.from(
    groups.values(),
  )
}


export default function LaboratoryWorkspace({
  accessToken,
}: Props) {
  const [orders, setOrders] =
    useState<LaboratoryQueueItem[]>([])

  const [laboratoryTests, setLaboratoryTests] =
    useState<LaboratoryTest[]>([])

  const [selectedOrder, setSelectedOrder] =
    useState<LaboratoryQueueItem | null>(null)

  const [selectedOrderItem, setSelectedOrderItem] =
    useState<ClinicalOrderItem | null>(null)

  const [loading, setLoading] =
    useState(true)

  const [startingOrder, setStartingOrder] =
    useState(false)

  const [savingResult, setSavingResult] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)

  const [success, setSuccess] =
    useState<string | null>(null)

  const [resultValues, setResultValues] =
    useState<ResultValue[]>([])

  const [interpretation, setInterpretation] =
    useState('')

  const [specimen, setSpecimen] =
    useState('')

  const [collectedAt, setCollectedAt] =
    useState('')

  const [draftResultId, setDraftResultId] =
    useState<string | null>(null)

  const [reviewingResult, setReviewingResult] =
    useState(false)

  const [queueFilter, setQueueFilter] =
    useState<'ALL' | ClinicalOrderItem['status']>('ALL')

  const [queueSearch, setQueueSearch] =
    useState('')

  const draftLoadToken =
    useRef(0)


  async function loadQueue() {
    setLoading(true)
    setError(null)

    try {
      const [
        queue,
        tests,
      ] = await Promise.all([
        listLaboratoryQueue(
          accessToken,
        ),
        listLaboratoryTests(
          accessToken,
        ),
      ])

      setOrders(queue)
      setLaboratoryTests(tests)

      setSelectedOrder(
        current =>
          current &&
          queue.some(
            order =>
              order.id === current.id,
          )
            ? queue.find(
                order =>
                  order.id === current.id,
              ) ?? null
            : queue[0] ?? null,
      )

      setSelectedOrderItem(
        currentItem => {
          if (!currentItem) {
            return null
          }

          const refreshedOrder =
            queue.find(
              order =>
                order.id ===
                selectedOrder?.id,
            )

          return (
            refreshedOrder?.items.find(
              item =>
                item.id === currentItem.id,
            ) ?? null
          )
        },
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load laboratory queue.',
      )
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    void loadQueue()
  }, [accessToken])


  function resetResultForm(
    item?: ClinicalOrderItem | null,
  ) {
    setDraftResultId(null)
    setReviewingResult(false)

    const test =
      getLaboratoryTestForItem(
        item ?? null,
        laboratoryTests,
      )

    setResultValues(
      test
        ? test.analytes.map(analyte => ({
            analyteId: analyte.id,
            value: '',
          }))
        : [],
    )

    setInterpretation('')
    setSpecimen(
      test?.specimen ?? '',
    )
    setCollectedAt('')
  }



  async function loadDraftForOrder(
    order: LaboratoryQueueItem,
    orderItem: ClinicalOrderItem,
  ) {
    const token =
      ++draftLoadToken.current

    setDraftResultId(null)
    setReviewingResult(false)

    try {
      const results =
        await listOrderClinicalResults(
          accessToken,
          order.id,
        )

      // Ignore responses belonging to an older
      // order selection.
      if (
        token !== draftLoadToken.current
      ) {
        return
      }

      const draft =
        results.find(
          result =>
            result.status === 'DRAFT' &&
            result.order_item_id ===
              orderItem.id,
        )

      if (!draft) {
        return
      }

      const test =
        getLaboratoryTestForItem(
          orderItem,
          laboratoryTests,
        )

      if (!test) {
        return
      }

      setDraftResultId(draft.id)
      setSpecimen(
        draft.specimen ??
        test.specimen ??
        '',
      )

      setCollectedAt(
        draft.collected_at
          ? new Date(
              draft.collected_at,
            )
              .toISOString()
              .slice(0, 16)
          : '',
      )

      setInterpretation(
        draft.interpretation ??
        '',
      )

      setResultValues(
        test.analytes.map(
          analyte => {
            const saved =
              draft.values.find(
                value =>
                  value.analyte_id ===
                  analyte.id,
              )

            const value =
              saved?.value === null ||
              saved?.value === undefined
                ? ''
                : String(
                    saved.value,
                  )

            return {
              analyteId: analyte.id,
              value,
            }
          },
        ),
      )

      setSuccess(
        'Draft result restored.',
      )
    } catch (err) {
      if (
        token !== draftLoadToken.current
      ) {
        return
      }

      setError(
        err instanceof Error
          ? err.message
          : 'Unable to restore draft result.',
      )
    }
  }


  function selectOrderItem(
    order: LaboratoryQueueItem,
    orderItem: ClinicalOrderItem,
  ) {
    draftLoadToken.current += 1

    setSelectedOrder(order)
    setSelectedOrderItem(orderItem)
    setError(null)
    setSuccess(null)
    resetResultForm(orderItem)

    if (
      orderItem.status ===
      'IN_PROGRESS'
    ) {
      void loadDraftForOrder(
        order,
        orderItem,
      )
    }
  }


  function updateResultValue(
    analyteId: string,
    value: string,
  ) {
    setResultValues(
      current => {
        const existing =
          current.some(
            item =>
              String(item.analyteId) ===
              String(analyteId),
          )

        if (existing) {
          return current.map(
            item =>
              String(item.analyteId) ===
              String(analyteId)
                ? {
                    ...item,
                    value,
                  }
                : item,
          )
        }

        return [
          ...current,
          {
            analyteId,
            value,
          },
        ]
      },
    )
  }


  const filteredOrders = orders.filter(order => {
    const matchesStatus =
      queueFilter === 'ALL' ||
      order.items.some(item => item.item_type === 'LABORATORY' && item.status === queueFilter)

    const search = queueSearch.trim().toLowerCase()
    const matchesSearch = !search ||
      order.patient_name.toLowerCase().includes(search) ||
      order.hospital_number.toLowerCase().includes(search) ||
      order.items.some(item => {
        const name = typeof item.details.test_name === 'string' ? item.details.test_name : ''
        const code = typeof item.details.test_code === 'string' ? item.details.test_code : ''
        return name.toLowerCase().includes(search) || code.toLowerCase().includes(search)
      })

    return matchesStatus && matchesSearch
  })

  const groupedOrders =
    groupLaboratoryOrders(filteredOrders)

  const laboratoryItemCount = orders.flatMap(order => order.items).filter(item => item.item_type === 'LABORATORY')
  const queueCounts = {
    all: laboratoryItemCount.length,
    requested: laboratoryItemCount.filter(item => item.status === 'REQUESTED').length,
    received: laboratoryItemCount.filter(item => item.status === 'RECEIVED').length,
    processing: laboratoryItemCount.filter(item => item.status === 'IN_PROGRESS').length,
  }

  const selectedLaboratoryTest =
    getLaboratoryTestForItem(
      selectedOrderItem,
      laboratoryTests,
    )


  async function receiveSelectedOrderItem() {
    if (!selectedOrder || !selectedOrderItem) {
      return
    }

    setStartingOrder(true)
    setError(null)
    setSuccess(null)

    try {
      const updated =
        await receiveLaboratoryOrderItem(
          accessToken,
          selectedOrderItem.id,
        )

      const updatedQueueItem:
        LaboratoryQueueItem = {
          ...selectedOrder,
          status: updated.status as
            LaboratoryQueueItem['status'],
          items: updated.items,
        }

      const updatedItem =
        updated.items.find(
          item =>
            item.id ===
            selectedOrderItem.id,
        )

      setSelectedOrder(
        updatedQueueItem,
      )

      setSelectedOrderItem(
        updatedItem ??
          selectedOrderItem,
      )

      setOrders(
        current =>
          current.map(
            order =>
              order.id === updated.id
                ? updatedQueueItem
                : order,
          ),
      )

      setSuccess(
        'Laboratory investigation received.',
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to receive laboratory investigation.',
      )
    } finally {
      setStartingOrder(false)
    }
  }


  async function startSelectedOrderItem() {
    if (!selectedOrder || !selectedOrderItem) {
      return
    }

    setStartingOrder(true)
    setError(null)
    setSuccess(null)

    try {
      const updated =
        await startLaboratoryOrderItem(
          accessToken,
          selectedOrderItem.id,
        )

      const updatedQueueItem:
        LaboratoryQueueItem = {
          ...selectedOrder,
          status: updated.status as
            LaboratoryQueueItem['status'],
          started_at:
            updated.started_at,
          items: updated.items,
        }

      const updatedItem =
        updated.items.find(
          item =>
            item.id ===
            selectedOrderItem.id,
        )

      setSelectedOrder(
        updatedQueueItem,
      )

      setSelectedOrderItem(
        updatedItem ??
          selectedOrderItem,
      )

      setOrders(
        current =>
          current.map(
            order =>
              order.id === updated.id
                ? updatedQueueItem
                : order,
          ),
      )

      setSuccess(
        'Laboratory investigation started.',
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to start laboratory investigation.',
      )
    } finally {
      setStartingOrder(false)
    }
  }


  async function saveResultDraft() {
    if (!selectedOrder || !selectedOrderItem) {
      setError(
        'Select a laboratory investigation before saving a result.',
      )
      return
    }

    if (
      selectedOrderItem.status !==
      'IN_PROGRESS'
    ) {
      setError(
        'Start the laboratory order before saving a draft.',
      )
      return
    }

    const test =
      getLaboratoryTestForItem(
        selectedOrderItem,
        laboratoryTests,
      )

    if (!test) {
      setError(
        'Laboratory test definition could not be found.',
      )
      return
    }

    const values = []

    for (const analyte of test.analytes) {
      const entry =
        resultValues.find(
          item =>
            item.analyteId ===
            analyte.id,
        )

      const rawValue =
        entry?.value.trim() ?? ''

      if (!rawValue) {
        continue
      }

      if (
        analyte.data_type ===
        'NUMERIC'
      ) {
        const numericValue =
          Number(rawValue)

        if (
          !Number.isFinite(
            numericValue,
          )
        ) {
          setError(
            `${analyte.name} must be a valid number.`,
          )
          return
        }

        values.push({
          analyte_id:
            analyte.id,
          value_numeric:
            numericValue,
        })

        continue
      }

      if (
        analyte.data_type ===
        'BOOLEAN'
      ) {
        values.push({
          analyte_id:
            analyte.id,
          value_boolean:
            rawValue === 'true',
        })

        continue
      }

      if (
        analyte.data_type ===
        'CODED'
      ) {
        values.push({
          analyte_id:
            analyte.id,
          value_code:
            rawValue,
        })

        continue
      }

      values.push({
        analyte_id:
          analyte.id,
        value_text:
          rawValue,
      })
    }

    setSavingResult(true)
    setError(null)
    setSuccess(null)

    try {
      const payload = {
        order_id:
          selectedOrder.id,

        order_item_id:
          selectedOrderItem.id,

        result_type:
          'LABORATORY' as const,

        status:
          'DRAFT' as const,

        specimen:
          specimen.trim() ||
          test.specimen ||
          undefined,

        collected_at:
          collectedAt
            ? new Date(
                collectedAt,
              ).toISOString()
            : undefined,

        interpretation:
          interpretation.trim() ||
          undefined,

        values,
      }

      const saved =
        draftResultId
          ? await updateClinicalResult(
              accessToken,
              draftResultId,
              payload,
            )
          : await createClinicalResult(
              accessToken,
              payload,
            )

      setDraftResultId(saved.id)

      setSuccess(
        'Laboratory result saved as draft.',
      )

      setReviewingResult(false)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to save laboratory draft.',
      )
    } finally {
      setSavingResult(false)
    }
  }


  async function finalizeResult() {
    if (!draftResultId) {
      setError(
        'Save the result as a draft before finalizing.',
      )
      return
    }

    setSavingResult(true)
    setError(null)
    setSuccess(null)

    try {
      await finalizeClinicalResult(
        accessToken,
        draftResultId,
      )

      setSuccess(
        'Laboratory result finalized successfully.',
      )

      setDraftResultId(null)
      setReviewingResult(false)

      await loadQueue()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to finalize laboratory result.',
      )
    } finally {
      setSavingResult(false)
    }
  }



  return (
    <section className="workspace-content laboratory-workspace">
      <div className="doctor-workspace">
        <div className="page-header">
          <div>
            <p className="eyebrow">
              CLINICAL WORKSPACE
            </p>

            <h1>
              Laboratory
            </h1>

            <p>
              Review pending laboratory orders,
              process investigations, and manually
              record results.
            </p>
          </div>
        </div>


        {(error || success) && (
          <section className="workspace-panel">
            {error && (
              <p>
                {error}
              </p>
            )}

            {success && (
              <p>
                {success}
              </p>
            )}
          </section>
        )}


        <section className="laboratory-metrics" aria-label="Laboratory queue summary">
          <button type="button" className={queueFilter === 'ALL' ? 'laboratory-metric active' : 'laboratory-metric'} onClick={() => setQueueFilter('ALL')}>
            <strong>{queueCounts.all}</strong><span>Total tests</span>
          </button>
          <button type="button" className={queueFilter === 'REQUESTED' ? 'laboratory-metric active' : 'laboratory-metric'} onClick={() => setQueueFilter('REQUESTED')}>
            <strong>{queueCounts.requested}</strong><span>Awaiting specimen</span>
          </button>
          <button type="button" className={queueFilter === 'RECEIVED' ? 'laboratory-metric active' : 'laboratory-metric'} onClick={() => setQueueFilter('RECEIVED')}>
            <strong>{queueCounts.received}</strong><span>Ready to process</span>
          </button>
          <button type="button" className={queueFilter === 'IN_PROGRESS' ? 'laboratory-metric active' : 'laboratory-metric'} onClick={() => setQueueFilter('IN_PROGRESS')}>
            <strong>{queueCounts.processing}</strong><span>Processing</span>
          </button>
        </section>

        <div className="laboratory-workspace-grid">
          <section className="workspace-panel laboratory-queue-panel">
            <div className="laboratory-queue-toolbar">
              <div>
                <p className="eyebrow">WORK QUEUE</p>
                <h2>Laboratory Queue</h2>
              </div>
              <span>{groupedOrders.length} {groupedOrders.length === 1 ? 'patient' : 'patients'}</span>
            </div>
            <div className="laboratory-queue-search">
              <input value={queueSearch} onChange={event => setQueueSearch(event.target.value)} placeholder="Search patient, MRN or test" aria-label="Search laboratory queue" />
            </div>

            {loading && (
              <p>
                Loading laboratory queue...
              </p>
            )}

            {!loading &&
              orders.length === 0 && (
                <p>
                  No laboratory orders are waiting.
                </p>
              )}

            {!loading &&
              groupedOrders.map(group => (
                <section
                  key={group.key}
                  className="workspace-panel"
                >
                  <div className="panel-header">
                    <div>
                      <h3>
                        {group.patient_name}
                      </h3>

                      <p>
                        {group.hospital_number}
                        {' · '}
                        Episode{' '}
                        {group.episode_number}
                      </p>
                    </div>

                    <span>
                      {group.orders.length}{' '}
                      {group.orders.length === 1
                        ? 'test'
                        : 'tests'}
                    </span>
                  </div>

                  <div>
                    {group.orders.map(order => (
                      <section
                        key={order.id}
                        className="laboratory-order-group"
                      >
                        <div className="laboratory-order-group-header">
                          <strong>
                            Laboratory Order
                          </strong>

                          <span>
                            {order.priority}
                          </span>
                        </div>

                        <div>
                          {order.items
                            .filter(
                              item =>
                                item.item_type ===
                                'LABORATORY',
                            )
                            .map(item => {
                              const test =
                                getLaboratoryTestForItem(
                                  item,
                                  laboratoryTests,
                                )

                              const label =
                                test?.name ??
                                (
                                  typeof item.details.test_name ===
                                  'string'
                                    ? item.details.test_name
                                    : typeof item.details.test_code ===
                                      'string'
                                      ? item.details.test_code
                                      : 'Laboratory Investigation'
                                )

                              return (
                                <button
                                  key={item.id}
                                  type="button"
                                  className={
                                    selectedOrder?.id === order.id &&
                                    selectedOrderItem?.id === item.id
                                      ? 'laboratory-order-item active'
                                      : 'laboratory-order-item'
                                  }
                                  onClick={() =>
                                    selectOrderItem(
                                      order,
                                      item,
                                    )
                                  }
                                >
                                  <span>
                                    {label}
                                  </span>

                                  <small>
                                    {getLaboratoryStatusLabel(
                                      item.status as LaboratoryQueueItem['status'],
                                    )}
                                  </small>
                                </button>
                              )
                            })}
                        </div>
                      </section>
                    ))}
                  </div>
                </section>
              ))}
          </section>


          <section className="workspace-panel laboratory-detail-panel">
            {!selectedOrder ? (
              <p>
                Select a laboratory order to begin.
              </p>
            ) : (
              <>
                <div className="laboratory-investigation-header">
                  <div className="laboratory-investigation-title">
                    <p className="eyebrow">
                      LABORATORY INVESTIGATION
                    </p>

                    <h2>
                      {getInvestigationName(
                        selectedOrder,
                      )}
                    </h2>

                    <p className="laboratory-patient-name">
                      {selectedOrder.patient_name}
                    </p>
                  </div>

                  <span className="laboratory-status-badge">
                    {selectedOrderItem
                      ? getLaboratoryStatusLabel(
                          selectedOrderItem.status as LaboratoryQueueItem['status'],
                        )
                      : 'No investigation selected'}
                  </span>

                  <div className="laboratory-investigation-meta">
                    <span>
                      <strong>MRN</strong>
                      {selectedOrder.hospital_number}
                    </span>

                    <span>
                      <strong>Episode</strong>
                      {selectedOrder.episode_number}
                    </span>

                    <span>
                      <strong>Ordered by</strong>
                      {selectedOrder.ordering_clinician_name}
                    </span>

                    <span>
                      <strong>Priority</strong>
                      {selectedOrder.priority}
                    </span>
                  </div>
                </div>


                {selectedOrderItem?.status ===
                  'REQUESTED' && (
                  <section className="laboratory-workflow-card">
                    <div className="laboratory-workflow-indicator pending">
                      <span />
                    </div>

                    <div className="laboratory-workflow-content">
                      <p className="eyebrow">
                        SPECIMEN WORKFLOW
                      </p>

                      <h3>
                        Awaiting specimen receipt
                      </h3>

                      <p>
                        This investigation is waiting
                        for the specimen to arrive at
                        the laboratory.
                      </p>
                    </div>

                    <button
                      type="button"
                      className="primary-button laboratory-workflow-action"
                      disabled={startingOrder}
                      onClick={() =>
                        void receiveSelectedOrderItem()
                      }
                    >
                      {startingOrder
                        ? 'Receiving...'
                        : 'Receive Specimen'}
                    </button>
                  </section>
                )}


                {selectedOrderItem?.status ===
                  'RECEIVED' && (
                  <section className="laboratory-workflow-card">
                    <div className="laboratory-workflow-indicator received">
                      <span>✓</span>
                    </div>

                    <div className="laboratory-workflow-content">
                      <p className="eyebrow">
                        SPECIMEN WORKFLOW
                      </p>

                      <h3>
                        Specimen received
                      </h3>

                      <p>
                        The investigation has been
                        received and is ready for
                        laboratory processing.
                      </p>
                    </div>

                    <button
                      type="button"
                      className="primary-button laboratory-workflow-action"
                      disabled={startingOrder}
                      onClick={() =>
                        void startSelectedOrderItem()
                      }
                    >
                      {startingOrder
                        ? 'Starting...'
                        : 'Start Processing'}
                    </button>
                  </section>
                )}


                {selectedOrderItem?.status ===
                  'IN_PROGRESS' && (
                  reviewingResult ? (
                    <section className="laboratory-result-form laboratory-result-review">
                      <div className="laboratory-result-heading">
                        <div>
                          <p className="eyebrow">
                            REPORT REVIEW
                          </p>

                          <h3>
                            Review Laboratory Result
                          </h3>

                          <p>
                            Verify the report before finalizing it.
                          </p>
                        </div>

                        <span>
                          DRAFT
                        </span>
                      </div>

                      <div className="laboratory-result-metadata">
                        <div>
                          <strong>Specimen</strong>
                          <span>
                            {specimen || 'Not recorded'}
                          </span>
                        </div>

                        <div>
                          <strong>Collected</strong>
                          <span>
                            {collectedAt
                              ? new Date(
                                  collectedAt,
                                ).toLocaleString()
                              : 'Not recorded'}
                          </span>
                        </div>
                      </div>

                      <div className="laboratory-result-review-table">
                        <div className="laboratory-result-review-header">
                          <span>Analyte</span>
                          <span>Result</span>
                          <span>Unit</span>
                          <span>Reference</span>
                        </div>

                        {selectedLaboratoryTest?.analytes.map(
                          analyte => {
                            const entry =
                              resultValues.find(
                                item =>
                                  item.analyteId ===
                                  analyte.id,
                              )

                            const value =
                              entry?.value.trim() ?? ''

                            if (!value) {
                              return null
                            }

                            const reference =
                              analyte.reference_text ??
                              (
                                analyte.reference_low !== null &&
                                analyte.reference_high !== null
                                  ? `${analyte.reference_low}–${analyte.reference_high}`
                                  : analyte.reference_low !== null
                                    ? `≥ ${analyte.reference_low}`
                                    : analyte.reference_high !== null
                                      ? `≤ ${analyte.reference_high}`
                                      : '—'
                              )

                            return (
                              <div
                                key={analyte.id}
                                className="laboratory-result-review-row"
                              >
                                <span>
                                  {analyte.name}
                                </span>

                                <strong>
                                  {value}
                                </strong>

                                <span>
                                  {analyte.unit ?? '—'}
                                </span>

                                <span>
                                  {reference}
                                </span>
                              </div>
                            )
                          },
                        )}
                      </div>

                      <div className="laboratory-interpretation laboratory-result-review-interpretation">
                        <span>
                          Interpretation / Comment
                        </span>

                        <p>
                          {interpretation.trim() ||
                            'No interpretation recorded.'}
                        </p>
                      </div>

                      <div className="laboratory-result-actions">
                        <button
                          type="button"
                          className="secondary-button"
                          disabled={savingResult}
                          onClick={() =>
                            setReviewingResult(false)
                          }
                        >
                          Back to Edit
                        </button>

                        <button
                          type="button"
                          className="primary-button"
                          disabled={savingResult}
                          onClick={() =>
                            void finalizeResult()
                          }
                        >
                          {savingResult
                            ? 'Finalizing...'
                            : 'Finalize Result'}
                        </button>
                      </div>
                    </section>
                  ) : (
                    <section className="laboratory-result-form">
                      <div className="laboratory-result-heading">
                        <div>
                          <p className="eyebrow">
                            RESULT ENTRY
                          </p>

                          <h3>
                            Enter Laboratory Result
                          </h3>

                          {draftResultId && (
                            <p>
                              Draft result saved. You can continue editing before review.
                            </p>
                          )}
                        </div>

                        {draftResultId && (
                          <span>
                            DRAFT
                          </span>
                        )}
                      </div>

                      <div className="laboratory-result-metadata">
                        <label>
                          <span>
                            Specimen
                          </span>

                          <input
                            type="text"
                            value={specimen}
                            onChange={event =>
                              setSpecimen(
                                event.target.value,
                              )
                            }
                            placeholder={
                              selectedLaboratoryTest?.specimen ??
                              'Enter specimen'
                            }
                          />
                        </label>

                        <label>
                          <span>
                            Collection date / time
                          </span>

                          <input
                            type="datetime-local"
                            value={collectedAt}
                            onChange={event =>
                              setCollectedAt(
                                event.target.value,
                              )
                            }
                          />
                        </label>
                      </div>

                      <div className="laboratory-result-fields">
                        {selectedLaboratoryTest?.analytes.map(
                          analyte => {
                            const entry =
                              resultValues.find(
                                item =>
                                  item.analyteId ===
                                  analyte.id,
                              )

                            const value =
                              entry?.value ?? ''

                            return (
                              <div
                                key={analyte.id}
                                className="laboratory-result-row"
                              >
                                <div className="laboratory-result-label">
                                  <span>
                                    {analyte.name}
                                  </span>

                                  {analyte.reference_text && (
                                    <small>
                                      Ref: {analyte.reference_text}
                                    </small>
                                  )}
                                </div>

                                <div className="laboratory-result-input">
                                  {analyte.data_type ===
                                  'CODED' ? (
                                    <select
                                      value={value}
                                      onChange={event =>
                                        updateResultValue(
                                          analyte.id,
                                          event.target.value,
                                        )
                                      }
                                    >
                                      <option value="">
                                        Select result
                                      </option>

                                      {(
                                        analyte.options ??
                                        []
                                      ).map(
                                        (
                                          option: string,
                                        ) => (
                                          <option
                                            key={option}
                                            value={option}
                                          >
                                            {option}
                                          </option>
                                        ),
                                      )}
                                    </select>
                                  ) : analyte.data_type ===
                                    'BOOLEAN' ? (
                                    <select
                                      value={value}
                                      onChange={event =>
                                        updateResultValue(
                                          analyte.id,
                                          event.target.value,
                                        )
                                      }
                                    >
                                      <option value="">
                                        Select result
                                      </option>

                                      <option value="true">
                                        Yes
                                      </option>

                                      <option value="false">
                                        No
                                      </option>
                                    </select>
                                  ) : (
                                    <input
                                      type={
                                        analyte.data_type ===
                                        'NUMERIC'
                                          ? 'number'
                                          : 'text'
                                      }
                                      inputMode={
                                        analyte.data_type ===
                                        'NUMERIC'
                                          ? 'decimal'
                                          : 'text'
                                      }
                                      value={value}
                                      onChange={event =>
                                        updateResultValue(
                                          analyte.id,
                                          event.target.value,
                                        )
                                      }
                                      placeholder={
                                        analyte.data_type ===
                                        'NUMERIC'
                                          ? 'Enter value'
                                          : 'Enter result'
                                      }
                                    />
                                  )}

                                  {analyte.unit && (
                                    <span>
                                      {analyte.unit}
                                    </span>
                                  )}
                                </div>
                              </div>
                            )
                          },
                        )}
                      </div>

                      <div className="laboratory-interpretation">
                        <label>
                          <span>
                            Interpretation / Comment
                          </span>

                          <textarea
                            value={interpretation}
                            onChange={event =>
                              setInterpretation(
                                event.target.value,
                              )
                            }
                            rows={5}
                            placeholder="Enter laboratory interpretation or comments..."
                          />
                        </label>
                      </div>

                      <div className="laboratory-result-actions">
                        <button
                          type="button"
                          className="secondary-button"
                          disabled={savingResult}
                          onClick={() =>
                            void saveResultDraft()
                          }
                        >
                          {savingResult
                            ? 'Saving...'
                            : 'Save Draft'}
                        </button>

                        <button
                          type="button"
                          className="primary-button"
                          disabled={
                            savingResult ||
                            !draftResultId
                          }
                          onClick={() =>
                            setReviewingResult(true)
                          }
                        >
                          Review Result
                        </button>
                      </div>
                    </section>
                  )
                )}
              </>
            )}
          </section>
        </div>
      </div>
    </section>
  )
}
