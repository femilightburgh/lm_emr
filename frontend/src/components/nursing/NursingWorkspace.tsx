import {
  useEffect,
  useState,
} from 'react'


import {
  INITIAL_INTAKE_FORM,
  INITIAL_VITALS_FORM,
} from './nursing/constants'

import type {
  NursingIntakeFormState,
  VitalsFormState,
} from './nursing/types'


import {
  documentToIntake,
  intakeToPayload,
} from './nursing/documentUtils'


import {
  useNursingVitals,
} from './nursing/useNursingVitals'

import {
  useNursingMedications,
} from './nursing/useNursingMedications'


import {
  useNursingRouting,
} from './nursing/useNursingRouting'


import {
  useNursingQueue,
} from './nursing/useNursingQueue'


import {
  useNursingPatientHistory,
} from './nursing/useNursingPatientHistory'


import {
  startNursing,
  type Episode,
} from '../../api/episodes'


import {
  getCurrentStaff,
} from '../../api/staff'


import {
  createEncounter,
  listEpisodeEncounters,
  type Encounter,
} from '../../api/encounters'


import {
  createClinicalDocument,
  listEncounterClinicalDocuments,
  signClinicalDocument,
  updateClinicalDocument,
  type ClinicalDocument,
} from '../../api/clinicalDocuments'


import NursingQueue from './NursingQueue'
import NursingPatientSummary from './NursingPatientSummary'
import NursingVitalsForm from './NursingVitalsForm'
import NursingIntakeForm from './NursingIntakeForm'
import NursingRoutingSection from './NursingRoutingSection'
import NursingMedicationSection from './NursingMedicationSection'


interface Props {
  accessToken: string
  staffId: string
}

