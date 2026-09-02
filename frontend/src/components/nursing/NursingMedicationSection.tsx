import {
  useState,
} from 'react'

import {
  getMedicationTreatmentHistory,
  type MedicationAdministrationStatus,
  type MedicationNursingDose,
  type MedicationNursingRound,
  type MedicationNursingSummary,
  type MedicationTreatmentHistory,
} from '../../api/medicationDoses'


interface Props {
  accessToken: string
  summary: MedicationNursingSummary | null
  loading: boolean
  savingDoseId: string | null

  onAdminister: (
    doseId: string,
    status: MedicationAdministrationStatus,
    reason?: string,
  ) => void
}


function formatDateTime(
  value: string,
): string {
  return new Date(
    value,
  ).toLocaleString()
}


function formatTime(
  value: string,
): string {
  return new Date(
    value,
  ).toLocaleTimeString(
    [],
    {
      hour: 'numeric',
      minute: '2-digit',
    },
  )
}


function getMedicationDisplay(
  dose: MedicationNursingDose,
): string {
  const parts = [
    dose.dose,
    dose.dose_unit,
    dose.route,
  ].filter(Boolean)

  return parts.join(' · ')
}


function getStatusLabel(
  dose: MedicationNursingDose,
): string {
  return dose.administration_status
    ?? dose.scheduled_state
}


function isActionable(
  dose: MedicationNursingDose,
): boolean {
  return (
    dose.administration_status === null
    && (
      dose.scheduled_state === 'DUE'
      || dose.scheduled_state === 'OVERDUE'
    )
  )
}


interface DoseListProps {
  doses: MedicationNursingDose[]
  savingDoseId: string | null
  onAdminister: Props['onAdminister']
  showActions: boolean
}


