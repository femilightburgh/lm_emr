import {
  useState,
} from 'react'

import type {
  ClinicalOrder,
  ClinicalOrderType,
} from '../../api/clinicalOrders'

import type {
  LaboratoryTest,
} from '../../api/laboratory'

import type {
  ClinicalResult,
} from '../../api/clinicalResults'


interface Props {
  orders: ClinicalOrder[]
  clinicalResults: ClinicalResult[]
  loading: boolean
  saving: boolean
  cancellingOrderId: string | null
  encounterClosed: boolean

  orderType: ClinicalOrderType
  orderPriority: string

  laboratoryTests: LaboratoryTest[]
  selectedLaboratoryTestId: string

  orderTestCode: string
  orderTestName: string
  orderStudyCode: string
  orderMedicationId: string
  orderDose: string

  prescriptionMedicine: string
  prescriptionStrength: string
  prescriptionDoseUnit: string
  prescriptionRoute: string
  prescriptionFrequency: string
  prescriptionDuration: string
  prescriptionDurationUnit: string
  prescriptionQuantity: string
  prescriptionDirections: string
  prescriptionIndication: string

  onOrderTypeChange: (
    value: ClinicalOrderType,
  ) => void

  onOrderPriorityChange: (
    value: string,
  ) => void

  onLaboratoryTestChange: (
    value: string,
  ) => void


  onOrderTestCodeChange?: (
    value: string,
  ) => void

  onOrderTestNameChange?: (
    value: string,
  ) => void

  onOrderStudyCodeChange: (
    value: string,
  ) => void

  onOrderMedicationIdChange: (
    value: string,
  ) => void

  onOrderDoseChange: (
    value: string,
  ) => void

  onPrescriptionMedicineChange: (
    value: string,
  ) => void

  onPrescriptionStrengthChange: (
    value: string,
  ) => void

  onPrescriptionDoseUnitChange: (
    value: string,
  ) => void

  onPrescriptionRouteChange: (
    value: string,
  ) => void

  onPrescriptionFrequencyChange: (
    value: string,
  ) => void

  onPrescriptionDurationChange: (
    value: string,
  ) => void

  onPrescriptionDurationUnitChange: (
    value: string,
  ) => void

  onPrescriptionQuantityChange: (
    value: string,
  ) => void

  onPrescriptionDirectionsChange: (
    value: string,
  ) => void

  onPrescriptionIndicationChange: (
    value: string,
  ) => void

  onSave: () => void
  onCancel: (
    orderId: string,
  ) => void
}


function getOrderLabel(
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

  if (order.order_type === 'RADIOLOGY') {
    const studyCode =
      order.details.study_code

    return typeof studyCode === 'string' &&
      studyCode.trim()
      ? studyCode
      : 'Radiology investigation'
  }

  const medicationId =
    order.details.medication_id

  return typeof medicationId === 'string' &&
    medicationId.trim()
    ? medicationId
    : 'Medication'
}


function getOrderDetail(
  order: ClinicalOrder,
): string {
  if (order.order_type === 'LABORATORY') {
    const code = order.details.test_code

    return typeof code === 'string' &&
      code.trim()
      ? code
      : 'Laboratory'
  }

  if (order.order_type === 'RADIOLOGY') {
    return 'Radiology'
  }

  const dose = order.details.dose

  return typeof dose === 'string' &&
    dose.trim()
    ? dose
    : 'Medication'
}


