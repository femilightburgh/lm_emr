import type { Episode } from '../../api/episodes'


interface Props {
  waitingEpisodes: Episode[]
  activeEpisodes: Episode[]
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


function getPatientName(
  episode: Episode,
  patientNames: Record<string, string>,
): string {
  return (
    patientNames[episode.patient_id] ??
    'Patient'
  )
}


export default function NursingQueue({
  waitingEpisodes,
  activeEpisodes,
  patientNames,

  loading,
  loadingEncounter,
  startingEpisodeId,

  onStartNursing,
  onContinueNursing,
}: Props) {
  return (
    <div className="nursing-queue">

      {/* ================================================================== */}
      {/* Waiting for Nursing                                               */}
      {/* ================================================================== */}

      <section className="nursing-queue-section">

        <div className="nursing-queue-header">

          <div>

            <p className="eyebrow">
              QUEUE
            </p>

            <h3>
              Waiting for nursing
            </h3>

          </div>


          <span className="nursing-queue-count">
            {waitingEpisodes.length}
          </span>

        </div>


        {loading ? (
          <div className="admin-empty-state">
            Loading nursing queue...
          </div>
        ) : waitingEpisodes.length === 0 ? (
          <div className="admin-empty-state">
            No patients are currently waiting
            for nursing.
          </div>
        ) : (
          <div className="nursing-queue-list">

            {waitingEpisodes.map(
              episode => (
                <article
                  key={episode.id}
                  className="nursing-queue-item"
                >

                  <div className="nursing-queue-patient">

                    <strong>
                      {getPatientName(
                        episode,
                        patientNames,
                      )}
                    </strong>

                    <p>
                      {episode.title}
                    </p>

                  </div>


                  <span className="nursing-queue-status">
                    Waiting
                  </span>


                  <button
                    type="button"
                    className="primary-button"
                    disabled={
                      startingEpisodeId ===
                      episode.id
                    }
                    onClick={() =>
                      onStartNursing(
                        episode.id,
                      )
                    }
                  >
                    {startingEpisodeId ===
                    episode.id
                      ? 'Starting...'
                      : 'Start Nursing'}
                  </button>

                </article>
              ),
            )}

          </div>
        )}

      </section>


      {/* ================================================================== */}
      {/* Nursing in Progress                                               */}
      {/* ================================================================== */}

      <section className="nursing-queue-section">

        <div className="nursing-queue-header">

          <div>

            <p className="eyebrow">
              ACTIVE
            </p>

            <h3>
              Nursing in progress
            </h3>

          </div>


          <span className="nursing-queue-count">
            {activeEpisodes.length}
          </span>

        </div>


        {activeEpisodes.length === 0 ? (
          <div className="admin-empty-state">
            No nursing assessments are
            currently in progress.
          </div>
        ) : (
          <div className="nursing-queue-list">

            {activeEpisodes.map(
              episode => (
                <article
                  key={episode.id}
                  className="nursing-queue-item"
                >

                  <div className="nursing-queue-patient">

                    <strong>
                      {getPatientName(
                        episode,
                        patientNames,
                      )}
                    </strong>

                    <p>
                      {episode.title}
                    </p>

                  </div>


                  <span className="nursing-queue-status">
                    Nursing in progress
                  </span>


                  <button
                    type="button"
                    className="primary-button"
                    disabled={
                      loadingEncounter
                    }
                    onClick={() =>
                      onContinueNursing(
                        episode,
                      )
                    }
                  >
                    {loadingEncounter
                      ? 'Opening...'
                      : 'Continue'}
                  </button>

                </article>
              ),
            )}

          </div>
        )}

      </section>

    </div>
  )
}
