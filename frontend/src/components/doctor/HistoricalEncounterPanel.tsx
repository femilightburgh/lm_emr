import type { ClinicalDocument } from '../../api/clinicalDocuments'
import type { ClinicalDiagnosis } from '../../api/diagnoses'
import type { ClinicalOrder } from '../../api/clinicalOrders'
import type { ClinicalEvent, Encounter } from '../../api/encounters'
import type { Episode } from '../../api/episodes'
import type { Vitals } from '../../api/vitals'
import SignedClinicalDocumentSummary from './SignedClinicalDocumentSummary'
import HistoricalDoctorDocumentViewer from './HistoricalDoctorDocumentViewer'
import { documentToIntake } from '../nursing/nursing/documentUtils'
import { useState } from 'react'


interface Props {
  episode: Episode | null
  encounter: Encounter | null

  documents: ClinicalDocument[]
  diagnoses: ClinicalDiagnosis[]
  orders: ClinicalOrder[]
  vitals: Vitals[]
  timeline: ClinicalEvent[]

  loading: boolean
  onCloseHistory: () => void
}


function formatDate(
  value: string | null | undefined,
): string {
  if (!value) {
    return '—'
  }

  return new Date(value).toLocaleString()
}


function vitalValue(
  value: number | null | undefined,
): string {
  return value === null ||
    value === undefined
    ? '—'
    : String(value)
}


function documentText(
  value: string | undefined,
): string {
  return value?.trim() || 'Not documented'
}

function NursingHistoricalDocumentViewer({
  document,
}: {
  document: ClinicalDocument
}) {
  const intake =
    documentToIntake(document)

  return (
    <section className="doctor-history-nursing-document">
      <header>
        <div>
          <p className="eyebrow">
            SIGNED NURSING DOCUMENT
          </p>

          <h3>
            Nursing intake
          </h3>

          <p>
            Read-only clinical record · v{document.version}
          </p>
        </div>

        <span className="doctor-history-status doctor-history-status-complete">
          {document.status}
        </span>
      </header>

      <div className="doctor-history-nursing-document-grid">

        <section>
          <p className="eyebrow">
            PRESENTING PROBLEM
          </p>

          <div className="doctor-history-document-field">
            <span>
              Presenting complaint
            </span>
            <strong>
              {documentText(
                intake.presenting_complaint,
              )}
            </strong>
          </div>

          <div className="doctor-history-document-field">
            <span>
              History of presenting complaint
            </span>
            <strong>
              {documentText(
                intake.history_of_presenting_complaint,
              )}
            </strong>
          </div>
        </section>


        <section>
          <p className="eyebrow">
            MEDICAL BACKGROUND
          </p>

          <div className="doctor-history-document-field">
            <span>
              Known allergies
            </span>
            <strong>
              {documentText(
                intake.known_allergies,
              )}
            </strong>
          </div>

          <div className="doctor-history-document-field">
            <span>
              Allergy notes
            </span>
            <strong>
              {documentText(
                intake.allergy_notes,
              )}
            </strong>
          </div>

          <div className="doctor-history-document-field">
            <span>
              Past medical history
            </span>
            <strong>
              {documentText(
                intake.past_medical_history,
              )}
            </strong>
          </div>

          <div className="doctor-history-document-field">
            <span>
              Current medications
            </span>
            <strong>
              {documentText(
                intake.current_medications,
              )}
            </strong>
          </div>

          <div className="doctor-history-document-field">
            <span>
              Surgical history
            </span>
            <strong>
              {documentText(
                intake.surgical_history,
              )}
            </strong>
          </div>
        </section>


        <section>
          <p className="eyebrow">
            CLINICAL ASSESSMENT
          </p>

          <div className="doctor-history-document-field">
            <span>
              General appearance
            </span>
            <strong>
              {documentText(
                intake.general_appearance,
              )}
            </strong>
          </div>

          <div className="doctor-history-document-field">
            <span>
              Level of consciousness
            </span>
            <strong>
              {documentText(
                intake.level_of_consciousness,
              )}
            </strong>
          </div>

          <div className="doctor-history-document-field">
            <span>
              Mobility
            </span>
            <strong>
              {documentText(
                intake.mobility_status,
              )}
            </strong>
          </div>

          <div className="doctor-history-document-field">
            <span>
              Pain
            </span>
            <strong>
              {intake.pain_score
                ? `${intake.pain_score}${
                    intake.pain_location
                      ? ` · ${intake.pain_location}`
                      : ''
                  }`
                : 'Not documented'}
            </strong>
          </div>
        </section>


        <section>
          <p className="eyebrow">
            RISK & SAFETY
          </p>

          <div className="doctor-history-document-field">
            <span>
              Fall risk
            </span>
            <strong>
              {documentText(
                intake.fall_risk,
              )}
            </strong>
          </div>

          <div className="doctor-history-document-field">
            <span>
              Pressure injury risk
            </span>
            <strong>
              {documentText(
                intake.pressure_injury_risk,
              )}
            </strong>
          </div>

          <div className="doctor-history-document-field">
            <span>
              Infection precautions
            </span>
            <strong>
              {documentText(
                intake.infection_precautions,
              )}
            </strong>
          </div>
        </section>


        <section className="doctor-history-document-wide">
          <p className="eyebrow">
            NURSING OBSERVATIONS
          </p>

          <div className="doctor-history-document-field">
            <span>
              Nursing observations
            </span>
            <strong>
              {documentText(
                intake.nursing_observations,
              )}
            </strong>
          </div>

          <div className="doctor-history-document-field">
            <span>
              Immediate concerns
            </span>
            <strong>
              {documentText(
                intake.immediate_concerns,
              )}
            </strong>
          </div>
        </section>


        <section className="doctor-history-document-wide">
          <p className="eyebrow">
            HANDOVER
          </p>

          <div className="doctor-history-document-field">
            <span>
              Handover notes
            </span>
            <strong>
              {documentText(
                intake.handover_notes,
              )}
            </strong>
          </div>
        </section>

      </div>
    </section>
  )
}