function getOrderStatusLabel(
  status: ClinicalOrder['status'],
): string {
  const labels: Record<
    ClinicalOrder['status'],
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


function getOrderTypeLabel(
  type: ClinicalOrderType,
): string {
  if (type === 'LABORATORY') {
    return 'Laboratory'
  }

  if (type === 'RADIOLOGY') {
    return 'Radiology'
  }

  return 'Medication'
}


export default function ClinicalOrdersPanel({
  orders,
  clinicalResults,
  loading,
  saving,
  cancellingOrderId,
  encounterClosed,

  orderType,
  orderPriority,

  laboratoryTests,
  selectedLaboratoryTestId,

  orderTestCode,
  orderTestName,
  orderStudyCode,
  orderDose,

  prescriptionMedicine,
  prescriptionStrength,
  prescriptionDoseUnit,
  prescriptionRoute,
  prescriptionFrequency,
  prescriptionDuration,
  prescriptionDurationUnit,
  prescriptionQuantity,
  prescriptionDirections,
  prescriptionIndication,

  onOrderTypeChange,
  onOrderPriorityChange,
  onLaboratoryTestChange,
  onOrderStudyCodeChange,
  onOrderDoseChange,

  onPrescriptionMedicineChange,
  onPrescriptionStrengthChange,
  onPrescriptionDoseUnitChange,
  onPrescriptionRouteChange,
  onPrescriptionFrequencyChange,
  onPrescriptionDurationChange,
  onPrescriptionDurationUnitChange,
  onPrescriptionQuantityChange,
  onPrescriptionDirectionsChange,
  onPrescriptionIndicationChange,

  onSave,
  onCancel,
}: Props) {
  const [expandedResultId, setExpandedResultId] =
    useState<string | null>(null)

  const canSave =
    !encounterClosed &&
    !saving &&
    (
      orderType === 'LABORATORY'
        ? (
            orderTestCode.trim() &&
            orderTestName.trim()
          )
        : orderType === 'RADIOLOGY'
          ? orderStudyCode.trim()
          : (
              prescriptionMedicine.trim() &&
              orderDose.trim() &&
              prescriptionRoute.trim() &&
              prescriptionFrequency.trim()
            )
    )

  return (
    <section className="workspace-panel doctor-orders-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">
            CLINICAL ORDERS
          </p>

          <h2>
            Orders
          </h2>

          <p>
            Request investigations, imaging, or medication
            for this encounter.
          </p>
        </div>

        <span>
          {orders.length}{' '}
          {orders.length === 1
            ? 'order'
            : 'orders'}
        </span>
      </div>

      <details className="doctor-order-entry">
        <summary className="doctor-order-entry-summary">
          <div>
            <p className="eyebrow">
              NEW ORDER
            </p>

            <strong>
              Create clinical order
            </strong>

            <small>
              Investigation, imaging, or medication
            </small>
          </div>

          <span>
            Open
          </span>
        </summary>

        <div className="doctor-order-entry-body">
          <div className="doctor-order-row">
          <label>
            <span>
              Order type
            </span>

            <select
              disabled={encounterClosed}
              value={orderType}
              onChange={event =>
                onOrderTypeChange(
                  event.target.value as ClinicalOrderType,
                )
              }
            >
              <option value="LABORATORY">
                Laboratory
              </option>

              <option value="RADIOLOGY">
                Radiology
              </option>

              <option value="MEDICATION">
                Medication
              </option>
            </select>
          </label>

          <label>
            <span>
              Priority
            </span>

            <select
              disabled={encounterClosed}
              value={orderPriority}
              onChange={event =>
                onOrderPriorityChange(
                  event.target.value,
                )
              }
            >
              <option value="ROUTINE">
                Routine
              </option>

              <option value="URGENT">
                Urgent
              </option>

              <option value="STAT">
                STAT
              </option>
            </select>
          </label>
        </div>

        {orderType === 'LABORATORY' && (
          <div className="doctor-laboratory-order">
            <label>
              <span>
                Laboratory investigation
              </span>

              <select
                disabled={
                  encounterClosed
                }
                value={
                  selectedLaboratoryTestId
                }
                onChange={event =>
                  onLaboratoryTestChange(
                    event.target.value,
                  )
                }
              >
                <option value="">
                  Select laboratory investigation
                </option>

                {laboratoryTests.map(test => (
                  <option
                    key={test.id}
                    value={test.id}
                  >
                    {test.code}
                    {' — '}
                    {test.name}
                  </option>
                ))}
              </select>
            </label>

            {selectedLaboratoryTestId && (
              <div className="doctor-selected-order-preview">
                <span>
                  Selected investigation
                </span>

                <strong>
                  {orderTestName}
                </strong>

                <small>
                  {orderTestCode}
                </small>
              </div>
            )}

          </div>
        )}

        {orderType === 'RADIOLOGY' && (
          <div className="doctor-order-specific-fields">
            <label>
              <span>
                Study code
              </span>

              <input
                disabled={encounterClosed}
                value={orderStudyCode}
                onChange={event =>
                  onOrderStudyCodeChange(
                    event.target.value,
                  )
                }
                placeholder="e.g. CXR"
              />
            </label>
          </div>
        )}

        {orderType === 'MEDICATION' && (
          <div className="doctor-order-specific-fields">
            <div className="doctor-order-row">
              <label>
                <span>
                  Medicine
                </span>

                <input
                  disabled={encounterClosed}
                  value={prescriptionMedicine}
                  onChange={event =>
                    onPrescriptionMedicineChange(
                      event.target.value,
                    )
                  }
                  placeholder="e.g. Amoxicillin"
                />
              </label>

              <label>
                <span>
                  Strength
                </span>

                <input
                  disabled={encounterClosed}
                  value={prescriptionStrength}
                  onChange={event =>
                    onPrescriptionStrengthChange(
                      event.target.value,
                    )
                  }
                  placeholder="e.g. 500 mg"
                />
              </label>
            </div>

            <div className="doctor-order-row">
              <label>
                <span>
                  Dose
                </span>

                <input
                  disabled={encounterClosed}
                  value={orderDose}
                  onChange={event =>
                    onOrderDoseChange(
                      event.target.value,
                    )
                  }
                  placeholder="e.g. 500"
                />
              </label>

              <label>
                <span>
                  Dose unit
                </span>

                <input
                  disabled={encounterClosed}
                  value={prescriptionDoseUnit}
                  onChange={event =>
                    onPrescriptionDoseUnitChange(
                      event.target.value,
                    )
                  }
                  placeholder="e.g. mg"
                />
              </label>
            </div>

            <div className="doctor-order-row">
              <label>
                <span>
                  Route
                </span>

                <select
                  disabled={encounterClosed}
                  value={prescriptionRoute}
                  onChange={event =>
                    onPrescriptionRouteChange(
                      event.target.value,
                    )
                  }
                >
                  <option value="">
                    Select route
                  </option>
                  <option value="ORAL">
                    Oral
                  </option>
                  <option value="IV">
                    Intravenous
                  </option>
                  <option value="IM">
                    Intramuscular
                  </option>
                  <option value="SC">
                    Subcutaneous
                  </option>
                  <option value="TOPICAL">
                    Topical
                  </option>
                  <option value="INHALED">
                    Inhaled
                  </option>
                  <option value="RECTAL">
                    Rectal
                  </option>
                  <option value="OTHER">
                    Other
                  </option>
                </select>
              </label>

              <label>
                <span>
                  Frequency
                </span>

                <input
                  disabled={encounterClosed}
                  value={prescriptionFrequency}
                  onChange={event =>
                    onPrescriptionFrequencyChange(
                      event.target.value,
                    )
                  }
                  placeholder="e.g. TDS"
                />
              </label>
            </div>

            <div className="doctor-order-row">
              <label>
                <span>
                  Duration
                </span>

                <input
                  disabled={encounterClosed}
                  value={prescriptionDuration}
                  onChange={event =>
                    onPrescriptionDurationChange(
                      event.target.value,
                    )
                  }
                  placeholder="e.g. 5"
                />
              </label>

              <label>
                <span>
                  Duration unit
                </span>

                <select
                  disabled={encounterClosed}
                  value={prescriptionDurationUnit}
                  onChange={event =>
                    onPrescriptionDurationUnitChange(
                      event.target.value,
                    )
                  }
                >
                  <option value="">
                    Select unit
                  </option>
                  <option value="days">
                    Days
                  </option>
                  <option value="weeks">
                    Weeks
                  </option>
                  <option value="months">
                    Months
                  </option>
                  <option value="doses">
                    Doses
                  </option>
                </select>
              </label>
            </div>

            <div className="doctor-order-row">
              <label>
                <span>
                  Quantity
                </span>

                <input
                  disabled={encounterClosed}
                  value={prescriptionQuantity}
                  onChange={event =>
                    onPrescriptionQuantityChange(
                      event.target.value,
                    )
                  }
                  placeholder="e.g. 15 capsules"
                />
              </label>
            </div>

            <div className="doctor-order-row">
              <label>
                <span>
                  Directions
                </span>

                <textarea
                  disabled={encounterClosed}
                  value={prescriptionDirections}
                  onChange={event =>
                    onPrescriptionDirectionsChange(
                      event.target.value,
                    )
                  }
                  placeholder="Instructions for the patient"
                  rows={3}
                />
              </label>

              <label>
                <span>
                  Indication
                </span>

                <textarea
                  disabled={encounterClosed}
                  value={prescriptionIndication}
                  onChange={event =>
                    onPrescriptionIndicationChange(
                      event.target.value,
                    )
                  }
                  placeholder="Reason for prescribing"
                  rows={3}
                />
              </label>
            </div>
          </div>
        )}

          <div className="doctor-order-actions">
            <button
            type="button"
            className="primary-button"
            disabled={!canSave}
            onClick={onSave}
          >
            {encounterClosed
              ? 'Encounter Closed'
              : saving
                ? orderType === 'MEDICATION'
                  ? 'Creating Prescription...'
                  : 'Creating...'
                : orderType === 'MEDICATION'
                  ? 'Create Prescription'
                  : 'Create Order'}
            </button>
          </div>
        </div>
      </details>

      <div className="doctor-encounter-orders">
        <div className="doctor-encounter-orders-header">
          <div>
            <p className="eyebrow">
              RECORDED
            </p>

            <h3>
              Encounter Orders
            </h3>
          </div>
        </div>

        {loading && (
          <p className="doctor-orders-empty">
            Loading orders...
          </p>
        )}

        {!loading &&
          orders.length === 0 && (
          <p className="doctor-orders-empty">
            No clinical orders recorded for this encounter.
          </p>
        )}

        {!loading &&
          orders.map(order => {
            const result =
              clinicalResults.find(
                clinicalResult =>
                  clinicalResult.order_id ===
                  order.id,
              )

            const canViewResult =
              order.order_type === 'LABORATORY' &&
              order.status === 'COMPLETED' &&
              result?.status === 'FINAL'

            const expanded =
              canViewResult &&
              expandedResultId === result?.id

            return (
            <div
              key={order.id}
              className="doctor-recorded-order"
            >
              <div
                className={
                  canViewResult
                    ? 'doctor-recorded-order-main clickable'
                    : 'doctor-recorded-order-main'
                }
                role={
                  canViewResult
                    ? 'button'
                    : undefined
                }
                tabIndex={
                  canViewResult
                    ? 0
                    : undefined
                }
                onClick={() => {
                  if (!canViewResult) {
                    return
                  }

                  setExpandedResultId(
                    expanded
                      ? null
                      : result.id,
                  )
                }}
                onKeyDown={event => {
                  if (
                    !canViewResult ||
                    (
                      event.key !== 'Enter' &&
                      event.key !== ' '
                    )
                  ) {
                    return
                  }

                  event.preventDefault()

                  setExpandedResultId(
                    expanded
                      ? null
                      : result.id,
                  )
                }}
              >
                <strong>
                  {getOrderLabel(order)}
                </strong>

                <span>
                  {getOrderDetail(order)}
                  {' · '}
                  {getOrderTypeLabel(
                    order.order_type,
                  )}
                </span>
              </div>

              <div className="doctor-recorded-order-meta">
                <span>
                  {getOrderStatusLabel(
                    order.status,
                  )}
                </span>

                <span>
                  {order.priority}
                </span>
              </div>

              {canViewResult && (
                <button
                  type="button"
                  className="doctor-order-result-toggle"
                  onClick={() =>
                    setExpandedResultId(
                      expanded
                        ? null
                        : result.id,
                    )
                  }
                >
                  {expanded
                    ? 'Hide Result'
                    : 'View Result'}
                </button>
              )}

              {order.status !== 'COMPLETED' &&
                order.status !== 'CANCELLED' && (
                <button
                  type="button"
                  className="doctor-order-cancel"
                  disabled={
                    cancellingOrderId ===
                    order.id
                  }
                  onClick={() =>
                    onCancel(order.id)
                  }
                >
                  {cancellingOrderId ===
                    order.id
                    ? 'Cancelling...'
                    : 'Cancel'}
                </button>
              )}

              {expanded && result && (
                <div className="doctor-order-result">
                  <div className="doctor-order-result-meta">
                    <div>
                      <span>Specimen</span>
                      <strong>
                        {result.specimen ??
                          'Not recorded'}
                      </strong>
                    </div>

                    <div>
                      <span>Collected</span>
                      <strong>
                        {result.collected_at
                          ? new Date(
                              result.collected_at,
                            ).toLocaleString()
                          : 'Not recorded'}
                      </strong>
                    </div>

                    <div>
                      <span>Reported</span>
                      <strong>
                        {result.reported_at
                          ? new Date(
                              result.reported_at,
                            ).toLocaleString()
                          : 'Not recorded'}
                      </strong>
                    </div>
                  </div>

                  <div className="doctor-order-result-table">
                    <div className="doctor-order-result-table-header">
                      <span>Analyte</span>
                      <span>Result</span>
                      <span>Unit</span>
                      <span>Reference</span>
                      <span>Flag</span>
                    </div>

                    {result.values.map(
                      value => (
                        <div
                          key={value.id}
                          className="doctor-order-result-table-row"
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
                            {String(
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
                    )}
                  </div>

                  <div className="doctor-order-result-interpretation">
                    <span>
                      Interpretation
                    </span>

                    <p>
                      {result.interpretation ??
                        'No interpretation recorded.'}
                    </p>
                  </div>
                </div>
              )}
            </div>
            )
          })}
      </div>
    </section>
  )
}