function DoseList({
  doses,
  savingDoseId,
  onAdminister,
  showActions,
}: DoseListProps) {
  const [
    selectedDoseId,
    setSelectedDoseId,
  ] = useState<string | null>(null)

  const [
    reason,
    setReason,
  ] = useState('')


  function openAction(
    doseId: string,
  ) {
    setSelectedDoseId(
      doseId,
    )
    setReason('')
  }


  function closeAction() {
    setSelectedDoseId(null)
    setReason('')
  }


  function submit(
    status: MedicationAdministrationStatus,
  ) {
    if (!selectedDoseId) {
      return
    }

    onAdminister(
      selectedDoseId,
      status,
      reason.trim() || undefined,
    )

    closeAction()
  }


  return (
    <>
      {doses.map(
        dose => {
          const actionable =
            showActions &&
            isActionable(dose)

          const saving =
            savingDoseId === dose.id

          return (
            <article
              key={dose.id}
              className="nursing-medication-item"
            >
              <div>
                <p className="eyebrow">
                  {formatDateTime(
                    dose.scheduled_at,
                  )}
                </p>

                <strong>
                  {dose.medicine_name}
                </strong>

                <p>
                  {getMedicationDisplay(
                    dose,
                  )}
                </p>

                <p>
                  {dose.frequency}
                  {dose.strength
                    ? ` · ${dose.strength}`
                    : ''}
                </p>

                {dose.administration_at && (
                  <p>
                    Recorded:{' '}
                    {formatDateTime(
                      dose.administration_at,
                    )}
                  </p>
                )}

                {dose.reason && (
                  <p>
                    Reason: {dose.reason}
                  </p>
                )}
              </div>

              <div>
                <span className="nursing-queue-status">
                  {getStatusLabel(dose)}
                </span>

                {actionable && (
                  <div
                    style={{
                      display: 'flex',
                      gap: '0.5rem',
                      flexWrap: 'wrap',
                      marginTop: '0.75rem',
                    }}
                  >
                    <button
                      type="button"
                      className="primary-button"
                      disabled={saving}
                      onClick={() =>
                        openAction(
                          dose.id,
                        )
                      }
                    >
                      {saving
                        ? 'Saving...'
                        : 'Record outcome'}
                    </button>
                  </div>
                )}
              </div>
            </article>
          )
        },
      )}

      {selectedDoseId && (
        <div
          className="nursing-medication-action"
          style={{
            marginTop: '1rem',
            padding: '1rem',
            border: '1px solid var(--border-color, #e5e7eb)',
            borderRadius: '0.5rem',
          }}
        >
          <p className="eyebrow">
            MEDICATION OUTCOME
          </p>

          <h4>
            Record nursing outcome
          </h4>

          <label>
            <span>
              Reason / note
            </span>

            <textarea
              value={reason}
              onChange={event =>
                setReason(
                  event.target.value,
                )
              }
              rows={3}
              placeholder="Required for held, missed, or refused doses."
            />
          </label>

          <div
            style={{
              display: 'flex',
              gap: '0.5rem',
              flexWrap: 'wrap',
              marginTop: '0.75rem',
            }}
          >
            <button
              type="button"
              className="primary-button"
              onClick={() =>
                submit('GIVEN')
              }
            >
              Given
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={() =>
                submit('HELD')
              }
            >
              Held
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={() =>
                submit('MISSED')
              }
            >
              Missed
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={() =>
                submit('REFUSED')
              }
            >
              Refused
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={
                closeAction
              }
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </>
  )
}


function RoundBlock({
  title,
  round,
  savingDoseId,
  onAdminister,
  showActions,
}: {
  title: string
  round: MedicationNursingRound | null
  savingDoseId: string | null
  onAdminister: Props['onAdminister']
  showActions: boolean
}) {
  if (!round) {
    return null
  }

  return (
    <section>
      <div className="section-heading">
        <div>
          <p className="eyebrow">
            {title}
          </p>

          <h4>
            {formatTime(
              round.scheduled_at,
            )}
          </h4>
        </div>
      </div>

      <DoseList
        doses={round.doses}
        savingDoseId={savingDoseId}
        onAdminister={onAdminister}
        showActions={showActions}
      />
    </section>
  )
}


export default function NursingMedicationSection({
  accessToken,
  summary,
  loading,
  savingDoseId,
  onAdminister,
}: Props) {
  const [
    selectedTreatmentId,
    setSelectedTreatmentId,
  ] = useState<string | null>(null)

  const [
    treatmentHistory,
    setTreatmentHistory,
  ] = useState<MedicationTreatmentHistory | null>(null)

  const [
    loadingTreatmentHistory,
    setLoadingTreatmentHistory,
  ] = useState(false)

  async function togglePrescriptionHistory(
    treatmentId: string,
  ) {
    if (
      selectedTreatmentId === treatmentId
    ) {
      setSelectedTreatmentId(null)
      setTreatmentHistory(null)
      return
    }

    setSelectedTreatmentId(treatmentId)
    setTreatmentHistory(null)
    setLoadingTreatmentHistory(true)

    try {
      const history =
        await getMedicationTreatmentHistory(
          accessToken,
          treatmentId,
        )

      setTreatmentHistory(history)
    } catch (err) {
      console.error(
        'Unable to load medication history.',
        err,
      )

      setSelectedTreatmentId(null)
      setTreatmentHistory(null)
    } finally {
      setLoadingTreatmentHistory(false)
    }
  }


  return (
    <section className="workspace-section">

      <div className="section-heading">
        <div>
          <p className="eyebrow">
            MEDICATIONS
          </p>

          <h3>
            Inpatient medication rounds
          </h3>

          <p>
            Focus on the current medication round,
            then review upcoming and recent rounds.
          </p>
        </div>

        {summary && (
          <span>
            {summary.prescriptions.length}
          </span>
        )}
      </div>


      {loading && (
        <div className="admin-empty-state">
          Loading medication rounds...
        </div>
      )}


      {!loading && !summary && (
        <div className="admin-empty-state">
          No medication summary available.
        </div>
      )}


      {!loading && summary && (
        <div className="nursing-medication-list">

          {summary.round.current_round ? (
            <RoundBlock
              title="CURRENT ROUND"
              round={
                summary.round.current_round
              }
              savingDoseId={
                savingDoseId
              }
              onAdminister={
                onAdminister
              }
              showActions
            />
          ) : (
            <div className="admin-empty-state">
              No medication doses are currently
              due or overdue.
            </div>
          )}


          {summary.round.upcoming_rounds.length > 0 && (
            <details className="nursing-collapsible">
              <summary>
                <span>
                  UPCOMING ROUNDS
                </span>

                <strong>
                  {summary.round.upcoming_rounds.length}
                </strong>
              </summary>

              <div className="nursing-collapsible-content">
                {summary.round.upcoming_rounds.map(
                  round => (
                    <RoundBlock
                      key={round.scheduled_at}
                      title="ROUND"
                      round={round}
                      savingDoseId={
                        savingDoseId
                      }
                      onAdminister={
                        onAdminister
                      }
                      showActions={false}
                    />
                  ),
                )}
              </div>
            </details>
          )}


          {summary.round.previous_round && (
            <details className="nursing-collapsible">
              <summary>
                <span>
                  PREVIOUS ROUND
                </span>

                <strong>
                  {formatTime(
                    summary.round.previous_round.scheduled_at,
                  )}
                </strong>
              </summary>

              <div className="nursing-collapsible-content">
                <RoundBlock
                  title="PREVIOUS ROUND"
                  round={
                    summary.round.previous_round
                  }
                  savingDoseId={
                    savingDoseId
                  }
                  onAdminister={
                    onAdminister
                  }
                  showActions={false}
                />
              </div>
            </details>
          )}


        <section
          style={{
            marginTop: '1.5rem',
          }}
        >
          <div className="section-heading">
            <div>
              <p className="eyebrow">
                ACTIVE PRESCRIPTIONS
              </p>
            </div>
          </div>

          {summary.prescriptions.map(
            prescription => {
              const expanded =
                selectedTreatmentId ===
                prescription.treatment_id

              const history =
                expanded &&
                treatmentHistory?.treatment
                  .treatment_id ===
                  prescription.treatment_id
                  ? treatmentHistory
                  : null

              return (
                <article
                  key={prescription.treatment_id}
                  className="nursing-medication-item"
                >
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() =>
                      void togglePrescriptionHistory(
                        prescription.treatment_id,
                      )
                    }
                    style={{
                      width: '100%',
                      textAlign: 'left',
                    }}
                  >
                    <div>
                      <strong>
                        {prescription.medicine_name}
                      </strong>

                      <p>
                        {prescription.dose}
                        {prescription.dose_unit
                          ? ` ${prescription.dose_unit}`
                          : ''}
                        {' · '}
                        {prescription.route}
                        {' · '}
                        {prescription.frequency}
                      </p>

                      <p>
                        {prescription.given_count}
                        {' given · '}
                        {prescription.held_count}
                        {' held · '}
                        {prescription.missed_count}
                        {' missed · '}
                        {prescription.refused_count}
                        {' refused · '}
                        {prescription.remaining_count}
                        {' remaining'}
                      </p>

                      {prescription.next_dose_at && (
                        <p>
                          Next dose:{' '}
                          {formatDateTime(
                            prescription.next_dose_at,
                          )}
                        </p>
                      )}
                    </div>
                  </button>

                  {expanded && (
                    <div
                      style={{
                        marginTop: '1rem',
                        paddingTop: '1rem',
                        borderTop:
                          '1px solid var(--border-color, #e5e7eb)',
                      }}
                    >
                      <p className="eyebrow">
                        MEDICATION HISTORY
                      </p>

                      {loadingTreatmentHistory && (
                        <div className="admin-empty-state">
                          Loading medication history...
                        </div>
                      )}

                      {!loadingTreatmentHistory &&
                        history && (
                          <div>
                            {history.doses.map(
                              dose => (
                                <div
                                  key={dose.id}
                                  style={{
                                    display: 'flex',
                                    justifyContent:
                                      'space-between',
                                    alignItems:
                                      'flex-start',
                                    gap: '1rem',
                                    padding:
                                      '0.65rem 0',
                                    borderBottom:
                                      '1px solid var(--border-color, #e5e7eb)',
                                  }}
                                >
                                  <div>
                                    <strong>
                                      {formatDateTime(
                                        dose.scheduled_at,
                                      )}
                                    </strong>

                                    {dose.administration_at && (
                                      <p>
                                        Recorded:{' '}
                                        {formatDateTime(
                                          dose.administration_at,
                                        )}
                                      </p>
                                    )}

                                    {dose.dose_given && (
                                      <p>
                                        Dose given:{' '}
                                        {dose.dose_given}
                                      </p>
                                    )}

                                    {dose.reason && (
                                      <p>
                                        Reason:{' '}
                                        {dose.reason}
                                      </p>
                                    )}

                                    {dose.notes && (
                                      <p>
                                        Notes:{' '}
                                        {dose.notes}
                                      </p>
                                    )}
                                  </div>

                                  <span className="nursing-queue-status">
                                    {dose.administration_status ??
                                      dose.scheduled_state}
                                  </span>
                                </div>
                              ),
                            )}
                          </div>
                        )}
                    </div>
                  )}
                </article>
              )
            },
          )}
        </section>

        </div>
      )}

    </section>
  )
}
