import type { Episode } from '../../api/episodes'


interface Props {
  waitingEpisodes: Episode[]
  activeEpisodes: Episode[]
  admittedEpisodes: Episode[]
  patientNames: Record<string, string>

  loading: boolean
  loadingEncounter: boolean
  startingEpisodeId: string | null

  onStartNursing: (
    episodeId: string,
  ) => void

  onContinueNursing: (
    episode: Episode,
  ) => void
}


type QueueState =
  | 'WAITING'
  | 'IN_PROGRESS'
  | 'ADMITTED'


interface QueueRowProps {
  episode: Episode
  patientNames: Record<string, string>
  state: QueueState
  actionLabel: string
  disabled: boolean
  onAction: () => void
}


function getPatientName(
  episode: Episode,
  patientNames: Record<string, string>,
): string {
  return (
    patientNames[episode.patient_id] ??
    'Patient'
  )
}


function getInitials(
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


function getStateLabel(
  state: QueueState,
): string {
  switch (state) {
    case 'WAITING':
      return 'Waiting'

    case 'IN_PROGRESS':
      return 'In progress'

    case 'ADMITTED':
      return 'Admitted'
  }
}


function getStateDescription(
  state: QueueState,
): string {
  switch (state) {
    case 'WAITING':
      return 'Nursing assessment has not started.'

    case 'IN_PROGRESS':
      return 'Nursing assessment is already in progress.'

    case 'ADMITTED':
      return 'Patient is currently on admission.'
  }
}


function getEpisodeDescription(
  episode: Episode,
  state: QueueState,
): string {
  if (state === 'ADMITTED') {
    return 'Current admission'
  }

  return episode.title
}


function QueueRow({
  episode,
  patientNames,
  state,
  actionLabel,
  disabled,
  onAction,
}: QueueRowProps) {
  const patientName =
    getPatientName(
      episode,
      patientNames,
    )

  return (
    <article
      className={`nursing-command-row nursing-command-row-${state.toLowerCase()}`}
    >

      <div className="nursing-command-patient">

        <span className="nursing-command-avatar">
          {getInitials(
            patientName,
          )}
        </span>

        <div className="nursing-command-patient-copy">

          <strong>
            {patientName}
          </strong>

          <small>
            {episode.episode_number}
            {' · '}
            {getEpisodeDescription(
              episode,
              state,
            )}
          </small>

          <span className="nursing-command-description">
            {getStateDescription(
              state,
            )}
          </span>

        </div>

      </div>


      <span
        className={`nursing-command-status nursing-command-status-${state.toLowerCase()}`}
      >
        {getStateLabel(
          state,
        )}
      </span>


      <button
        type="button"
        className="primary-button nursing-command-action"
        disabled={disabled}
        onClick={onAction}
      >
        {actionLabel}
        <span aria-hidden="true">
          →
        </span>
      </button>

    </article>
  )
}


export default function NursingQueue({
  waitingEpisodes,
  activeEpisodes,
  admittedEpisodes,
  patientNames,
  loading,
  loadingEncounter,
  startingEpisodeId,
  onStartNursing,
  onContinueNursing,
}: Props) {
  const uniquePatientIds =
    new Set(
      [
        ...waitingEpisodes,
        ...activeEpisodes,
        ...admittedEpisodes,
      ].map(
        episode =>
          episode.patient_id,
      ),
    )

  const totalPatients =
    uniquePatientIds.size

  const activeWork =
    waitingEpisodes.length +
    activeEpisodes.length

  return (
    <div className="nursing-command-centre">

      <section className="nursing-workload-metrics">

        <article className="nursing-workload-metric nursing-workload-metric-primary">

          <strong>
            {totalPatients}
          </strong>

          <span>
            Patients
          </span>

        </article>


        <article className="nursing-workload-metric nursing-workload-metric-attention">

          <strong>
            {activeWork}
          </strong>

          <span>
            Open nursing work
          </span>

        </article>


        <article className="nursing-workload-metric">

          <strong>
            {waitingEpisodes.length}
          </strong>

          <span>
            Waiting
          </span>

        </article>


        <article className="nursing-workload-metric">

          <strong>
            {admittedEpisodes.length}
          </strong>

          <span>
            On admission
          </span>

        </article>

      </section>


      <section className="nursing-work-queue">

        <header className="nursing-command-header">

          <div>

            <p className="eyebrow">
              WORK QUEUE
            </p>

            <h2>
              Nursing workload
            </h2>

            <p>
              Start new nursing assessments, continue active work,
              or open an inpatient chart.
            </p>

          </div>

        </header>


        {loading ? (

          <div className="nursing-command-empty">
            Loading nursing workload...
          </div>

        ) : (

          <>

            {/* ========================================================== */}
            {/* WAITING                                                     */}
            {/* ========================================================== */}

            <section className="nursing-command-section nursing-command-section-priority">

              <header>

                <div>

                  <p className="eyebrow">
                    NEXT TO WORK
                  </p>

                  <h3>
                    Waiting for nursing
                  </h3>

                  <p className="nursing-command-section-help">
                    Patients whose nursing assessment has not started.
                  </p>

                </div>

                <span>
                  {waitingEpisodes.length}
                </span>

              </header>


              {waitingEpisodes.length === 0 ? (

                <div className="nursing-command-empty">
                  No patients are currently waiting for nursing.
                </div>

              ) : (

                waitingEpisodes.map(
                  episode => (
                    <QueueRow
                      key={episode.id}
                      episode={episode}
                      patientNames={patientNames}
                      state="WAITING"
                      actionLabel={
                        startingEpisodeId === episode.id
                          ? 'Starting...'
                          : 'Start nursing'
                      }
                      disabled={
                        startingEpisodeId === episode.id ||
                        loadingEncounter
                      }
                      onAction={() =>
                        onStartNursing(
                          episode.id,
                        )
                      }
                    />
                  ),
                )

              )}

            </section>


            {/* ========================================================== */}
            {/* ACTIVE                                                      */}
            {/* ========================================================== */}

            <section className="nursing-command-section">

              <header>

                <div>

                  <p className="eyebrow">
                    ACTIVE WORK
                  </p>

                  <h3>
                    Nursing in progress
                  </h3>

                  <p className="nursing-command-section-help">
                    Continue assessments that have already been started.
                  </p>

                </div>

                <span>
                  {activeEpisodes.length}
                </span>

              </header>


              {activeEpisodes.length === 0 ? (

                <div className="nursing-command-empty">
                  No nursing assessments are currently in progress.
                </div>

              ) : (

                activeEpisodes.map(
                  episode => (
                    <QueueRow
                      key={episode.id}
                      episode={episode}
                      patientNames={patientNames}
                      state="IN_PROGRESS"
                      actionLabel={
                        loadingEncounter
                          ? 'Opening...'
                          : 'Continue'
                      }
                      disabled={
                        loadingEncounter
                      }
                      onAction={() =>
                        onContinueNursing(
                          episode,
                        )
                      }
                    />
                  ),
                )

              )}

            </section>


            {/* ========================================================== */}
            {/* INPATIENTS                                                   */}
            {/* ========================================================== */}

            <section className="nursing-command-section">

              <header>

                <div>

                  <p className="eyebrow">
                    INPATIENTS
                  </p>

                  <h3>
                    Patients on admission
                  </h3>

                  <p className="nursing-command-section-help">
                    Open an admitted patient's inpatient nursing workspace.
                  </p>

                </div>

                <span>
                  {admittedEpisodes.length}
                </span>

              </header>


              {admittedEpisodes.length === 0 ? (

                <div className="nursing-command-empty">
                  No patients are currently on admission.
                </div>

              ) : (

                admittedEpisodes.map(
                  episode => (
                    <QueueRow
                      key={episode.id}
                      episode={episode}
                      patientNames={patientNames}
                      state="ADMITTED"
                      actionLabel={
                        loadingEncounter
                          ? 'Opening...'
                          : 'Open chart'
                      }
                      disabled={
                        loadingEncounter
                      }
                      onAction={() =>
                        onContinueNursing(
                          episode,
                        )
                      }
                    />
                  ),
                )

              )}

            </section>

          </>

        )}

      </section>

    </div>
  )
}
