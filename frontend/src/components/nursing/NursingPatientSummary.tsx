import type { Episode } from '../../api/episodes'
import type {
  ClinicalEvent,
  Encounter,
} from '../../api/encounters'
import type { Patient } from '../../types'


interface PreviousVisit {
  episode: Episode
  encounters: Encounter[]
  eventsByEncounter: Record<
    string,
    ClinicalEvent[]
  >
}


interface Props {
  episode: Episode
  encounter: Encounter

  patient: Patient | null
  loadingPatient: boolean

  previousEpisodes: Episode[]
  loadingPreviousEpisodes: boolean

  previousVisits: PreviousVisit[]
  loadingPreviousVisits: boolean
}


function formatDate(
  value: string | null,
): string {
  if (!value) {
    return '—'
  }

  return new Date(
    value,
  ).toLocaleDateString()
}


function formatDateTime(
  value: string,
): string {
  return new Date(
    value,
  ).toLocaleString()
}


function formatEventType(
  value: string,
): string {
  return value
    .replaceAll('_', ' ')
    .toLowerCase()
    .replace(
      /\b\w/g,
      character =>
        character.toUpperCase(),
    )
}


function formatEventPayload(
  payload: Record<string, unknown> | null,
): string {
  if (!payload) {
    return ''
  }

  const entries =
    Object.entries(payload)

  if (entries.length === 0) {
    return ''
  }

  return entries
    .map(
      ([key, value]) => {
        const label =
          key
            .replaceAll('_', ' ')
            .replace(
              /\b\w/g,
              character =>
                character.toUpperCase(),
            )

        let formattedValue: string

        if (
          value === null ||
          value === undefined
        ) {
          formattedValue = '—'
        } else if (
          Array.isArray(value)
        ) {
          formattedValue =
            value.join(', ')
        } else if (
          typeof value === 'object'
        ) {
          formattedValue =
            JSON.stringify(value)
        } else {
          formattedValue =
            String(value)
        }

        return `${label}: ${formattedValue}`
      },
    )
    .join(' · ')
}


function ContextValue({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <div className="nursing-vital-card">
      <span>
        {label}
      </span>

      <strong>
        {value || '—'}
      </strong>
    </div>
  )
}


