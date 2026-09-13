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
  ).toLocaleString(
    [],
    {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    },
  )
}


function formatTime(
  value: string,
): string {
  return new Date(
    value,
  ).toLocaleTimeString(
    [],
    {
      hour: '2-digit',
      minute: '2-digit',
    },
  )
}


function medicationDisplay(
  dose: MedicationNursingDose,
): string {
  return [
    dose.dose,
    dose.dose_unit,
    dose.route,
  ]
    .filter(Boolean)
    .join(' · ')
}


function statusLabel(
  dose: MedicationNursingDose,
): string {
  return (
    dose.administration_status ??
    dose.scheduled_state
  )
}


function statusClass(
  dose: MedicationNursingDose,
): string {
  const status =
    (
      dose.administration_status ??
      dose.scheduled_state ??
      ''
    ).toLowerCase()

  return `nursing-medication-status nursing-medication-status-${status}`
}


function isActionable(
  dose: MedicationNursingDose,
): boolean {
  return (
    dose.administration_status === null &&
    (
      dose.scheduled_state === 'DUE' ||
      dose.scheduled_state === 'OVERDUE'
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


  if (doses.length === 0) {
    return (
      <div className="nursing-medication-empty">
        No doses in this round.
      </div>
    )
  }


  return (
    <div className="nursing-medication-dose-list">

      {doses.map(
        dose => {

          const actionable =
            showActions &&
            isActionable(dose)

          const saving =
            savingDoseId === dose.id

          const selected =
            selectedDoseId === dose.id


          return (
            <article
              key={dose.id}
              className={
                actionable
                  ? 'nursing-medication-dose nursing-medication-dose-actionable'
                  : 'nursing-medication-dose'
              }
            >

              <div className="nursing-medication-dose-main">

                <div className="nursing-medication-dose-time">
                  {formatDateTime(
                    dose.scheduled_at,
                  )}
                </div>

                <h4>
                  {dose.medicine_name}
                </h4>

                <p className="nursing-medication-dose-primary">
                  {medicationDisplay(
                    dose,
                  )}
                </p>

                <p className="nursing-medication-dose-secondary">
                  {dose.frequency}

                  {dose.strength
                    ? ` · ${dose.strength}`
                    : ''}
                </p>

                {dose.administration_at && (
                  <p className="nursing-medication-dose-meta">
                    Recorded{' '}
                    {formatDateTime(
                      dose.administration_at,
                    )}
                  </p>
                )}

                {dose.reason && (
                  <p className="nursing-medication-dose-meta">
                    Reason: {dose.reason}
                  </p>
                )}

              </div>


              <div className="nursing-medication-dose-action">

                <span
                  className={statusClass(dose)}
                >
                  {statusLabel(dose)}
                </span>


                {actionable && (
                  <button
                    type="button"
                    className="nursing-medication-record-button"
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
                )}

              </div>


              {selected && (
                <div className="nursing-medication-outcome">

                  <div>

                    <p className="nursing-medication-outcome-eyebrow">
                      MEDICATION OUTCOME
                    </p>

                    <h5>
                      Record nursing outcome
                    </h5>

                  </div>


                  <label className="nursing-medication-reason">

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
                      placeholder="Add a note when clinically relevant."
                    />

                  </label>


                  <div className="nursing-medication-outcome-actions">

                    <button
                      type="button"
                      className="nursing-medication-outcome-given"
                      onClick={() =>
                        submit('GIVEN')
                      }
                    >
                      Given
                    </button>

                    <button
                      type="button"
                      onClick={() =>
                        submit('HELD')
                      }
                    >
                      Held
                    </button>

                    <button
                      type="button"
                      onClick={() =>
                        submit('MISSED')
                      }
                    >
                      Missed
                    </button>

                    <button
                      type="button"
                      onClick={() =>
                        submit('REFUSED')
                      }
                    >
                      Refused
                    </button>

                    <button
                      type="button"
                      onClick={
                        closeAction
                      }
                    >
                      Cancel
                    </button>

                  </div>

                </div>
              )}

            </article>
          )
        },
      )}

    </div>
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
    <section className="nursing-medication-round">

      <div className="nursing-medication-round-heading">

        <div>

          <span>
            {title}
          </span>

          <strong>
            {formatTime(
              round.scheduled_at,
            )}
          </strong>

        </div>

        <small>
          {round.doses.length}
          {' '}
          dose
          {round.doses.length === 1
            ? ''
            : 's'}
        </small>

      </div>


      <DoseList
        doses={round.doses}
        savingDoseId={
          savingDoseId
        }
        onAdminister={
          onAdminister
        }
        showActions={
          showActions
        }
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
      selectedTreatmentId ===
      treatmentId
    ) {
      setSelectedTreatmentId(null)
      setTreatmentHistory(null)
      return
    }


    setSelectedTreatmentId(
      treatmentId,
    )

    setTreatmentHistory(null)
    setLoadingTreatmentHistory(true)


    try {

      const history =
        await getMedicationTreatmentHistory(
          accessToken,
          treatmentId,
        )

      setTreatmentHistory(
        history,
      )

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


  if (loading) {
    return (
      <div className="nursing-medication-state">
        <span className="nursing-medication-state-indicator" />
        Loading medication rounds...
      </div>
    )
  }


  if (!summary) {
    return (
      <div className="nursing-medication-state">
        No medication summary available.
      </div>
    )
  }


  return (
    <div className="nursing-medication-module">

      {/* ================================================================ */}
      {/* Current round                                                    */}
      {/* ================================================================ */}

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

        <div className="nursing-medication-no-due">

          <div className="nursing-medication-no-due-mark">
            ✓
          </div>

          <div>

            <strong>
              No doses currently due or overdue
            </strong>

            <span>
              There is no immediate medication administration
              action for this patient.
            </span>

          </div>

        </div>

      )}


      {/* ================================================================ */}
      {/* Upcoming rounds                                                  */}
      {/* ================================================================ */}

      {summary.round.upcoming_rounds.length > 0 && (

        <details className="nursing-medication-collapsible">

          <summary>

            <div>

              <span>
                UPCOMING ROUNDS
              </span>

              <strong>
                Next scheduled administrations
              </strong>

            </div>

            <span>
              {summary.round.upcoming_rounds.length}
            </span>

          </summary>


          <div className="nursing-medication-collapsible-body">

            {summary.round.upcoming_rounds.map(
              round => (
                <RoundBlock
                  key={
                    round.scheduled_at
                  }
                  title="UPCOMING ROUND"
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


      {/* ================================================================ */}
      {/* Previous round                                                   */}
      {/* ================================================================ */}

      {summary.round.previous_round && (

        <details className="nursing-medication-collapsible">

          <summary>

            <div>

              <span>
                PREVIOUS ROUND
              </span>

              <strong>
                Administration history
              </strong>

            </div>

            <span>
              {formatTime(
                summary.round.previous_round.scheduled_at,
              )}
            </span>

          </summary>


          <div className="nursing-medication-collapsible-body">

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


      {/* ================================================================ */}
      {/* Active prescriptions                                              */}
      {/* ================================================================ */}

      <section className="nursing-medication-prescriptions">

        <div className="nursing-medication-subheading">

          <div>

            <span>
              ACTIVE PRESCRIPTIONS
            </span>

            <strong>
              {summary.prescriptions.length}
              {' '}
              active
            </strong>

          </div>

          <small>
            Select a prescription to review its administration history.
          </small>

        </div>


        <div className="nursing-medication-prescription-list">

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


              const nextState =
                prescription.next_dose_state


              return (
                <article
                  key={
                    prescription.treatment_id
                  }
                  className="nursing-medication-prescription"
                >

                  <button
                    type="button"
                    className="nursing-medication-prescription-trigger"
                    onClick={() =>
                      void togglePrescriptionHistory(
                        prescription.treatment_id,
                      )
                    }
                  >

                    <div className="nursing-medication-prescription-main">

                      <div className="nursing-medication-prescription-name-row">

                        <strong>
                          {prescription.medicine_name}
                        </strong>

                        {nextState && (
                          <span
                            className={`nursing-medication-next-state nursing-medication-next-state-${nextState.toLowerCase()}`}
                          >
                            {nextState}
                          </span>
                        )}

                      </div>


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


                      <p className="nursing-medication-prescription-counts">

                        <span>
                          {prescription.given_count}
                          {' given'}
                        </span>

                        <span>
                          {prescription.held_count}
                          {' held'}
                        </span>

                        <span>
                          {prescription.missed_count}
                          {' missed'}
                        </span>

                        <span>
                          {prescription.refused_count}
                          {' refused'}
                        </span>

                        <span>
                          {prescription.remaining_count}
                          {' remaining'}
                        </span>

                      </p>

                    </div>


                    <div className="nursing-medication-prescription-next">

                      {prescription.next_dose_at ? (
                        <>
                          <span>
                            NEXT DOSE
                          </span>

                          <strong>
                            {formatDateTime(
                              prescription.next_dose_at,
                            )}
                          </strong>
                        </>
                      ) : (
                        <span>
                          No next dose scheduled
                        </span>
                      )}

                    </div>


                    <span className="nursing-medication-prescription-chevron">
                      {expanded
                        ? '↑'
                        : '→'}
                    </span>

                  </button>


                  {expanded && (

                    <div className="nursing-medication-history">

                      <div className="nursing-medication-history-heading">

                        <div>

                          <span>
                            MEDICATION HISTORY
                          </span>

                          <strong>
                            Administration record
                          </strong>

                        </div>

                        <button
                          type="button"
                          onClick={() =>
                            togglePrescriptionHistory(
                              prescription.treatment_id,
                            )
                          }
                        >
                          Close
                        </button>

                      </div>


                      {loadingTreatmentHistory && (
                        <div className="nursing-medication-state">
                          Loading medication history...
                        </div>
                      )}


                      {!loadingTreatmentHistory &&
                        history && (

                          <div className="nursing-medication-history-list">

                            {history.doses.map(
                              dose => (

                                <div
                                  key={dose.id}
                                  className="nursing-medication-history-row"
                                >

                                  <div>

                                    <strong>
                                      {formatDateTime(
                                        dose.scheduled_at,
                                      )}
                                    </strong>

                                    {dose.administration_at && (
                                      <span>
                                        Recorded{' '}
                                        {formatDateTime(
                                          dose.administration_at,
                                        )}
                                      </span>
                                    )}

                                    {dose.dose_given && (
                                      <span>
                                        Dose given:{' '}
                                        {dose.dose_given}
                                      </span>
                                    )}

                                    {dose.reason && (
                                      <span>
                                        Reason:{' '}
                                        {dose.reason}
                                      </span>
                                    )}

                                    {dose.notes && (
                                      <span>
                                        Notes:{' '}
                                        {dose.notes}
                                      </span>
                                    )}

                                  </div>


                                  <span
                                    className={statusClass(
                                      dose,
                                    )}
                                  >
                                    {statusLabel(
                                      dose,
                                    )}
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

        </div>

      </section>

    </div>
  )
}
