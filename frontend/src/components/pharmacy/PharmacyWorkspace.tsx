import {
  useEffect,
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


export default function PharmacyWorkspace({
  accessToken,
}: Props) {
  const [queue, setQueue] =
    useState<PharmacyQueueItem[]>([])

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState<string | null>(null)

  const [processingOrderId, setProcessingOrderId] =
    useState<string | null>(null)

  const [dispenseQuantity, setDispenseQuantity] =
    useState<Record<string, string>>({})

  const [dispenseNotes, setDispenseNotes] =
    useState<Record<string, string>>({})


  async function loadQueue() {
    setLoading(true)
    setError(null)

    try {
      const results =
        await listPharmacyQueue(
          accessToken,
        )

      setQueue(results)
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


  async function handleReceive(
    orderId: string,
  ) {
    setProcessingOrderId(orderId)
    setError(null)

    try {
      await receivePrescription(
        accessToken,
        orderId,
      )

      await loadQueue()
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
    orderId: string,
  ) {
    setProcessingOrderId(orderId)
    setError(null)

    try {
      await startPrescription(
        accessToken,
        orderId,
      )

      await loadQueue()
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


  async function handleDispense(
    item: PharmacyQueueItem,
  ) {
    const quantity =
      dispenseQuantity[item.id]?.trim() ?? ''

    if (!quantity) {
      setError(
        'Enter the quantity dispensed before completing the prescription.',
      )
      return
    }

    setProcessingOrderId(item.id)
    setError(null)

    try {
      await dispensePrescription(
        accessToken,
        item.id,
        quantity,
        dispenseNotes[item.id] ?? '',
      )

      setDispenseQuantity(current => {
        const next = { ...current }
        delete next[item.id]
        return next
      })

      setDispenseNotes(current => {
        const next = { ...current }
        delete next[item.id]
        return next
      })

      await loadQueue()
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
    <section className="workspace-content">
      <div className="workspace-header">
        <div>
          <p className="eyebrow">
            PHARMACY
          </p>

          <h1>
            Pharmacy Workspace
          </h1>

          <p>
            Review prescriptions awaiting
            pharmacy attention.
          </p>
        </div>
      </div>

      {error && (
        <div className="workspace-panel">
          <p>{error}</p>

          <button
            type="button"
            className="primary-button"
            onClick={() =>
              void loadQueue()
            }
          >
            Retry
          </button>
        </div>
      )}

      {!error && (
        <section className="workspace-panel pharmacy-queue-panel">
          <div className="panel-header">
            <div>
              <h2>
                Prescription Queue
              </h2>

              <p>
                {queue.length}{' '}
                prescription
                {queue.length === 1
                  ? ''
                  : 's'} awaiting attention.
              </p>
            </div>

            <button
              type="button"
              className="secondary-button"
              onClick={() =>
                void loadQueue()
              }
              disabled={loading}
            >
              Refresh
            </button>
          </div>

          {loading ? (
            <p>
              Loading pharmacy queue...
            </p>
          ) : queue.length === 0 ? (
            <p>
              No prescriptions are currently
              awaiting pharmacy attention.
            </p>
          ) : (
            <div className="pharmacy-queue-list">
              {queue.map(item => (
                <article
                  key={item.id}
                  className="pharmacy-queue-card"
                >
                  <div className="pharmacy-queue-card-header">
                    <div className="pharmacy-queue-card-title">
                      <strong>
                        {item.medicine_name ??
                          'Medication'}
                      </strong>

                      <span>
                        {item.strength ?? 'Strength not recorded'}
                      </span>
                    </div>

                    <div className="pharmacy-queue-meta">
                      <span className="pharmacy-queue-pill">
                        {getStatusLabel(item.status)}
                      </span>

                      <span className="pharmacy-queue-pill">
                        {item.priority}
                      </span>
                    </div>
                  </div>

                  <div className="pharmacy-queue-section">
                    <h3>
                      Prescription
                    </h3>

                    <div className="pharmacy-queue-grid">
                      <div className="pharmacy-queue-field">
                        <span>Dose</span>
                        <strong>
                          {item.dose ?? 'Not recorded'}
                          {item.dose_unit
                            ? ` ${item.dose_unit}`
                            : ''}
                        </strong>
                      </div>

                      <div className="pharmacy-queue-field">
                        <span>Route</span>
                        <strong>
                          {item.route ?? 'Not recorded'}
                        </strong>
                      </div>

                      <div className="pharmacy-queue-field">
                        <span>Frequency</span>
                        <strong>
                          {item.frequency ?? 'Not recorded'}
                        </strong>
                      </div>

                      <div className="pharmacy-queue-field">
                        <span>Duration</span>
                        <strong>
                          {item.duration
                            ? `${item.duration} ${
                                item.duration_unit ?? ''
                              }`
                            : 'Not recorded'}
                        </strong>
                      </div>
                    </div>
                  </div>

                  <div className="pharmacy-queue-section">
                    <h3>
                      Patient & Prescriber
                    </h3>

                    <div className="pharmacy-queue-grid">
                      <div className="pharmacy-queue-field">
                        <span>Patient</span>
                        <strong>
                          {item.patient_name}
                        </strong>
                      </div>

                      <div className="pharmacy-queue-field">
                        <span>Hospital Number</span>
                        <strong>
                          {item.hospital_number}
                        </strong>
                      </div>

                      <div className="pharmacy-queue-field">
                        <span>Episode</span>
                        <strong>
                          {item.episode_number}
                        </strong>
                      </div>

                      <div className="pharmacy-queue-field">
                        <span>Prescriber</span>
                        <strong>
                          {item.ordering_clinician_name}
                        </strong>
                      </div>
                    </div>
                  </div>

                  <div className="pharmacy-queue-actions">
                    {item.status === 'REQUESTED' && (
                      <button
                        type="button"
                        className="primary-button"
                        disabled={
                          processingOrderId === item.id
                        }
                        onClick={() =>
                          void handleReceive(item.id)
                        }
                      >
                        {processingOrderId === item.id
                          ? 'Receiving...'
                          : 'Receive Prescription'}
                      </button>
                    )}

                    {item.status === 'RECEIVED' && (
                      <button
                        type="button"
                        className="primary-button"
                        disabled={
                          processingOrderId === item.id
                        }
                        onClick={() =>
                          void handleStart(item.id)
                        }
                      >
                        {processingOrderId === item.id
                          ? 'Starting...'
                          : 'Start Processing'}
                      </button>
                    )}

                    {item.status === 'IN_PROGRESS' && (
                      <div className="pharmacy-dispense-form">
                        <label>
                          <span>
                            Quantity dispensed
                          </span>

                          <input
                            value={
                              dispenseQuantity[item.id] ??
                              ''
                            }
                            disabled={
                              processingOrderId === item.id
                            }
                            onChange={event =>
                              setDispenseQuantity(
                                current => ({
                                  ...current,
                                  [item.id]:
                                    event.target.value,
                                }),
                              )
                            }
                            placeholder={
                              item.quantity ??
                              'e.g. 15 tablets'
                            }
                          />
                        </label>

                        <label>
                          <span>
                            Notes
                          </span>

                          <textarea
                            value={
                              dispenseNotes[item.id] ??
                              ''
                            }
                            disabled={
                              processingOrderId === item.id
                            }
                            onChange={event =>
                              setDispenseNotes(
                                current => ({
                                  ...current,
                                  [item.id]:
                                    event.target.value,
                                }),
                              )
                            }
                            placeholder="Optional dispensing note"
                            rows={2}
                          />
                        </label>

                        <button
                          type="button"
                          className="primary-button"
                          disabled={
                            processingOrderId === item.id ||
                            !(
                              dispenseQuantity[item.id] ??
                              ''
                            ).trim()
                          }
                          onClick={() =>
                            void handleDispense(item)
                          }
                        >
                          {processingOrderId === item.id
                            ? 'Dispensing...'
                            : 'Dispense Medication'}
                        </button>
                      </div>
                    )}
                  </div>

                  {(item.quantity ||
                    item.directions ||
                    item.indication) && (
                    <div className="pharmacy-queue-section">
                      <h3>
                        Instructions
                      </h3>

                      {item.quantity && (
                        <p className="pharmacy-queue-text">
                          <strong>Quantity:</strong>{' '}
                          {item.quantity}
                        </p>
                      )}

                      {item.directions && (
                        <p className="pharmacy-queue-text">
                          <strong>Directions:</strong>{' '}
                          {item.directions}
                        </p>
                      )}

                      {item.indication && (
                        <p className="pharmacy-queue-text">
                          <strong>Indication:</strong>{' '}
                          {item.indication}
                        </p>
                      )}
                    </div>
                  )}
                </article>
              ))}
            </div>
          )}
        </section>
      )}
    </section>
  )
}
