/*
==============================================================================
LIGHTBURGH EMR

Inpatient Nursing Workspace

==============================================================================

Purpose
-------
Provides the nursing workspace for patients who are already admitted.

Responsibilities
----------------
• Display the admitted patient's clinical context.
• Display scheduled inpatient medication doses.
• Record medication administration outcomes.
• Display recorded vital signs.
• Record new vital signs.

Clinic nursing intake and routing do not belong here.
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
import NursingPatientSummary from './NursingPatientSummary'

import type {
  VitalsFormState,
} from './nursing/types'

import {
  INITIAL_VITALS_FORM,
} from './nursing/constants'


interface Props {
  accessToken: string

  episode: Episode
  encounter: Encounter

  patient: Parameters<
    typeof NursingPatientSummary
  >[0]['patient']

  patientNames: Record<string, string>

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


  return (
    <section className="workspace-content">

      <div className="welcome-panel">

        <div>

          <p className="eyebrow">
            INPATIENT NURSING
          </p>

          <h2>
            {patient
              ? [
                  patient.first_name,
                  patient.middle_name,
                  patient.last_name,
                ]
                  .filter(Boolean)
                  .join(' ')
              : 'Patient'}
          </h2>

          <p>
            Episode {episode.episode_number}
            {' · '}
            {episode.title}
          </p>

        </div>


        <button
          type="button"
          className="secondary-button"
          onClick={onBack}
        >
          Back to queue
        </button>

      </div>


      <section className="workspace-section">

        <div className="section-heading">

          <div>

            <p className="eyebrow">
              ADMISSION
            </p>

            <h3>
              Current admission
            </h3>

          </div>

          <span className="nursing-queue-status">
            Admitted
          </span>

        </div>


        <NursingPatientSummary
          episode={episode}
          encounter={encounter}
          patient={patient}
          loadingPatient={false}
          previousEpisodes={[]}
          loadingPreviousEpisodes={false}
          previousVisits={[]}
          loadingPreviousVisits={false}
        />

      </section>


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


      <section className="workspace-section">

        <div className="section-heading">

          <div>

            <p className="eyebrow">
              CLINICAL OBSERVATIONS
            </p>

            <h3>
              Latest vital signs
            </h3>

          </div>

        </div>


        {loadingVitals && (
          <div className="admin-empty-state">
            Loading recorded vital signs...
          </div>
        )}


        {!loadingVitals &&
          !latestVitals && (
            <div className="admin-empty-state">
              No vital signs have been
              recorded for this admission yet.
            </div>
          )}


        {!loadingVitals &&
          latestVitals && (
            <div className="nursing-vitals-summary">

              <div className="nursing-vital-card">
                <span>
                  Temperature
                </span>

                <strong>
                  {latestVitals.payload.temperature != null
                    ? `${latestVitals.payload.temperature} °C`
                    : '—'}
                </strong>
              </div>


              <div className="nursing-vital-card">
                <span>
                  Heart rate
                </span>

                <strong>
                  {latestVitals.payload.heart_rate != null
                    ? `${latestVitals.payload.heart_rate} bpm`
                    : '—'}
                </strong>
              </div>


              <div className="nursing-vital-card">
                <span>
                  Respiratory rate
                </span>

                <strong>
                  {latestVitals.payload.respiratory_rate != null
                    ? `${latestVitals.payload.respiratory_rate} /min`
                    : '—'}
                </strong>
              </div>


              <div className="nursing-vital-card">
                <span>
                  Blood pressure
                </span>

                <strong>
                  {latestVitals.payload.systolic_bp != null &&
                  latestVitals.payload.diastolic_bp != null
                    ? `${latestVitals.payload.systolic_bp}/${latestVitals.payload.diastolic_bp} mmHg`
                    : '—'}
                </strong>
              </div>


              <div className="nursing-vital-card">
                <span>
                  SpO₂
                </span>

                <strong>
                  {latestVitals.payload.spo2 != null
                    ? `${latestVitals.payload.spo2}%`
                    : '—'}
                </strong>
              </div>


              <div className="nursing-vital-card">
                <span>
                  Weight
                </span>

                <strong>
                  {latestVitals.payload.weight != null
                    ? `${latestVitals.payload.weight} kg`
                    : '—'}
                </strong>
              </div>

            </div>
          )}

      </section>


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
  )
}
