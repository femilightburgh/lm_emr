import { useState } from 'react'

import type { Vitals } from '../../api/vitals'


interface Props {
  vitals: Vitals[]
  nursingVitals: Vitals[]
  saving: boolean
  encounterClosed: boolean

  temperature: string
  heartRate: string
  respiratoryRate: string
  systolicBp: string
  diastolicBp: string
  spo2: string
  weight: string

  onTemperatureChange: (value: string) => void
  onHeartRateChange: (value: string) => void
  onRespiratoryRateChange: (value: string) => void
  onSystolicBpChange: (value: string) => void
  onDiastolicBpChange: (value: string) => void
  onSpo2Change: (value: string) => void
  onWeightChange: (value: string) => void

  onSave: () => void
}


function formatRecordedVitals(
  vital: Vitals,
): string {
  const parts: string[] = []

  if (vital.payload.temperature != null) {
    parts.push(
      `Temp ${vital.payload.temperature} °C`,
    )
  }

  if (vital.payload.heart_rate != null) {
    parts.push(
      `HR ${vital.payload.heart_rate} bpm`,
    )
  }

  if (vital.payload.respiratory_rate != null) {
    parts.push(
      `RR ${vital.payload.respiratory_rate}/min`,
    )
  }

  if (
    vital.payload.systolic_bp != null ||
    vital.payload.diastolic_bp != null
  ) {
    const systolic =
      vital.payload.systolic_bp ?? '—'

    const diastolic =
      vital.payload.diastolic_bp ?? '—'

    parts.push(
      `BP ${systolic}/${diastolic} mmHg`,
    )
  }

  if (vital.payload.spo2 != null) {
    parts.push(
      `SpO₂ ${vital.payload.spo2}%`,
    )
  }

  if (vital.payload.weight != null) {
    parts.push(
      `Wt ${vital.payload.weight} kg`,
    )
  }

  return parts.join(' · ')
}