export default function NursingPatientSummary({
  episode,
  encounter,
  patient,
  loadingPatient,

  previousEpisodes,
  loadingPreviousEpisodes,

  previousVisits,
  loadingPreviousVisits,
}: Props) {
  return (
    <>
      {/* ================================================================== */}
      {/* Patient Context                                                   */}
      {/* ================================================================== */}

      <section className="nursing-section">

        <div className="nursing-section-heading">

          <div>
            <p className="eyebrow">
              PATIENT CONTEXT
            </p>

            <h3>
              Clinical background
            </h3>

            <p>
              Information that may be relevant
              to the current nursing assessment.
            </p>
          </div>

        </div>


        {loadingPatient && (
          <div className="admin-empty-state">
            Loading patient information...
          </div>
        )}


        {!loadingPatient &&
          patient && (
            <div className="nursing-section-grid">

              <ContextValue
                label="Blood group"
                value={
                  patient.blood_group ??
                  '—'
                }
              />


              <ContextValue
                label="Genotype"
                value={
                  patient.genotype ??
                  '—'
                }
              />


              <ContextValue
                label="Phone"
                value={
                  patient.phone_number ??
                  '—'
                }
              />


              <ContextValue
                label="Allergies"
                value="See nursing intake"
              />


              <ContextValue
                label="Next of kin"
                value={
                  patient.next_of_kin_name ??
                  '—'
                }
              />


              <ContextValue
                label="Relationship"
                value={
                  patient
                    .next_of_kin_relationship ??
                  '—'
                }
              />

            </div>
          )}


        {!loadingPatient &&
          !patient && (
            <div className="admin-empty-state">
              Patient information could not
              be loaded.
            </div>
          )}

      </section>


      {/* ================================================================== */}
      {/* Current Care Context                                               */}
      {/* ================================================================== */}

      <section className="nursing-section">

        <div className="nursing-section-heading">

          <div>
            <p className="eyebrow">
              CURRENT CARE
            </p>

            <h3>
              Episode and encounter
            </h3>
          </div>

        </div>


        <div className="nursing-section-grid">

          <ContextValue
            label="Episode"
            value={
              episode.episode_number
            }
          />


          <ContextValue
            label="Visit"
            value={
              episode.title
            }
          />


          <ContextValue
            label="Encounter"
            value={
              encounter.title
            }
          />


          <ContextValue
            label="Started"
            value={
              formatDateTime(
                encounter.started_at,
              )
            }
          />


          <ContextValue
            label="Encounter status"
            value={
              encounter.status
            }
          />


          <ContextValue
            label="Episode opened"
            value={
              formatDateTime(
                episode.opened_at,
              )
            }
          />

        </div>

      </section>


      {/* ================================================================== */}
      {/* Previous Visits                                                   */}
      {/* ================================================================== */}

      <section className="nursing-section nursing-history">

        <div className="nursing-section-heading">

          <div>
            <p className="eyebrow">
              HISTORY
            </p>

            <h3>
              Previous visits
            </h3>

            <p>
              Review prior episodes, encounters,
              and recorded clinical events.
            </p>
          </div>

        </div>


        {loadingPreviousEpisodes && (
          <div className="admin-empty-state">
            Loading previous visits...
          </div>
        )}


        {!loadingPreviousEpisodes &&
          previousEpisodes.length === 0 && (
            <div className="admin-empty-state">
              No previous visits found for
              this patient.
            </div>
          )}


        {!loadingPreviousEpisodes &&
          previousEpisodes.length > 0 && (

            <div>

              {previousEpisodes.map(
                previousEpisode => {

                  const visit =
                    previousVisits.find(
                      item =>
                        item.episode.id ===
                        previousEpisode.id,
                    )


                  return (
                    <div
                      key={
                        previousEpisode.id
                      }
                      className="nursing-history-item"
                    >

                      <div className="nursing-section-heading">

                        <div>

                          <p className="eyebrow">
                            PREVIOUS EPISODE
                          </p>

                          <h3>
                            {
                              previousEpisode.title
                            }
                          </h3>

                          <p>
                            Episode{' '}
                            {
                              previousEpisode
                                .episode_number
                            }
                          </p>

                        </div>


                        <div
                          style={{
                            textAlign:
                              'right',
                          }}
                        >

                          <strong>
                            {
                              previousEpisode
                                .status
                            }
                          </strong>

                          <p>
                            Opened:{' '}
                            {formatDate(
                              previousEpisode
                                .opened_at,
                            )}
                          </p>

                          {previousEpisode.closed_at && (
                            <p>
                              Closed:{' '}
                              {formatDate(
                                previousEpisode
                                  .closed_at,
                              )}
                            </p>
                          )}

                        </div>

                      </div>


                      {visit && (
                        <div>

                          <p className="eyebrow">
                            ENCOUNTERS
                          </p>


                          {visit.encounters.length ===
                            0 && (
                              <p>
                                No encounters
                                recorded for
                                this episode.
                              </p>
                            )}


                          <div>

                            {visit.encounters.map(
                              previousEncounter => {

                                const events =
                                  visit
                                    .eventsByEncounter[
                                    previousEncounter
                                      .id
                                  ] ??
                                  []


                                return (
                                  <div
                                    key={
                                      previousEncounter
                                        .id
                                    }
                                    className="nursing-history-item"
                                    style={{
                                      marginTop:
                                        '10px',
                                    }}
                                  >

                                    <strong>
                                      {
                                        previousEncounter
                                          .title
                                      }
                                    </strong>


                                    <p>
                                      Started:{' '}
                                      {formatDateTime(
                                        previousEncounter
                                          .started_at,
                                      )}
                                    </p>


                                    <p>
                                      Status:{' '}
                                      {
                                        previousEncounter
                                          .status
                                      }
                                    </p>


                                    {events.length >
                                      0 && (
                                        <div
                                          style={{
                                            marginTop:
                                              '12px',
                                          }}
                                        >

                                          <p className="eyebrow">
                                            CLINICAL EVENTS
                                          </p>


                                          <div>

                                            {events.map(
                                              event => (
                                                <div
                                                  key={
                                                    event.id
                                                  }
                                                  className="nursing-history-item"
                                                  style={{
                                                    marginTop:
                                                      '8px',
                                                    background:
                                                      '#f8fafb',
                                                  }}
                                                >

                                                  <strong>
                                                    {formatEventType(
                                                      event.event_type,
                                                    )}
                                                  </strong>


                                                  <p>
                                                    {formatDateTime(
                                                      event.occurred_at,
                                                    )}
                                                  </p>


                                                  {event.payload && (
                                                    <p>
                                                      {formatEventPayload(
                                                        event.payload,
                                                      )}
                                                    </p>
                                                  )}

                                                </div>
                                              ),
                                            )}

                                          </div>

                                        </div>
                                      )}


                                    {events.length ===
                                      0 && (
                                        <p
                                          style={{
                                            marginTop:
                                              '8px',
                                          }}
                                        >
                                          No clinical
                                          events
                                          recorded for
                                          this encounter.
                                        </p>
                                      )}

                                  </div>
                                )
                              },
                            )}

                          </div>

                        </div>
                      )}


                      {!visit &&
                        loadingPreviousVisits && (
                          <p
                            style={{
                              marginTop:
                                '12px',
                            }}
                          >
                            Loading clinical
                            history...
                          </p>
                        )}


                      {!visit &&
                        !loadingPreviousVisits && (
                          <p
                            style={{
                              marginTop:
                                '12px',
                            }}
                          >
                            Clinical history is
                            not available for
                            this visit.
                          </p>
                        )}

                    </div>
                  )
                },
              )}

            </div>
          )}

      </section>

    </>
  )
}
