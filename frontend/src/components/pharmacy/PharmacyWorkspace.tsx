import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  apiRequest,
} from '../../api/client'


interface PharmacyQueueItem {
  id: string
  encounter_id: string
  patient_id: string
  patient_name: string
  hospital_number: string
  episode_number: string
  ordering_clinician_name: string

  status:
    | 'REQUESTED'
    | 'RECEIVED'
    | 'IN_PROGRESS'

  priority: string

  prescription_id: string | null
  medicine_name: string | null
  strength: string | null
  dose: string | null
  dose_unit: string | null
  route: string | null
  frequency: string | null
  duration: string | null
  duration_unit: string | null
  quantity: string | null
  directions: string | null
  indication: string | null

  ordered_at: string
  started_at: string | null
}


interface Props {
  accessToken: string
}


async function listPharmacyQueue(
  accessToken: string,
): Promise<PharmacyQueueItem[]> {
  return apiRequest<PharmacyQueueItem[]>(
    '/prescriptions/queue',
    {},
    accessToken,
  )
}


async function receivePrescription(
  accessToken: string,
  orderId: string,
): Promise<void> {
  await apiRequest(
    `/prescriptions/${orderId}/receive`,
    {
      method: 'POST',
    },
    accessToken,
  )
}


async function startPrescription(
  accessToken: string,
  orderId: string,
): Promise<void> {
  await apiRequest(
    `/prescriptions/${orderId}/start`,
    {
      method: 'POST',
    },
    accessToken,
  )
}


async function dispensePrescription(
  accessToken: string,
  orderId: string,
  quantityDispensed: string,
  notes: string,
): Promise<void> {
  await apiRequest(
    `/prescriptions/${orderId}/dispense`,
    {
      method: 'POST',
      body: JSON.stringify({
        quantity_dispensed: quantityDispensed,
        notes: notes.trim() || null,
      }),
    },
    accessToken,
  )
}


function getStatusLabel(
  status: PharmacyQueueItem['status'],
): string {
  const labels: Record<
    PharmacyQueueItem['status'],
    string
  > = {
    REQUESTED: 'Awaiting receipt',
    RECEIVED: 'Received',
    IN_PROGRESS: 'Processing',
  }

  return labels[status]
}


function formatDateTime(
  value: string,
): string {
  return new Date(value).toLocaleString(
    [],
    {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    },
  )
}