export default function HistoricalEncounterPanel({
  episode,
  encounter,
  documents,
  diagnoses,
  orders,
  vitals,
  timeline,
  loading,
  onCloseHistory,
}: Props) {
  const [selectedDocumentId, setSelectedDocumentId] =
    useState<string | null>(null)

  if (!episode || !encounter) {
    return null
  }

  const sortedVitals =
    vitals
      .slice()
      .sort(
        (a, b) =>
          new Date(
            b.occurred_at,
          ).getTime() -
          new Date(
            a.occurred_at,
          ).getTime(),
      )

  function clinicalDocumentIdFromEvent(
    event: ClinicalEvent,
  ): string | null {
    const value =
      event.payload?.clinical_document_id

    return typeof value === 'string' &&
      value.trim()
      ? value
      : null
  }

  const sortedTimeline =
    timeline
      .slice()
      .sort(
        (a, b) =>
          new Date(
            b.occurred_at,
          ).getTime() -
          new Date(
            a.occurred_at,
          ).getTime(),
      )

  return (
    <section className="workspace-panel doctor-historical-encounter">
      <header className="doctor-historical-header">
        <div>
          <p className="eyebrow">
            HISTORICAL ENCOUNTER
          </p>

          <h2>
            {encounter.title}
          </h2>

          <p>
            {episode.episode_number}
            {' · '}
            {episode.title}
          </p>
        </div>

        <div className="doctor-historical-header-status">
          <span>
            {encounter.status}
          </span>

          <small>
            {formatDate(
              encounter.started_at,
            )}
            {encounter.ended_at
              ? ` – ${formatDate(
                  encounter.ended_at,
                )}`
              : ''}
          </small>
        </div>
      </header>

      <div className="doctor-historical-actions">
        <button
          type="button"
          className="secondary-button"
          onClick={onCloseHistory}
        >
          Close history
        </button>
      </div>

      {loading ? (
        <div className="doctor-historical-empty">
          Loading historical encounter…
        </div>
      ) : (
        <div className="doctor-historical-sections">

          <section className="doctor-history-section">
            <header>
              <div>
                <p className="eyebrow">
                  DOCUMENTS
                </p>
                <h3>
                  Clinical documents
                </h3>
              </div>

              <span className="doctor-history-count">
                {documents.length}
              </span>
            </header>

            {documents.length === 0 ? (
              <div className="doctor-history-empty">
                No clinical documents recorded.
              </div>
            ) : (
              <div className="doctor-history-list">
                {documents.map(document => {
                  const isDoctorDocument =
                    document.document_type ===
                      'INITIAL_CLERKING' ||
                    document.document_type ===
                      'PROGRESS_NOTE'

                  const isSelected =
                    selectedDocumentId ===
                    document.id

                  return (
                    <div
                      key={document.id}
                      className={
                        `doctor-history-document-row${
                          isSelected
                            ? ' is-selected'
                            : ''
                        }`
                      }
                    >
                      <button
                        type="button"
                        className="doctor-history-document-button"
                        onClick={() =>
                          isDoctorDocument
                            ? setSelectedDocumentId(
                                isSelected
                                  ? null
                                  : document.id,
                              )
                            : undefined
                        }
                        disabled={!isDoctorDocument}
                      >
                        <span>
                          <strong>
                            {document.document_type}
                          </strong>

                          <span>
                            Version {document.version}
                            {document.signed_at
                              ? ` · signed ${formatDate(
                                  document.signed_at,
                                )}`
                              : ''}
                          </span>
                        </span>

                        <span className="doctor-history-document-action">
                          <span
                            className={
                              document.status ===
                                'SIGNED' ||
                              document.status ===
                                'AMENDED'
                                ? 'doctor-history-status doctor-history-status-complete'
                                : 'doctor-history-status'
                            }
                          >
                            {document.status}
                          </span>

                          {isDoctorDocument && (
                            <span>
                              {isSelected
                                ? 'Hide clinical note'
                                : 'View clinical note →'}
                            </span>
                          )}
                        </span>
                      </button>

                      {isSelected && (
                        <div className="doctor-history-document-viewer">
                          <HistoricalDoctorDocumentViewer
                            document={document}
                          />
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </section>


          <section className="doctor-history-section">
            <header>
              <div>
                <p className="eyebrow">
                  DIAGNOSES
                </p>
                <h3>
                  Clinical diagnoses
                </h3>
              </div>

              <span className="doctor-history-count">
                {diagnoses.length}
              </span>
            </header>

            {diagnoses.length === 0 ? (
              <div className="doctor-history-empty">
                No diagnoses recorded.
              </div>
            ) : (
              <div className="doctor-history-list">
                {diagnoses.map(diagnosis => (
                  <div
                    key={diagnosis.id}
                    className="doctor-history-row"
                  >
                    <div>
                      <strong>
                        {diagnosis.diagnosis_name}
                      </strong>

                      <span>
                        {diagnosis.code
                          ? `${diagnosis.code} · `
                          : ''}
                        {diagnosis.diagnosis_type}
                        {' · '}
                        {diagnosis.certainty}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>


          <section className="doctor-history-section">
            <header>
              <div>
                <p className="eyebrow">
                  ORDERS
                </p>
                <h3>
                  Clinical orders
                </h3>
              </div>

              <span className="doctor-history-count">
                {orders.length}
              </span>
            </header>

            {orders.length === 0 ? (
              <div className="doctor-history-empty">
                No clinical orders recorded.
              </div>
            ) : (
              <div className="doctor-history-list">
                {orders.map(order => (
                  <div
                    key={order.id}
                    className="doctor-history-row"
                  >
                    <div>
                      <strong>
                        {order.order_type}
                      </strong>

                      <span>
                        Priority {order.priority}
                      </span>
                    </div>

                    <span className="doctor-history-status">
                      {order.status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </section>


          <section className="doctor-history-section">
            <header>
              <div>
                <p className="eyebrow">
                  VITALS
                </p>
                <h3>
                  Recorded observations
                </h3>
              </div>

              <span className="doctor-history-count">
                {vitals.length}
              </span>
            </header>

            {sortedVitals.length === 0 ? (
              <div className="doctor-history-empty">
                No vitals recorded.
              </div>
            ) : (
              <div className="doctor-history-vitals">
                {sortedVitals.map(vital => (
                  <div
                    key={vital.id}
                    className="doctor-history-vital"
                  >
                    <div className="doctor-history-vital-time">
                      <strong>
                        {formatDate(
                          vital.occurred_at,
                        )}
                      </strong>
                    </div>

                    <div className="doctor-history-vital-values">
                      <span>
                        <small>Temp</small>
                        <strong>
                          {vitalValue(
                            vital.payload.temperature,
                          )}
                          {vital.payload.temperature !==
                            null &&
                            vital.payload.temperature !==
                              undefined
                            ? ' °C'
                            : ''}
                        </strong>
                      </span>

                      <span>
                        <small>BP</small>
                        <strong>
                          {vitalValue(
                            vital.payload.systolic_bp,
                          )}
                          /
                          {vitalValue(
                            vital.payload.diastolic_bp,
                          )}
                        </strong>
                      </span>

                      <span>
                        <small>HR</small>
                        <strong>
                          {vitalValue(
                            vital.payload.heart_rate,
                          )}
                          {vital.payload.heart_rate !==
                            null &&
                            vital.payload.heart_rate !==
                              undefined
                            ? ' bpm'
                            : ''}
                        </strong>
                      </span>

                      <span>
                        <small>RR</small>
                        <strong>
                          {vitalValue(
                            vital.payload.respiratory_rate,
                          )}
                          {vital.payload.respiratory_rate !==
                            null &&
                            vital.payload.respiratory_rate !==
                              undefined
                            ? ' /min'
                            : ''}
                        </strong>
                      </span>

                      <span>
                        <small>SpO₂</small>
                        <strong>
                          {vitalValue(
                            vital.payload.spo2,
                          )}
                          {vital.payload.spo2 !==
                            null &&
                            vital.payload.spo2 !==
                              undefined
                            ? ' %'
                            : ''}
                        </strong>
                      </span>

                      <span>
                        <small>Weight</small>
                        <strong>
                          {vitalValue(
                            vital.payload.weight,
                          )}
                          {vital.payload.weight !==
                            null &&
                            vital.payload.weight !==
                              undefined
                            ? ' kg'
                            : ''}
                        </strong>
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>


          <section className="doctor-history-section">
            <header>
              <div>
                <p className="eyebrow">
                  TIMELINE
                </p>
                <h3>
                  Clinical activity
                </h3>
              </div>

              <span className="doctor-history-count">
                {timeline.length}
              </span>
            </header>

            {sortedTimeline.length === 0 ? (
              <div className="doctor-history-empty">
                No clinical events recorded.
              </div>
            ) : (
              <div className="doctor-history-timeline">
                {sortedTimeline.map(event => {
                  const clinicalDocumentId =
                    clinicalDocumentIdFromEvent(
                      event,
                    )

                  const linkedDocument =
                    clinicalDocumentId
                      ? documents.find(
                          document =>
                            document.id ===
                            clinicalDocumentId,
                        ) ?? null
                      : null

                  const isClinicalNote =
                    event.event_type ===
                    'CLINICAL_NOTE_RECORDED'

                  const canOpenDocument =
                    Boolean(
                      isClinicalNote &&
                      linkedDocument,
                    )

                  return (
                    <div
                      key={event.id}
                      className={
                        `doctor-history-timeline-item${
                          canOpenDocument
                            ? ' is-clickable'
                            : ''
                        }`
                      }
                    >
                      <span className="doctor-history-timeline-dot" />

                      <div>
                        <strong>
                          {event.event_type}
                        </strong>

                        <span>
                          {formatDate(
                            event.occurred_at,
                          )}
                        </span>

                        {linkedDocument && (
                          <span className="doctor-history-timeline-document">
                            {linkedDocument.document_type}
                            {' · '}
                            v{linkedDocument.version}
                          </span>
                        )}

                        {canOpenDocument && (
                          <>
                            <button
                              type="button"
                              className="doctor-history-timeline-action"
                              onClick={() =>
                                setSelectedDocumentId(
                                  selectedDocumentId ===
                                    clinicalDocumentId
                                    ? null
                                    : clinicalDocumentId,
                                )
                              }
                            >
                              {selectedDocumentId ===
                              clinicalDocumentId
                                ? 'Hide clinical document'
                                : 'View clinical document →'}
                            </button>

                            {selectedDocumentId ===
                              clinicalDocumentId &&
                              linkedDocument && (
                                <div className="doctor-history-document-viewer">
                                  {linkedDocument.document_type ===
                                  'NURSING_INTAKE' ? (
                                    <NursingHistoricalDocumentViewer
                                      document={
                                        linkedDocument
                                      }
                                    />
                                  ) : (
                                    <SignedClinicalDocumentSummary
                                      document={
                                        linkedDocument
                                      }
                                    />
                                  )}
                                </div>
                              )}
                          </>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </section>

        </div>
      )}
    </section>
  )
}