export default function VitalsPanel({
  vitals,
  nursingVitals,
  saving,
  encounterClosed,

  temperature,
  heartRate,
  respiratoryRate,
  systolicBp,
  diastolicBp,
  spo2,
  weight,

  onTemperatureChange,
  onHeartRateChange,
  onRespiratoryRateChange,
  onSystolicBpChange,
  onDiastolicBpChange,
  onSpo2Change,
  onWeightChange,

  onSave,
}: Props) {
  const [showEntryForm, setShowEntryForm] =
    useState(false)

  const [activeVitalSource, setActiveVitalSource] =
    useState<'NURSING' | 'DOCTOR'>('NURSING')

  const latestNursingVital =
    nursingVitals.length > 0
      ? nursingVitals[nursingVitals.length - 1]
      : null

  const latestDoctorVital =
    vitals.length > 0
      ? vitals[vitals.length - 1]
      : null

  const effectiveVitalSource =
    activeVitalSource === 'NURSING' &&
    !latestNursingVital &&
    latestDoctorVital
      ? 'DOCTOR'
      : activeVitalSource

  const displayedVital =
    effectiveVitalSource === 'DOCTOR'
      ? latestDoctorVital
      : latestNursingVital

  return (
    <section className="workspace-panel doctor-vitals-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">
            CLINICAL MEASUREMENTS
          </p>

          <h2>
            Vitals
          </h2>

          <p>
            Record the patient’s current vital signs.
          </p>
        </div>
      </div>

      <div className="doctor-latest-vitals">
        <div className="doctor-vitals-source-switch">
          <p className="eyebrow">
            LATEST OBSERVATIONS
          </p>

          <div className="doctor-vitals-source-tabs">
            <button
              type="button"
              className={
                effectiveVitalSource === 'NURSING'
                  ? 'active'
                  : ''
              }
              disabled={!latestNursingVital}
              onClick={() =>
                setActiveVitalSource(
                  'NURSING',
                )
              }
            >
              Nursing
            </button>

            <button
              type="button"
              className={
                effectiveVitalSource === 'DOCTOR'
                  ? 'active'
                  : ''
              }
              disabled={!latestDoctorVital}
              onClick={() =>
                setActiveVitalSource(
                  'DOCTOR',
                )
              }
            >
              Doctor
            </button>
          </div>
        </div>

        <div className="doctor-vitals-current-source">
          <span>
            {effectiveVitalSource === 'NURSING'
              ? 'NURSING'
              : 'DOCTOR'}
          </span>

          {displayedVital ? (
            <>
              <strong>
                {formatRecordedVitals(
                  displayedVital,
                )}
              </strong>

              <small>
                {new Date(
                  displayedVital.occurred_at,
                ).toLocaleString()}
              </small>
            </>
          ) : (
            <strong>
              No observations recorded.
            </strong>
          )}
        </div>

        <button
          type="button"
          className="secondary-button doctor-vitals-toggle"
          onClick={() =>
            setShowEntryForm(
              current => !current,
            )
          }
        >
          {showEntryForm
            ? 'Hide entry form'
            : 'Record additional vitals'}

          <span aria-hidden="true">
            {showEntryForm ? '⌃' : '⌄'}
          </span>
        </button>
      </div>

      {showEntryForm && (
        <>
          <div className="doctor-vitals-form">
            <div className="doctor-vital-field">
              <label>
                <span>Temperature</span>

                <div>
                  <input
                    inputMode="decimal"
                    disabled={encounterClosed}
                    value={temperature}
                    onChange={event =>
                      onTemperatureChange(
                        event.target.value,
                      )
                    }
                    placeholder="36.8"
                  />

                  <small>°C</small>
                </div>
              </label>
            </div>

            <div className="doctor-vital-field">
              <label>
                <span>Heart rate</span>

                <div>
                  <input
                    inputMode="numeric"
                    disabled={encounterClosed}
                    value={heartRate}
                    onChange={event =>
                      onHeartRateChange(
                        event.target.value,
                      )
                    }
                    placeholder="72"
                  />

                  <small>bpm</small>
                </div>
              </label>
            </div>

            <div className="doctor-vital-field">
              <label>
                <span>Respiratory rate</span>

                <div>
                  <input
                    inputMode="numeric"
                    disabled={encounterClosed}
                    value={respiratoryRate}
                    onChange={event =>
                      onRespiratoryRateChange(
                        event.target.value,
                      )
                    }
                    placeholder="16"
                  />

                  <small>/min</small>
                </div>
              </label>
            </div>

            <div className="doctor-vital-field doctor-bp-field">
              <label>
                <span>Blood pressure</span>

                <div className="doctor-bp-inputs">
                  <input
                    inputMode="numeric"
                    disabled={encounterClosed}
                    value={systolicBp}
                    onChange={event =>
                      onSystolicBpChange(
                        event.target.value,
                      )
                    }
                    placeholder="120"
                    aria-label="Systolic blood pressure"
                  />

                  <span>/</span>

                  <input
                    inputMode="numeric"
                    disabled={encounterClosed}
                    value={diastolicBp}
                    onChange={event =>
                      onDiastolicBpChange(
                        event.target.value,
                      )
                    }
                    placeholder="80"
                    aria-label="Diastolic blood pressure"
                  />

                  <small>mmHg</small>
                </div>
              </label>
            </div>

            <div className="doctor-vital-field">
              <label>
                <span>SpO₂</span>

                <div>
                  <input
                    inputMode="numeric"
                    disabled={encounterClosed}
                    value={spo2}
                    onChange={event =>
                      onSpo2Change(
                        event.target.value,
                      )
                    }
                    placeholder="98"
                  />

                  <small>%</small>
                </div>
              </label>
            </div>

            <div className="doctor-vital-field">
              <label>
                <span>Weight</span>

                <div>
                  <input
                    inputMode="decimal"
                    disabled={encounterClosed}
                    value={weight}
                    onChange={event =>
                      onWeightChange(
                        event.target.value,
                      )
                    }
                    placeholder="70"
                  />

                  <small>kg</small>
                </div>
              </label>
            </div>
          </div>

          <div className="doctor-vitals-actions">
            <button
              type="button"
              className="primary-button"
              disabled={
                saving ||
                encounterClosed
              }
              onClick={onSave}
            >
              {encounterClosed
                ? 'Encounter Closed'
                : saving
                  ? 'Recording...'
                  : 'Record Vitals'}
            </button>
          </div>
        </>
      )}

    </section>
  )
}
