import {
  useCallback,
  useEffect,
  useState,
} from 'react'

import {
  getMedicationNursingSummary,
  getMedicationTreatmentHistory,
  type MedicationNursingSummary,
  type MedicationTreatmentHistory,
} from '../../api/medicationDoses'

interface Props {
  accessToken: string
  episodeId: string
}

function formatDateTime(
  value: string,
): string {
  return new Date(value).toLocaleString()
}

function formatCount(
  count: number,
  singular: string,
  plural: string,
): string {
  return `${count} ${count === 1 ? singular : plural}`
}

export default function DoctorMedicationTreatmentReview({
  accessToken,
  episodeId,
}: Props) {
  const [
    summary,
    setSummary,
  ] = useState<MedicationNursingSummary | null>(
    null,
  )

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    error,
    setError,
  ] = useState<string | null>(null)

  const [
    selectedTreatmentId,
    setSelectedTreatmentId,
  ] = useState<string | null>(null)

  const [
    treatmentHistory,
    setTreatmentHistory,
  ] = useState<MedicationTreatmentHistory | null>(
    null,
  )

  const [
    loadingHistory,
    setLoadingHistory,
  ] = useState(false)

  const loadSummary = useCallback(
    async () => {
      setLoading(true)
      setError(null)

      try {
        const response =
          await getMedicationNursingSummary(
            accessToken,
            episodeId,
          )

        setSummary(response)
      } catch (err) {
        setSummary(null)
        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load medication treatment summary.',
        )
      } finally {
        setLoading(false)
      }
    },
    [
      accessToken,
      episodeId,
    ],
  )

  useEffect(() => {
    void loadSummary()
  }, [loadSummary])

  async function toggleTreatmentHistory(
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
    setLoadingHistory(true)

    try {
      const history =
        await getMedicationTreatmentHistory(
          accessToken,
          treatmentId,
        )

      setTreatmentHistory(history)
    } catch (err) {
      setTreatmentHistory(null)
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load medication history.',
      )
    } finally {
      setLoadingHistory(false)
    }
  }

  return (
    <section className="workspace-section doctor-medication-review">
      <div className="section-heading">
        <div>
          <p className="eyebrow">
            MEDICATIONS & TREATMENT
          </p>

          <h3>
            Medication treatment review
          </h3>

          <p>
            Review active treatments and whether scheduled doses have been given, held, missed, or refused.
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
          Loading medication treatment summary...
        </div>
      )}

      {!loading && error && (
        <div className="admin-empty-state">
          {error}
        </div>
      )}

      {!loading &&
        !error &&
        summary &&
        summary.prescriptions.length === 0 && (
          <div className="admin-empty-state">
            No active medication treatments.
          </div>
        )}

      {!loading &&
        !error &&
        summary &&
        summary.prescriptions.length > 0 && (
          <div className="nursing-medication-list">
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

                const needsAttention =
                  prescription.missed_count > 0 ||
                  prescription.held_count > 0 ||
                  prescription.refused_count > 0 ||
                  prescription.next_dose_state ===
                    'OVERDUE'

                return (
                  <article
                    key={
                      prescription.treatment_id
                    }
                    className="nursing-medication-item"
                  >
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() =>
                        void toggleTreatmentHistory(
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
                          {formatCount(
                            prescription.given_count,
                            'given',
                            'given',
                          )}
                          {' · '}
                          {formatCount(
                            prescription.held_count,
                            'held',
                            'held',
                          )}
                          {' · '}
                          {formatCount(
                            prescription.missed_count,
                            'missed',
                            'missed',
                          )}
                          {' · '}
                          {formatCount(
                            prescription.refused_count,
                            'refused',
                            'refused',
                          )}
                        </p>

                        {prescription.next_dose_at && (
                          <p>
                            Next dose:{' '}
                            {formatDateTime(
                              prescription.next_dose_at,
                            )}
                          </p>
                        )}

                        {needsAttention && (
                          <p>
                            Attention required
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
                          DOSE HISTORY
                        </p>

                        {loadingHistory && (
                          <div className="admin-empty-state">
                            Loading medication history...
                          </div>
                        )}

                        {!loadingHistory &&
                          !history && (
                            <div className="admin-empty-state">
                              Medication history unavailable.
                            </div>
                          )}

                        {!loadingHistory &&
                          history && (
                            <div>
                              {history.doses.map(
                                dose => (
                                  <div
                                    key={dose.id}
                                    style={{
                                      padding:
                                        '0.75rem 0',
                                      borderBottom:
                                        '1px solid var(--border-color, #e5e7eb)',
                                    }}
                                  >
                                    <strong>
                                      {formatDateTime(
                                        dose.scheduled_at,
                                      )}
                                    </strong>

                                    <p>
                                      {dose.dose}
                                      {dose.dose_unit
                                        ? ` ${dose.dose_unit}`
                                        : ''}
                                      {' · '}
                                      {dose.route}
                                    </p>

                                    <p>
                                      Status:{' '}
                                      {dose.administration_status ??
                                        dose.scheduled_state}
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
                                        Reason:{' '}
                                        {dose.reason}
                                      </p>
                                    )}
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
        )}
    </section>
  )
}