export default function NursingWorkspace({
  accessToken,
  staffId,
}: Props) {

  // ==========================================================================
  // Nursing Document State
  // ==========================================================================

  const [nursingDocument, setNursingDocument] =
    useState<ClinicalDocument | null>(null)


  // ==========================================================================
  // General Loading / Saving State
  // ==========================================================================

  const [loadingEncounter, setLoadingEncounter] =
    useState(false)

  const [savingDocument, setSavingDocument] =
    useState(false)

  const [signingDocument, setSigningDocument] =
    useState(false)

  const [startingEpisodeId, setStartingEpisodeId] =
    useState<string | null>(null)

  const [currentStaffId, setCurrentStaffId] =
    useState<string | null>(null)

  const [selectedEpisode, setSelectedEpisode] =
    useState<Episode | null>(null)

  const [nursingEncounter, setNursingEncounter] =
    useState<Encounter | null>(null)


  // ==========================================================================
  // Messages
  // ==========================================================================

  const [error, setError] =
    useState<string | null>(null)

  const [success, setSuccess] =
    useState<string | null>(null)


  const {
    patient,
    loadingPatient,
    previousEpisodes,
    loadingPreviousEpisodes,
    previousVisits,
    loadingPreviousVisits,
    loadPatient,
    loadPreviousEpisodes,
    clearPatientHistory,
  } = useNursingPatientHistory({
    accessToken,
    onError: setError,
  })


  const {
    episodes,
    admittedEpisodes,
    patientNames,
    loading,
    loadQueue,
    setEpisodes,
  } = useNursingQueue({
    accessToken,
    onError: setError,
  })


  const {
    recordedVitals,
    loadingVitals,
    savingVitals,
    loadRecordedVitals,
    saveVitals,
    resetVitals,
    clearRecordedVitals,
  } = useNursingVitals({
    accessToken,
    onError: setError,
    onSuccess: setSuccess,
  })


  const {
    medicationSummary,
    loadingMedications,
    savingMedicationDoseId,
    loadMedicationDoses,
    administerMedicationDose,
    clearMedicationDoses,
  } = useNursingMedications({
    accessToken,
    onError: setError,
    onSuccess: setSuccess,
  })


  // ==========================================================================
  // Form State
  // ==========================================================================

  const [vitals, setVitals] =
    useState<VitalsFormState>(
      INITIAL_VITALS_FORM,
    )

  const [intake, setIntake] =
    useState<NursingIntakeFormState>(
      INITIAL_INTAKE_FORM,
    )


  const {
    departments,
    loadingDepartments,
    selectedDepartmentId,
    patientRouted,
    routingPatient,
    loadDepartments,
    routePatient,
    setSelectedDepartmentId,
    resetRouting,
  } = useNursingRouting({
    accessToken,
    onError: setError,
    onSuccess: setSuccess,
  })


  // ==========================================================================
  // Current Staff
  // ==========================================================================

  useEffect(() => {
    let cancelled = false

    async function loadCurrentStaff() {
      try {
        const currentStaff =
          await getCurrentStaff(
            accessToken,
          )

        if (!cancelled) {
          setCurrentStaffId(
            currentStaff.id,
          )
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Unable to load the authenticated Staff profile.',
          )
        }
      }
    }

    void loadCurrentStaff()

    return () => {
      cancelled = true
    }
  }, [accessToken])


  // ==========================================================================
  // Queue
  // ==========================================================================

  // ==========================================================================
  // Form Helpers
  // ==========================================================================

  function updateVitals(
    field: keyof VitalsFormState,
    value: string,
  ) {
    setVitals(current => ({
      ...current,
      [field]: value,
    }))
  }


  function updateIntake(
    field: keyof NursingIntakeFormState,
    value: string,
  ) {
    setIntake(current => ({
      ...current,
      [field]: value,
    }))
  }


  function resetAssessmentForms() {
    setVitals(
      INITIAL_VITALS_FORM,
    )

    setIntake(
      INITIAL_INTAKE_FORM,
    )
  }


  // ==========================================================================
  // Open Nursing Encounter
  // ==========================================================================

  async function openNursingEncounter(
    episode: Episode,
  ) {
    setLoadingEncounter(true)
    setError(null)
    setSuccess(null)

    try {

      const encounters =
        await listEpisodeEncounters(
          accessToken,
          episode.id,
        )


      let encounter: Encounter | undefined

      if (episode.status === 'ADMITTED') {

        encounter =
          encounters.find(
            item =>
              item.title ===
                'Inpatient Nursing' &&
              item.status === 'OPEN',
          )

        if (!encounter) {
          if (!currentStaffId) {
            throw new Error(
              'Authenticated user does not have a Staff profile.',
            )
          }

          encounter =
            await createEncounter(
              accessToken,
              {
                episode_id: episode.id,
                staff_id: currentStaffId,
                title: 'Inpatient Nursing',
              },
            )
        }

      } else {

        encounter =
          encounters.find(
            item =>
              item.title ===
                'Nursing Intake' &&
              item.status === 'OPEN',
          )

        if (!encounter) {
          throw new Error(
            'The nursing encounter could not be found.',
          )
        }
      }


      setSelectedEpisode(
        episode,
      )

      resetRouting()

      await loadDepartments(
        episode.hospital_id,
      )

      setNursingEncounter(
        encounter,
      )

      clearPatientHistory()

      clearRecordedVitals()
      clearMedicationDoses()

      resetAssessmentForms()


      // ----------------------------------------------------------------------
      // Load patient
      // ----------------------------------------------------------------------

      await loadPatient(
        episode.patient_id,
      )


      // ----------------------------------------------------------------------
      // Load previous episodes
      // ----------------------------------------------------------------------

      await loadPreviousEpisodes(
        episode.patient_id,
        episode.id,
      )


      // ----------------------------------------------------------------------
      // Load recorded vitals
      // ----------------------------------------------------------------------

      await loadRecordedVitals(
        encounter.id,
      )

      if (
        episode.status === 'ADMITTED'
      ) {
        await loadMedicationDoses(
          episode.id,
        )
      }


      // ----------------------------------------------------------------------
      // Load nursing document
      // ----------------------------------------------------------------------

      const documents =
        await listEncounterClinicalDocuments(
          accessToken,
          encounter.id,
        )


      const signedDocument =
        documents.find(
          document =>
            document.document_type ===
              'NURSING_INTAKE' &&
            document.status === 'SIGNED',
        )

      const draftDocument =
        documents.find(
          document =>
            document.document_type ===
              'NURSING_INTAKE' &&
            document.status === 'DRAFT',
        )

      const existingDocument =
        signedDocument ??
        draftDocument


      if (existingDocument) {

        setNursingDocument(
          existingDocument,
        )

        setIntake(
          documentToIntake(
            existingDocument,
          ),
        )

      } else {

        setNursingDocument(
          null,
        )

        setIntake(
          INITIAL_INTAKE_FORM,
        )

      }

    } catch (err) {

      setError(
        err instanceof Error
          ? err.message
          : 'Unable to open the nursing encounter.',
      )

    } finally {

      setLoadingEncounter(false)

    }
  }


  // ==========================================================================
  // Start Nursing
  // ==========================================================================

  async function handleStartNursing(
    episodeId: string,
  ) {
    setStartingEpisodeId(
      episodeId,
    )

    setError(null)
    setSuccess(null)

    try {

      const updated =
        await startNursing(
          accessToken,
          episodeId,
        )


      setEpisodes(current =>
        current.map(episode =>
          episode.id === updated.id
            ? updated
            : episode,
        ),
      )


      await openNursingEncounter(
        updated,
      )

    } catch (err) {

      setError(
        err instanceof Error
          ? err.message
          : 'Unable to start nursing intake.',
      )

    } finally {

      setStartingEpisodeId(
        null,
      )

    }
  }


  async function handleContinueNursing(
    episode: Episode,
  ) {
    await openNursingEncounter(
      episode,
    )
  }

  // ==========================================================================
  // Save Vitals
  // ==========================================================================

  async function handleSaveVitals() {
    if (!nursingEncounter) {
      return
    }

    const created =
      await saveVitals(
        nursingEncounter.id,
        vitals,
      )

    if (created) {
      setVitals(
        resetVitals(),
      )
    }
  }


  // ==========================================================================
  // Save Nursing Intake
  // ==========================================================================

  async function handleSaveDocument() {

    if (
      !nursingEncounter ||
      !selectedEpisode
    ) {
      return
    }


    setSavingDocument(true)
    setError(null)
    setSuccess(null)


    try {

      const content =
        intakeToPayload(
          intake,
        )


      if (nursingDocument) {

        const updated =
          await updateClinicalDocument(
            accessToken,
            nursingDocument.id,
            staffId,
            content,
          )

        setNursingDocument(
          updated,
        )

      } else {

        const created =
          await createClinicalDocument(
            accessToken,
            {
              encounter_id:
                nursingEncounter.id,

              document_type:
                'NURSING_INTAKE',

              authored_by:
                staffId,

              content,
            },
          )

        setNursingDocument(
          created,
        )

      }


      setSuccess(
        'Nursing intake saved as a draft.',
      )

    } catch (err) {

      setError(
        err instanceof Error
          ? err.message
          : 'Unable to save nursing intake.',
      )

    } finally {

      setSavingDocument(false)

    }
  }


  // ==========================================================================
  // Sign Nursing Intake
  // ==========================================================================

  async function handleSignDocument() {

    if (!nursingDocument) {
      setError(
        'Save the nursing intake before signing it.',
      )
      return
    }


    setSigningDocument(true)
    setError(null)
    setSuccess(null)


    try {

      const signed =
        await signClinicalDocument(
          accessToken,
          nursingDocument.id,
        )


      setNursingDocument(
        signed,
      )


      setSuccess(
        'Nursing intake signed successfully.',
      )

    } catch (err) {

      setError(
        err instanceof Error
          ? err.message
          : 'Unable to sign nursing intake.',
      )

    } finally {

      setSigningDocument(false)

    }
  }

  async function handleRoutePatient() {
    if (!selectedEpisode) {
      return
    }

    if (
      nursingDocument?.status !==
      'SIGNED'
    ) {
      setError(
        'Sign the nursing intake before routing the patient.',
      )
      return
    }

    const updated =
      await routePatient(
        selectedEpisode.id,
      )

    if (updated) {
      setSelectedEpisode(
        updated,
      )

      await loadQueue()
    }
  }


  // ==========================================================================
  // Back to Queue
  // ==========================================================================

  function handleBackToQueue() {

    setSelectedEpisode(null)

    setNursingEncounter(null)

    clearPatientHistory()

    setNursingDocument(null)

    clearRecordedVitals()

    resetAssessmentForms()

    setError(null)

    setSuccess(null)

    void loadQueue()
  }


  // ==========================================================================
  // Derived Queue State
  // ==========================================================================

  const waitingEpisodes =
    episodes.filter(
      episode =>
        episode.flow_status ===
        'WAITING_FOR_NURSING',
    )


  const activeEpisodes =
    episodes.filter(
      episode =>
        episode.flow_status ===
        'NURSING_IN_PROGRESS',
    )


  // ==========================================================================
  // Assessment Workspace
  // ==========================================================================

  if (
    selectedEpisode &&
    nursingEncounter
  ) {

    const documentSigned =
      nursingDocument?.status ===
      'SIGNED'


    const latestVitals =
      recordedVitals.length > 0
        ? recordedVitals[
            recordedVitals.length - 1
          ]
        : null


    return (
      <section className="workspace-content">

        {/* ================================================================ */}
        {/* Header                                                           */}
        {/* ================================================================ */}

        {/* ================================================================ */}
        {/* Patient Header                                                   */}
        {/* ================================================================ */}

        <div className="nursing-patient-header">

          <div className="nursing-patient-identity">

            <p className="eyebrow">
              NURSING ASSESSMENT
            </p>

            <h1 className="nursing-patient-name">
              {patient
                ? [
                    patient.first_name,
                    patient.middle_name,
                    patient.last_name,
                  ]
                    .filter(Boolean)
                    .join(' ')
                : 'Patient'}
            </h1>

            {patient && (
              <div className="nursing-patient-meta">

                <span>
                  Hospital No.{' '}
                  <strong>
                    {patient.hospital_number}
                  </strong>
                </span>

                <span>
                  {patient.sex}
                </span>

                <span>
                  {(() => {
                    const today =
                      new Date()

                    const birthDate =
                      new Date(
                        patient.date_of_birth,
                      )

                    let age =
                      today.getFullYear() -
                      birthDate.getFullYear()

                    const monthDifference =
                      today.getMonth() -
                      birthDate.getMonth()

                    if (
                      monthDifference < 0 ||
                      (
                        monthDifference === 0 &&
                        today.getDate() <
                          birthDate.getDate()
                      )
                    ) {
                      age--
                    }

                    return `${age} years`
                  })()}
                </span>

              </div>
            )}

          </div>


          <div className="nursing-patient-episode">

            <p className="eyebrow">
              CURRENT EPISODE
            </p>

            <strong>
              {selectedEpisode.title}
            </strong>

            <p>
              Episode{' '}
              {selectedEpisode.episode_number}
            </p>

            <p>
              Nursing encounter started{' '}
              {new Date(
                nursingEncounter.started_at,
              ).toLocaleString()}
            </p>

            <button
              type="button"
              className="secondary-button"
              onClick={
                handleBackToQueue
              }
              style={{
                marginTop: '12px',
              }}
            >
              Back to queue
            </button>

          </div>

        </div>




        {/* ================================================================ */}
        {/* Messages                                                         */}
        {/* ================================================================ */}

        {error && (
          <div className="admin-error">
            {error}
          </div>
        )}


        {success && (
          <div className="admin-empty-state">
            {success}
          </div>
        )}


        {/* ================================================================ */}
        {/* Patient Summary                                                  */}
        {/* ================================================================ */}

        <NursingPatientSummary
          episode={selectedEpisode}
          encounter={nursingEncounter}
          patient={patient}
          loadingPatient={loadingPatient}
          previousEpisodes={
            previousEpisodes
          }
          loadingPreviousEpisodes={
            loadingPreviousEpisodes
          }
          previousVisits={
            previousVisits
          }
          loadingPreviousVisits={
            loadingPreviousVisits
          }
        />


        {selectedEpisode.status === 'ADMITTED' ? (

          <>
            {/* ============================================================ */}
            {/* Inpatient Medication Administration                         */}
            {/* ============================================================ */}

            <NursingMedicationSection
              accessToken={accessToken}
              summary={medicationSummary}
              loading={loadingMedications}
              savingDoseId={
                savingMedicationDoseId
              }
              onAdminister={(
                doseId,
                status,
                reason,
              ) => {
                void administerMedicationDose(
                  doseId,
                  status,
                  reason,
                ).then(
                  success => {
                    if (
                      success &&
                      selectedEpisode
                    ) {
                      void loadMedicationDoses(
                        selectedEpisode.id,
                      )
                    }
                  },
                )
              }}
            />


            {/* ============================================================ */}
            {/* Inpatient Observations                                       */}
            {/* ============================================================ */}

                          <section className="workspace-section">

                <div className="section-heading">

                  <div>

                    <p className="eyebrow">
                      VITAL SIGNS
                    </p>

                    <h3>
                      Latest observations
                    </h3>

                  </div>

                  {latestVitals && (
                    <span className="nursing-vitals-time">
                      {new Date(
                        latestVitals.occurred_at,
                      ).toLocaleTimeString(
                        [],
                        {
                          hour: '2-digit',
                          minute: '2-digit',
                        },
                      )}
                    </span>
                  )}

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
                      recorded for this encounter
                      yet.
                    </div>
                  )}


                {!loadingVitals &&
                  latestVitals && (
                    <div className="nursing-latest-vitals">

                      <div className="nursing-latest-vital">
                        <span>
                          HR
                        </span>

                        <strong>
                          {latestVitals.payload.heart_rate != null
                            ? `${latestVitals.payload.heart_rate} bpm`
                            : '—'}
                        </strong>
                      </div>


                      <div className="nursing-latest-vital">
                        <span>
                          BP
                        </span>

                        <strong>
                          {latestVitals.payload.systolic_bp != null &&
                          latestVitals.payload.diastolic_bp != null
                            ? `${latestVitals.payload.systolic_bp}/${latestVitals.payload.diastolic_bp}`
                            : '—'}
                        </strong>

                        {latestVitals.payload.systolic_bp != null &&
                        latestVitals.payload.diastolic_bp != null && (
                          <small>
                            mmHg
                          </small>
                        )}
                      </div>


                      <div className="nursing-latest-vital">
                        <span>
                          RR
                        </span>

                        <strong>
                          {latestVitals.payload.respiratory_rate != null
                            ? `${latestVitals.payload.respiratory_rate} /min`
                            : '—'}
                        </strong>
                      </div>


                      <div className="nursing-latest-vital">
                        <span>
                          SpO₂
                        </span>

                        <strong>
                          {latestVitals.payload.spo2 != null
                            ? `${latestVitals.payload.spo2}%`
                            : '—'}
                        </strong>
                      </div>


                      <div className="nursing-latest-vital">
                        <span>
                          Temp
                        </span>

                        <strong>
                          {latestVitals.payload.temperature != null
                            ? `${latestVitals.payload.temperature} °C`
                            : '—'}
                        </strong>
                      </div>


                      <div className="nursing-latest-vital">
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


                {latestVitals && (
                  <div className="nursing-vital-recorded">
                    Recorded{' '}
                    {new Date(
                      latestVitals.occurred_at,
                    ).toLocaleString()}
                  </div>
                )}


                {recordedVitals.length > 1 && (
                  <details className="nursing-collapsible nursing-vitals-history">

                    <summary>

                      <div>

                        <span className="nursing-collapsible-label">
                          PREVIOUS OBSERVATIONS
                        </span>

                        <span className="nursing-collapsible-summary">
                          {recordedVitals.length - 1}
                          {' '}
                          {recordedVitals.length - 1 === 1
                            ? 'previous observation'
                            : 'previous observations'}
                        </span>

                      </div>

                      <span className="nursing-collapsible-chevron">
                        ▾
                      </span>

                    </summary>


                    <div className="nursing-compact-content">

                      {recordedVitals
                        .slice(0, -1)
                        .reverse()
                        .map(
                          observation => (
                            <div
                              key={
                                observation.id
                              }
                              className="nursing-vitals-history-row"
                            >

                              <div>
                                <strong>
                                  {new Date(
                                    observation.occurred_at,
                                  ).toLocaleString()}
                                </strong>
                              </div>


                              <div className="nursing-vitals-history-values">

                                <span>
                                  HR{' '}
                                  {observation.payload.heart_rate != null
                                    ? `${observation.payload.heart_rate}`
                                    : '—'}
                                </span>

                                <span>
                                  BP{' '}
                                  {observation.payload.systolic_bp != null &&
                                  observation.payload.diastolic_bp != null
                                    ? `${observation.payload.systolic_bp}/${observation.payload.diastolic_bp}`
                                    : '—'}
                                </span>

                                <span>
                                  RR{' '}
                                  {observation.payload.respiratory_rate != null
                                    ? `${observation.payload.respiratory_rate}`
                                    : '—'}
                                </span>

                                <span>
                                  SpO₂{' '}
                                  {observation.payload.spo2 != null
                                    ? `${observation.payload.spo2}%`
                                    : '—'}
                                </span>

                                <span>
                                  Temp{' '}
                                  {observation.payload.temperature != null
                                    ? `${observation.payload.temperature} °C`
                                    : '—'}
                                </span>

                                <span>
                                  Weight{' '}
                                  {observation.payload.weight != null
                                    ? `${observation.payload.weight} kg`
                                    : '—'}
                                </span>

                              </div>

                            </div>
                          ),
                        )}

                    </div>

                  </details>
                )}

              </section>



            {/* ============================================================ */}
            {/* Record Inpatient Vitals                                      */}
            {/* ============================================================ */}

            <NursingVitalsForm
              vitals={vitals}
              disabled={false}
              saving={savingVitals}
              onChange={updateVitals}
              onSave={() =>
                void handleSaveVitals()
              }
            />

          </>

        ) : (

          <>
            {/* ============================================================ */}
            {/* Clinic Nursing Intake                                        */}
            {/* ============================================================ */}

            <NursingVitalsForm
              vitals={vitals}
              disabled={false}
              saving={savingVitals}
              onChange={updateVitals}
              onSave={() =>
                void handleSaveVitals()
              }
            />


            <NursingIntakeForm
              intake={intake}
              disabled={
                documentSigned ||
                savingDocument ||
                signingDocument
              }
              saving={
                savingDocument ||
                signingDocument
              }
              status={
                nursingDocument
                  ? nursingDocument.status
                  : 'DRAFT'
              }
              onChange={updateIntake}
              onSave={() =>
                void handleSaveDocument()
              }
              onSign={() =>
                void handleSignDocument()
              }
            />

            {documentSigned && (
              <NursingRoutingSection
                departments={departments}
                selectedDepartmentId={
                  selectedDepartmentId
                }
                loadingDepartments={
                  loadingDepartments
                }
                disabled={
                  routingPatient ||
                  loadingEncounter
                }
                routing={routingPatient}
                routed={patientRouted}
                onDepartmentChange={
                  setSelectedDepartmentId
                }
                onRoute={() =>
                  void handleRoutePatient()
                }
              />
            )}

          </>

        )}

      </section>
    )
  }

          // Queue Workspace
  // ==========================================================================

  return (
    <section className="workspace-content">

      <div className="welcome-panel">

        <div>

          <p className="eyebrow">
            NURSING
          </p>

          <h2>
            Nursing workspace
          </h2>

          <p>
            Review patients waiting for
            nursing assessment and continue
            active nursing encounters.
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
          {loading
            ? 'Loading...'
            : 'Refresh'}
        </button>

      </div>


      {error && (
        <div className="admin-error">
          {error}
        </div>
      )}


      {success && (
        <div className="admin-empty-state">
          {success}
        </div>
      )}


      <NursingQueue
        waitingEpisodes={
          waitingEpisodes
        }
        activeEpisodes={
          activeEpisodes
        }
        admittedEpisodes={
          admittedEpisodes
        }
        patientNames={
          patientNames
        }
        loading={loading}
        loadingEncounter={
          loadingEncounter
        }
        startingEpisodeId={
          startingEpisodeId
        }
        onStartNursing={
          episodeId => {
            void handleStartNursing(
              episodeId,
            )
          }
        }
        onContinueNursing={
          episode => {
            void handleContinueNursing(
              episode,
            )
          }
        }
      />

    </section>
  )
}