export default function PharmacyWorkspace({
  accessToken,
}: Props) {
  const [queue, setQueue] =
    useState<PharmacyQueueItem[]>([])

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState<string | null>(null)

  const [selectedId, setSelectedId] =
    useState<string | null>(null)

  const [processingOrderId, setProcessingOrderId] =
    useState<string | null>(null)

  const [dispenseQuantity, setDispenseQuantity] =
    useState('')

  const [dispenseNotes, setDispenseNotes] =
    useState('')

  const [queueFilter, setQueueFilter] =
    useState<'ALL' | PharmacyQueueItem['status']>('ALL')

  const [queueSearch, setQueueSearch] =
    useState('')


  async function loadQueue(
    preferredId?: string | null,
  ) {
    setLoading(true)
    setError(null)

    try {
      const results =
        await listPharmacyQueue(
          accessToken,
        )

      setQueue(results)

      setSelectedId(current => {
        const wanted =
          preferredId ?? current

        if (
          wanted &&
          results.some(item =>
            item.id === wanted,
          )
        ) {
          return wanted
        }

        return results[0]?.id ?? null
      })
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load pharmacy queue.',
      )
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    void loadQueue()
  }, [accessToken])


  const filteredQueue =
    useMemo(() => {
      const query =
        queueSearch.trim().toLowerCase()

      return queue.filter(item => {
        const matchesFilter =
          queueFilter === 'ALL' ||
          item.status === queueFilter

        if (!matchesFilter) {
          return false
        }

        if (!query) {
          return true
        }

        return [
          item.patient_name,
          item.hospital_number,
          item.episode_number,
          item.medicine_name,
          item.strength,
          item.ordering_clinician_name,
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase()
          .includes(query)
      })
    }, [
      queue,
      queueFilter,
      queueSearch,
    ])


  const groupedQueue =
    useMemo(() => {
      const groups = new Map<string, {
        patient_id: string
        patient_name: string
        hospital_number: string
        episode_number: string
        items: PharmacyQueueItem[]
      }>()

      for (const item of filteredQueue) {
        const key = `${item.patient_id}:${item.episode_number}`
        const existing = groups.get(key)

        if (existing) {
          existing.items.push(item)
        } else {
          groups.set(key, {
            patient_id: item.patient_id,
            patient_name: item.patient_name,
            hospital_number: item.hospital_number,
            episode_number: item.episode_number,
            items: [item],
          })
        }
      }

      return Array.from(groups.values())
    }, [filteredQueue])


  const selectedItem =
    queue.find(
      item =>
        item.id === selectedId,
    ) ?? null


  const selectedPatientGroup =
    useMemo(() => {
      if (!selectedItem) {
        return null
      }

      const items = queue.filter(item =>
        item.patient_id === selectedItem.patient_id &&
        item.episode_number === selectedItem.episode_number,
      )

      return {
        items,
        requested: items.filter(item => item.status === 'REQUESTED').length,
        received: items.filter(item => item.status === 'RECEIVED').length,
        processing: items.filter(item => item.status === 'IN_PROGRESS').length,
      }
    }, [queue, selectedItem])


  useEffect(() => {
    if (!selectedItem) {
      setDispenseQuantity('')
      setDispenseNotes('')
      return
    }

    setDispenseQuantity(
      selectedItem.quantity ?? '',
    )
    setDispenseNotes('')
  }, [selectedItem])


  const counts = {
    total: queue.length,
    requested: queue.filter(
      item => item.status === 'REQUESTED',
    ).length,
    received: queue.filter(
      item => item.status === 'RECEIVED',
    ).length,
    processing: queue.filter(
      item => item.status === 'IN_PROGRESS',
    ).length,
  }


  async function handleReceive(
    item: PharmacyQueueItem,
  ) {
    setProcessingOrderId(item.id)
    setError(null)

    try {
      await receivePrescription(
        accessToken,
        item.id,
      )

      await loadQueue(item.id)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to receive prescription.',
      )
    } finally {
      setProcessingOrderId(null)
    }
  }


  async function handleStart(
    item: PharmacyQueueItem,
  ) {
    setProcessingOrderId(item.id)
    setError(null)

    try {
      await startPrescription(
        accessToken,
        item.id,
      )

      await loadQueue(item.id)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to start prescription.',
      )
    } finally {
      setProcessingOrderId(null)
    }
  }


  async function handleDispense() {
    if (!selectedItem) {
      return
    }

    const quantity =
      dispenseQuantity.trim()

    if (!quantity) {
      setError(
        'Enter the quantity dispensed before completing the prescription.',
      )
      return
    }

    setProcessingOrderId(
      selectedItem.id,
    )
    setError(null)

    try {
      await dispensePrescription(
        accessToken,
        selectedItem.id,
        quantity,
        dispenseNotes,
      )

      await loadQueue(null)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to dispense prescription.',
      )
    } finally {
      setProcessingOrderId(null)
    }
  }


  return (
    <section className="workspace-content pharmacy-workspace">

      <header className="pharmacy-command-header">
        <div>
          <p className="eyebrow">PHARMACY</p>
          <h1>Dispensing Workbench</h1>
          <p>
            Review, process and dispense active medication orders.
          </p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={() =>
            void loadQueue(selectedId)
          }
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh queue'}
        </button>
      </header>


      {error && (
        <div className="admin-error pharmacy-message">
          {error}
        </div>
      )}


      <section className="pharmacy-metrics" aria-label="Pharmacy workload">
        <article className="pharmacy-metric pharmacy-metric-primary">
          <strong>{counts.total}</strong>
          <span>Total prescriptions</span>
        </article>

        <article className="pharmacy-metric">
          <strong>{counts.requested}</strong>
          <span>Awaiting receipt</span>
        </article>

        <article className="pharmacy-metric">
          <strong>{counts.received}</strong>
          <span>Received</span>
        </article>

        <article className="pharmacy-metric">
          <strong>{counts.processing}</strong>
          <span>Processing</span>
        </article>
      </section>


      <section className="pharmacy-workbench">

        <aside className="pharmacy-queue-panel">

          <div className="pharmacy-queue-header">
            <div>
              <p className="eyebrow">WORK QUEUE</p>
              <h2>Prescriptions</h2>
            </div>

            <span className="pharmacy-queue-count">
              {groupedQueue.length} patients
            </span>
          </div>


          <div className="pharmacy-queue-tools">

            <input
              value={queueSearch}
              onChange={event =>
                setQueueSearch(
                  event.target.value,
                )
              }
              placeholder="Search patient, MRN or medicine"
              aria-label="Search pharmacy queue"
            />

            <div className="pharmacy-filter-row">
              {([
                ['ALL', 'All'],
                ['REQUESTED', 'Awaiting'],
                ['RECEIVED', 'Received'],
                ['IN_PROGRESS', 'Processing'],
              ] as const).map(
                ([value, label]) => (
                  <button
                    key={value}
                    type="button"
                    className={
                      queueFilter === value
                        ? 'active'
                        : ''
                    }
                    onClick={() =>
                      setQueueFilter(value)
                    }
                  >
                    {label}
                  </button>
                ),
              )}
            </div>

          </div>


          <div className="pharmacy-queue-list">

            {loading && (
              <div className="pharmacy-empty-state">
                Loading pharmacy queue...
              </div>
            )}

            {!loading &&
              filteredQueue.length === 0 && (
                <div className="pharmacy-empty-state">
                  No prescriptions match this queue.
                </div>
              )}

            {!loading &&
              groupedQueue.map(group => (
                <section
                  key={`${group.patient_id}:${group.episode_number}`}
                  className="pharmacy-patient-group"
                >
                  <header
                    className={[
                      'pharmacy-patient-group-header',
                      group.items.some(item => item.id === selectedId)
                        ? 'selected'
                        : '',
                    ]
                      .filter(Boolean)
                      .join(' ')}
                  >
                    <div>
                      <strong>{group.patient_name}</strong>
                      <small>
                        {group.hospital_number}
                        {' · '}
                        {group.episode_number}
                      </small>
                    </div>
                    <div className="pharmacy-patient-group-summary">
                      <span>
                        {group.items.length} {group.items.length === 1 ? 'prescription' : 'prescriptions'}
                      </span>
                      <small>
                        {group.items.filter(item => item.status === 'REQUESTED').length} awaiting
                        {' · '}
                        {group.items.filter(item => item.status === 'RECEIVED').length} received
                        {' · '}
                        {group.items.filter(item => item.status === 'IN_PROGRESS').length} processing
                      </small>
                    </div>
                  </header>

                  <div className="pharmacy-patient-prescriptions">
                    {group.items.map(item => (
                      <button
                        key={item.id}
                        type="button"
                        className={
                          item.id === selectedId
                            ? 'pharmacy-queue-row active'
                            : 'pharmacy-queue-row'
                        }
                        onClick={() =>
                          setSelectedId(item.id)
                        }
                      >
                        <span className="pharmacy-queue-row-main">
                          <strong>
                            {item.medicine_name ??
                              'Medication'}
                            {item.strength ? ` ${item.strength}` : ''}
                          </strong>

                          <small>
                            {item.dose ?? 'Dose not recorded'}
                            {' · '}
                            {item.route ?? 'Route not recorded'}
                            {' · '}
                            {item.frequency ?? 'Frequency not recorded'}
                          </small>
                        </span>

                        <span className="pharmacy-queue-row-side">
                          <span>
                            {item.priority}
                          </span>

                          <em>
                            {getStatusLabel(
                              item.status,
                            )}
                          </em>
                        </span>
                      </button>
                    ))}
                  </div>
                </section>
              ))}

          </div>
        </aside>


        <main className="pharmacy-detail-panel">

          {!selectedItem ? (
            <div className="pharmacy-detail-empty">
              <strong>No prescription selected</strong>
              <span>
                Select an item from the pharmacy queue to begin.
              </span>
            </div>
          ) : (
            <>

              <header className="pharmacy-detail-header pharmacy-detail-header-v8">

                <div className="pharmacy-detail-patient-heading">
                  <p className="eyebrow">
                    PATIENT · PRESCRIPTION
                  </p>

                  <h2>{selectedItem.patient_name}</h2>

                  <p>
                    {selectedItem.hospital_number}
                    {' · '}
                    {selectedItem.episode_number}
                  </p>

                  <div className="pharmacy-selected-medication">
                    <strong>
                      {selectedItem.medicine_name ?? 'Medication'}
                      {selectedItem.strength
                        ? ` ${selectedItem.strength}`
                        : ''}
                    </strong>
                    <span>
                      {selectedItem.dose ?? 'Dose not recorded'}
                      {' · '}
                      {selectedItem.route ?? 'Route not recorded'}
                      {' · '}
                      {selectedItem.frequency ?? 'Frequency not recorded'}
                    </span>
                  </div>
                </div>

                <span className="pharmacy-status-badge">
                  {getStatusLabel(
                    selectedItem.status,
                  )}
                </span>

              </header>


              <section className="pharmacy-patient-context">

                <div>
                  <span>Patient</span>
                  <strong>
                    {selectedItem.patient_name}
                  </strong>
                  <small>
                    {selectedItem.hospital_number}
                    {' · '}
                    {selectedItem.episode_number}
                  </small>
                </div>

                <div>
                  <span>Prescriber</span>
                  <strong>
                    {selectedItem.ordering_clinician_name}
                  </strong>
                </div>

                <div>
                  <span>Ordered</span>
                  <strong>
                    {formatDateTime(
                      selectedItem.ordered_at,
                    )}
                  </strong>
                </div>

                <div>
                  <span>Priority</span>
                  <strong>
                    {selectedItem.priority}
                  </strong>
                </div>

              </section>


              {selectedPatientGroup && (
                <section className="pharmacy-patient-workload">
                  <div className="pharmacy-patient-workload-heading">
                    <div>
                      <p className="eyebrow">
                        PATIENT MEDICATION WORKLOAD
                      </p>
                      <strong>
                        {selectedPatientGroup.items.length}{' '}
                        {selectedPatientGroup.items.length === 1 ? 'prescription' : 'prescriptions'} for this episode
                      </strong>
                    </div>
                    <span>
                      {selectedPatientGroup.requested} awaiting
                      {' · '}
                      {selectedPatientGroup.received} received
                      {' · '}
                      {selectedPatientGroup.processing} processing
                    </span>
                  </div>
                </section>
              )}


              <section className="pharmacy-prescription-card">

                <div className="pharmacy-section-heading">
                  <div>
                    <p className="eyebrow">
                      DIRECTIONS
                    </p>
                    <h3>Prescription details</h3>
                  </div>
                </div>

                <div className="pharmacy-prescription-grid">

                  <div>
                    <span>Dose</span>
                    <strong>
                      {selectedItem.dose ??
                        'Not recorded'}
                      {selectedItem.dose_unit
                        ? ` ${selectedItem.dose_unit}`
                        : ''}
                    </strong>
                  </div>

                  <div>
                    <span>Route</span>
                    <strong>
                      {selectedItem.route ??
                        'Not recorded'}
                    </strong>
                  </div>

                  <div>
                    <span>Frequency</span>
                    <strong>
                      {selectedItem.frequency ??
                        'Not recorded'}
                    </strong>
                  </div>

                  <div>
                    <span>Duration</span>
                    <strong>
                      {selectedItem.duration
                        ? `${selectedItem.duration} ${
                            selectedItem.duration_unit ?? ''
                          }`
                        : 'Not recorded'}
                    </strong>
                  </div>

                  <div>
                    <span>Prescribed quantity</span>
                    <strong>
                      {selectedItem.quantity ??
                        'Not recorded'}
                    </strong>
                  </div>

                  <div>
                    <span>Indication</span>
                    <strong>
                      {selectedItem.indication ??
                        'Not recorded'}
                    </strong>
                  </div>

                </div>

                {selectedItem.directions && (
                  <div className="pharmacy-directions">
                    <span>Administration directions</span>
                    <p>
                      {selectedItem.directions}
                    </p>
                  </div>
                )}

              </section>


              <section className="pharmacy-lifecycle">

                <div className="pharmacy-section-heading">
                  <div>
                    <p className="eyebrow">
                      WORKFLOW
                    </p>
                    <h3>Prescription lifecycle</h3>
                  </div>
                </div>

                <div className="pharmacy-lifecycle-steps">
                  {([
                    ['REQUESTED', 'Ordered'],
                    ['RECEIVED', 'Received'],
                    ['IN_PROGRESS', 'Processing'],
                    ['DONE', 'Dispensed'],
                  ] as const).map(
                    ([step, label], index) => {
                      const order =
                        selectedItem.status === 'REQUESTED'
                          ? 0
                          : selectedItem.status === 'RECEIVED'
                            ? 1
                            : 2

                      const current =
                        step === selectedItem.status

                      const complete =
                        step === 'DONE'
                          ? false
                          : index < order

                      return (
                        <div
                          key={step}
                          className={[
                            'pharmacy-lifecycle-step',
                            current ? 'current' : '',
                            complete ? 'complete' : '',
                          ]
                            .filter(Boolean)
                            .join(' ')}
                        >
                          <span>
                            {index + 1}
                          </span>
                          <strong>{label}</strong>
                        </div>
                      )
                    },
                  )}
                </div>

              </section>


              <section className="pharmacy-action-panel">

                {selectedItem.status === 'REQUESTED' && (
                  <>
                    <div>
                      <p className="eyebrow">
                        NEXT ACTION
                      </p>
                      <h3>Receive prescription</h3>
                      <p>
                        Confirm that the prescription has reached pharmacy
                        before processing it.
                      </p>
                    </div>

                    <button
                      type="button"
                      className="primary-button pharmacy-primary-action"
                      disabled={
                        processingOrderId ===
                        selectedItem.id
                      }
                      onClick={() =>
                        void handleReceive(
                          selectedItem,
                        )
                      }
                    >
                      {processingOrderId ===
                      selectedItem.id
                        ? 'Receiving...'
                        : 'Receive Prescription'}
                    </button>
                  </>
                )}


                {selectedItem.status === 'RECEIVED' && (
                  <>
                    <div>
                      <p className="eyebrow">
                        NEXT ACTION
                      </p>
                      <h3>Start processing</h3>
                      <p>
                        Begin dispensing preparation for this prescription.
                      </p>
                    </div>

                    <button
                      type="button"
                      className="primary-button pharmacy-primary-action"
                      disabled={
                        processingOrderId ===
                        selectedItem.id
                      }
                      onClick={() =>
                        void handleStart(
                          selectedItem,
                        )
                      }
                    >
                      {processingOrderId ===
                      selectedItem.id
                        ? 'Starting...'
                        : 'Start Processing'}
                    </button>
                  </>
                )}


                {selectedItem.status === 'IN_PROGRESS' && (
                  <div className="pharmacy-dispense-area">

                    <div>
                      <p className="eyebrow">
                        DISPENSING
                      </p>
                      <h3>Complete dispensing</h3>
                      <p>
                        Record the quantity actually supplied to the patient.
                      </p>
                    </div>

                    <div className="pharmacy-dispense-fields">

                      <label>
                        <span>Quantity dispensed</span>
                        <input
                          value={dispenseQuantity}
                          onChange={event =>
                            setDispenseQuantity(
                              event.target.value,
                            )
                          }
                          placeholder="Enter quantity"
                        />
                      </label>

                      <label>
                        <span>Dispensing notes</span>
                        <textarea
                          value={dispenseNotes}
                          onChange={event =>
                            setDispenseNotes(
                              event.target.value,
                            )
                          }
                          placeholder="Optional notes"
                          rows={3}
                        />
                      </label>

                    </div>

                    <button
                      type="button"
                      className="primary-button pharmacy-primary-action"
                      disabled={
                        processingOrderId ===
                        selectedItem.id
                      }
                      onClick={() =>
                        void handleDispense()
                      }
                    >
                      {processingOrderId ===
                      selectedItem.id
                        ? 'Dispensing...'
                        : 'Dispense Medication'}
                    </button>

                  </div>
                )}

              </section>

            </>
          )}

        </main>

      </section>

    </section>
  )
}
