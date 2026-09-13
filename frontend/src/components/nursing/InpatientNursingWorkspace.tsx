/*
==============================================================================
LIGHTBURGH EMR

Inpatient Nursing Clinical Cockpit

Presentation/workflow layer for admitted patients.

Clinical data and API behavior remain owned by the existing nursing hooks and
child components.
==============================================================================
*/

import {
  useState,
} from 'react'

import type {
  Episode,
} from '../../api/episodes'

import type {
  Encounter,
} from '../../api/encounters'

import type {
  MedicationAdministrationStatus,
  MedicationNursingSummary,
} from '../../api/medicationDoses'

import NursingMedicationSection from './NursingMedicationSection'
import NursingVitalsForm from './NursingVitalsForm'

import type {
  VitalsFormState,
} from './nursing/types'

import {
  INITIAL_VITALS_FORM,
} from './nursing/constants'

import './InpatientNursingWorkspace.css'


interface PatientLike {
  first_name: string
  middle_name?: string | null
  last_name: string
  hospital_number: string
  sex: string
  date_of_birth: string
  blood_group?: string | null
  genotype?: string | null
}


interface Props {
  accessToken: string

  episode: Episode
  encounter: Encounter

  patient: PatientLike | null

  patientNames?: Record<string, string>

  medicationSummary: MedicationNursingSummary | null
  loadingMedications: boolean
  savingMedicationDoseId: string | null

  recordedVitals: Array<{
    id: string
    occurred_at: string
    payload: Record<string, any>
  }>

  loadingVitals: boolean
  savingVitals: boolean

  onBack: () => void

  onAdministerMedication: (
    doseId: string,
    status: MedicationAdministrationStatus,
    reason?: string,
  ) => void

  onSaveVitals: (
    vitals: VitalsFormState,
  ) => Promise<boolean>
}


function fullName(
  patient: PatientLike | null,
): string {
  if (!patient) {
    return 'Patient'
  }

  return [
    patient.first_name,
    patient.middle_name,
    patient.last_name,
  ]
    .filter(Boolean)
    .join(' ')
}


function initials(
  name: string,
): string {
  return name
    .split(' ')
    .filter(Boolean)
    .map(
      part => part.charAt(0),
    )
    .slice(0, 2)
    .join('')
    .toUpperCase()
}


function ageFromDob(
  value: string | null | undefined,
): string {
  if (!value) {
    return 'Age —'
  }

  const dob = new Date(value)
  const today = new Date()

  let age =
    today.getFullYear() -
    dob.getFullYear()

  const month =
    today.getMonth() -
    dob.getMonth()

  if (
    month < 0 ||
    (
      month === 0 &&
      today.getDate() <
        dob.getDate()
    )
  ) {
    age--
  }

  return `${age} years`
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


function vitalValue(
  payload: Record<string, any>,
  key: string,
  suffix = '',
): string {
  const value = payload[key]

  if (
    value === null ||
    value === undefined ||
    value === ''
  ) {
    return '—'
  }

  return `${value}${suffix}`
}


export default function InpatientNursingWorkspace({
  accessToken,
  episode,
  encounter,
  patient,

  medicationSummary,
  loadingMedications,
  savingMedicationDoseId,

  recordedVitals,
  loadingVitals,
  savingVitals,

  onBack,

  onAdministerMedication,
  onSaveVitals,
}: Props) {

  const [
    vitals,
    setVitals,
  ] = useState<VitalsFormState>(
    INITIAL_VITALS_FORM,
  )


  const latestVitals =
    recordedVitals.length > 0
      ? recordedVitals[
          recordedVitals.length - 1
        ]
      : null


  const patientName =
    fullName(patient)


  /*
   * This count represents active prescriptions, not individual doses.
   */
  const activePrescriptionCount =
    medicationSummary?.prescriptions?.length ?? 0


  /*
   * This represents the number of active prescriptions whose next
   * scheduled administration is currently due or overdue.
   */
  const dueMedicationCount =
    medicationSummary?.prescriptions?.filter(
      prescription =>
        prescription.next_dose_state === 'DUE' ||
        prescription.next_dose_state === 'OVERDUE',
    ).length ?? 0


  const currentRoundDoseCount =
    medicationSummary?.round.current_round?.doses?.length ?? 0


  function updateVitals(
    field: keyof VitalsFormState,
    value: string,
  ) {
    setVitals(current => ({
      ...current,
      [field]: value,
    }))
  }


  async function handleSaveVitals() {
    const saved =
      await onSaveVitals(
        vitals,
      )

    if (saved) {
      setVitals(
        INITIAL_VITALS_FORM,
      )
    }
  }


  function scrollTo(
    id: string,
  ) {
    const element =
      document.getElementById(id)

    if (!element) {
      return
    }

    element.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    })

    /*
     * Give keyboard users a useful focus target without changing the
     * clinical component's existing behavior.
     */
    window.setTimeout(() => {
      element.focus?.({
        preventScroll: true,
      })
    }, 350)
  }


  return (
    <section className="nursing-inpatient-cockpit">

      {/* ================================================================== */}
      {/* Patient header                                                     */}
      {/* ================================================================== */}

      <header className="nursing-inpatient-header">

        <div className="nursing-inpatient-patient">

          <div className="nursing-inpatient-avatar">
            {initials(patientName)}
          </div>

          <div className="nursing-inpatient-patient-copy">

            <p className="nursing-inpatient-eyebrow">
              INPATIENT NURSING
            </p>

            <h1>
              {patientName}
            </h1>

            <p className="nursing-inpatient-demographics">

              <strong>
                {patient?.hospital_number ?? 'MRN —'}
              </strong>

              <span>
                ·
              </span>

              <span>
                {patient?.sex ?? 'Sex —'}
              </span>

              <span>
                ·
              </span>

              <span>
                {ageFromDob(
                  patient?.date_of_birth,
                )}
              </span>

            </p>

          </div>

        </div>


        <div className="nursing-inpatient-header-actions">

          <div className="nursing-inpatient-status-block">

            <span className="nursing-inpatient-status-pill">
              ADMITTED
            </span>

            <div className="nursing-inpatient-episode-ref">

              <span>
                EPISODE
              </span>

              <strong>
                {episode.episode_number}
              </strong>

            </div>

          </div>


          <button
            type="button"
            className="nursing-inpatient-back-button"
            onClick={onBack}
          >
            ← Back to queue
          </button>

        </div>

      </header>


      {/* ================================================================== */}
      {/* Patient context                                                     */}
      {/* ================================================================== */}

      <section
        id="nursing-patient-context"
        tabIndex={-1}
        className="nursing-inpatient-context"
      >

        <div className="nursing-inpatient-context-item">

          <span>
            Blood group
          </span>

          <strong>
            {patient?.blood_group ?? 'Not recorded'}
          </strong>

        </div>


        <div className="nursing-inpatient-context-item">

          <span>
            Genotype
          </span>

          <strong>
            {patient?.genotype ?? 'Not recorded'}
          </strong>

        </div>


        <div className="nursing-inpatient-context-item">

          <span>
            Admission started
          </span>

          <strong>
            {formatDateTime(
              encounter.started_at,
            )}
          </strong>

        </div>


        <div className="nursing-inpatient-context-item">

          <span>
            Encounter
          </span>

          <strong>
            {encounter.title}
          </strong>

        </div>

      </section>


      {/* ================================================================== */}
      {/* Current shift                                                       */}
      {/* ================================================================== */}

      <section className="nursing-inpatient-section nursing-shift-overview">

        <div className="nursing-inpatient-section-heading">

          <div>

            <p className="nursing-inpatient-eyebrow">
              CURRENT SHIFT
            </p>

            <h2>
              Nursing work
            </h2>

          </div>

          <span className="nursing-inpatient-heading-note">
            Patient overview
          </span>

        </div>


        <div className="nursing-shift-grid">

          {/* -------------------------------------------------------------- */}
          {/* Medications                                                     */}
          {/* -------------------------------------------------------------- */}

          <article className="nursing-shift-card">

            <div className="nursing-shift-card-main">

              <div className="nursing-shift-card-label">
                MEDICATIONS
              </div>

              <div className="nursing-shift-card-value">
                {activePrescriptionCount}
              </div>

              <div className="nursing-shift-card-description">
                active prescriptions
              </div>

              <div
                className={
                  dueMedicationCount > 0
                    ? 'nursing-shift-card-alert'
                    : 'nursing-shift-card-muted'
                }
              >
                {dueMedicationCount > 0
                  ? `${dueMedicationCount} medication${
                      dueMedicationCount === 1
                        ? ''
                        : 's'
                    } due or overdue`
                  : 'Nothing due or overdue'}
              </div>

            </div>

            <button
              type="button"
              className="nursing-shift-card-action"
              aria-label="View medication rounds"
              onClick={() =>
                scrollTo(
                  'nursing-medication-rounds',
                )
              }
            >
              <span>
                View rounds
              </span>

              <span aria-hidden="true">
                →
              </span>
            </button>

          </article>


          {/* -------------------------------------------------------------- */}
          {/* Observations                                                     */}
          {/* -------------------------------------------------------------- */}

          <article className="nursing-shift-card">

            <div className="nursing-shift-card-main">

              <div className="nursing-shift-card-label">
                OBSERVATIONS
              </div>

              <div className="nursing-shift-card-value nursing-shift-card-value-small">

                {latestVitals
                  ? 'Recorded'
                  : 'Pending'}

              </div>

              <div className="nursing-shift-card-description">

                {latestVitals
                  ? `Last recorded ${formatTime(
                      latestVitals.occurred_at,
                    )}`
                  : 'No vital signs recorded'}

              </div>

              <div className="nursing-shift-card-muted">
                Clinical observations
              </div>

            </div>

            <button
              type="button"
              className="nursing-shift-card-action"
              aria-label="Record vital signs"
              onClick={() =>
                scrollTo(
                  'nursing-vitals-entry',
                )
              }
            >
              <span>
                Record vitals
              </span>

              <span aria-hidden="true">
                →
              </span>
            </button>

          </article>


          {/* -------------------------------------------------------------- */}
          {/* Admission                                                        */}
          {/* -------------------------------------------------------------- */}

          <article className="nursing-shift-card">

            <div className="nursing-shift-card-main">

              <div className="nursing-shift-card-label">
                ADMISSION
              </div>

              <div className="nursing-shift-card-value nursing-shift-card-value-small">
                Active
              </div>

              <div className="nursing-shift-card-description">
                Inpatient episode
              </div>

              <div className="nursing-shift-card-muted">
                {episode.episode_number}
              </div>

            </div>

            <button
              type="button"
              className="nursing-shift-card-action"
              aria-label="View patient admission context"
              onClick={() =>
                scrollTo(
                  'nursing-patient-context',
                )
              }
            >
              <span>
                View context
              </span>

              <span aria-hidden="true">
                →
              </span>

            </button>

          </article>

        </div>

      </section>


      {/* ================================================================== */}
      {/* Medication administration                                          */}
      {/* ================================================================== */}

      <section
        id="nursing-medication-rounds"
        tabIndex={-1}
        className="nursing-inpatient-section"
      >

        <div className="nursing-inpatient-section-heading">

          <div>

            <p className="nursing-inpatient-eyebrow">
              MEDICATION ADMINISTRATION
            </p>

            <h2>
              Medication rounds
            </h2>

          </div>

          <div className="nursing-inpatient-section-stat">

            <strong>
              {loadingMedications
                ? '—'
                : activePrescriptionCount}
            </strong>

            <span>
              active prescriptions
            </span>

          </div>

        </div>


        {!loadingMedications &&
          currentRoundDoseCount > 0 && (

            <div className="nursing-current-round-banner">

              <div>

                <span>
                  CURRENT ROUND
                </span>

                <strong>
                  {currentRoundDoseCount}
                  {' '}
                  scheduled dose
                  {currentRoundDoseCount === 1
                    ? ''
                    : 's'}
                </strong>

              </div>

              <span>
                Review and record administration outcomes below.
              </span>

            </div>

          )}


        <div className="nursing-inpatient-medication-shell">

          <NursingMedicationSection
            accessToken={accessToken}
            summary={medicationSummary}
            loading={loadingMedications}
            savingDoseId={
              savingMedicationDoseId
            }
            onAdminister={
              onAdministerMedication
            }
          />

        </div>

      </section>


      {/* ================================================================== */}
      {/* Latest observations                                                 */}
      {/* ================================================================== */}

      <section className="nursing-inpatient-section">

        <div className="nursing-inpatient-section-heading">

          <div>

            <p className="nursing-inpatient-eyebrow">
              CLINICAL OBSERVATIONS
            </p>

            <h2>
              Latest vital signs
            </h2>

          </div>

          {latestVitals && (
            <span className="nursing-inpatient-heading-note">
              Recorded{' '}
              {formatDateTime(
                latestVitals.occurred_at,
              )}
            </span>
          )}

        </div>


        {loadingVitals && (

          <div className="nursing-inpatient-empty">

            <span className="nursing-inpatient-loading-dot" />

            Loading recorded vital signs...

          </div>

        )}


        {!loadingVitals &&
          !latestVitals && (

            <div className="nursing-inpatient-empty nursing-inpatient-empty-attention">

              <strong>
                No vital signs recorded
              </strong>

              <span>
                Record the patient's current observations below.
              </span>

              <button
                type="button"
                className="nursing-inpatient-empty-action"
                onClick={() =>
                  scrollTo(
                    'nursing-vitals-entry',
                  )
                }
              >
                Record vital signs →
              </button>

            </div>

          )}


        {!loadingVitals &&
          latestVitals && (

            <div className="nursing-inpatient-vitals-grid">

              <div className="nursing-inpatient-vital-card">

                <span>
                  Temperature
                </span>

                <strong>
                  {vitalValue(
                    latestVitals.payload,
                    'temperature',
                    ' °C',
                  )}
                </strong>

              </div>


              <div className="nursing-inpatient-vital-card">

                <span>
                  Heart rate
                </span>

                <strong>
                  {vitalValue(
                    latestVitals.payload,
                    'heart_rate',
                    ' bpm',
                  )}
                </strong>

              </div>


              <div className="nursing-inpatient-vital-card">

                <span>
                  Respiratory rate
                </span>

                <strong>
                  {vitalValue(
                    latestVitals.payload,
                    'respiratory_rate',
                    ' /min',
                  )}
                </strong>

              </div>


              <div className="nursing-inpatient-vital-card">

                <span>
                  Blood pressure
                </span>

                <strong>
                  {latestVitals.payload.systolic_bp != null &&
                  latestVitals.payload.diastolic_bp != null
                    ? `${latestVitals.payload.systolic_bp}/${latestVitals.payload.diastolic_bp}`
                    : '—'}
                </strong>

                <small>
                  mmHg
                </small>

              </div>


              <div className="nursing-inpatient-vital-card">

                <span>
                  SpO₂
                </span>

                <strong>
                  {vitalValue(
                    latestVitals.payload,
                    'spo2',
                    '%',
                  )}
                </strong>

              </div>


              <div className="nursing-inpatient-vital-card">

                <span>
                  Weight
                </span>

                <strong>
                  {vitalValue(
                    latestVitals.payload,
                    'weight',
                    ' kg',
                  )}
                </strong>

              </div>

            </div>

          )}

      </section>


      {/* ================================================================== */}
      {/* Record observations                                                 */}
      {/* ================================================================== */}

      <section
        id="nursing-vitals-entry"
        tabIndex={-1}
        className="nursing-inpatient-section nursing-vitals-workspace"
      >

        <div className="nursing-inpatient-section-heading">

          <div>

            <p className="nursing-inpatient-eyebrow">
              OBSERVATIONS
            </p>

            <h2>
              Record new vital signs
            </h2>

          </div>

          <span className="nursing-inpatient-heading-note">
            Current patient
          </span>

        </div>


        <NursingVitalsForm
          vitals={vitals}
          disabled={false}
          saving={savingVitals}
          onChange={updateVitals}
          onSave={() =>
            void handleSaveVitals()
          }
        />

      </section>

    </section>
  )
}
